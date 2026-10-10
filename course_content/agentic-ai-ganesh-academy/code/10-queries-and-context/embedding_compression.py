

import re

from sklearn.metrics.pairwise import cosine_similarity

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


# Configuration


CHROMA_DB = "chroma_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K = 4
TOP_SENTENCES = 10


# Embedding Model


embedding_model = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL
)


# Load ChromaDB


vectorstore = Chroma(
    persist_directory=CHROMA_DB,
    embedding_function=embedding_model
)

retriever = vectorstore.as_retriever(
    search_kwargs={"k": TOP_K}
)


# Interactive Loop


while True:

    question = input("\nQuestion (exit to quit): ")

    if question.lower() == "exit":
        break

    docs = retriever.invoke(question)

    context = "\n".join(doc.page_content for doc in docs)

    print("\nOriginal Context\n")
    print(context)


    # Sentence Split


    sentences = []

    # Split into sentences (ingest.py removed the newlines, so "\n" would give whole chunks)
    for line in re.split(r"(?<=[.!?])\s+", context):
        line = line.strip()

        if len(line) > 20:
            sentences.append(line)


    # Embeddings


    question_embedding = embedding_model.embed_query(question)

    sentence_embeddings = embedding_model.embed_documents(sentences)


    # Similarity


    scores = cosine_similarity(
        [question_embedding],
        sentence_embeddings
    )[0]

    ranked = sorted(
        zip(sentences, scores),
        key=lambda x: x[1],
        reverse=True
    )

    print("\nCompressed Context\n")

    for sentence, score in ranked[:TOP_SENTENCES]:
        print(f"{score:.3f}  {sentence}")
