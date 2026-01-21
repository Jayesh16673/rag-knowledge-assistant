from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_docs(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,  # Reduced from 800 for memory efficiency
        chunk_overlap=50  # Reduced from 150 for smaller footprint
    )
    return splitter.split_documents(docs)
