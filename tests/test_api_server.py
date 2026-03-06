import importlib
from dataclasses import replace

import pytest

fastapi = pytest.importorskip("fastapi")
pytest.importorskip("langchain_openai")
pytest.importorskip("langchain_community")
from fastapi.testclient import TestClient


class FakeRAG:
    def __init__(self):
        self.vectorstore = object()
        self.vectorstore_dir = "data/vectorstore"

    def process_and_store(self, file_path: str):
        return None

    def add_document(self, file_path: str):
        return None

    def query(self, question: str):
        return {"answer": f"echo:{question}", "source_documents": ["doc-1"]}

    def save_vectorstore(self):
        return None

    def load_vectorstore(self):
        return None


def _build_client(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    module = importlib.import_module("src.api.api_server")
    module = importlib.reload(module)
    module.rag_instance = FakeRAG()
    module.settings = replace(
        module.settings,
        api_allowed_extensions=(".txt",),
        api_max_upload_size_mb=1,
    )
    return TestClient(module.app)


def test_reject_unsupported_extension(monkeypatch):
    client = _build_client(monkeypatch)
    response = client.post(
        "/process-document/",
        files={"file": ("bad.pdf", b"hello", "application/pdf")},
    )
    assert response.status_code == 400


def test_reject_too_large_upload(monkeypatch):
    client = _build_client(monkeypatch)
    response = client.post(
        "/process-document/",
        files={"file": ("big.txt", b"a" * (2 * 1024 * 1024), "text/plain")},
    )
    assert response.status_code == 413


def test_query_success(monkeypatch):
    client = _build_client(monkeypatch)
    response = client.post("/query/", json={"question": "hello"})
    assert response.status_code == 200
    assert response.json()["answer"] == "echo:hello"
