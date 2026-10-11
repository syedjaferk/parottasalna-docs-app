# Session 2 · Control flow and loops

## The big idea

A pipeline is a loop with decisions inside: **for every record**, decide whether to keep it, fix
it, skip it or stop. `if` makes the decisions; `for` and `while` repeat them. With `break` and
`continue` you control exactly which records go through.

**Everyday example:** a sorting desk at a courier office. Each parcel is checked: damaged ones go
back, local ones to one bin, outstation ones to another. If the conveyor jams, everything stops.

```{raw} html
:file: ../diagrams/s02-loop.html
```

## Decisions: if / elif / else

```python
status = "returned"
amount = 1800.0

if status == "delivered":
    revenue = amount
elif status in ("returned", "cancelled"):
    revenue = 0.0
else:
    raise ValueError(f"unknown status: {status!r}")

print(revenue)
```

```text
0.0
```

Python checks the conditions **top to bottom** and runs only the first one that's true. The final
`else` that raises an error is a good habit: an unexpected value should stop the pipeline, not slip
through as if it were fine.

### Truthiness, and/or, and one-line conditions

Empty values (`""`, `0`, `None`, `[]`, `{}`) count as `False`; almost everything else counts as `True`:

```python
city = ""
print(city or "UNKNOWN")                         # `or` picks the first truthy value
quantity, price = 3, 250.0
print("bulk" if quantity >= 10 else "single")    # conditional expression
print(quantity > 0 and price > 0)                # both must be true
```

```text
UNKNOWN
single
True
```

### match: many cases on one value (Python 3.10+)

```python
def category_code(category):
    match category:
        case "Electronics":
            return "ELEC"
        case "Stationery" | "Books":
            return "STAT"
        case _:
            return "OTHER"

print(category_code("Electronics"), category_code("Books"), category_code("Home"))
```

```text
ELEC STAT OTHER
```

## for loops over records

A `for` loop works on anything you can step through: lists, strings, files. Here we read the orders
file line by line (Session 7 covers files properly):

```python
with open("data/orders.csv") as f:
    header = next(f)                 # read past the header line
    for line in f:
        fields = line.strip().split(",")
        print(fields[0], fields[4], fields[8])
        if fields[0] == "1003":
            break                    # just the first three, for now
```

```text
1001 Laptop delivered
1002 Mouse delivered
1003 Notebook delivered
```

### enumerate and zip

`enumerate` adds a counter, which is useful for reporting line numbers. `zip` pairs two sequences,
for example column names with values:

```python
header = "order_id,city,status".split(",")
values = "1005,,delivered".split(",")

for position, (column, value) in enumerate(zip(header, values), start=1):
    flag = "  <- empty!" if value == "" else ""
    print(position, column, repr(value) + flag)
```

```text
1 order_id '1005'
2 city ''  <- empty!
3 status 'delivered'
```

`dict(zip(header, values))` turns the pair into a record: `{'order_id': '1005', 'city': '', ...}`.
You'll use this all the time.

## continue, break and loop-else

- `continue` skips **this** record and moves to the next one.
- `break` stops the loop entirely.
- A loop's `else` runs only if the loop finished **without** `break`.

```python
total = 0.0
with open("data/orders.csv") as f:
    next(f)
    for line_no, line in enumerate(f, start=2):           # line 1 is the header
        f_ = line.strip().split(",")
        if f_[8] != "delivered":
            continue                                       # skip cancelled / returned
        if int(f_[6]) <= 0:
            print(f"line {line_no}: bad quantity, stopping")
            break
        total += int(f_[6]) * float(f_[7])
    else:
        print("all lines processed")

print(f"delivered revenue: ₹{total:,.2f}")
```

```text
all lines processed
delivered revenue: ₹121,700.00
```

Two things to notice:

- Python's `,` format groups digits in **thousands** (`121,700`), not the Indian lakh style
  (`1,21,700`). For lakh/crore formatting you'd write a small helper or use the `babel` library.
- That total counts order **1008 twice**, because the file has a duplicate row. Loops do exactly
  what you tell them; removing duplicates is your job (Sessions 5 and 12).

## while: repeat until a condition changes

Use `while` when you don't know in advance how many rounds you need, for example retrying a flaky
source:

```python
import random

random.seed(7)                     # make the "random" failures repeatable
attempt = 0
while True:
    attempt += 1
    ok = random.random() > 0.6     # pretend: 40 % chance the source answers
    print(f"attempt {attempt}: {'ok' if ok else 'failed'}")
    if ok or attempt == 5:
        break
```

```text
attempt 1: failed
attempt 2: failed
attempt 3: ok
```

Always make sure a `while` loop **can end**: here it stops after success or 5 attempts.

## Counting while looping

A dictionary works as a set of counters, which is how you build quick data-quality summaries:

```python
counts = {}
with open("data/orders.csv") as f:
    next(f)
    for line in f:
        status = line.strip().split(",")[8]
        counts[status] = counts.get(status, 0) + 1
print(counts)
```

```text
{'delivered': 11, 'returned': 1, 'cancelled': 1}
```

## Common mistakes

- **`=` instead of `==`** in a condition is a syntax error. Comparison is `==`.
- **Checking `if x == True`.** Just write `if x`, and `if x is None` for `None`.
- **Infinite `while` loops.** Every `while` needs a way out (a counter, `break`, or a changing condition).
- **Modifying a list while looping over it.** Items get skipped. Build a new list instead (Session 6).
- **Forgetting the header line** when reading CSV by hand: `int("quantity")` fails.

## Hands-on exercises

**Exercise 1 · Order size.** Label an order `"small"` (under ₹1,000), `"medium"` (₹1,000–₹9,999)
or `"large"` (₹10,000 and up). Test it with 450, 1500 and 55000.

<details class="solution"><summary>Solution</summary>

```python
def size(amount):
    if amount < 1000:
        return "small"
    elif amount < 10000:
        return "medium"
    return "large"

for a in (450, 1500, 55000):
    print(a, size(a))
```

</details>

**Exercise 2 · Count by city.** Count orders per city in `orders.csv`, treating an empty city as
`"UNKNOWN"`.

<details class="solution"><summary>Solution</summary>

```python
counts = {}
with open("data/orders.csv") as f:
    next(f)
    for line in f:
        city = line.strip().split(",")[3] or "UNKNOWN"
        counts[city] = counts.get(city, 0) + 1
print(counts)
```

Chennai 5, Coimbatore 2, Madurai 2, UNKNOWN 1, Trichy 2, Salem 1.

</details>

**Exercise 3 · First expensive order.** Print the first order whose unit price is over ₹10,000, then
stop reading.

<details class="solution"><summary>Solution</summary>

```python
with open("data/orders.csv") as f:
    next(f)
    for line in f:
        fields = line.strip().split(",")
        if float(fields[7]) > 10000:
            print("first expensive order:", fields[0], fields[4])
            break
    else:
        print("none found")
```

`1001 Laptop`. The `else` would only print if no order matched.

</details>

**Exercise 4 · Rows with problems.** Print the line number of every row with an empty field.

<details class="solution"><summary>Solution</summary>

```python
with open("data/orders.csv") as f:
    next(f)
    for line_no, line in enumerate(f, start=2):
        if "" in line.strip().split(","):
            print("empty field on line", line_no)
```

Line 6 (order 1005, missing city).

</details>

**Exercise 5 · Find duplicates.** Print order IDs that appear more than once.

<details class="solution"><summary>Solution</summary>

```python
seen = set()
with open("data/orders.csv") as f:
    next(f)
    for line in f:
        order_id = line.split(",")[0]
        if order_id in seen:
            print("duplicate:", order_id)
        seen.add(order_id)
```

`duplicate: 1008`. A `set` remembers what you've seen; Session 5 explains why it's fast.

</details>

**Exercise 6 · Retry with backoff.** Rewrite the `while` retry loop so it waits 1, 2, 4… seconds
between attempts (use `time.sleep`, and keep the 5-attempt limit).

<details class="solution"><summary>Solution</summary>

```py
import random
import time

attempt, delay = 0, 1
while True:
    attempt += 1
    if random.random() > 0.6:
        print("success on attempt", attempt)
        break
    if attempt == 5:
        print("giving up")
        break
    print(f"failed, waiting {delay}s")
    time.sleep(delay)
    delay *= 2           # exponential backoff
```

Doubling the wait gives a struggling server time to recover, the same idea Airflow's retries use
(Module 5).

</details>
