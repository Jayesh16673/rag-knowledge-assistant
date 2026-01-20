from rank_bm25 import BM25Okapi
import numpy as np
from app.retrieval.reranker import rerank_documents


class HybridRetriever:
    def __init__(self, vectorstore, documents):
        self.vectorstore = vectorstore
        self.documents = documents

        # BM25 corpus
        self.corpus = [doc.page_content.split() for doc in documents]
        self.bm25 = BM25Okapi(self.corpus)

    def retrieve(self, query: str, k: int = 10):
        # --- BM25 retrieval ---
        tokenized_query = query.split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        bm25_top_idx = np.argsort(bm25_scores)[-k:]

        bm25_docs = [self.documents[i] for i in bm25_top_idx]

        # --- Semantic retrieval ---
        semantic_docs = self.vectorstore.similarity_search(query, k=k)

        # --- Merge & deduplicate ---
        seen = set()
        merged_docs = []

        for doc in bm25_docs + semantic_docs:
            content = doc.page_content
            if content not in seen:
                seen.add(content)
                merged_docs.append(doc)

        # --- 🔥 RERANK ---
        reranked_docs = rerank_documents(query, merged_docs, top_k=5)

        return reranked_docs
