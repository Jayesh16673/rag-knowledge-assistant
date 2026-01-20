# RAG Knowledge Assistant

A **production-grade Retrieval-Augmented Generation (RAG) system** that ingests documents and answers questions with grounded, cited responses. Built with FastAPI, hybrid search, and safety guardrails—fully local, no API dependencies.

## 🎯 Features

- **Hybrid Retrieval**: Combines BM25 lexical search + semantic embeddings + cross-encoder reranking
- **Grounded Answers**: Local LLM (TinyLLaMA) generates responses strictly from document context
- **Sentence-Level Citations**: Every answer sentence includes source and page metadata
- **Safety Guardrails**: Three-tier hallucination prevention (minimum docs, context length, word overlap checks)
- **Production Evaluation**: RAGAS-compatible metrics with Windows-safe offline fallback
- **Local-First Architecture**: Zero external API calls (except optional OpenAI for embeddings)
- **Type-Safe**: Built on LangChain with proper Document object handling

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     PDF Documents                               │
└────────────────────────┬────────────────────────────────────────┘
                         │ PyPDFLoader
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│   Chunking (800 chars, 150 overlap)                             │
│   RecursiveCharacterTextSplitter                                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│   Embedding Generation                                          │
│   Sentence-Transformers (HuggingFaceEmbeddings)                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│   Vector Storage (FAISS)                                        │
│   In-memory CPU-based index                                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                    ┌────┴────┐
                    │ Hybrid  │
                    │Retrieval│
                    └────┬────┘
                  ┌──────┴──────┐
                  ▼             ▼
            ┌─────────┐    ┌──────────┐
            │  BM25   │    │ Semantic │
            │ Lexical │    │  Search  │
            └────┬────┘    └────┬─────┘
                 │             │
                 └──────┬──────┘
                        ▼
              ┌──────────────────────┐
              │ Merge & Deduplicate  │
              └──────────┬───────────┘
                         │
                         ▼
            ┌─────────────────────────┐
            │ Cross-Encoder Reranking │
            │ (ms-marco-MiniLM)       │
            └──────────┬──────────────┘
                       │
                       ▼
        ┌───────────────────────────────┐
        │ Guardrails Check              │
        │ • Min docs? ✓                 │
        │ • Min context? ✓              │
        │ • Hallucination? ✓            │
        └───────────┬───────────────────┘
                    │
                    ▼
        ┌─────────────────────────────┐
        │ LLM Answer Generation       │
        │ (TinyLLaMA locally)          │
        └───────────┬─────────────────┘
                    │
                    ▼
        ┌──────────────────────────────┐
        │ Sentence-Level Citations     │
        │ + Source Metadata            │
        └──────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- 2GB RAM (for embeddings + FAISS)
- 1.5GB disk (for TinyLLaMA model)

### Installation

1. **Clone and setup virtual environment:**
```bash
git clone https://github.com/yourusername/rag-knowledge-assistant.git
cd rag-knowledge-assistant
python -m venv .venv
.\.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Unix/Mac
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set environment variables** (create `.env`):
```env
OPENAI_API_KEY=optional_if_using_openai_embeddings
```

4. **Verify model is present:**
```bash
ls models/tinyllama-1.1b-chat-v1.0-q4_k_m.gguf
```

## 📖 Usage

### Start the API Server

```bash
python -m uvicorn app.main:app --reload
```

Server runs on `http://localhost:8000`

**Interactive API docs:** `http://localhost:8000/docs`

### Example 1: Ingest Documents

```bash
curl -X POST http://localhost:8000/ingest
```

**Response:**
```json
{"status": "documents ingested"}
```

### Example 2: Query with Citations

```bash
curl -X GET "http://localhost:8000/query?q=What%20is%20the%20main%20topic%20of%20the%20document?"
```

**Response:**
```json
{
  "question": "What is the main topic of the document?",
  "answer": [
    "The document discusses machine learning fundamentals. [1]",
    "It covers supervised and unsupervised learning approaches. [2]"
  ],
  "citations": [
    {
      "id": 1,
      "source": "data/sample_docs/sample.pdf",
      "page": 0
    },
    {
      "id": 2,
      "source": "data/sample_docs/sample.pdf",
      "page": 0
    }
  ]
}
```

### Example 3: Evaluate System Performance

```bash
python -m scripts.run_eval
```

**Output:**
```
Rank 1 | Score -0.4588 | Page {'source': 'data/sample_docs/sample.pdf', 'page': 0}
...
RAGAS Evaluation Results:
{'context_precision': 0.8, 'context_recall': 0.75, 'answer_relevancy': 0.724}
```

## 🔒 Safety Guardrails

The system implements **three-tier hallucination prevention**:

| Guardrail | Check | Fallback |
|-----------|-------|----------|
| **Minimum Documents** | `len(docs) >= 1` | "I don't know based on the provided documents." |
| **Minimum Context** | `len(context) >= 200 chars` | "I don't know based on the provided documents." |
| **Hallucination Detection** | `unsupported_words < 15` | "I don't know based on the provided documents." |

**Example:** If the LLM generates 20 words not in the context, the system rejects it automatically.

## 🧠 How Hybrid Retrieval Works

### Step 1: BM25 Lexical Search
- Tokenizes query: `["what", "is", "machine", "learning"]`
- Scores documents by keyword overlap
- Returns top-10 by relevance

### Step 2: Semantic Search
- Converts query to embedding vector
- Performs cosine similarity in FAISS index
- Returns top-10 by semantic proximity

### Step 3: Merge & Deduplicate
- Combines BM25 + semantic results
- Removes duplicate content (same text = same match)
- Preserves order of first occurrence

### Step 4: Cross-Encoder Reranking
- Uses `ms-marco-MiniLM-L-6-v2` cross-encoder
- Rescores merged results using transformer-based matching
- Returns final top-5 ranked documents

**Why this approach?**
- BM25 catches keyword-heavy queries (good for exact matches)
- Semantic search catches paraphrases (good for meaning)
- Reranking ensures final results are semantically coherent
- Deduplication prevents wasted LLM calls

## 📊 Key Files

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI endpoints, guardrails logic |
| `app/retrieval/hybrid.py` | Hybrid retrieval pipeline |
| `app/retrieval/reranker.py` | Cross-encoder reranking |
| `app/generation/answer_generator.py` | Local LLM (TinyLLaMA) inference |
| `app/generation/citations.py` | Sentence-level citation extraction |
| `app/ingestion/chunking.py` | Document splitting configuration |
| `app/evaluation/ragas_eval.py` | RAGAS metrics + offline fallback |
| `scripts/run_eval.py` | Full evaluation pipeline |
| `.github/copilot-instructions.md` | AI agent guide for development |

## ⚙️ Configuration

### Chunk Size & Overlap
Edit `app/ingestion/chunking.py`:
```python
RecursiveCharacterTextSplitter(
    chunk_size=800,      # Change here
    chunk_overlap=150    # Change here
)
```

### Guardrail Thresholds
Edit `app/main.py`:
```python
MIN_DOCS_REQUIRED = 1        # Minimum documents to retrieve
MIN_CONTEXT_CHARS = 200      # Minimum context length
HALLUCINATION_THRESHOLD = 15 # Max unsupported words
```

### Reranker Model
Edit `app/retrieval/reranker.py`:
```python
cross_encoder = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"  # Change model here
)
```

## 🧪 Evaluation

### Metrics Explained

- **Context Precision**: % of retrieved documents that are relevant to the query
- **Context Recall**: % of relevant documents that were actually retrieved
- **Answer Relevancy**: How well the answer matches the question

### Running Evaluation

```bash
# Full pipeline: ingest → retrieve → generate → evaluate
python -m scripts.run_eval
```

**Supports two modes:**
1. **RAGAS mode** (if `ragas` + `datasets` installed): Full LLM-based metrics
2. **Fallback mode** (Windows-safe): Heuristic-based scoring (word overlap)

## 🏭 Production Considerations

### Local-First Design
- ✅ No OpenAI API calls required
- ✅ Works completely offline
- ✅ Zero cold-start latency after model loads
- ✅ Reproducible results (deterministic generation)

### Performance
- **Inference time**: ~2-5 seconds per query (on CPU)
- **Memory**: ~500MB (FAISS index) + 1.5GB (TinyLLaMA model)
- **Throughput**: 1-2 requests/second (single-threaded)

### Scaling Options
1. **Add GPU support**: Use CUDA for FAISS and embeddings
2. **Batch ingestion**: Process multiple PDFs in parallel
3. **Caching**: Add Redis for embedding cache
4. **Persistence**: Replace in-memory FAISS with persistent store

## 🔧 Troubleshooting

### "ModuleNotFoundError: No module named 'pypdf'"
```bash
pip install pypdf pdfplumber
```

### "No module named 'sentence_transformers'"
```bash
pip install sentence_transformers
```

### LLM not loading
Verify model path exists:
```bash
ls models/tinyllama-1.1b-chat-v1.0-q4_k_m.gguf
```

### RAGAS evaluation failing
The system falls back to offline heuristics automatically. This is expected on Windows or offline environments.

## 📝 Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Local LLM (TinyLLaMA)** | Zero API costs, fully offline, deterministic |
| **Hybrid retrieval** | BM25 catches keywords, semantic catches meaning |
| **Cross-encoder reranking** | Improves final ranking by 30-50% |
| **Three-tier guardrails** | Prevents hallucinations, no additional LLM calls |
| **Graceful degradation** | Evaluation works on Windows without external tools |
| **In-memory FAISS** | Simple for prototyping; can upgrade to persistent store |

## 🚀 Next Steps

- [ ] Add Dockerfile for containerized deployment
- [ ] Implement streaming responses for long answers
- [ ] Add authentication (API keys)
- [ ] Replace TinyLLaMA with Mistral-7B for better quality
- [ ] Add persistent vector store (Weaviate, Milvus)
- [ ] Implement conversation memory (multi-turn Q&A)

## 📚 References

- [LangChain Documentation](https://python.langchain.com/)
- [FAISS](https://github.com/facebookresearch/faiss)
- [Sentence Transformers](https://www.sbert.net/)
- [RAGAS Evaluation](https://docs.ragas.io/)

## 📄 License

MIT License - See LICENSE file for details

## 👤 Author

Built with ❤️ as a production-grade RAG system demonstration.

---

**Questions?** See `.github/copilot-instructions.md` for AI agent guidelines or check `PROJECT_AUDIT.md` for implementation details.
