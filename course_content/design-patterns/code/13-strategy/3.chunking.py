"""Strategy + AI: swap how a RAG pipeline splits text into chunks."""


def by_size(text, size=20):
    return [text[i:i + size] for i in range(0, len(text), size)]


def by_paragraph(text):
    return [p.strip() for p in text.split("\n\n") if p.strip()]


def by_sentence(text):
    return [s.strip() + "." for s in text.split(".") if s.strip()]


def ingest(text, chunker=by_paragraph):
    chunks = chunker(text)
    print(f"{len(chunks)} chunks via {chunker.__name__}: {chunks}")
    return chunks


doc = "Python is easy.\n\nIt has many libraries. People love it."
ingest(doc, by_paragraph)    # 2 chunks
ingest(doc, by_sentence)     # 3 chunks
ingest(doc, by_size)         # 3 chunks of 20 characters
