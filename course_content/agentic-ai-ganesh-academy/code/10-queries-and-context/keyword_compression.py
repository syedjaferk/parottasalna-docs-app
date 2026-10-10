"""
Keyword Context Compression

Flow

Question
    ↓
Retrieve Chunks
    ↓
Extract Keywords
    ↓
Keep Matching Sentences
"""

import re

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# -----------------------------
# Configuration
# -----------------------------

CHROMA_DB = "chroma_db"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

TOP_K = 4

STOPWORDS = {
    "what",
    "is",
    "are",
    "the",
    "of",
    "for",
    "a",
    "an",
    "to",
    "in",
    "on",
    "how",
    "does",
    "do",
    "why",
    "when",
    "where",
    "which",
    "can",
    "be",
    "about",
}

# -----------------------------
# Embedding Model
# -----------------------------

embedding_model = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL
)

# -----------------------------
# ChromaDB
# -----------------------------

vectorstore = Chroma(
    persist_directory=CHROMA_DB,
    embedding_function=embedding_model
)

retriever = vectorstore.as_retriever(
    search_kwargs={"k": TOP_K}
)

# -----------------------------
# Interactive Loop
# -----------------------------

while True:

    question = input("\nQuestion (exit to quit): ")

    if question.lower() == "exit":
        break

    docs = retriever.invoke(question)

    context = "\n".join(doc.page_content for doc in docs)

    print("\nOriginal Context\n")
    print(context)


    # Extract Keywords


    words = re.findall(r"\w+", question.lower())

    keywords = [
        word
        for word in words
        if word not in STOPWORDS
    ]

    print("\nKeywords:", keywords)


    # Keep Relevant Sentences


    compressed = []

    # Split into sentences (ingest.py removed the newlines, so "\n" would give whole chunks)
    for sentence in re.split(r"(?<=[.!?])\s+", context):

        lower = sentence.lower()

        for keyword in keywords:

            if keyword in lower:
                compressed.append(sentence.strip())
                break

    print("\nCompressed Context\n")

    for sentence in compressed:
        print(sentence)
