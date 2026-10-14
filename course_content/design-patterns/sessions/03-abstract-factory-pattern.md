# Session 3 · Abstract Factory pattern

## The big idea

Factory Method creates **one** kind of object. Sometimes you need a whole **family** of objects that
must match each other: all "AWS" pieces together, or all "local" pieces together. Mixing an S3
storage with a local queue by mistake causes bugs that are hard to find.

The **Abstract Factory** pattern gives you one factory per family. Pick the factory once, and every
object it creates belongs to the same family.

**Everyday example:** a furniture showroom with "Modern" and "Classic" sets. You choose the set
once, and the sofa, table and chair all match.

:::{admonition} In plain words
:class: tip
When several objects must **match each other**, get them all from one factory for that family. Pick the family once, and every piece you get belongs together.

**Reach for it when:**

- you have sets of objects that only work together (local vs cloud, light vs dark theme)
- mixing pieces from different sets would cause bugs
- switching the whole set should be a one-line change
:::

## Without Abstract Factory

`0.mixed.py`: the caller picks each piece, so mismatches are easy.

```python
storage = S3Storage()
queue = LocalQueue()      # oops: cloud storage with a local queue
```

Nothing stops this. The code runs on a laptop and breaks in production.

## With Abstract Factory

`1.abstract_factory.py`:

```python
from abc import ABC, abstractmethod

class Storage(ABC):
    @abstractmethod
    def save(self, name: str, data: str): ...

class Queue(ABC):
    @abstractmethod
    def push(self, msg: str): ...

# Family 1: local development
class FileStorage(Storage):
    def save(self, name, data): print(f"[file] saved {name}")
class MemoryQueue(Queue):
    def push(self, msg): print(f"[memory] queued {msg}")

# Family 2: AWS
class S3Storage(Storage):
    def save(self, name, data): print(f"[s3] uploaded {name}")
class SQSQueue(Queue):
    def push(self, msg): print(f"[sqs] sent {msg}")

# The factories
class InfraFactory(ABC):
    @abstractmethod
    def create_storage(self) -> Storage: ...
    @abstractmethod
    def create_queue(self) -> Queue: ...

class LocalFactory(InfraFactory):
    def create_storage(self): return FileStorage()
    def create_queue(self): return MemoryQueue()

class AWSFactory(InfraFactory):
    def create_storage(self): return S3Storage()
    def create_queue(self): return SQSQueue()

def run_app(factory: InfraFactory):
    storage = factory.create_storage()
    queue = factory.create_queue()
    storage.save("report.pdf", "...")
    queue.push("report ready")

run_app(LocalFactory())
run_app(AWSFactory())
```

```text
[file] saved report.pdf
[memory] queued report ready
[s3] uploaded report.pdf
[sqs] sent report ready
```

`run_app` never names a concrete class, so a mismatch is impossible.

```{raw} html
:file: ../diagrams/s03-abstract-factory.html
```

## Factory Method vs Abstract Factory

| | Factory Method | Abstract Factory |
|---|---|---|
| Creates | one product | a family of related products |
| Typical form | one function or method | a class with several `create_*` methods |
| Use when | "which class?" | "which set of classes that go together?" |

## Abstract Factory + AI: one switch for the whole stack

A RAG app needs an LLM, an embedding model and a vector store that fit together (`2.rag_stack.py`):

```python
class RagStackFactory(ABC):
    @abstractmethod
    def create_llm(self): ...
    @abstractmethod
    def create_embeddings(self): ...
    @abstractmethod
    def create_vector_store(self): ...

class LocalRagStack(RagStackFactory):      # Ollama + Chroma
    ...
class CloudRagStack(RagStackFactory):      # hosted LLM + pgvector
    ...
```

Changing from laptop to cloud is one line: `factory = CloudRagStack()`.

## Common mistakes

- **Using it for two unrelated objects.** If the products don't have to match, use plain factories.
- **Adding a new product type late.** Adding `create_cache()` means editing every factory. Decide the
  product list early.
- **Leaking concrete classes** (`isinstance(storage, S3Storage)`). Then the family is not hidden.

## Hands-on exercises

**Exercise 1 · Light and dark UI.** Build `LightFactory` and `DarkFactory` that create a `Button`
and a `Checkbox` that print their theme.

<details class="solution"><summary>Solution</summary>

```python
class LightButton:
    def draw(self): print("light button")
class DarkButton:
    def draw(self): print("dark button")
class LightCheckbox:
    def draw(self): print("light checkbox")
class DarkCheckbox:
    def draw(self): print("dark checkbox")

class LightFactory:
    def create_button(self): return LightButton()
    def create_checkbox(self): return LightCheckbox()
class DarkFactory:
    def create_button(self): return DarkButton()
    def create_checkbox(self): return DarkCheckbox()

def render(f):
    f.create_button().draw()
    f.create_checkbox().draw()

render(DarkFactory())
```

</details>

**Exercise 2 · Pick the factory from an environment variable.**

<details class="solution"><summary>Solution</summary>

```python
import os

factories = {"local": LocalFactory, "aws": AWSFactory}
env = os.getenv("APP_ENV", "local")
factory = factories[env]()
run_app(factory)
```

Run with `APP_ENV=aws python app.py`.

</details>

**Exercise 3 · Add a third family.** Add an `AzureFactory` (Blob storage + Service Bus queue).

<details class="solution"><summary>Solution</summary>

```python
class BlobStorage(Storage):
    def save(self, name, data): print(f"[blob] uploaded {name}")
class ServiceBusQueue(Queue):
    def push(self, msg): print(f"[servicebus] sent {msg}")

class AzureFactory(InfraFactory):
    def create_storage(self): return BlobStorage()
    def create_queue(self): return ServiceBusQueue()
```

`run_app` is untouched. Adding a family is easy; adding a product type is the hard direction.

</details>

## Full source

<details class="source">
<summary>1.abstract_factory.py</summary>

```{literalinclude} ../code/03-abstract-factory/1.abstract_factory.py
:language: python
```

</details>

**Downloads:**
{download}`0.mixed.py <../code/03-abstract-factory/0.mixed.py>` ·
{download}`1.abstract_factory.py <../code/03-abstract-factory/1.abstract_factory.py>` ·
{download}`2.rag_stack.py <../code/03-abstract-factory/2.rag_stack.py>`
