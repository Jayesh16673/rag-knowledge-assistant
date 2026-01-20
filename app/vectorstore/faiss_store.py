from langchain_community.vectorstores import FAISS
from app.embeddings.embedder import get_embedder


def create_vectorstore(documents):
    embeddings = get_embedder()
    return FAISS.from_documents(documents, embeddings)
