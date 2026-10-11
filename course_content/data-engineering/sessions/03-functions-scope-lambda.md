# Session 3 · Functions, scope, lambda, map and filter

## The big idea

Pipelines are built from small, reusable steps: *parse a line*, *clean a city*, *compute an
amount*, *check a rule*. Each step is a **function**: give it input, get output back. Small
functions are easy to test, easy to reuse, and easy to put together in different orders.

**Everyday example:** a kitchen. "Chop", "fry" and "season" are separate skills. A recipe is just
those steps in order, and the same "chop" works for every dish.

## Defining and calling functions

```python
def order_amount(quantity: int, unit_price: float, discount: float = 0.0) -> float:
    """Total for one order line, after a percentage discount (0–100)."""
    return round(quantity * unit_price * (1 - discount / 100), 2)

print(order_amount(2, 450))                    # default discount
print(order_amount(2, 450, 10))                # positional
print(order_amount(unit_price=450, quantity=2, discount=10))   # keyword arguments, any order
help(order_amount)
```

```text
900.0
810.0
810.0
Help on function order_amount in module __main__:

order_amount(quantity: int, unit_price: float, discount: float = 0.0) -> float
    Total for one order line, after a percentage discount (0–100).

```

- **Type hints** (`quantity: int`, `-> float`) document what the function expects. Python doesn't
  enforce them, but editors and tools like `mypy` use them to catch mistakes.
- The **docstring** (the first string inside) is what `help()` shows. Write one for every function
  someone else will call.

## A function that turns a line into a record

```python
HEADER = "order_id,order_date,customer_id,city,product,category,quantity,unit_price,status".split(",")

def parse_order(line: str) -> dict:
    """One CSV line → a dict with typed values."""
    record = dict(zip(HEADER, line.strip().split(",")))
    record["order_id"] = int(record["order_id"])
    record["quantity"] = int(record["quantity"])
    record["unit_price"] = float(record["unit_price"])
    record["city"] = record["city"] or None
    return record

print(parse_order("1005,2025-01-05,C04,,Pen,Stationery,20,10,delivered"))
```

```text
{'order_id': 1005, 'order_date': '2025-01-05', 'customer_id': 'C04', 'city': None, 'product': 'Pen', 'category': 'Stationery', 'quantity': 20, 'unit_price': 10.0, 'status': 'delivered'}
```

This one function is now the **only** place that knows the file layout. If a column is added, you
change one function, not twenty loops.

## *args and **kwargs

`*args` collects extra positional arguments into a tuple; `**kwargs` collects extra keyword
arguments into a dict. They're handy for passing options through:

```python
def log_event(event, *tags, **fields):
    print(event, tags, fields)

log_event("load_finished", "orders", "daily", rows=12, seconds=5.2)
```

```text
load_finished ('orders', 'daily') {'rows': 12, 'seconds': 5.2}
```

## Scope: where names live

When Python looks up a name, it searches four places in order, known as **LEGB**:

```{raw} html
:file: ../diagrams/s03-scope.html
```

```python
TAX_RATE = 0.18                       # Global: defined at the top of the module

def with_tax(amount):
    tax = amount * TAX_RATE           # `tax` and `amount` are Local; TAX_RATE is found in Global
    return round(amount + tax, 2)     # `round` comes from Built-ins

print(with_tax(1000))
print("tax" in globals())             # the local `tax` vanished when the function returned
```

```text
1180.0
False
```

Assigning to a name inside a function makes it **local**, which surprises people:

```python
rows_loaded = 0

def load(batch):
    try:
        rows_loaded += len(batch)     # assignment → Python treats rows_loaded as local
    except UnboundLocalError as e:
        print("UnboundLocalError:", e)

load([1, 2, 3])
```

```text
UnboundLocalError: local variable 'rows_loaded' referenced before assignment
```

(Python 3.11 and later word it as *cannot access local variable 'rows_loaded' where it is not
associated with a value*. Same error, clearer message.)

You *could* write `global rows_loaded`, but the clean fix is to **return** the new value and let the
caller keep track. Functions that only use their arguments are easy to test and reuse.

```python
def load(batch, rows_loaded):
    return rows_loaded + len(batch)

total = 0
total = load([1, 2, 3], total)
total = load([4, 5], total)
print(total)
```

```text
5
```

### The mutable default trap

Default values are created **once**, when the function is defined:

```python
def add_error(message, errors=[]):        # ✗ one shared list for every call
    errors.append(message)
    return errors

print(add_error("empty city"))
print(add_error("bad price"))             # the first error is still there!

def add_error_safe(message, errors=None): # ✓
    errors = [] if errors is None else errors
    errors.append(message)
    return errors

print(add_error_safe("empty city"), add_error_safe("bad price"))
```

```text
['empty city']
['empty city', 'bad price']
['empty city'] ['bad price']
```

## lambda: small, unnamed functions

`lambda args: expression` creates a tiny function in place. It's most useful as a **key** for
sorting or picking:

```python
orders = [
    {"id": 1001, "product": "Laptop", "amount": 55000.0},
    {"id": 1002, "product": "Mouse", "amount": 900.0},
    {"id": 1011, "product": "Monitor", "amount": 9500.0},
]
by_amount = sorted(orders, key=lambda o: o["amount"], reverse=True)
print([o["product"] for o in by_amount])
print(max(orders, key=lambda o: o["amount"])["product"])
```

```text
['Laptop', 'Monitor', 'Mouse']
Laptop
```

If a lambda grows past one short expression, give it a name with `def`.

## map and filter

- `map(func, items)` applies a function to every item.
- `filter(func, items)` keeps the items for which the function returns true.

Both are **lazy**: they produce results only when you ask (wrap them in `list()` to see them).

```python
cities = ["  chennai", "MADURAI ", "", "salem"]
cleaned = list(map(lambda c: c.strip().title(), cities))
non_empty = list(filter(None, cleaned))           # None = "keep truthy values"
print(cleaned)
print(non_empty)

prices = [450, 55000, 40, 9500]
print(list(filter(lambda p: p >= 1000, prices)))
```

```text
['Chennai', 'Madurai', '', 'Salem']
['Chennai', 'Madurai', 'Salem']
[55000, 9500]
```

The same with comprehensions (Session 6), which most Python developers find easier to read:
`[c.strip().title() for c in cities]` and `[p for p in prices if p >= 1000]`.

## Functions are values: a list of data-quality rules

Because functions are ordinary values, you can keep them in a list and apply them all. This is the
core idea behind data-quality tools like Great Expectations (Module 4):

```python
def has_city(r):     return bool(r["city"])
def positive_qty(r): return r["quantity"] > 0
def known_status(r): return r["status"] in {"delivered", "returned", "cancelled"}

RULES = [has_city, positive_qty, known_status]

record = {"order_id": 1005, "city": None, "quantity": 20, "status": "delivered"}
failed = [rule.__name__ for rule in RULES if not rule(record)]
print(failed)
```

```text
['has_city']
```

Adding a check is now just adding a function to `RULES`.

## Common mistakes

- **Forgetting `return`.** A function without it returns `None`; `amount = order_amount(...)` then
  breaks later, far from the bug.
- **Mutable defaults** (`=[]`, `={}`), shown above.
- **Hidden globals.** Functions that read or change module-level variables are hard to test. Pass
  values in and return them.
- **Calling vs. passing.** `sorted(orders, key=get_amount)` passes the function; `key=get_amount()`
  calls it once and passes the result (usually an error).

## Hands-on exercises

**Exercise 1 · Clean a city.** Write `clean_city(raw)` returning a title-cased city, or `"UNKNOWN"`
for empty or whitespace-only input.

<details class="solution"><summary>Solution</summary>

```python
def clean_city(raw: str) -> str:
    city = (raw or "").strip()
    return city.title() if city else "UNKNOWN"

print([clean_city(c) for c in ["  chennai", "", "   ", None, "MADURAI"]])
```

</details>

**Exercise 2 · Parse the whole file.** Use `parse_order` to load every line of `orders.csv` into a
list of dicts, and print how many there are and the total quantity.

<details class="solution"><summary>Solution</summary>

```python
HEADER = "order_id,order_date,customer_id,city,product,category,quantity,unit_price,status".split(",")

def parse_order(line):
    r = dict(zip(HEADER, line.strip().split(",")))
    r["quantity"], r["unit_price"] = int(r["quantity"]), float(r["unit_price"])
    return r

with open("data/orders.csv") as f:
    next(f)
    orders = [parse_order(line) for line in f]
print(len(orders), sum(o["quantity"] for o in orders))     # 13 99
```

</details>

**Exercise 3 · Sort by date, then amount.** Sort the orders by `order_date`, and by amount
(highest first) within the same date.

<details class="solution"><summary>Solution</summary>

```python
orders = [
    {"id": 1004, "date": "2025-01-05", "amount": 1800.0},
    {"id": 1005, "date": "2025-01-05", "amount": 200.0},
    {"id": 1003, "date": "2025-01-04", "amount": 400.0},
]
result = sorted(orders, key=lambda o: (o["date"], -o["amount"]))
print([o["id"] for o in result])      # [1003, 1004, 1005]
```

A tuple key sorts by the first item, then the second. Negate a number to reverse just that part.

</details>

**Exercise 4 · map + filter.** From `["450", "abc", "55000", "", "9500"]`, keep only values that are
digits and convert them to ints, using `filter` and `map`.

<details class="solution"><summary>Solution</summary>

```python
raw = ["450", "abc", "55000", "", "9500"]
print(list(map(int, filter(str.isdigit, raw))))      # [450, 55000, 9500]
```

`str.isdigit` and `int` are already functions, so no lambda is needed.

</details>

**Exercise 5 · More rules.** Add rules `price_positive` and `valid_date` (the date parses with
`date.fromisoformat`) to `RULES`, and report failures for
`{"city": "Chennai", "quantity": 1, "unit_price": -5, "status": "delivered", "order_date": "2025-13-01"}`.

<details class="solution"><summary>Solution</summary>

```python
from datetime import date

def has_city(r):       return bool(r["city"])
def price_positive(r): return r["unit_price"] > 0
def valid_date(r):
    try:
        date.fromisoformat(r["order_date"])
        return True
    except ValueError:
        return False

RULES = [has_city, price_positive, valid_date]
record = {"city": "Chennai", "quantity": 1, "unit_price": -5, "status": "delivered", "order_date": "2025-13-01"}
print([rule.__name__ for rule in RULES if not rule(record)])    # ['price_positive', 'valid_date']
```

</details>

**Exercise 6 · A tiny pipeline.** Write `run(lines, *steps)` that passes every line through each
step function in order, and use it with `str.strip`, `str.lower` and a function that replaces
`","` with `"|"`.

<details class="solution"><summary>Solution</summary>

```python
def run(lines, *steps):
    out = []
    for line in lines:
        for step in steps:
            line = step(line)
        out.append(line)
    return out

print(run(["  A,B ", "C,D\n"], str.strip, str.lower, lambda s: s.replace(",", "|")))
# ['a|b', 'c|d']
```

Every orchestration tool (Airflow, dbt, Spark) is built on this idea: steps you can put together.

</details>
