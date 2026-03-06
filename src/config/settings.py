import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


def _as_bool(value: str, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _as_int(value: str, default: int) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    openai_api_base: str | None
    openai_model: str
    temperature: float
    chunk_size: int
    chunk_overlap: int
    retrieval_k: int
    vectorstore_dir: str
    auto_persist: bool
    api_max_upload_size_mb: int
    api_allowed_extensions: tuple[str, ...]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    env_path = Path.cwd() / ".env"
    if env_path.exists():
        load_dotenv(env_path)

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("请设置 OPENAI_API_KEY 环境变量")

    allowed = os.getenv("API_ALLOWED_EXTENSIONS", ".pdf,.txt,.docx")
    allowed_extensions = tuple(
        ext.strip().lower() for ext in allowed.split(",") if ext.strip()
    )

    return Settings(
        openai_api_key=api_key,
        openai_api_base=os.getenv("OPENAI_API_BASE"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo-instruct"),
        temperature=float(os.getenv("OPENAI_TEMPERATURE", "0")),
        chunk_size=_as_int(os.getenv("RAG_CHUNK_SIZE"), 1000),
        chunk_overlap=_as_int(os.getenv("RAG_CHUNK_OVERLAP"), 200),
        retrieval_k=_as_int(os.getenv("RAG_RETRIEVAL_K"), 4),
        vectorstore_dir=os.getenv("RAG_VECTORSTORE_DIR", "data/vectorstore"),
        auto_persist=_as_bool(os.getenv("RAG_AUTO_PERSIST"), True),
        api_max_upload_size_mb=_as_int(os.getenv("API_MAX_UPLOAD_SIZE_MB"), 20),
        api_allowed_extensions=allowed_extensions or (".pdf", ".txt", ".docx"),
    )

