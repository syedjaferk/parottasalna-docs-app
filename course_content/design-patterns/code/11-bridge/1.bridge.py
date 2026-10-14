"""Bridge: WHAT the report is and HOW it is exported vary independently."""
from abc import ABC, abstractmethod


# Implementation side: HOW to output
class Exporter(ABC):
    @abstractmethod
    def export(self, title: str, rows: list[str]) -> str: ...


class PDFExporter(Exporter):
    def export(self, title, rows):
        return f"[PDF] {title}: " + " | ".join(rows)


class CSVExporter(Exporter):
    def export(self, title, rows):
        return f"[CSV] {title}\n" + "\n".join(rows)


# Abstraction side: WHAT the report is
class Report(ABC):
    def __init__(self, exporter: Exporter):
        self.exporter = exporter          # <- the bridge

    @abstractmethod
    def data(self) -> list[str]: ...

    def generate(self) -> str:
        return self.exporter.export(self.__class__.__name__, self.data())


class SalesReport(Report):
    def data(self): return ["Jan: 100", "Feb: 150"]


class InventoryReport(Report):
    def data(self): return ["Laptops: 12", "Mice: 80"]


print(SalesReport(PDFExporter()).generate())
print(InventoryReport(CSVExporter()).generate())

report = SalesReport(PDFExporter())
report.exporter = CSVExporter()      # switch the implementation at run time
print(report.generate())
