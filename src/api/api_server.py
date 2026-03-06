import json
import logging
import os
import tempfile
import time
import uuid
from asyncio import Lock
from collections import defaultdict
from contextlib import asynccontextmanager
from pathlib import Path
from threading import Lock as ThreadLock
from typing import Optional

from fastapi import APIRouter, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel, Field

from src.config.settings import Settings
from src.core.rag_system import RAGSystem
from src.utils.utils import load_env_vars

settings: Settings = load_env_vars()

rag_instance: Optional[RAGSystem] = None
rag_lock = Lock()
rate_lock = ThreadLock()
request_counters: dict[tuple[str, int], int] = defaultdict(int)

logger = logging.getLogger("hylreg.api")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

HTTP_REQUESTS_TOTAL = Counter(
    "hylreg_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)
HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "hylreg_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
)

api_v1 = APIRouter(prefix="/api/v1", tags=["v1"])
MUTATING_AND_QUERY_PATHS = {
    "/process-document/",
    "/query/",
    "/add-document/",
    "/save-index/",
    "/reload-index/",
}
PUBLIC_PATHS = {
    "/",
    "/health",
    "/metrics",
    "/api/v1/",
    "/api/v1/health",
    "/api/v1/metrics",
}


@asynccontextmanager
async def lifespan(_: FastAPI):
    global rag_instance
    try:
        rag_instance = RAGSystem(settings=settings)
        logger.info("RAG system initialized")
    except Exception as exc:
        logger.exception("RAG system initialization failed: %s", exc)
    yield


app = FastAPI(
    title="HylReg-RAG API",
    description="基于检索增强生成(Retrieval-Augmented Generation)的API服务",
    version="1.0.0",
    lifespan=lifespan,
)


def _is_protected_path(path: str) -> bool:
    for suffix in MUTATING_AND_QUERY_PATHS:
        if path == suffix or path == f"/api/v1{suffix}":
            return True
    return False


def _is_legacy_path(path: str) -> bool:
    if path.startswith("/api/v1"):
        return False
    if path == "/":
        return True
    if path in {"/health", "/metrics"}:
        return True
    return path in MUTATING_AND_QUERY_PATHS


def _legacy_successor_path(path: str) -> str:
    if path == "/":
        return "/api/v1/"
    return f"/api/v1{path}"


def _enforce_api_auth(request: Request):
    if not settings.api_auth_token:
        return
    if request.url.path in PUBLIC_PATHS:
        return
    if not _is_protected_path(request.url.path):
        return

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="缺少或无效的Authorization头")
    token = auth_header.removeprefix("Bearer ").strip()
    if token != settings.api_auth_token:
        raise HTTPException(status_code=401, detail="鉴权失败")


def _enforce_rate_limit(request: Request):
    if settings.api_rate_limit_per_minute <= 0:
        return
    if request.url.path in PUBLIC_PATHS:
        return
    if not _is_protected_path(request.url.path):
        return

    forwarded = request.headers.get("X-Forwarded-For", "")
    client_ip = (
        forwarded.split(",")[0].strip()
        if forwarded
        else (request.client.host if request.client else "unknown")
    )
    current_window = int(time.time() // 60)
    key = (client_ip, current_window)

    with rate_lock:
        request_counters[key] += 1
        total = request_counters[key]
        stale_windows = [
            k
            for k in request_counters
            if k[0] == client_ip and k[1] < current_window - 1
        ]
        for stale_key in stale_windows:
            request_counters.pop(stale_key, None)

    if total > settings.api_rate_limit_per_minute:
        raise HTTPException(status_code=429, detail="请求过于频繁，请稍后重试")


def _attach_legacy_headers(path: str, response: Response):
    if not _is_legacy_path(path):
        return
    response.headers["Deprecation"] = "true"
    response.headers["Sunset"] = settings.api_legacy_sunset
    response.headers["Link"] = (
        f'<{_legacy_successor_path(path)}>; rel="successor-version"'
    )
    response.headers["Warning"] = '299 - "Deprecated API path, use /api/v1 equivalents"'


@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    method = request.method
    path = request.url.path
    start = time.perf_counter()

    response = None
    status = 500
    try:
        _enforce_api_auth(request)
        _enforce_rate_limit(request)
        response = await call_next(request)
        status = response.status_code
        return response
    except HTTPException as exc:
        status = exc.status_code
        response = JSONResponse(
            status_code=exc.status_code, content={"detail": exc.detail}
        )
        return response
    finally:
        elapsed = time.perf_counter() - start
        HTTP_REQUESTS_TOTAL.labels(method=method, path=path, status=str(status)).inc()
        HTTP_REQUEST_DURATION_SECONDS.labels(method=method, path=path).observe(elapsed)
        payload = {
            "event": "request",
            "request_id": request_id,
            "method": method,
            "path": path,
            "status": status,
            "duration_ms": round(elapsed * 1000, 2),
        }
        logger.info(json.dumps(payload, ensure_ascii=False))
        if response is not None:
            response.headers["X-Request-ID"] = request_id
            _attach_legacy_headers(path, response)


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1)


def _require_rag() -> RAGSystem:
    if not rag_instance:
        raise HTTPException(status_code=500, detail="RAG系统未正确初始化")
    return rag_instance


async def _save_upload_to_temp(file: UploadFile) -> tuple[str, str]:
    filename = file.filename or "uploaded_file"
    suffix = Path(filename).suffix.lower()
    if suffix not in settings.api_allowed_extensions:
        allowed = ", ".join(settings.api_allowed_extensions)
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {suffix}，仅支持 {allowed}",
        )

    temp_dir = tempfile.mkdtemp()
    temp_file_path = os.path.join(temp_dir, filename)
    max_bytes = settings.api_max_upload_size_mb * 1024 * 1024
    total = 0

    try:
        with open(temp_file_path, "wb") as buffer:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > max_bytes:
                    raise HTTPException(
                        status_code=413,
                        detail=f"文件大小超过限制（{settings.api_max_upload_size_mb}MB）",
                    )
                buffer.write(chunk)
    except Exception:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
        raise
    finally:
        await file.close()

    return temp_dir, temp_file_path


def _cleanup_temp_dir(temp_dir: str):
    if not os.path.exists(temp_dir):
        return
    for root, _, files in os.walk(temp_dir, topdown=False):
        for name in files:
            try:
                os.remove(os.path.join(root, name))
            except FileNotFoundError:
                pass
        try:
            os.rmdir(root)
        except OSError:
            pass


@app.get("/")
@api_v1.get("/")
async def root():
    return {"message": "欢迎使用HylReg-RAG API", "status": "running", "version": "v1"}


@app.post("/process-document/")
@api_v1.post("/process-document/")
async def process_document(file: UploadFile = File(...)):
    rag = _require_rag()
    temp_dir, temp_file_path = await _save_upload_to_temp(file)
    try:
        async with rag_lock:
            rag.process_and_store(temp_file_path)
        return JSONResponse(
            status_code=200,
            content={"message": f"成功处理文档: {file.filename}"},
        )
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"处理文档时出错: {exc}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"处理文档时出错: {exc}")
    finally:
        _cleanup_temp_dir(temp_dir)


@app.post("/query/")
@api_v1.post("/query/")
async def query(request: QueryRequest):
    rag = _require_rag()
    try:
        async with rag_lock:
            result = rag.query(request.question)
        return JSONResponse(
            status_code=200,
            content={
                "question": request.question,
                "answer": result["answer"],
                "sources": result["source_documents"],
            },
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"查询时出错: {exc}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"查询时出错: {exc}")


@app.post("/add-document/")
@api_v1.post("/add-document/")
async def add_document(file: UploadFile = File(...)):
    rag = _require_rag()
    temp_dir, temp_file_path = await _save_upload_to_temp(file)
    try:
        async with rag_lock:
            rag.add_document(temp_file_path)
        return JSONResponse(
            status_code=200,
            content={"message": f"成功添加文档: {file.filename} 至现有知识库"},
        )
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"添加文档时出错: {exc}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"添加文档时出错: {exc}")
    finally:
        _cleanup_temp_dir(temp_dir)


@app.get("/health")
@api_v1.get("/health")
async def health_check():
    if not rag_instance:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "reason": "RAG instance not initialized"},
        )

    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "vectorstore_loaded": rag_instance.vectorstore is not None,
            "vectorstore_dir": settings.vectorstore_dir,
        },
    )


@app.post("/save-index/")
@api_v1.post("/save-index/")
async def save_index():
    rag = _require_rag()
    try:
        async with rag_lock:
            rag.save_vectorstore()
        return JSONResponse(
            status_code=200,
            content={"message": f"向量索引已保存到 {settings.vectorstore_dir}"},
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"保存索引失败: {exc}")


@app.post("/reload-index/")
@api_v1.post("/reload-index/")
async def reload_index():
    rag = _require_rag()
    try:
        async with rag_lock:
            rag.load_vectorstore()
        return JSONResponse(
            status_code=200,
            content={
                "message": "索引加载完成",
                "vectorstore_loaded": rag.vectorstore is not None,
                "vectorstore_dir": settings.vectorstore_dir,
            },
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"重载索引失败: {exc}")


@app.get("/metrics")
@api_v1.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


app.include_router(api_v1)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
