import re


def split_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s for s in sentences if s]


def add_citations(answer, chunks):
    """
    For each sentence, attach the most relevant source
    (simple but reliable baseline).
    """

    sentences = split_sentences(answer)

    citations = []
    cited_sentences = []

    for idx, sentence in enumerate(sentences, start=1):
        # Assign best chunk (simple: first chunk match)
        source_doc = chunks[0]

        cited_sentences.append(f"{sentence} [{idx}]")

        citations.append({
            "id": idx,
            "source": source_doc.metadata.get("source"),
            "page": source_doc.metadata.get("page")
        })

    return cited_sentences, citations
