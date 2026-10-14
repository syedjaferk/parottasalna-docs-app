"""Hooks: steps with an empty default that subclasses may override."""
from abc import ABC, abstractmethod


class Pipeline(ABC):
    def run(self):
        self.before_run()          # hook: does nothing by default
        rows = self.transform(self.extract())
        if not self.should_skip(rows):
            self.load(rows)
        self.after_run()           # hook

    def before_run(self): pass
    def after_run(self): pass
    def should_skip(self, rows) -> bool: return False

    @abstractmethod
    def extract(self): ...

    def transform(self, rows): return rows
    def load(self, rows): print(f"saving {len(rows)} rows")


class TimedPipeline(Pipeline):
    def extract(self): return ["a", "b"]
    def before_run(self): print("⏱ start")
    def after_run(self): print("⏱ done")


class EmptySkippingPipeline(Pipeline):
    def extract(self): return []
    def should_skip(self, rows): return len(rows) == 0


TimedPipeline().run()
EmptySkippingPipeline().run()     # prints nothing: no rows, load skipped
print("(empty pipeline skipped loading)")
