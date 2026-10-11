# Session 6 · Comprehensions and generators

## The big idea

Two tools you'll use in almost every pipeline:

- **Comprehensions** build a new list, dict or set from an existing one in a single, readable line:
  *"the amount for every delivered order"*.
- **Generators** produce values **one at a time, on demand**. A generator pipeline can process a
  50 GB file on a laptop, because only one row is in memory at any moment.

**Everyday example:** a buffet vs a waiter. A comprehension lays out every dish at once (a list);
a generator is a waiter bringing the next dish only when you're ready.

Run the examples in order in one session. We start from the parsed orders:

```python
HEADER = "order_id,order_date,customer_id,city,product,category,quantity,unit_price,status".split(",")

def parse_order(line):
    r = dict(zip(HEADER, line.strip().split(",")))
    r["order_id"], r["quantity"], r["unit_price"] = int(r["order_id"]), int(r["quantity"]), float(r["unit_price"])
    return r

with open("data/orders.csv") as f:
    next(f)
    orders = [parse_order(line) for line in f]
print(len(orders))
```

```text
13
```

## List comprehensions

`[expression for item in items if condition]` reads almost like English:

```python
amounts = [o["quantity"] * o["unit_price"] for o in orders if o["status"] == "delivered"]
print(amounts)
print(sum(amounts))

labels = ["big" if o["unit_price"] >= 10000 else "small" for o in orders[:4]]
print(labels)
```

```text
[55000.0, 900.0, 400.0, 200.0, 1500.0, 750.0, 750.0, 52000.0, 200.0, 9500.0, 500.0]
121700.0
['big', 'small', 'small', 'small']
```

The same loop written out takes four lines and an empty list to start from. Notice the two kinds of
`if`:

- `... for o in orders if cond` **filters** (drops items);
- `a if cond else b` at the front **chooses a value** (keeps every item).

## Dict and set comprehensions

```python
price_by_product = {o["product"]: o["unit_price"] for o in orders}          # dict
cities = {o["city"] for o in orders if o["city"]}                           # set: unique values
print(price_by_product["Monitor"], sorted(cities))

totals = {o["order_id"]: o["quantity"] * o["unit_price"] for o in orders}
print(len(totals))       # 12, not 13: the duplicate order 1008 collapsed into one key
```

```text
9500.0 ['Chennai', 'Coimbatore', 'Madurai', 'Salem', 'Trichy']
12
```

## Nested comprehensions: flattening

Each customer has a list of tags. To get one flat list, put the `for` clauses in the same order as
nested loops:

```python
import json

with open("data/customers.json") as f:
    customers = json.load(f)

pairs = [(c["customer_id"], tag) for c in customers for tag in c["tags"]]
print(pairs)
```

```text
[('C01', 'prime'), ('C03', 'student'), ('C05', 'prime'), ('C05', 'student')]
```

If it needs more than two `for`s or a long condition, use a normal loop; readability wins.

## Generator expressions: lazy comprehensions

Swap `[...]` for `(...)` and nothing is computed until you ask:

```python
import sys

squares_list = [n * n for n in range(1_000_000)]
squares_gen = (n * n for n in range(1_000_000))
print(sys.getsizeof(squares_list) > 8_000_000, sys.getsizeof(squares_gen) < 500)
print(sum(n * n for n in range(1_000_000)))      # no extra brackets needed inside a call
```

```text
True True
333332833333500000
```

The list holds a million numbers (about 8 MB); the generator holds only *how to make the next one*.

## Generator functions: yield

A function with `yield` returns a generator. Each `next()` runs it until the next `yield`, then
**pauses**, keeping its local variables:

```python
def read_lines(path):
    print("  (opening file)")
    with open(path) as f:
        next(f)                              # skip the header
        for line in f:
            yield line.rstrip("\n")

lines = read_lines("data/orders.csv")
print(type(lines).__name__)                  # nothing has run yet: no "(opening file)"
print(next(lines))
print(next(lines))
```

```text
generator
  (opening file)
1001,2025-01-03,C01,Chennai,Laptop,Electronics,1,55000,delivered
1002,2025-01-03,C02,Coimbatore,Mouse,Electronics,2,450,delivered
```

## A streaming pipeline

Small generators that each do one job, connected like pipes. Each row flows through **all** the
stages before the next row is read:

```{raw} html
:file: ../diagrams/s06-pipeline.html
```

```python
def read_lines(path):
    with open(path) as f:
        next(f)
        for line in f:
            yield line

def parse(lines):
    for line in lines:
        yield parse_order(line)

def only_delivered(rows):
    for r in rows:
        if r["status"] == "delivered":
            yield r

def deduplicate(rows, key="order_id"):
    seen = set()
    for r in rows:
        if r[key] not in seen:
            seen.add(r[key])
            yield r

def batches(rows, size):
    batch = []
    for r in rows:
        batch.append(r)
        if len(batch) == size:
            yield batch
            batch = []
    if batch:
        yield batch

pipeline = batches(deduplicate(only_delivered(parse(read_lines("data/orders.csv")))), size=4)
for batch in pipeline:
    print([r["order_id"] for r in batch])
```

```text
[1001, 1002, 1003, 1005]
[1007, 1008, 1009, 1010]
[1011, 1012]
```

Swap `read_lines` for an API reader or a database cursor and the rest still works. That's the power
of small, lazy steps. (`batches` would be `itertools.batched(rows, 4)` on Python 3.12+.)

## itertools: generator power tools

```python
from itertools import chain, groupby, islice

print(list(islice(read_lines("data/orders.csv"), 2)))                 # first 2, then stop reading
print(list(chain(["header"], ["row 1", "row 2"])))                     # join iterables end to end

delivered = sorted(only_delivered(parse(read_lines("data/orders.csv"))), key=lambda r: r["category"])
for category, rows in groupby(delivered, key=lambda r: r["category"]):
    print(category, len(list(rows)))
```

```text
['1001,2025-01-03,C01,Chennai,Laptop,Electronics,1,55000,delivered\n', '1002,2025-01-03,C02,Coimbatore,Mouse,Electronics,2,450,delivered\n']
['header', 'row 1', 'row 2']
Electronics 5
Home 2
Stationery 4
```

:::{warning}
`groupby` only groups **neighbouring** items with the same key, so sort by that key first (as
above). Unsorted input gives you the same category several times.
:::

## Common mistakes

- **Using a generator twice.** It's empty after the first pass. Call the generator function again,
  or use a list if you really need the data twice.
- **`len(gen)`** doesn't exist: a generator doesn't know its length until it has been read.
- **Over-clever comprehensions.** Three nested `for`s with conditions are harder to read than a loop.
- **Comprehensions for side effects.** `[print(x) for x in rows]` builds a useless list. Use a `for` loop.
- **Closing files early.** `with open(...)` must be *inside* the generator; if it's outside, the file
  may close before the generator is read.

## Hands-on exercises

**Exercise 1 · Electronics products.** With one comprehension, list the products in the
Electronics category, without duplicates, sorted.

<details class="solution"><summary>Solution</summary>

```python
print(sorted({o["product"] for o in orders if o["category"] == "Electronics"}))
```

```text
['Headphones', 'Keyboard', 'Laptop', 'Monitor', 'Mouse']
```

</details>

**Exercise 2 · Email lookup.** Build `{customer_id: email}` for customers who have an email (Meena
doesn't).

<details class="solution"><summary>Solution</summary>

```python
emails = {c["customer_id"]: c["email"] for c in customers if c["email"]}
print(len(emails), emails["C01"])
```

```text
5 arun@example.com
```

</details>

**Exercise 3 · Stream the events.** Write a generator `good_events(path)` that yields parsed JSON
objects from `events.jsonl` and silently skips broken lines. Count the `purchase` events.

<details class="solution"><summary>Solution</summary>

```python
import json

def good_events(path):
    with open(path) as f:
        for line in f:
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue

print(sum(1 for e in good_events("data/events.jsonl") if e["event"] == "purchase"))
```

```text
3
```

`sum(1 for ...)` counts items from a generator without building a list.

</details>

**Exercise 4 · Running total.** Write a generator `running_total(amounts)` that yields the
cumulative sum after each amount.

<details class="solution"><summary>Solution</summary>

```python
def running_total(amounts):
    total = 0
    for a in amounts:
        total += a
        yield total

print(list(running_total([900, 400, 200])))
```

```text
[900, 1300, 1500]
```

(`itertools.accumulate` does the same thing.)

</details>

**Exercise 5 · Add a stage.** Add `with_amount(rows)` to the streaming pipeline, so each row gets an
`amount` field, and print the total amount of all delivered, de-duplicated orders.

<details class="solution"><summary>Solution</summary>

```python
def with_amount(rows):
    for r in rows:
        r["amount"] = r["quantity"] * r["unit_price"]
        yield r

rows = with_amount(deduplicate(only_delivered(parse(read_lines("data/orders.csv")))))
print(sum(r["amount"] for r in rows))
```

```text
120950.0
```

Compare with 121700.0 earlier: de-duplicating removed the second ₹750 water-bottle row.

</details>

**Exercise 6 · Top 3 by amount, lazily.** Use `heapq.nlargest` on a generator to get the 3 biggest
order amounts without sorting everything.

<details class="solution"><summary>Solution</summary>

```python
import heapq

amounts = (o["quantity"] * o["unit_price"] for o in parse(read_lines("data/orders.csv")))
print(heapq.nlargest(3, amounts))
```

```text
[55000.0, 52000.0, 9500.0]
```

`nlargest` keeps only the top 3 while reading, which is handy when the input is huge.

</details>
