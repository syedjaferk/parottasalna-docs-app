"""Facade + AI: hide a whole RAG pipeline behind ingest() and ask().

The vector store and LLM are small offline stand-ins with LangChain-shaped methods
(add_texts, similarity_search, invoke), so the file runs without any service.
"""
from types import SimpleNamespace as NS


class FakeLLM:
    """Offline stand-in with the same .invoke(...).content shape as a LangChain chat model."""
    def __init__(self):
        self.calls = 0

    def invoke(self, prompt):
        self.calls += 1
        return type("Msg", (), {"content": f"(answer #{self.calls} to: {str(prompt)[:40]})"})()


class TinyVectorStore:
    """Keyword-overlap "search", shaped like a LangChain vector store."""
    def __init__(self):
        self.texts = []

    def add_texts(self, texts):
        self.texts.extend(texts)

    def similarity_search(self, query, k=3):
        words = set(query.lower().split())
        ranked = sorted(self.texts, key=lambda t: -len(words & set(t.lower().split())))
        return [NS(page_content=t) for t in ranked[:k]]


class RagFacade:
    def __init__(self, llm, vector_store):
        self._llm = llm
        self._store = vector_store

    def ingest(self, text: str):
        chunks = [p.strip() for p in text.split("\n\n") if p.strip()]
        self._store.add_texts(chunks)

    def ask(self, question: str) -> str:
        docs = self._store.similarity_search(question, k=1)
        context = "\n\n".join(d.page_content for d in docs)
        prompt = f"Answer using only this context:\n{context}\n\nQuestion: {question}"
        print("--- prompt sent to the LLM ---\n" + prompt + "\n------------------------------")
        return self._llm.invoke(prompt).content


notes = """A Singleton makes sure a class has only one instance.

A Facade gives one simple entry point to a complicated system.

An Adapter makes one interface fit another."""

rag = RagFacade(FakeLLM(), TinyVectorStore())
rag.ingest(notes)
print(rag.ask("What does a Facade give?"))
