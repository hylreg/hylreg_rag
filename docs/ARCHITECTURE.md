# Architecture

## Layers

1. `src/config`: environment-driven settings and validation.
2. `src/core`: RAG orchestration (loading, chunking, vector indexing, querying).
3. `src/utils`: shared helpers and local sample data generation.
4. `src/cli`: command-line user interface and entrypoints.
5. `src/api`: FastAPI service wrapper around the core engine.

## Runtime Flow

1. Load settings from `.env` and process environment.
2. Initialize `RAGSystem` with model/splitting/retrieval parameters.
3. Load and split documents.
4. Build or update FAISS vectorstore.
5. Execute retrieval + generation via LangChain `RetrievalQA`.

## Persistence

- Default vectorstore path: `data/vectorstore`.
- Auto-persist controlled by `RAG_AUTO_PERSIST`.
- API/CLI provide explicit save and reload operations.

## Extension Points

- Swap vector backend in `src/core/rag_system.py`.
- Add model provider support in `src/config/settings.py` + core initialization.
- Add new document loaders in `_load_single_document` and `_load_directory_documents`.

