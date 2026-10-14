# Session 7 · Decorator pattern

## The big idea

You want to **add behaviour** to an object or function (logging, timing, retrying, caching) without
changing its code and without creating a subclass for every combination. The **Decorator** pattern
wraps the original in another object with the **same interface** that does something extra before or
after.

**Everyday example:** a gift. The gift is the same inside. You wrap it in paper, then add a ribbon,
then a card. Each layer adds something, and you can pick which layers to use.

(The Python `@decorator` syntax is a close cousin. We cover both.)

:::{admonition} In plain words
:class: tip
**Wrap** something to give it an extra feature (logging, timing, retry) without changing it. The wrapped thing still looks and works the same from outside, and you can stack wrappers.

**Reach for it when:**

- you want the same extra behaviour on many functions or objects
- the extra work isn't part of the function's real job
- subclasses for every combination of features would explode
:::

## Without Decorator

`0.no_decorator.py`: extras pile up inside the function.

```python
import time

def get_price(item):
    start = time.time()
    print(f"calling get_price({item})")
    price = {"apple": 120, "mango": 200}[item]
    print(f"took {time.time() - start:.4f}s")
    return price
```

Timing and logging are mixed with the real work, and you copy them into every function.

## With Python function decorators

`1.func_decorator.py`:

```python
import time
from functools import wraps

def timed(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {time.perf_counter() - start:.4f}s")
        return result
    return wrapper

def logged(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"calling {func.__name__}{args}")
        return func(*args, **kwargs)
    return wrapper

@logged
@timed
def get_price(item):
    return {"apple": 120, "mango": 200}[item]

get_price("apple")
```

```text
calling get_price('apple',)
get_price took 0.0000s
```

`get_price` contains only the real logic. Stack decorators like layers. `@wraps` keeps the original
name and docstring.

## The classic object version

`2.classic.py`: wrap objects that share an interface. This works for classes too.

```python
from abc import ABC, abstractmethod

class Coffee(ABC):
    @abstractmethod
    def cost(self) -> int: ...
    @abstractmethod
    def description(self) -> str: ...

class Espresso(Coffee):
    def cost(self): return 100
    def description(self): return "Espresso"

class AddOn(Coffee):                       # the decorator base
    def __init__(self, coffee: Coffee):
        self._coffee = coffee

class Milk(AddOn):
    def cost(self): return self._coffee.cost() + 20
    def description(self): return self._coffee.description() + " + Milk"

class Sugar(AddOn):
    def cost(self): return self._coffee.cost() + 5
    def description(self): return self._coffee.description() + " + Sugar"

order = Sugar(Milk(Espresso()))
print(order.description(), order.cost())    # Espresso + Milk + Sugar 125
```

Without decorators, you would need `EspressoWithMilk`, `EspressoWithMilkAndSugar`, ... a class for
every combination.

```{raw} html
:file: ../diagrams/s07-decorator.html
```

## Decorator + AI: retry and cache around an LLM call

LLM calls fail and cost money. Add that protection without touching the call itself
(`3.llm_decorators.py`):

```python
import time
from functools import wraps, lru_cache

def retry(times=3, delay=1):
    def deco(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == times:
                        raise
                    print(f"attempt {attempt} failed: {e}. retrying...")
                    time.sleep(delay)
        return wrapper
    return deco

@lru_cache(maxsize=256)
@retry(times=3, delay=2)
def ask_llm(prompt: str) -> str:
    return llm.invoke(prompt).content
```

The same question is answered from the cache for free, and a flaky network is retried.

## Common mistakes

- **Forgetting `@wraps`.** Your function's `__name__` becomes `wrapper`, which breaks debugging.
- **Wrong order.** `@lru_cache` above `@retry` caches the final answer. Swap them and you cache the
  retrying wrapper, which is rarely what you want. Read stacked decorators from bottom to top.
- **Caching functions with side effects** (sending emails). A cached call does nothing the second time.
- **Decorators that change the return type.** The wrapper must behave like the original.

## Hands-on exercises

**Exercise 1 · `@timed` for async.** Write a timing decorator that works on `async def`.

<details class="solution"><summary>Solution</summary>

```python
import time, asyncio
from functools import wraps

def timed_async(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        print(f"{func.__name__} took {time.perf_counter() - start:.3f}s")
        return result
    return wrapper

@timed_async
async def fetch():
    await asyncio.sleep(0.5)
    return "done"

asyncio.run(fetch())
```

</details>

**Exercise 2 · `@require_admin`.** A decorator that raises `PermissionError` unless
`user["role"] == "admin"`.

<details class="solution"><summary>Solution</summary>

```python
from functools import wraps

def require_admin(func):
    @wraps(func)
    def wrapper(user, *args, **kwargs):
        if user.get("role") != "admin":
            raise PermissionError("admins only")
        return func(user, *args, **kwargs)
    return wrapper

@require_admin
def delete_all(user):
    print("deleted everything")

delete_all({"role": "admin"})
```

</details>

**Exercise 3 · Pizza toppings.** Rebuild the coffee example for pizza with `Cheese` and `Olives`.

<details class="solution"><summary>Solution</summary>

```python
class Pizza:
    def cost(self): return 200
    def description(self): return "Margherita"

class Topping:
    def __init__(self, pizza): self._p = pizza

class Cheese(Topping):
    def cost(self): return self._p.cost() + 40
    def description(self): return self._p.description() + " + Cheese"

class Olives(Topping):
    def cost(self): return self._p.cost() + 25
    def description(self): return self._p.description() + " + Olives"

p = Olives(Cheese(Pizza()))
print(p.description(), p.cost())    # Margherita + Cheese + Olives 265
```

</details>

## Full source

<details class="source">
<summary>1.func_decorator.py</summary>

```{literalinclude} ../code/07-decorator/1.func_decorator.py
:language: python
```

</details>

<details class="source">
<summary>3.llm_decorators.py</summary>

```{literalinclude} ../code/07-decorator/3.llm_decorators.py
:language: python
```

</details>

**Downloads:**
{download}`0.no_decorator.py <../code/07-decorator/0.no_decorator.py>` ·
{download}`1.func_decorator.py <../code/07-decorator/1.func_decorator.py>` ·
{download}`2.classic.py <../code/07-decorator/2.classic.py>` ·
{download}`3.llm_decorators.py <../code/07-decorator/3.llm_decorators.py>`
