# Session 1 · Singleton pattern

## The big idea

Some things in a program should exist **exactly once**: the app settings, the logger, the database
connection pool, the LLM client. If every part of the code makes its own copy, you waste memory,
open too many connections and end up with copies that disagree with each other.

The **Singleton** pattern guarantees two things: the class has **only one instance**, and everyone
gets **that same instance**.

**Everyday example:** the electricity meter of a house. There is one meter. The kitchen, the fan
and the TV are all counted on it. Nobody installs a second meter for each room.

:::{admonition} In plain words
:class: tip
Make sure there is only **one** of something, and that every part of the program uses that same one. The first person to ask creates it; everyone after that gets the one that already exists.

**Reach for it when:**

- several copies of the same thing would waste memory or connections
- copies could disagree (settings, a cache, a logger)
- there is a real rule that only one may exist, not just that one is convenient
:::

## Without Singleton

`0.no_singleton.py`: every call builds a new object.

```python
class Config:
    def __init__(self):
        print("Loading config from disk...")
        self.settings = {"debug": False}

a = Config()
b = Config()

a.settings["debug"] = True
print(a is b)               # False
print(b.settings["debug"])  # False  ← b never heard about the change
```

```text
Loading config from disk...
Loading config from disk...
False
False
```

Two objects, two disk reads, two different truths. In a real app this shows up as "I changed the
setting but nothing happened".

## With Singleton

`1.singleton_new.py`: Python calls `__new__` to build the object, so we decide there whether to
build a new one or return the old one.

```python
class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print("Loading config from disk...")
            cls._instance = super().__new__(cls)
            cls._instance.settings = {"debug": False}
        return cls._instance

a = Config()
b = Config()

a.settings["debug"] = True
print(a is b)               # True
print(b.settings["debug"])  # True
```

```text
Loading config from disk...
True
True
```

Loaded once, shared by everyone.

```{raw} html
:file: ../diagrams/s01-singleton.html
```

Note that we set the data inside `__new__` and did **not** write an `__init__`. Python runs
`__init__` on every call, even when `__new__` returns the old object, so it would reset your data.

## Ways to build one in Python

**1. A module is already a Singleton** (`2.module_singleton/`). Python imports a module once and
caches it. This is the simplest option and often the best:

```python
# settings.py
DEBUG = False
DB_URL = "postgresql://localhost/app"
```

```python
# anywhere else
import settings
settings.DEBUG = True      # everyone importing settings sees this
```

**2. A decorator** (`3.decorator.py`): reusable for any class.

```python
def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

@singleton
class Logger:
    def __init__(self):
        self.lines = []

assert Logger() is Logger()
```

**3. Thread-safe version** (`4.thread_safe.py`): if two threads call `Config()` at the same
moment, both may see `_instance is None` and both create one. A lock fixes that:

```python
import threading

class Config:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:               # fast check, no lock
            with cls._lock:
                if cls._instance is None:       # check again inside the lock
                    cls._instance = super().__new__(cls)
        return cls._instance
```

This is called **double-checked locking**.

## Singleton + AI: one LLM client

Creating an LLM client reads keys, sets up HTTP sessions and sometimes loads a model. You want
that once per process (`5.llm_client.py`):

```python
from functools import lru_cache
from langchain_groq import ChatGroq

@lru_cache(maxsize=1)
def get_llm():
    print("Creating LLM client...")
    return ChatGroq(model="openai/gpt-oss-120b")

llm_1 = get_llm()
llm_2 = get_llm()
print(llm_1 is llm_2)    # True, "Creating LLM client..." printed once
```

`lru_cache(maxsize=1)` on a function with no arguments is the shortest Singleton in Python.
FastAPI apps use exactly this trick for settings and database sessions.

## Common mistakes

- **Using it for everything.** A Singleton is global state in a nice costume. Use it only when
  "exactly one" is a real rule (config, pool, logger), not just because it is convenient.
- **Forgetting threads.** The plain `__new__` version can create two objects under load. Use the
  lock version in web apps.
- **Putting data in `__init__`.** It runs on every `Config()` call and wipes your state.
- **Hard-to-test code.** Tests share the one instance, so one test leaks into the next. Add a
  reset method for tests, or pass the object in as an argument instead of importing it everywhere.
- **Subclassing surprises.** All subclasses of a `_instance`-based Singleton share the same
  `_instance` unless each class has its own.

## Hands-on exercises

Try each one before opening the solution.

**Exercise 1 · Logger.** Build a `Logger` Singleton with `log(msg)` and `show()`. Log from two
different variables and check both see all messages.

<details class="solution"><summary>Solution</summary>

```python
class Logger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.lines = []
        return cls._instance

    def log(self, msg: str):
        self.lines.append(msg)

    def show(self):
        for line in self.lines:
            print(line)

a = Logger()
b = Logger()
a.log("server started")
b.log("user logged in")
a.show()
# server started
# user logged in
```

</details>

**Exercise 2 · Reset for tests.** Add a way to throw the instance away so each test starts clean.

<details class="solution"><summary>Solution</summary>

```python
class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.settings = {}
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None

c1 = Config()
Config.reset()
c2 = Config()
print(c1 is c2)    # False
```

Call `Config.reset()` in a test's setup or teardown. Never call it in production code.

</details>

**Exercise 3 · Break it, then fix it.** Make the plain version create two objects using threads,
then fix it with a lock.

<details class="solution"><summary>Solution</summary>

```python
import threading, time

class Slow:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            time.sleep(0.1)                 # pretend loading takes time
            cls._instance = super().__new__(cls)
        return cls._instance

ids = []
def work():
    ids.append(id(Slow()))

threads = [threading.Thread(target=work) for _ in range(5)]
[t.start() for t in threads]
[t.join() for t in threads]
print(len(set(ids)))    # usually more than 1  ← broken
```

Fix: add `_lock = threading.Lock()` and the double check from the thread-safe section. Now
`len(set(ids))` is always `1`.

</details>

**Exercise 4 · Decorator on two classes.** Apply the `singleton` decorator to `Logger` and
`Cache`. Are they the same object?

<details class="solution"><summary>Solution</summary>

```python
@singleton
class Logger: ...

@singleton
class Cache: ...

print(Logger() is Logger())   # True
print(Cache() is Cache())     # True
print(Logger() is Cache())    # False
```

Each class gets its own single instance, because `instances` is keyed by the class.

One catch: after decoration, `Logger` is a function, not a class, so `isinstance(x, Logger)`
fails. That is one reason to prefer `__new__` or `lru_cache`.

</details>

**Exercise 5 · Database connection.** Write `get_connection()` that opens a SQLite connection
only once and returns the same one on every call.

<details class="solution"><summary>Solution</summary>

```python
import sqlite3
from functools import lru_cache

@lru_cache(maxsize=1)
def get_connection():
    print("Opening connection...")
    return sqlite3.connect("app.db", check_same_thread=False)

c1 = get_connection()
c2 = get_connection()
print(c1 is c2)    # True
```

`check_same_thread=False` lets other threads use the connection. For heavy traffic use a
connection **pool** instead, and make the pool the Singleton.

</details>

## Full source

<details class="source">
<summary>1.singleton_new.py</summary>

```{literalinclude} ../code/01-singleton/1.singleton_new.py
:language: python
```

</details>

<details class="source">
<summary>4.thread_safe.py</summary>

```{literalinclude} ../code/01-singleton/4.thread_safe.py
:language: python
```

</details>

<details class="source">
<summary>5.llm_client.py</summary>

```{literalinclude} ../code/01-singleton/5.llm_client.py
:language: python
```

</details>

**Downloads:**
{download}`0.no_singleton.py <../code/01-singleton/0.no_singleton.py>` ·
{download}`1.singleton_new.py <../code/01-singleton/1.singleton_new.py>` ·
{download}`2.module_singleton/settings.py <../code/01-singleton/2.module_singleton/settings.py>` ·
{download}`2.module_singleton/app.py <../code/01-singleton/2.module_singleton/app.py>` ·
{download}`3.decorator.py <../code/01-singleton/3.decorator.py>` ·
{download}`4.thread_safe.py <../code/01-singleton/4.thread_safe.py>` ·
{download}`5.llm_client.py <../code/01-singleton/5.llm_client.py>`
