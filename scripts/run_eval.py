from app.evaluation.ragas_eval import run_ragas_evaluation
from app.retrieval.hybrid import HybridRetriever
from app.generation.answer_generator import generate_answer
from app.ingestion.loaders import load_pdf
from app.ingestion.chunking import chunk_docs
from app.vectorstore.faiss_store import create_vectorstore


def main():
    # ---------- Load & Index ----------
    docs = load_pdf("data/sample_docs/sample.pdf")
    chunks = chunk_docs(docs)

    vectorstore = create_vectorstore(chunks)
    retriever = HybridRetriever(vectorstore, chunks)

    # ---------- Evaluation Questions ----------
    questions = [
        "What is this document about?",
        "What is NOT mentioned in the document?"
    ]

    answers = []
    contexts = []

    for q in questions:
        retrieved_docs = retriever.retrieve(q)
        context = [d.page_content for d in retrieved_docs]

        answer = generate_answer(q, "\n".join(context))

        answers.append(answer)
        contexts.append(context)

    # ---------- Run RAGAS ----------
    results = run_ragas_evaluation(
        questions=questions,
        answers=answers,
        contexts=contexts
    )

    print("\nRAGAS Evaluation Results:")
    print(results)


if __name__ == "__main__":
    main()
