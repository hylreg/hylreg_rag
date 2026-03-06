import os
import tempfile
from asyncio import Lock
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.config.settings import Settings
from src.core.rag_system import RAGSystem
from src.utils.utils import load_env_vars


settings: Settings = load_env_vars()

# 创建全局RAG实例
rag_instance: Optional[RAGSystem] = None
rag_lock = Lock()

@asynccontextmanager
async def lifespan(_: FastAPI):
    global rag_instance
    try:
        rag_instance = RAGSystem(settings=settings)
        print("RAG系统初始化成功")
    except Exception as e:
        print(f"RAG系统初始化失败: {str(e)}")
    yield


# 创建FastAPI应用
app = FastAPI(
    title="HylReg-RAG API",
    description="基于检索增强生成(Retrieval-Augmented Generation)的API服务",
    version="1.0.0",
    lifespan=lifespan,
)


class QueryRequest(BaseModel):
    """
    查询请求的数据模型
    """
    question: str = Field(..., min_length=1)


def _require_rag() -> RAGSystem:
    if not rag_instance:
        raise HTTPException(status_code=500, detail="RAG系统未正确初始化")
    return rag_instance


async def _save_upload_to_temp(file: UploadFile) -> tuple[str, str]:
    filename = file.filename or ""
    suffix = Path(filename).suffix.lower()
    if suffix not in settings.api_allowed_extensions:
        allowed = ", ".join(settings.api_allowed_extensions)
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {suffix}，仅支持 {allowed}")

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
async def root():
    """
    根路径，返回API信息
    """
    return {"message": "欢迎使用HylReg-RAG API", "status": "running"}


@app.post("/process-document/")
async def process_document(file: UploadFile = File(...)):
    """
    上传并处理文档
    """
    rag = _require_rag()
    temp_dir, temp_file_path = await _save_upload_to_temp(file)

    try:
        async with rag_lock:
            rag.process_and_store(temp_file_path)
        return JSONResponse(
            status_code=200,
            content={"message": f"成功处理文档: {file.filename}"}
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"处理文档时出错: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理文档时出错: {str(e)}")
    finally:
        _cleanup_temp_dir(temp_dir)


@app.post("/query/")
async def query(request: QueryRequest):
    """
    查询端点
    """
    rag = _require_rag()
    try:
        async with rag_lock:
            result = rag.query(request.question)
        return JSONResponse(
            status_code=200,
            content={
                "question": request.question,
                "answer": result["answer"],
                "sources": result["source_documents"]
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"查询时出错: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询时出错: {str(e)}")


@app.post("/add-document/")
async def add_document(file: UploadFile = File(...)):
    """
    向现有知识库添加文档
    """
    rag = _require_rag()
    temp_dir, temp_file_path = await _save_upload_to_temp(file)

    try:
        async with rag_lock:
            rag.add_document(temp_file_path)
        return JSONResponse(
            status_code=200,
            content={"message": f"成功添加文档: {file.filename} 至现有知识库"}
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"添加文档时出错: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加文档时出错: {str(e)}")
    finally:
        _cleanup_temp_dir(temp_dir)


@app.get("/health")
async def health_check():
    """
    健康检查端点
    """
    if not rag_instance:
        return JSONResponse(status_code=503, content={"status": "unhealthy", "reason": "RAG instance not initialized"})
    
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "vectorstore_loaded": rag_instance.vectorstore is not None,
            "vectorstore_dir": settings.vectorstore_dir,
        },
    )


@app.post("/save-index/")
async def save_index():
    rag = _require_rag()
    try:
        async with rag_lock:
            rag.save_vectorstore()
        return JSONResponse(
            status_code=200,
            content={"message": f"向量索引已保存到 {settings.vectorstore_dir}"},
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存索引失败: {str(e)}")


@app.post("/reload-index/")
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重载索引失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
