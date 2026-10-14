# Session 13 · Strategy pattern

## The big idea

You have **one job** that can be done in **several ways**, and you want to switch the way without
rewriting the code that uses it. The **Strategy** pattern puts each way in its own small class (or
function) with the same interface, and the caller just *plugs one in*.

**Everyday example:** going to the airport. You can take a cab, a bus or the metro. The goal
("reach the airport") is the same. You choose the method by budget or time.

:::{admonition} In plain words
:class: tip
A job can be done in **several ways**. Put each way in its own small piece with the same shape, and let the caller plug in the one it wants.

**Reach for it when:**

- an `if/elif` chooses between different ways of doing the same job
- new ways keep being added
- you want to switch the way at run time or test each one alone
:::

## Without Strategy

`0.no_strategy.py`: a growing `if/elif`.

```python
def checkout(total, customer_type):
    if customer_type == "regular":
        return total
    elif customer_type == "student":
        return total * 0.9
    elif customer_type == "premium":
        return total * 0.8
    elif customer_type == "festival":
        return total - 100
    raise ValueError(customer_type)
```

Each new offer edits this function, risks old offers and makes testing harder.

## With Strategy

`1.strategy.py`:

```python
from abc import ABC, abstractmethod

class Discount(ABC):
    @abstractmethod
    def apply(self, total: float) -> float: ...

class NoDiscount(Discount):
    def apply(self, total): return total

class StudentDiscount(Discount):
    def apply(self, total): return total * 0.9

class PremiumDiscount(Discount):
    def apply(self, total): return total * 0.8

class FlatOff(Discount):
    def __init__(self, amount): self.amount = amount
    def apply(self, total): return max(total - self.amount, 0)

class Cart:
    def __init__(self, discount: Discount):
        self.discount = discount
        self.total = 0
    def add(self, price): self.total += price
    def checkout(self): return self.discount.apply(self.total)

cart = Cart(StudentDiscount())
cart.add(500); cart.add(500)
print(cart.checkout())            # 900.0

cart.discount = FlatOff(100)      # swap at run time
print(cart.checkout())            # 900
```

A new offer is a new class. `Cart` never changes.

```{raw} html
:file: ../diagrams/s13-strategy.html
```

## The Pythonic way: functions are strategies

Because functions are objects, a strategy can be just a function (`2.func_strategy.py`):

```python
def student(total):  return total * 0.9
def premium(total):  return total * 0.8
def flat_100(total): return max(total - 100, 0)

def checkout(total, discount=lambda t: t):
    return discount(total)

print(checkout(1000, student))      # 900.0
print(checkout(1000, flat_100))     # 900
```

If a strategy has no state, a function is shorter and just as clear. Use a class when it needs
settings (`FlatOff(amount)`) or several methods.

## Strategy + AI: swap how you chunk text

In RAG, how you split documents changes answer quality. Try different strategies on the same
pipeline (`3.chunking.py`):

```python
def by_size(text, size=500):
    return [text[i:i + size] for i in range(0, len(text), size)]

def by_paragraph(text):
    return [p.strip() for p in text.split("\n\n") if p.strip()]

def by_sentence(text):
    return [s.strip() + "." for s in text.split(".") if s.strip()]

def ingest(text, chunker=by_paragraph):
    chunks = chunker(text)
    print(f"{len(chunks)} chunks via {chunker.__name__}")
    return chunks

doc = "Python is easy.\n\nIt has many libraries. People love it."
ingest(doc, by_paragraph)    # 2 chunks via by_paragraph
ingest(doc, by_sentence)     # 3 chunks via by_sentence
```

The same idea applies to retrieval (similarity vs MMR), prompt styles and model choice.

## Strategy vs Factory

- **Factory** answers "which object do I create?"
- **Strategy** answers "which behaviour do I use?"

They often work together: a factory picks the strategy from a config value.

## Common mistakes

- **Too few variations.** Two simple options don't need classes. An `if` is fine.
- **Strategies that need to know about the caller.** Pass the data in as arguments instead.
- **Choosing the strategy inside the strategy.** Selection belongs outside, in the caller or a factory.
- **Different method signatures.** All strategies must be interchangeable.

## Hands-on exercises

**Exercise 1 · Sorting.** Let a `Sorter` use a strategy: `by_name`, `by_age`, `by_age_desc`.

<details class="solution"><summary>Solution</summary>

```python
people = [{"name": "Kavya", "age": 9}, {"name": "Arun", "age": 30}, {"name": "Banu", "age": 21}]

by_name = lambda p: p["name"]
by_age = lambda p: p["age"]

def sort_people(items, key, reverse=False):
    return sorted(items, key=key, reverse=reverse)

print(sort_people(people, by_age, reverse=True)[0]["name"])    # Arun
```

Python's `sorted(key=...)` is itself the Strategy pattern.

</details>

**Exercise 2 · Shipping cost.** Add `Standard`, `Express` and `Pickup` strategies based on weight.

<details class="solution"><summary>Solution</summary>

```python
class Shipping(ABC):
    @abstractmethod
    def cost(self, kg: float) -> float: ...

class Standard(Shipping):
    def cost(self, kg): return 40 + 10 * kg
class Express(Shipping):
    def cost(self, kg): return 100 + 25 * kg
class Pickup(Shipping):
    def cost(self, kg): return 0

def price(kg, strategy: Shipping):
    return strategy.cost(kg)

print(price(2, Express()))    # 150
```

</details>

**Exercise 3 · Pick the strategy by name.** Combine with a dictionary (a mini factory).

<details class="solution"><summary>Solution</summary>

```python
strategies = {"student": student, "premium": premium, "flat": flat_100}

def checkout_by_name(total, name):
    return strategies[name](total)

print(checkout_by_name(1000, "premium"))    # 800.0
```

</details>

## Full source

<details class="source">
<summary>1.strategy.py</summary>

```{literalinclude} ../code/13-strategy/1.strategy.py
:language: python
```

</details>

<details class="source">
<summary>3.chunking.py</summary>

```{literalinclude} ../code/13-strategy/3.chunking.py
:language: python
```

</details>

**Downloads:**
{download}`0.no_strategy.py <../code/13-strategy/0.no_strategy.py>` ·
{download}`1.strategy.py <../code/13-strategy/1.strategy.py>` ·
{download}`2.func_strategy.py <../code/13-strategy/2.func_strategy.py>` ·
{download}`3.chunking.py <../code/13-strategy/3.chunking.py>`
