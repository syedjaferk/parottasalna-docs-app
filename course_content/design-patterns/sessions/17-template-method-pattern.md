# Session 17 · Template Method pattern

## The big idea

Several jobs follow the **same steps in the same order**, but a few steps differ. Copy-pasting the
whole flow into each job duplicates code and lets the order drift. The **Template Method** pattern
writes the fixed flow **once** in a base class, and lets subclasses fill in only the steps that
differ.

**Everyday example:** making tea or coffee. Boil water → brew → pour into cup → add extras. The
steps and order are the same. Only "brew" (tea leaves vs coffee powder) and "extras" (lemon vs
sugar) change.

:::{admonition} In plain words
:class: tip
Several jobs follow the **same steps in the same order**. Write that order once in a base class; each job fills in only the steps that are different.

**Reach for it when:**

- you've copy-pasted the same flow and changed one or two steps
- the order of steps must never drift
- frameworks call your code at fixed points (setUp, fit, get_queryset)
:::

## Without Template Method

`0.no_template.py`: two pipelines with the same skeleton copied.

```python
def csv_pipeline(path):
    print("connecting...")
    data = open(path).read().splitlines()      # extract (differs)
    data = [row.upper() for row in data]       # transform
    print(f"saving {len(data)} rows")          # load
    print("closing...")

def api_pipeline(url):
    print("connecting...")
    data = ["row1", "row2"]                    # extract (differs): pretend API call
    data = [row.upper() for row in data]       # transform (copied)
    print(f"saving {len(data)} rows")          # load (copied)
    print("closing...")
```

Fix a bug in "connecting" and you must remember to fix it twice.

## With Template Method

`1.template.py`:

```python
from abc import ABC, abstractmethod

class Pipeline(ABC):
    def run(self):                       # ← the template method: fixed order
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

class CSVPipeline(Pipeline):
    def __init__(self, path): self.path = path
    def extract(self):
        return open(self.path).read().splitlines()

class APIPipeline(Pipeline):
    def extract(self):
        return ["row1", "row2", "row3"]       # pretend this calls an API
    def transform(self, rows):
        return [r.strip().lower() for r in rows]

APIPipeline().run()
```

```text
connecting...
saving 3 rows
closing...
```

The **order** lives in `run()`. Subclasses can't mess it up, and they only write what is different.

```{raw} html
:file: ../diagrams/s17-template.html
```

## Hooks

A **hook** is a step with an empty default that subclasses *may* override (`2.hooks.py`):

```python
class Pipeline(ABC):
    def run(self):
        self.before_run()          # hook: does nothing by default
        ...
        self.after_run()           # hook

    def before_run(self): pass
    def after_run(self): pass
```

This is how frameworks work: Django's `get_queryset()`, `unittest`'s `setUp()` and `tearDown()` and
Scikit-learn's `fit()` are all template-method hooks.

## Template Method + AI: a document ingestion flow

Every source (PDF, web page, Notion) goes through the same RAG steps (`3.ingest.py`):

```python
class Ingestor(ABC):
    def ingest(self, source: str):
        text = self.load(source)            # differs
        text = self.clean(text)             # shared
        chunks = self.split(text)           # shared
        self.store(chunks)                  # shared

    @abstractmethod
    def load(self, source) -> str: ...

    def clean(self, text): return " ".join(text.split())
    def split(self, text, size=500): return [text[i:i + size] for i in range(0, len(text), size)]
    def store(self, chunks): print(f"stored {len(chunks)} chunks")

class TextFileIngestor(Ingestor):
    def load(self, source): return open(source).read()

class WebIngestor(Ingestor):
    def load(self, source):
        import urllib.request
        return urllib.request.urlopen(source).read().decode()
```

Adding a new source means writing one `load()`.

## Template Method vs Strategy

- **Template Method** uses **inheritance**: the subclass fills in steps of a fixed flow.
- **Strategy** uses **composition**: you plug in a whole algorithm from outside.

If you want to swap behaviour at run time, prefer Strategy. If the skeleton is truly fixed,
Template Method is simpler.

## Common mistakes

- **Subclasses overriding `run()`.** Then the fixed order is lost. Document that it is final.
- **Too many abstract steps.** If every step must be overridden, there is nothing shared.
- **Deep inheritance chains.** Keep it to one level where you can.
- **Forgetting to call `super()`** in a step that extends the default behaviour.

## Hands-on exercises

**Exercise 1 · Tea and coffee.** Write `Beverage.prepare()` with `boil_water`, `brew`, `pour`,
`add_extras`.

<details class="solution"><summary>Solution</summary>

```python
class Beverage(ABC):
    def prepare(self):
        self.boil_water()
        self.brew()
        self.pour()
        self.add_extras()

    def boil_water(self): print("boiling water")
    def pour(self): print("pouring into cup")

    @abstractmethod
    def brew(self): ...
    @abstractmethod
    def add_extras(self): ...

class Tea(Beverage):
    def brew(self): print("steeping tea leaves")
    def add_extras(self): print("adding lemon")

class Coffee(Beverage):
    def brew(self): print("dripping coffee")
    def add_extras(self): print("adding sugar and milk")

Coffee().prepare()
```

</details>

**Exercise 2 · Report generator.** Fixed flow: fetch → format → header/footer → send. Make
`PDFReport` and `EmailReport`.

<details class="solution"><summary>Solution</summary>

```python
class Report(ABC):
    def generate(self):
        data = self.fetch()
        body = self.format(data)
        print(f"== {self.title()} ==")
        print(body)
        print("== end ==")
        self.send()

    def title(self): return "Report"

    @abstractmethod
    def fetch(self): ...
    @abstractmethod
    def format(self, data): ...
    @abstractmethod
    def send(self): ...

class SalesReport(Report):
    def title(self): return "Sales"
    def fetch(self): return [100, 150]
    def format(self, data): return ", ".join(map(str, data))
    def send(self): print("emailed to manager")

SalesReport().generate()
```

</details>

**Exercise 3 · Add a hook.** Add `should_skip(rows)` to `Pipeline` that lets a subclass skip loading
when there is no data.

<details class="solution"><summary>Solution</summary>

```python
class Pipeline(ABC):
    def run(self):
        self.connect()
        rows = self.transform(self.extract())
        if not self.should_skip(rows):
            self.load(rows)
        self.close()

    def should_skip(self, rows) -> bool:
        return False                      # hook

class NonEmptyPipeline(APIPipeline):
    def should_skip(self, rows):
        return len(rows) == 0
```

</details>

## Full source

<details class="source">
<summary>1.template.py</summary>

```{literalinclude} ../code/17-template-method/1.template.py
:language: python
```

</details>

<details class="source">
<summary>3.ingest.py</summary>

```{literalinclude} ../code/17-template-method/3.ingest.py
:language: python
```

</details>

**Downloads:**
{download}`0.no_template.py <../code/17-template-method/0.no_template.py>` ·
{download}`1.template.py <../code/17-template-method/1.template.py>` ·
{download}`2.hooks.py <../code/17-template-method/2.hooks.py>` ·
{download}`3.ingest.py <../code/17-template-method/3.ingest.py>`
