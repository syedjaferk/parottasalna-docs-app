"""Flyweight + AI: many retrievers share one heavy embedding model.

load_embedding_model is a stand-in that just sleeps; a real one would load e.g.
sentence-transformers' all-MiniLM-L6-v2.
"""
import time


def load_embedding_model(name):
    time.sleep(0.5)                       # pretend: seconds and gigabytes
    return f"<model {name}>"


class ModelCache:
    _models = {}

    @classmethod
    def get(cls, name):
        if name not in cls._models:
            print(f"Loading {name}... (slow)")
            cls._models[name] = load_embedding_model(name)
        return cls._models[name]


class Retriever:
    def __init__(self, collection, model_name="all-MiniLM-L6-v2"):
        self.collection = collection                  # extrinsic: different per retriever
        self.model = ModelCache.get(model_name)       # intrinsic: shared


start = time.perf_counter()
retrievers = [Retriever(f"docs-{i}") for i in range(100)]
print(f"100 retrievers in {time.perf_counter() - start:.1f}s, "
      f"{len(ModelCache._models)} model in memory")
print(retrievers[0].model is retrievers[99].model)    # True
