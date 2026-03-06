import pytest

pytest.importorskip("langchain_openai")
pytest.importorskip("langchain_community")

from src.core.rag_system import RAGSystem


def test_load_documents_routes_directory(tmp_path, monkeypatch):
    rag = RAGSystem.__new__(RAGSystem)
    monkeypatch.setattr(rag, "_load_directory_documents", lambda path: ["dir-doc"])
    monkeypatch.setattr(rag, "_load_single_document", lambda path: ["file-doc"])

    assert rag.load_documents(str(tmp_path)) == ["dir-doc"]


def test_load_documents_routes_single_file(tmp_path, monkeypatch):
    rag = RAGSystem.__new__(RAGSystem)
    target = tmp_path / "a.txt"
    target.write_text("hi", encoding="utf-8")

    monkeypatch.setattr(rag, "_load_directory_documents", lambda path: ["dir-doc"])
    monkeypatch.setattr(rag, "_load_single_document", lambda path: ["file-doc"])

    assert rag.load_documents(str(target)) == ["file-doc"]


def test_save_vectorstore_requires_existing_index():
    rag = RAGSystem.__new__(RAGSystem)
    rag.vectorstore = None
    rag.vectorstore_dir = "data/vectorstore"

    try:
        rag.save_vectorstore()
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "没有可保存的向量数据库" in str(exc)
