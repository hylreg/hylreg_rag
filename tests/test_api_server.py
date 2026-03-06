import importlib
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace

import pytest

fastapi = pytest.importorskip("fastapi")
pytest.importorskip("langchain_openai")
pytest.importorskip("langchain_community")
from fastapi.testclient import TestClient  # noqa: E402


class FakeRAG:
    def __init__(self):
        self.vectorstore = object()
        self.vectorstore_dir = "data/vectorstore"
        self.query_count = 0
        self._lock = threading.Lock()

    def process_and_store(self, file_path: str):
        return None

    def add_document(self, file_path: str):
        return None

    def query(self, question: str):
        with self._lock:
            self.query_count += 1
        return {"answer": f"echo:{question}", "source_documents": ["doc-1"]}

    def save_vectorstore(self):
        return None

    def load_vectorstore(self):
        return None


def _build_client(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    module = importlib.import_module("src.api.api_server")
    module.rag_instance = FakeRAG()
    module.settings = replace(
        module.settings,
        api_allowed_extensions=(".txt",),
        api_max_upload_size_mb=1,
        api_auth_token=None,
        api_rate_limit_per_minute=1000,
    )
    module.request_counters.clear()
    return TestClient(module.app), module


def test_reject_unsupported_extension(monkeypatch):
    client, _ = _build_client(monkeypatch)
    response = client.post(
        "/api/v1/process-document/",
        files={"file": ("bad.pdf", b"hello", "application/pdf")},
    )
    assert response.status_code == 400


def test_reject_too_large_upload(monkeypatch):
    client, _ = _build_client(monkeypatch)
    response = client.post(
        "/api/v1/process-document/",
        files={"file": ("big.txt", b"a" * (2 * 1024 * 1024), "text/plain")},
    )
    assert response.status_code == 413


def test_accept_upload_at_size_limit(monkeypatch):
    client, _ = _build_client(monkeypatch)
    response = client.post(
        "/api/v1/process-document/",
        files={"file": ("ok.txt", b"a" * (1024 * 1024), "text/plain")},
    )
    assert response.status_code == 200


def test_query_success_in_v1(monkeypatch):
    client, _ = _build_client(monkeypatch)
    response = client.post("/api/v1/query/", json={"question": "hello"})
    assert response.status_code == 200
    assert response.json()["answer"] == "echo:hello"
    assert response.headers.get("X-Request-ID")


def test_query_supports_chinese(monkeypatch):
    client, _ = _build_client(monkeypatch)
    response = client.post("/api/v1/query/", json={"question": "你好，系统介绍一下"})
    assert response.status_code == 200
    assert "你好" in response.json()["answer"]


def test_metrics_exposed(monkeypatch):
    client, _ = _build_client(monkeypatch)
    _ = client.get("/api/v1/health")
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    assert "hylreg_http_requests_total" in response.text


def test_concurrent_queries(monkeypatch):
    client, module = _build_client(monkeypatch)

    def send_query(i: int):
        return client.post("/api/v1/query/", json={"question": f"q{i}"}).status_code

    with ThreadPoolExecutor(max_workers=5) as executor:
        statuses = list(executor.map(send_query, range(10)))

    assert statuses.count(200) == 10
    assert module.rag_instance.query_count == 10


def test_auth_required_when_configured(monkeypatch):
    client, module = _build_client(monkeypatch)
    module.settings = replace(module.settings, api_auth_token="secret-token")

    response = client.post("/api/v1/query/", json={"question": "hello"})
    assert response.status_code == 401


def test_auth_success_with_valid_bearer_token(monkeypatch):
    client, module = _build_client(monkeypatch)
    module.settings = replace(module.settings, api_auth_token="secret-token")

    response = client.post(
        "/api/v1/query/",
        json={"question": "hello"},
        headers={"Authorization": "Bearer secret-token"},
    )
    assert response.status_code == 200


def test_rate_limit_enforced(monkeypatch):
    client, module = _build_client(monkeypatch)
    module.settings = replace(module.settings, api_rate_limit_per_minute=2)

    assert client.post("/api/v1/query/", json={"question": "q1"}).status_code == 200
    assert client.post("/api/v1/query/", json={"question": "q2"}).status_code == 200
    assert client.post("/api/v1/query/", json={"question": "q3"}).status_code == 429


def test_legacy_route_includes_deprecation_headers(monkeypatch):
    client, _ = _build_client(monkeypatch)
    response = client.post("/query/", json={"question": "legacy"})
    assert response.status_code == 200
    assert response.headers.get("Deprecation") == "true"
    assert response.headers.get("Sunset")
    assert "/api/v1/query/" in (response.headers.get("Link") or "")
