from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import time
import logging

from app.ingestion.loaders import load_pdf
from app.ingestion.chunking import chunk_docs
from app.vectorstore.faiss_store import create_vectorstore
from app.retrieval.hybrid import HybridRetriever
from app.generation.answer_generator import generate_answer
from app.generation.citations import add_citations

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RAG Knowledge Assistant",
    description="Production-grade RAG system with hybrid retrieval and citations",
    version="1.0.0"
)

VECTORSTORE = None
DOCUMENTS = None
RETRIEVER = None

MIN_DOCS_REQUIRED = 1
MIN_CONTEXT_CHARS = 200
MAX_CONTEXT_LENGTH = 1000  # Reduced from 2000 for free tier memory


class IngestRequest(BaseModel):
    pdf_path: str = "data/sample_docs/sample.pdf"


@app.post("/ingest")
def ingest(request: IngestRequest = None):
    """
    Ingest a PDF document for Q&A.
    Default: data/sample_docs/sample.pdf
    Example: {"pdf_path": "data/my_document.pdf"}
    """
    global VECTORSTORE, DOCUMENTS, RETRIEVER

    start_time = time.time()
    pdf_path = request.pdf_path if request else "data/sample_docs/sample.pdf"

    if not Path(pdf_path).exists():
        raise HTTPException(
            status_code=404, detail=f"PDF not found: {pdf_path}")

    try:
        t1 = time.time()
        docs = load_pdf(pdf_path)
        logger.info(f"✓ PDF loaded in {time.time() - t1:.2f}s")

        t2 = time.time()
        chunks = chunk_docs(docs)
        logger.info(f"✓ Chunks created in {time.time() - t2:.2f}s")

        t3 = time.time()
        VECTORSTORE = create_vectorstore(chunks)
        logger.info(f"✓ Vectorstore built in {time.time() - t3:.2f}s")

        DOCUMENTS = chunks
        RETRIEVER = HybridRetriever(VECTORSTORE, DOCUMENTS)

        total_time = time.time() - start_time
        logger.info(f"✓ Total ingestion: {total_time:.2f}s")

        return {
            "status": "documents ingested",
            "pdf_path": pdf_path,
            "chunks_created": len(chunks),
            "ingest_time_seconds": total_time
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error ingesting PDF: {str(e)}")


@app.get("/query")
def query(q: str):
    """Query the ingested documents and get an answer with citations."""
    global RETRIEVER

    start_time = time.time()

    if RETRIEVER is None:
        raise HTTPException(
            status_code=400, detail="Documents not ingested yet")

    t1 = time.time()
    docs = RETRIEVER.retrieve(q)
    retrieval_time = time.time() - t1
    logger.info(f"✓ Retrieval in {retrieval_time:.2f}s ({len(docs)} docs)")

    # Guardrail 1: No documents
    if not docs or len(docs) < MIN_DOCS_REQUIRED:
        return {
            "question": q,
            "answer": "I don't know based on the provided documents.",
            "citations": [],
            "query_time_seconds": time.time() - start_time
        }

    # Limit context for faster LLM inference
    context = "\n".join([d.page_content for d in docs])
    if len(context) > MAX_CONTEXT_LENGTH:
        context = context[:MAX_CONTEXT_LENGTH] + "..."

    # Guardrail 2: Weak context
    if len(context) < MIN_CONTEXT_CHARS:
        return {
            "question": q,
            "answer": "I don't know based on the provided documents.",
            "citations": [],
            "query_time_seconds": time.time() - start_time
        }

    # Generate answer
    t2 = time.time()
    answer = generate_answer(q, context)
    llm_time = time.time() - t2
    logger.info(f"✓ LLM answer in {llm_time:.2f}s")

    # Guardrail 3: Hallucination check
    unsupported_words = [
        word for word in answer.lower().split()
        if word not in context.lower()
    ]

    if len(unsupported_words) > 15:
        return {
            "question": q,
            "answer": "I don't know based on the provided documents.",
            "citations": [],
            "query_time_seconds": time.time() - start_time
        }

    # Add citations
    t3 = time.time()
    cited_answer, citations = add_citations(answer, docs)
    citation_time = time.time() - t3
    logger.info(f"✓ Citations in {citation_time:.2f}s")

    total_time = time.time() - start_time
    logger.info(f"✓ Total query time: {total_time:.2f}s")

    return {
        "question": q,
        "answer": cited_answer,
        "citations": citations,
        "query_time_seconds": total_time,
        "breakdown": {
            "retrieval": retrieval_time,
            "llm_generation": llm_time,
            "citations": citation_time
        }
    }
