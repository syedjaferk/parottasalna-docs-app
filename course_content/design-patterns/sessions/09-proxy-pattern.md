# Session 9 · Proxy pattern

## The big idea

Sometimes you don't want callers to talk to the real object directly. It may be slow to create,
far away (on a network), expensive to call, or needs permission checks. The **Proxy** pattern puts a
**stand-in object with the same interface** in front. The caller can't tell the difference, but the
proxy can delay, cache, check or log before passing the call on.

**Everyday example:** a cheque. It stands in for money. It has the same purpose, but there are checks
(signature, balance) before real money moves.

:::{admonition} In plain words
:class: tip
Put a **stand-in** in front of the real object. It looks exactly the same to the caller, but it can wait to create the real thing, remember answers, or check permission first.

**Reach for it when:**

- the real object is slow, expensive, remote or sensitive
- you want lazy loading, caching, access checks or logging
- callers must not notice the difference
:::

## Without Proxy

`0.no_proxy.py`: the heavy object is built immediately, and every call is expensive.

```python
class ImageViewer:
    def __init__(self, path):
        print(f"Loading {path} from disk... (slow)")
        self.path = path

    def show(self):
        print(f"Showing {self.path}")

gallery = [ImageViewer(f"photo{i}.jpg") for i in range(5)]    # loads all 5 now, even if you view 1
gallery[0].show()
```

## With a virtual (lazy) proxy

`1.lazy_proxy.py`: load only when really needed.

```python
class RealImage:
    def __init__(self, path):
        print(f"Loading {path} from disk... (slow)")
        self.path = path
    def show(self):
        print(f"Showing {self.path}")

class LazyImage:
    def __init__(self, path):
        self.path = path
        self._real = None

    def show(self):
        if self._real is None:
            self._real = RealImage(self.path)      # created on first use
        self._real.show()

gallery = [LazyImage(f"photo{i}.jpg") for i in range(5)]    # instant
gallery[0].show()    # loads only photo0
gallery[0].show()    # already loaded
```

```text
Loading photo0.jpg from disk... (slow)
Showing photo0.jpg
Showing photo0.jpg
```

```{raw} html
:file: ../diagrams/s09-proxy.html
```

## Kinds of proxy

| Type | What it does | Example |
|---|---|---|
| **Virtual** | delays creating the real object | lazy image, lazy DB connection |
| **Caching** | remembers results | API response cache |
| **Protection** | checks permission | only admins can delete |
| **Remote** | represents something on another machine | gRPC / REST client stub |
| **Logging** | records calls | audit trail |

## A protection proxy

`2.protection_proxy.py`:

```python
class Database:
    def delete(self, table): print(f"deleted {table}")

class SecureDatabase:
    def __init__(self, db, user):
        self._db, self._user = db, user

    def delete(self, table):
        if self._user["role"] != "admin":
            raise PermissionError("only admins can delete")
        self._db.delete(table)

db = SecureDatabase(Database(), {"name": "Kavya", "role": "viewer"})
db.delete("users")      # PermissionError: only admins can delete
```

## Proxy + AI: caching LLM proxy

Same question again → answer from memory, no API cost (`3.llm_proxy.py`):

```python
class CachingLLM:
    def __init__(self, llm):
        self._llm = llm
        self._cache = {}
        self.hits = 0

    def invoke(self, prompt: str) -> str:
        if prompt in self._cache:
            self.hits += 1
            return self._cache[prompt]
        answer = self._llm.invoke(prompt).content
        self._cache[prompt] = answer
        return answer

llm = CachingLLM(real_llm)       # same .invoke() as before
llm.invoke("What is a proxy?")   # calls the API
llm.invoke("What is a proxy?")   # served from the cache, llm.hits == 1
```

## Proxy vs Decorator

They look the same in code (wrap, same interface). The **intent** differs:

- **Decorator** adds a new behaviour the caller asked for (retry, timing).
- **Proxy** controls access to the object (when it is made, who may call it, where it lives).

## Common mistakes

- **A proxy with a different interface.** Callers must be able to swap it for the real object.
- **Unbounded cache.** The dictionary grows forever. Use `lru_cache` or a size limit.
- **Caching LLM answers when randomness is wanted.** Only cache when `temperature` is 0 or the same
  answer is acceptable.
- **Forgetting thread safety** in a lazy proxy. Two threads may both create the real object.

## Hands-on exercises

**Exercise 1 · Logging proxy.** Print every method call and its arguments, then forward it.

<details class="solution"><summary>Solution</summary>

```python
class LoggingProxy:
    def __init__(self, target):
        self._target = target

    def __getattr__(self, name):
        attr = getattr(self._target, name)
        if not callable(attr):
            return attr
        def wrapper(*args, **kwargs):
            print(f"calling {name}{args}")
            return attr(*args, **kwargs)
        return wrapper

class Calc:
    def add(self, a, b): return a + b

c = LoggingProxy(Calc())
print(c.add(2, 3))
# calling add(2, 3)
# 5
```

</details>

**Exercise 2 · Rate-limit proxy.** Allow at most 3 calls per minute.

<details class="solution"><summary>Solution</summary>

```python
import time

class RateLimited:
    def __init__(self, target, limit=3, window=60):
        self._t, self._limit, self._window = target, limit, window
        self._calls = []

    def call(self, *args):
        now = time.time()
        self._calls = [t for t in self._calls if now - t < self._window]
        if len(self._calls) >= self._limit:
            raise RuntimeError("rate limit exceeded")
        self._calls.append(now)
        return self._t.call(*args)
```

</details>

**Exercise 3 · Expiry.** Make the LLM cache entries expire after 10 minutes.

<details class="solution"><summary>Solution</summary>

```python
import time

class ExpiringCache:
    def __init__(self, llm, ttl=600):
        self._llm, self._ttl, self._cache = llm, ttl, {}

    def invoke(self, prompt):
        hit = self._cache.get(prompt)
        if hit and time.time() - hit[1] < self._ttl:
            return hit[0]
        answer = self._llm.invoke(prompt).content
        self._cache[prompt] = (answer, time.time())
        return answer
```

</details>

## Full source

<details class="source">
<summary>1.lazy_proxy.py</summary>

```{literalinclude} ../code/09-proxy/1.lazy_proxy.py
:language: python
```

</details>

<details class="source">
<summary>3.llm_proxy.py</summary>

```{literalinclude} ../code/09-proxy/3.llm_proxy.py
:language: python
```

</details>

**Downloads:**
{download}`0.no_proxy.py <../code/09-proxy/0.no_proxy.py>` ·
{download}`1.lazy_proxy.py <../code/09-proxy/1.lazy_proxy.py>` ·
{download}`2.protection_proxy.py <../code/09-proxy/2.protection_proxy.py>` ·
{download}`3.llm_proxy.py <../code/09-proxy/3.llm_proxy.py>`
