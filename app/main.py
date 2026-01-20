from fastapi import FastAPI, HTTPException

from app.ingestion.loaders import load_pdf
from app.ingestion.chunking import chunk_docs
from app.vectorstore.faiss_store import create_vectorstore
from app.retrieval.hybrid import HybridRetriever
from app.generation.answer_generator import generate_answer
from app.generation.citations import add_citations

app = FastAPI()

VECTORSTORE = None
DOCUMENTS = None
RETRIEVER = None

MIN_DOCS_REQUIRED = 1
MIN_CONTEXT_CHARS = 200


@app.post("/ingest")
def ingest():
    global VECTORSTORE, DOCUMENTS, RETRIEVER

    docs = load_pdf("data/sample_docs/sample.pdf")
    chunks = chunk_docs(docs)

    VECTORSTORE = create_vectorstore(chunks)
    DOCUMENTS = chunks
    RETRIEVER = HybridRetriever(VECTORSTORE, DOCUMENTS)

    return {"status": "documents ingested"}


@app.get("/query")
def query(q: str):
    global RETRIEVER

    if RETRIEVER is None:
        raise HTTPException(
            status_code=400,
            detail="Documents not ingested yet"
        )

    docs = RETRIEVER.retrieve(q)

    # 🛑 Guardrail 1: No documents
    if not docs or len(docs) < MIN_DOCS_REQUIRED:
        return {
            "question": q,
            "answer": "I don’t know based on the provided documents.",
            "citations": []
        }

    context = "\n".join([d.page_content for d in docs])

    # 🛑 Guardrail 2: Weak context
    if len(context) < MIN_CONTEXT_CHARS:
        return {
            "question": q,
            "answer": "I don’t know based on the provided documents.",
            "citations": []
        }

    # ✅ Generate grounded answer
    answer = generate_answer(q, context)

    # 🛑 Guardrail 3: Hallucination check
    unsupported_words = [
        word for word in answer.lower().split()
        if word not in context.lower()
    ]

    if len(unsupported_words) > 15:
        return {
            "question": q,
            "answer": "I don’t know based on the provided documents.",
            "citations": []
        }

    # ✅ Sentence-level citations
    cited_answer, citations = add_citations(answer, docs)

    return {
        "question": q,
        "answer": cited_answer,
        "citations": citations
    }
