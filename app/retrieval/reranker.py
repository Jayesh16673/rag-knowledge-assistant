from sentence_transformers import CrossEncoder
from typing import List
from langchain_core.documents import Document

# Load once (important for performance)
cross_encoder = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


def rerank_documents(
    query: str,
    documents: List[Document],
    top_k: int = 5
) -> List[Document]:
    """
    Rerank documents using cross-encoder scoring
    """

    if not documents:
        return []

    pairs = [(query, doc.page_content) for doc in documents]

    scores = cross_encoder.predict(pairs)

    scored_docs = list(zip(documents, scores))

    # Sort by score (descending)
    scored_docs.sort(key=lambda x: x[1], reverse=True)

    # 🔍 Debug (optional)
    for i, (doc, score) in enumerate(scored_docs[:top_k]):
        print(f"Rank {i+1} | Score {score:.4f} | Page {doc.metadata}")

    return [doc for doc, _ in scored_docs[:top_k]]
