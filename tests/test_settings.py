from src.config.settings import get_settings


def test_get_settings_from_environment(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("RAG_CHUNK_SIZE", "512")
    monkeypatch.setenv("RAG_CHUNK_OVERLAP", "64")
    monkeypatch.setenv("RAG_RETRIEVAL_K", "2")
    monkeypatch.setenv("RAG_VECTORSTORE_DIR", "tmp/vector")
    monkeypatch.setenv("API_MAX_UPLOAD_SIZE_MB", "8")
    monkeypatch.setenv("API_ALLOWED_EXTENSIONS", ".txt,.pdf")

    settings = get_settings()

    assert settings.openai_api_key == "test-key"
    assert settings.chunk_size == 512
    assert settings.chunk_overlap == 64
    assert settings.retrieval_k == 2
    assert settings.vectorstore_dir == "tmp/vector"
    assert settings.api_max_upload_size_mb == 8
    assert settings.api_allowed_extensions == (".txt", ".pdf")

    get_settings.cache_clear()
