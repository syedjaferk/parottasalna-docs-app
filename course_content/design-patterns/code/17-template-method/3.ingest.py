"""Template Method + AI: every document source goes through the same RAG ingestion steps."""
import tempfile
from abc import ABC, abstractmethod


class Ingestor(ABC):
    def ingest(self, source: str):
        text = self.load(source)            # differs
        text = self.clean(text)             # shared
        chunks = self.split(text)           # shared
        self.store(chunks)                  # shared

    @abstractmethod
    def load(self, source) -> str: ...

    def clean(self, text): return " ".join(text.split())
    def split(self, text, size=40): return [text[i:i + size] for i in range(0, len(text), size)]
    def store(self, chunks): print(f"stored {len(chunks)} chunks via {type(self).__name__}")


class TextFileIngestor(Ingestor):
    def load(self, source):
        with open(source, encoding="utf-8") as f:
            return f.read()


class WebIngestor(Ingestor):
    def load(self, source):
        import urllib.request
        return urllib.request.urlopen(source, timeout=10).read().decode()


class StringIngestor(Ingestor):          # handy for tests: the "source" is the text itself
    def load(self, source): return source


with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
    f.write("Template Method keeps the order of steps in one place.\n\n" * 3)
TextFileIngestor().ingest(f.name)
StringIngestor().ingest("A short note about design patterns.")
# WebIngestor().ingest("https://example.com")    # needs internet
