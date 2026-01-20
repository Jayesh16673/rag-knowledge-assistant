# RAG Knowledge Assistant - AI Agent Guide

## Architecture Overview

This is a **Retrieval-Augmented Generation (RAG) system** built with FastAPI that ingests documents and retrieves relevant content via hybrid search. Key data flow:

1. **Ingestion** (`app/ingestion/`) → Load PDFs and chunk them (800 char chunks, 150 char overlap)
2. **Embedding** (`app/embeddings/`) → OpenAI embeddings vectorize chunks
3. **Storage** (`app/vectorstore/`) → FAISS stores vectors; documents kept in memory
4. **Retrieval** (`app/retrieval/`) → **HybridRetriever** combines BM25 lexical + semantic search
5. **API** (`app/api/` & `main.py`) → Two endpoints: `/ingest` and `/query`

## Critical Patterns

### Global State Management
The system uses **module-level globals** (`VECTORSTORE`, `DOCUMENTS`, `RETRIEVER`) in [app/main.py](app/main.py) - this is intentional for simplicity, not production-ready. Don't refactor to classes without purpose; understand this is a current design choice.

### Hybrid Retrieval Strategy
[app/retrieval/hybrid.py](app/retrieval/hybrid.py) implements a **dual-ranking approach**:
- **BM25** scores documents by keyword overlap (lexical relevance)
- **Vector similarity** scores by semantic embeddings
- Results are **deduplicated by content** and merged before returning top-k

When adding retrieval features, preserve this deduplication pattern to avoid duplicate results.

### Document Structure
All documents are LangChain `Document` objects with:
- `page_content`: The actual text
- `metadata`: Source information (e.g., page number, file path)

Respect this structure when filtering, scoring, or transforming results.

## Tech Stack & Dependencies

- **Framework**: FastAPI + Uvicorn (see `main.py`)
- **Embeddings**: OpenAI (configured via `OPENAI_API_KEY` in `.env`)
- **Vector Storage**: FAISS (in-memory, CPU-based)
- **Retrieval**: LangChain components + rank-bm25
- **Ingestion**: PyPDFLoader, RecursiveCharacterTextSplitter
- **Evaluation**: RAGAS library installed (metrics module empty - ready for implementation)

**Note**: FAISS index is recreated on each `/ingest` call—no persistence layer exists yet.

## Running & Development

**Start server**: `python -m uvicorn app.main:app --reload`
**Load environment**: Create `.env` with `OPENAI_API_KEY=<your-key>`

No tests exist; manual API testing via curl or Postman is current approach. Evaluation module at `app/evaluation/rag_metrics.py` is prepared but empty—use RAGAS for semantic evaluation.

## Key Files Reference

- [app/main.py](app/main.py) - API endpoints, global state
- [app/retrieval/hybrid.py](app/retrieval/hybrid.py) - Core retrieval logic (BM25 + semantic)
- [app/ingestion/chunking.py](app/ingestion/chunking.py) - Document splitting config (800/150)
- [app/vectorstore/faiss_store.py](app/vectorstore/faiss_store.py) - Vector index creation
- [app/core/config.py](app/core/config.py) - Config management (OpenAI API key)

## Evaluation & Testing

The evaluation system uses **graceful degradation**:
- **With RAGAS** (if available): Full semantic evaluation via `evaluate()` with metrics (context_precision, context_recall, answer_relevancy)
- **Without RAGAS/offline** (Windows-safe): Falls back to [_manual_evaluation()](app/evaluation/ragas_eval.py) with heuristic-based scoring
- The `run_ragas_evaluation()` function handles both paths automatically via try/except

This pattern allows Windows CI/offline environments to still run evaluations without LLM API calls.

## Common Tasks

**Add a new retrieval strategy**: Extend or replace `HybridRetriever` class, ensure it returns deduplicated `Document` objects.

**Change chunk size**: Edit `RecursiveCharacterTextSplitter` params in [app/ingestion/chunking.py](app/ingestion/chunking.py).

**Add evaluation metrics**: Implement functions in [app/evaluation/rag_metrics.py](app/evaluation/rag_metrics.py) using RAGAS (ragas library already in requirements).

**Support new document types**: Add loaders in [app/ingestion/loaders.py](app/ingestion/loaders.py) following PyPDFLoader pattern.

**Run evaluation script**: `python scripts/run_eval.py` - uses HybridRetriever to get context, calls local TinyLLaMA model for answer generation, then evaluates with RAGAS or manual fallback.
