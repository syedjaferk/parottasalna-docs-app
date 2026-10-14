# Session 4 · Builder pattern

## The big idea

Some objects have many settings, and most are optional. A constructor with 10 arguments is hard to
read: `Request("GET", url, None, None, 30, True, False, None)` means nothing. The **Builder**
pattern builds the object **step by step** with named steps, then gives you the finished object.

**Everyday example:** ordering a custom pizza. You choose the base, then sauce, then toppings, one at
a time. Only at the end does the kitchen make it.

:::{admonition} In plain words
:class: tip
Build a complicated object **one named step at a time** instead of one giant constructor call. At the end, `build()` checks everything and hands you the finished object.

**Reach for it when:**

- a constructor has many arguments, most of them optional
- building takes several steps, or the order matters
- you want to validate the whole object before it's used
:::

## Without Builder

`0.no_builder.py`:

```python
class Pizza:
    def __init__(self, size, crust, cheese, toppings, extra_cheese, sauce, gluten_free):
        ...

p = Pizza("large", "thin", True, ["olives", "corn"], False, "tomato", True)
```

Which `True` is which? Was `False` for `extra_cheese` or something else?

## With Builder

`1.builder.py`: each method sets one thing and returns `self`, so calls chain.

```python
from dataclasses import dataclass, field

@dataclass
class Pizza:
    size: str
    crust: str
    sauce: str
    toppings: list[str] = field(default_factory=list)
    extra_cheese: bool = False

class PizzaBuilder:
    def __init__(self):
        self._size = "medium"
        self._crust = "regular"
        self._sauce = "tomato"
        self._toppings = []
        self._extra_cheese = False

    def size(self, s):        self._size = s;        return self
    def crust(self, c):       self._crust = c;       return self
    def sauce(self, s):       self._sauce = s;       return self
    def topping(self, t):     self._toppings.append(t); return self
    def extra_cheese(self):   self._extra_cheese = True; return self

    def build(self) -> Pizza:
        if len(self._toppings) > 5:
            raise ValueError("max 5 toppings")
        return Pizza(self._size, self._crust, self._sauce, self._toppings, self._extra_cheese)

pizza = (PizzaBuilder()
         .size("large")
         .crust("thin")
         .topping("olives")
         .topping("corn")
         .extra_cheese()
         .build())
print(pizza)
```

```text
Pizza(size='large', crust='thin', sauce='tomato', toppings=['olives', 'corn'], extra_cheese=True)
```

Every line says what it sets. The checks live in `build()`, so you can never get an invalid pizza.

```{raw} html
:file: ../diagrams/s04-builder.html
```

## Do you need a builder in Python?

Python has **keyword arguments with defaults**, which solve many cases (`2.kwargs.py`):

```python
Pizza(size="large", crust="thin", toppings=["olives"], extra_cheese=True)
```

Use a Builder when:

- building takes **several steps** or the order matters,
- you need to **validate** at the end,
- the same builder should produce **different results** (reuse with `reset()`),
- the object is **immutable**, so it can't be changed after creation.

For simple data, a `dataclass` with defaults is enough.

## Builder + AI: building a prompt

A good prompt has parts: role, context, examples, question, output format (`3.prompt_builder.py`):

```python
class PromptBuilder:
    def __init__(self):
        self._parts = {}
        self._examples = []

    def role(self, text):      self._parts["role"] = text;     return self
    def context(self, text):   self._parts["context"] = text;  return self
    def example(self, q, a):   self._examples.append((q, a));  return self
    def question(self, text):  self._parts["question"] = text; return self
    def format(self, text):    self._parts["format"] = text;   return self

    def build(self) -> str:
        if "question" not in self._parts:
            raise ValueError("a prompt needs a question")
        out = []
        if "role" in self._parts:    out.append(f"You are {self._parts['role']}.")
        if "context" in self._parts: out.append(f"Context:\n{self._parts['context']}")
        for q, a in self._examples:  out.append(f"Q: {q}\nA: {a}")
        out.append(f"Question: {self._parts['question']}")
        if "format" in self._parts:  out.append(f"Answer format: {self._parts['format']}")
        return "\n\n".join(out)

prompt = (PromptBuilder()
          .role("a helpful Python tutor")
          .example("What is a list?", "An ordered collection.")
          .question("What is a tuple?")
          .format("one sentence")
          .build())
```

## Common mistakes

- **Forgetting `return self`.** The chain breaks with `'NoneType' has no attribute ...`.
- **Reusing a builder without resetting.** Toppings from the first pizza appear on the second.
- **No validation in `build()`.** Then a builder is just a long-winded constructor.
- **Using a builder for a 3-field object.** Keyword arguments are simpler.

## Hands-on exercises

**Exercise 1 · SQL query builder.** Build `select("name").from_("users").where("age > 18").build()`
→ `SELECT name FROM users WHERE age > 18`.

<details class="solution"><summary>Solution</summary>

```python
class QueryBuilder:
    def __init__(self):
        self._cols, self._table, self._where = "*", None, []

    def select(self, cols): self._cols = cols; return self
    def from_(self, table): self._table = table; return self
    def where(self, cond): self._where.append(cond); return self

    def build(self):
        if not self._table:
            raise ValueError("from_() is required")
        sql = f"SELECT {self._cols} FROM {self._table}"
        if self._where:
            sql += " WHERE " + " AND ".join(self._where)
        return sql

print(QueryBuilder().select("name").from_("users").where("age > 18").build())
```

This is only for learning. Real code must use parameterised queries to avoid SQL injection.

</details>

**Exercise 2 · Reset.** Add `reset()` so one builder makes two pizzas.

<details class="solution"><summary>Solution</summary>

```python
class PizzaBuilder:
    def __init__(self):
        self.reset()

    def reset(self):
        self._size, self._crust, self._sauce = "medium", "regular", "tomato"
        self._toppings, self._extra_cheese = [], False
        return self
```

Call `builder.reset()` after `build()` to start a fresh pizza.

</details>

**Exercise 3 · HTTP request builder.** Build a request with method, url, headers and a JSON body.
`build()` must fail if the url is missing.

<details class="solution"><summary>Solution</summary>

```python
class RequestBuilder:
    def __init__(self):
        self._method, self._url, self._headers, self._body = "GET", None, {}, None

    def method(self, m): self._method = m; return self
    def url(self, u): self._url = u; return self
    def header(self, k, v): self._headers[k] = v; return self
    def json(self, body): self._body = body; return self

    def build(self):
        if not self._url:
            raise ValueError("url is required")
        return {"method": self._method, "url": self._url,
                "headers": self._headers, "json": self._body}

req = RequestBuilder().method("POST").url("https://api.test/users").header("X-Key", "1").json({"a": 1}).build()
```

</details>

## Full source

<details class="source">
<summary>1.builder.py</summary>

```{literalinclude} ../code/04-builder/1.builder.py
:language: python
```

</details>

<details class="source">
<summary>3.prompt_builder.py</summary>

```{literalinclude} ../code/04-builder/3.prompt_builder.py
:language: python
```

</details>

**Downloads:**
{download}`0.no_builder.py <../code/04-builder/0.no_builder.py>` ·
{download}`1.builder.py <../code/04-builder/1.builder.py>` ·
{download}`2.kwargs.py <../code/04-builder/2.kwargs.py>` ·
{download}`3.prompt_builder.py <../code/04-builder/3.prompt_builder.py>`
