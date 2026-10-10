
import os
from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings


# Load Environment Variables


load_dotenv()


# Configuration


CHROMA_DB = "chroma_db"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

TOP_K = 4


# Embedding Model


print("Loading Embedding Model...")

embedding_model = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL
)


# Load ChromaDB


print("Loading ChromaDB...")

vectorstore = Chroma(
    persist_directory=CHROMA_DB,
    embedding_function=embedding_model
)

retriever = vectorstore.as_retriever(
    search_kwargs={"k": TOP_K}
)


# Groq LLM


print("Loading Groq Model...")

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)


# Compression Prompt


compression_prompt = ChatPromptTemplate.from_template(
"""
You are an expert Context Compression assistant.

Your task is NOT to answer the user's question.

Instead:

1. Read the user's question.
2. Read the retrieved context.
3. Remove every sentence that is unrelated.
4. Keep only information useful for answering.
5. Preserve important technical details.
6. Do not summarize unless necessary.
7. Return ONLY the compressed context.

Question:

{question}

Retrieved Context:

{context}

Compressed Context:
"""
)

compression_chain = compression_prompt | llm


# Interactive Loop


while True:

    question = input("\nAsk a Question (or 'exit'): ")

    if question.lower() == "exit":
        break

    print("\nRetrieving documents...\n")

    docs = retriever.invoke(question)

    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )

    print("=" * 70)
    print("ORIGINAL CONTEXT")
    print("=" * 70)

    print(context)

    print("\n\nCompressing using Groq...\n")

    compressed = compression_chain.invoke(
        {
            "question": question,
            "context": context
        }
    )

    print("=" * 70)
    print("COMPRESSED CONTEXT")
    print("=" * 70)

    print(compressed.content)

    print("\n")
