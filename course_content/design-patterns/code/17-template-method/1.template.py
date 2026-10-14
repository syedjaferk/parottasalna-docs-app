"""Template Method: the fixed order lives in run(); subclasses fill in only what differs."""
from abc import ABC, abstractmethod


class Pipeline(ABC):
    def run(self):                       # <- the template method: fixed order
        self.connect()
        raw = self.extract()
        clean = self.transform(raw)
        self.load(clean)
        self.close()

    def connect(self): print("connecting...")                 # shared default
    def close(self):   print("closing...")                    # shared default

    @abstractmethod
    def extract(self) -> list[str]: ...                       # must override

    def transform(self, rows: list[str]) -> list[str]:        # optional override
        return [r.upper() for r in rows]

    def load(self, rows: list[str]):
        print(f"saving {len(rows)} rows")


class ListPipeline(Pipeline):
    """Stands in for a CSV source: the rows are given directly."""
    def __init__(self, rows): self.rows = rows
    def extract(self): return list(self.rows)


class APIPipeline(Pipeline):
    def extract(self):
        return [" Row1", "ROW2 ", "row3"]       # pretend this calls an API

    def transform(self, rows):
        return [r.strip().lower() for r in rows]


ListPipeline(["a,1", "b,2"]).run()
APIPipeline().run()
