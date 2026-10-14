"""Abstract Factory + AI: the LLM, embeddings and vector store must come from one family.

The classes here are stand-ins that print what they are, so it runs offline. In a real app,
LocalRagStack would return Ollama + Chroma, and CloudRagStack a hosted LLM + pgvector.
"""
import os
from abc import ABC, abstractmethod


class Part:
    def __init__(self, name): self.name = name
    def __repr__(self): return self.name


class RagStackFactory(ABC):
    @abstractmethod
    def create_llm(self): ...

    @abstractmethod
    def create_embeddings(self): ...

    @abstractmethod
    def create_vector_store(self): ...


class LocalRagStack(RagStackFactory):      # runs on your laptop
    def create_llm(self): return Part("Ollama llama3")
    def create_embeddings(self): return Part("Ollama nomic-embed-text")
    def create_vector_store(self): return Part("Chroma (./chroma_db)")


class CloudRagStack(RagStackFactory):      # runs in production
    def create_llm(self): return Part("Hosted gpt-oss-120b")
    def create_embeddings(self): return Part("Hosted text-embedding-3-small")
    def create_vector_store(self): return Part("Postgres + pgvector")


def build_rag(factory: RagStackFactory):
    return factory.create_llm(), factory.create_embeddings(), factory.create_vector_store()


factory = {"local": LocalRagStack, "cloud": CloudRagStack}[os.getenv("RAG_STACK", "local")]()
llm, embeddings, store = build_rag(factory)
print(f"LLM: {llm}\nEmbeddings: {embeddings}\nVector store: {store}")
