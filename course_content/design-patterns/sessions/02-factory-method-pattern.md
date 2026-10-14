# Session 2 · Factory Method pattern

## The big idea

Your code often needs to create objects, but **which class** to create depends on a value that is
only known at run time (a setting, a user choice, a file extension). If you write `if/elif` for
that choice in many places, adding one new type means editing every place.

The **Factory Method** pattern moves the "which class?" decision into **one place**. The rest of the
code asks the factory for an object and just uses it.

**Everyday example:** a juice shop. You say "mango" and get a mango juice. You don't walk into the
kitchen and pick the fruit and machine yourself.

:::{admonition} In plain words
:class: tip
Don't make each part of your code decide which class to create. Put that decision in **one place** (the factory). Everyone else just says what they want by name.

**Reach for it when:**

- the same `if type == …` to create objects appears in several places
- the class to use depends on a setting, a user's choice or a file type
- you expect new types to be added later
:::

## Without a factory

`0.no_factory.py`: the decision is repeated everywhere.

```python
class EmailNotifier:
    def send(self, msg): print(f"EMAIL: {msg}")

class SMSNotifier:
    def send(self, msg): print(f"SMS: {msg}")

def welcome_user(channel: str):
    if channel == "email":
        n = EmailNotifier()
    elif channel == "sms":
        n = SMSNotifier()
    else:
        raise ValueError(f"unknown channel {channel}")
    n.send("Welcome!")

def send_invoice(channel: str):
    if channel == "email":      # same if/elif copied again
        n = EmailNotifier()
    elif channel == "sms":
        n = SMSNotifier()
    else:
        raise ValueError(f"unknown channel {channel}")
    n.send("Invoice ready")
```

Add WhatsApp and you must edit `welcome_user`, `send_invoice` and every other copy.

## With Factory Method

`1.factory.py`: one function decides, everyone else just asks.

```python
def create_notifier(channel: str):
    notifiers = {"email": EmailNotifier, "sms": SMSNotifier}
    try:
        return notifiers[channel]()
    except KeyError:
        raise ValueError(f"unknown channel {channel!r}. Choose from {list(notifiers)}")

def welcome_user(channel: str):
    create_notifier(channel).send("Welcome!")

def send_invoice(channel: str):
    create_notifier(channel).send("Invoice ready")

welcome_user("sms")       # SMS: Welcome!
```

To add WhatsApp you write one class and add one line to the dictionary. `welcome_user` and
`send_invoice` don't change.

```{raw} html
:file: ../diagrams/s02-factory.html
```

## The classic version: subclasses decide

`2.classic.py`: the textbook pattern uses a creator class with a `create()` method that
subclasses override.

```python
from abc import ABC, abstractmethod

class Notifier(ABC):
    @abstractmethod
    def send(self, msg: str): ...

class EmailNotifier(Notifier):
    def send(self, msg): print(f"EMAIL: {msg}")

class Alert(ABC):
    @abstractmethod
    def create_notifier(self) -> Notifier:      # ← the factory method
        ...

    def raise_alert(self, msg: str):
        self.create_notifier().send(msg)         # works with any notifier

class EmailAlert(Alert):
    def create_notifier(self) -> Notifier:
        return EmailNotifier()

EmailAlert().raise_alert("Disk is full")
```

In Python the dictionary version is usually enough. Use the class version when each creator also
has its own logic around the object.

## Factory + AI: pick the LLM provider

Same app, different model per environment (`3.llm_factory.py`):

```python
import os

def create_llm(provider: str):
    if provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(model="openai/gpt-oss-120b")
    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model="gpt-4o-mini")
    raise ValueError(f"unknown provider {provider!r}")

llm = create_llm(os.getenv("LLM_PROVIDER", "groq"))
```

Imports sit inside the branches, so you only need the package for the provider you actually use.

## Common mistakes

- **A factory for one class.** If there is only ever one type, `Notifier()` is fine.
- **A giant `if/elif` inside the factory.** Past 4 or 5 types, switch to a dictionary (registry).
- **Silent fallback.** Returning a default for an unknown name hides typos. Raise a clear error.
- **Callers checking the type afterwards** (`if isinstance(n, EmailNotifier)`). Then the factory
  isn't hiding anything. Give all products the same methods.

## Hands-on exercises

**Exercise 1 · WhatsApp.** Add a `whatsapp` channel to `1.factory.py`.

<details class="solution"><summary>Solution</summary>

```python
class WhatsAppNotifier:
    def send(self, msg): print(f"WHATSAPP: {msg}")

notifiers = {"email": EmailNotifier, "sms": SMSNotifier, "whatsapp": WhatsAppNotifier}
```

Nothing else changes.

</details>

**Exercise 2 · File readers.** Build `create_reader(path)` that returns `CSVReader`, `JSONReader`
or `TextReader` based on the file extension.

<details class="solution"><summary>Solution</summary>

```python
from pathlib import Path

class CSVReader:  
    def read(self, p): return Path(p).read_text().splitlines()
class JSONReader:
    def read(self, p):
        import json
        return json.loads(Path(p).read_text())
class TextReader:
    def read(self, p): return Path(p).read_text()

def create_reader(path: str):
    readers = {".csv": CSVReader, ".json": JSONReader, ".txt": TextReader}
    ext = Path(path).suffix.lower()
    if ext not in readers:
        raise ValueError(f"no reader for {ext!r}")
    return readers[ext]()
```

</details>

**Exercise 3 · Self-registering factory.** Let each class register itself, so the factory never
needs editing.

<details class="solution"><summary>Solution</summary>

```python
_registry = {}

def register(name):
    def wrap(cls):
        _registry[name] = cls
        return cls
    return wrap

@register("email")
class EmailNotifier:
    def send(self, msg): print(f"EMAIL: {msg}")

@register("sms")
class SMSNotifier:
    def send(self, msg): print(f"SMS: {msg}")

def create_notifier(name):
    return _registry[name]()
```

New classes just add `@register("x")`. This is how plugin systems work.

</details>

## Full source

<details class="source">
<summary>1.factory.py</summary>

```{literalinclude} ../code/02-factory/1.factory.py
:language: python
```

</details>

<details class="source">
<summary>3.llm_factory.py</summary>

```{literalinclude} ../code/02-factory/3.llm_factory.py
:language: python
```

</details>

**Downloads:**
{download}`0.no_factory.py <../code/02-factory/0.no_factory.py>` ·
{download}`1.factory.py <../code/02-factory/1.factory.py>` ·
{download}`2.classic.py <../code/02-factory/2.classic.py>` ·
{download}`3.llm_factory.py <../code/02-factory/3.llm_factory.py>`
