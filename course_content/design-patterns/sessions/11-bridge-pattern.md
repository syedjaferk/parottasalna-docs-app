# Session 11 · Bridge pattern

## The big idea

When a class can vary in **two independent directions**, inheritance explodes. A `Report` can be
*Sales* or *Inventory*, and can be exported as *PDF* or *Excel*. With subclasses you need
`SalesPDFReport`, `SalesExcelReport`, `InventoryPDFReport`, `InventoryExcelReport`. Add CSV and you
write two more. Add a third report type and you write three more.

The **Bridge** pattern splits the two directions into **two small hierarchies** connected by
composition: the report (abstraction) *holds* an exporter (implementation). Mix and match freely.

**Everyday example:** a TV and a remote. Any remote brand works with any TV that speaks the standard
signal. You don't build a "Samsung-TV-with-Sony-remote" product for every pair.

:::{admonition} In plain words
:class: tip
When a thing can change in **two separate ways** (what it is, and how it's output), keep those two apart and connect them, instead of a subclass for every combination.

**Reach for it when:**

- class names start combining two ideas: `SalesPDFReport`, `SalesCSVReport`…
- both directions keep growing independently
- you want to mix and match at run time
:::

## Without Bridge

`0.class_explosion.py`:

```python
class SalesPDFReport: ...
class SalesExcelReport: ...
class InventoryPDFReport: ...
class InventoryExcelReport: ...
# + CSV → 2 more, + Finance report → 3 more ...   2 × 2 = 4,  3 × 3 = 9
```

## With Bridge

`1.bridge.py`:

```python
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
        self.exporter = exporter          # ← the bridge

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
```

```text
[PDF] SalesReport: Jan: 100 | Feb: 150
[CSV] InventoryReport
Laptops: 12
Mice: 80
```

2 reports + 2 exporters = **4 classes** instead of 4 combos. With 3 + 3 it is 6 instead of 9, and
the gap grows fast. Adding `ExcelExporter` doesn't touch any report.

```{raw} html
:file: ../diagrams/s11-bridge.html
```

## Switch at run time

Because it is composition, you can change the implementation while the program runs:

```python
report = SalesReport(PDFExporter())
report.exporter = CSVExporter()      # now it exports CSV
```

## Bridge + AI: agent × model

An agent type (*Support*, *Researcher*) is one direction. The model backend (*Groq*, *OpenAI*,
*Local*) is the other (`2.agent_bridge.py`):

```python
class Backend(ABC):
    @abstractmethod
    def complete(self, prompt: str) -> str: ...

class Agent:
    system_prompt = ""
    def __init__(self, backend: Backend):
        self.backend = backend
    def ask(self, question: str) -> str:
        return self.backend.complete(f"{self.system_prompt}\n\n{question}")

class SupportAgent(Agent):
    system_prompt = "You are a polite customer support agent."

class ResearchAgent(Agent):
    system_prompt = "You are a careful researcher. Cite sources."
```

Any agent works with any backend. Swap the model for cost or privacy without rewriting agents.

## Bridge vs Adapter vs Strategy

- **Adapter** fixes a mismatch *after* the fact. Bridge is planned *up front*.
- **Strategy** (session 13) swaps one algorithm. Bridge splits a whole class into two hierarchies
  that evolve separately. The code looks similar; the scale and intent differ.

## Common mistakes

- **Using Bridge when only one dimension varies.** A plain interface is enough.
- **Putting export logic back in the report.** Then the two sides aren't independent.
- **Wide implementation interface.** Keep `Exporter` small, or every new exporter is painful.

## Hands-on exercises

**Exercise 1 · Add Excel.** Add an `ExcelExporter` and use it with both reports.

<details class="solution"><summary>Solution</summary>

```python
class ExcelExporter(Exporter):
    def export(self, title, rows):
        return f"[XLSX] {title} ({len(rows)} rows)"

print(SalesReport(ExcelExporter()).generate())
print(InventoryReport(ExcelExporter()).generate())
```

Zero changes to the reports.

</details>

**Exercise 2 · Shapes and colours.** `Circle` and `Square` can be `Red` or `Blue`. Build it with
Bridge.

<details class="solution"><summary>Solution</summary>

```python
class Color(ABC):
    @abstractmethod
    def fill(self) -> str: ...
class Red(Color):
    def fill(self): return "red"
class Blue(Color):
    def fill(self): return "blue"

class Shape:
    def __init__(self, color: Color): self.color = color
class Circle(Shape):
    def draw(self): return f"{self.color.fill()} circle"
class Square(Shape):
    def draw(self): return f"{self.color.fill()} square"

print(Square(Blue()).draw())    # blue square
```

</details>

**Exercise 3 · Notification × channel.** `Alert`/`Reminder` messages, sent through
`Email`/`SMS`. Write it and print `Reminder` via `SMS`.

<details class="solution"><summary>Solution</summary>

```python
class Channel(ABC):
    @abstractmethod
    def send(self, text: str): ...
class Email(Channel):
    def send(self, text): print(f"EMAIL: {text}")
class SMS(Channel):
    def send(self, text): print(f"SMS: {text}")

class Message:
    def __init__(self, channel: Channel): self.channel = channel
class Alert(Message):
    def notify(self, what): self.channel.send(f"🚨 ALERT: {what}")
class Reminder(Message):
    def notify(self, what): self.channel.send(f"⏰ Reminder: {what}")

Reminder(SMS()).notify("Class at 8 PM")
```

</details>

## Full source

<details class="source">
<summary>1.bridge.py</summary>

```{literalinclude} ../code/11-bridge/1.bridge.py
:language: python
```

</details>

<details class="source">
<summary>2.agent_bridge.py</summary>

```{literalinclude} ../code/11-bridge/2.agent_bridge.py
:language: python
```

</details>

**Downloads:**
{download}`0.class_explosion.py <../code/11-bridge/0.class_explosion.py>` ·
{download}`1.bridge.py <../code/11-bridge/1.bridge.py>` ·
{download}`2.agent_bridge.py <../code/11-bridge/2.agent_bridge.py>`
