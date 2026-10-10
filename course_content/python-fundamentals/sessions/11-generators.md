# Session 11 · Generators: the lazy workers of Python

📖 Based on the blog post [Python Generators: The Lazy Workers of Python](https://learn.parottasalna.com/blog/python-generators-the-lazy-workers-of-python/).

## The big idea

A normal function builds **all** its results and hands them over at once. A **generator** hands
them over **one at a time**, only when you ask for the next one. That makes generators *lazy*
(no work until needed) and *memory-efficient* (only one item in memory at a time).

**Everyday example:** a buffet vs a waiter. At a buffet all the food is laid out at once: that's a
**list**. A waiter brings one dish when you're ready for it: that's a **generator**.

```{raw} html
:file: ../diagrams/s11-lazy.html
```

## From a list to a generator

The normal way: build a list, then return it.

```python
def countdown_list(n):
    result = []
    while n > 0:
        result.append(n)
        n -= 1
    return result

print(countdown_list(5))
```

```text
[5, 4, 3, 2, 1]
```

The generator way: `yield` each value instead of collecting them.

```python
def countdown_gen(n):
    while n > 0:
        yield n
        n -= 1

for number in countdown_gen(5):
    print(number)
```

```text
5
4
3
2
1
```

Any function containing `yield` becomes a generator function. Calling it doesn't run the body; it
returns a **generator object** that runs the body bit by bit.

## What does yield do?

Think of `yield` as a `return` that **pauses** instead of finishing:

1. `next()` runs the body until the first `yield`, and hands out that value.
2. The function **pauses**, keeping all its local variables.
3. The next `next()` **resumes** right after the `yield`.
4. When the body ends, the generator raises `StopIteration`. A `for` loop catches it and stops.

```python
def countdown_gen(n):
    while n > 0:
        yield n
        n -= 1

gen = countdown_gen(3)
print(next(gen))
print(next(gen))
print(next(gen))
try:
    next(gen)
except StopIteration:
    print("StopIteration: no more values")
```

```text
3
2
1
StopIteration: no more values
```

## How much memory does it save?

```python
import sys

numbers_list = [n for n in range(1_000_000)]    # list comprehension: all at once
numbers_gen = (n for n in range(1_000_000))     # generator expression: round brackets

print(sys.getsizeof(numbers_list) > 8_000_000)
print(sys.getsizeof(numbers_gen) < 1_000)
print(sum(numbers_gen))
```

```text
True
True
499999500000
```

The list takes about **8 MB**; the generator object takes a couple of hundred bytes, whether it will
produce a thousand values or a billion. Notice the **generator expression**: like a list
comprehension, but with `( )`.

## Infinite sequences

A list can't be infinite. A generator can, because it only makes what you ask for:

```python
def infinite_counter(start=0):
    while True:
        yield start
        start += 1

counter = infinite_counter()
print(next(counter), next(counter), next(counter))
```

```text
0 1 2
```

## Real-world uses

**Reading huge files line by line.** Only one line is in memory at a time, so a 2 GB log file is no
problem:

```py
def read_large_file(file_path):
    with open(file_path) as f:
        for line in f:
            yield line

for log in read_large_file("biglog.txt"):
    print(log)
```

**Paginated APIs.** Fetch the next page only when the previous one is used up:

```py
import requests

def paginated_fetch(base_url):
    page = 1
    while True:
        data = requests.get(f"{base_url}?page={page}", timeout=10).json()
        if not data:
            break
        yield from data          # yield every item of this page
        page += 1
```

**Video frames** (with OpenCV), sensor readings, live events: anything that arrives as a stream.

## A generator pipeline

Generators can feed each other, like stations on an assembly line. Each row flows through the whole
pipeline before the next one is read. This example first writes a small CSV, so you can run it:

```python
with open("sales.csv", "w") as f:
    f.write("region,sales\nSouth Asia,100.5\nEurope,80\nSouth Asia,49.5\n")

def read_large_csv(file_path):
    with open(file_path) as f:
        header = next(f).strip().split(",")          # first line: column names
        for line in f:
            yield dict(zip(header, line.strip().split(",")))

def filter_region(rows, region_name):
    for row in rows:
        if row.get("region") == region_name:
            yield row

def sales_values(rows):
    for row in rows:
        yield float(row.get("sales", 0.0))

rows = read_large_csv("sales.csv")
south_asia = filter_region(rows, "South Asia")
print("Total South Asia Sales:", sum(sales_values(south_asia)))
```

```text
Total South Asia Sales: 150.0
```

The same code works on a 10 GB file, where `pandas.read_csv()` would try to load everything into
memory at once.

| Problem | Why generators help |
|---|---|
| Huge CSV / JSON / log files | no memory crash: one row at a time |
| ETL pipelines | small, composable, readable steps |
| Filtering and transforming | only processes what's actually needed |
| Real-time data (sensors, events) | handles items as they arrive |

## Common mistakes

- **Using a generator twice.** It's single-use: after one loop it's empty. Call the function again
  for a fresh one.
- **`len(gen)` or `gen[0]`**: generators have no length or index. Use `list(gen)` if you really
  need them (and lose the memory benefit).
- **Expecting the body to run when you call the function.** Nothing happens until the first
  `next()` or loop.
- **Forgetting to close files.** Use `with open(...)` inside the generator, as above.

## Hands-on exercises

**Exercise 1 · Even numbers.** Write `evens(limit)` that yields the even numbers up to `limit`.

<details class="solution"><summary>Solution</summary>

```python
def evens(limit):
    n = 0
    while n <= limit:
        yield n
        n += 2

print(list(evens(10)))     # [0, 2, 4, 6, 8, 10]
```

</details>

**Exercise 2 · Fibonacci.** Write an infinite `fibonacci()` generator and print the first 10 numbers.

<details class="solution"><summary>Solution</summary>

```python
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

fib = fibonacci()
print([next(fib) for _ in range(10)])    # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

</details>

**Exercise 3 · Single use.** Make `squares = (n * n for n in range(4))`, call `sum(squares)` twice.
Explain the results.

<details class="solution"><summary>Answer</summary>

```python
squares = (n * n for n in range(4))
print(sum(squares))    # 14
print(sum(squares))    # 0: the generator is already used up
```

</details>

**Exercise 4 · Errors only.** Write `errors(lines)` that yields only lines containing "ERROR", and
test it with a short list of log lines.

<details class="solution"><summary>Solution</summary>

```python
def errors(lines):
    for line in lines:
        if "ERROR" in line:
            yield line.strip()

logs = ["INFO start", "ERROR disk full", "INFO retry", "ERROR timeout"]
for e in errors(logs):
    print(e)
```

Pass it `open("app.log")` instead of a list and it works on a file of any size.

</details>

**Exercise 5 · Batches.** Write `batches(items, size)` that yields lists of `size` items (the last
batch may be smaller).

<details class="solution"><summary>Solution</summary>

```python
def batches(items, size):
    batch = []
    for item in items:
        batch.append(item)
        if len(batch) == size:
            yield batch
            batch = []
    if batch:
        yield batch

print(list(batches(range(7), 3)))    # [[0, 1, 2], [3, 4, 5], [6]]
```

Useful for sending records to a database or an API a few hundred at a time.

</details>

**Exercise 6 · Pipeline.** Using the sales pipeline above, add a step `above(values, limit)` that
only passes sales over 60, and print the total for South Asia.

<details class="solution"><summary>Solution</summary>

```python
def above(values, limit):
    for v in values:
        if v > limit:
            yield v

with open("sales.csv", "w") as f:
    f.write("region,sales\nSouth Asia,100.5\nEurope,80\nSouth Asia,49.5\n")

def rows_from(path):
    with open(path) as f:
        header = next(f).strip().split(",")
        for line in f:
            yield dict(zip(header, line.strip().split(",")))

south = (r for r in rows_from("sales.csv") if r["region"] == "South Asia")
print(sum(above((float(r["sales"]) for r in south), 60)))    # 100.5
```

</details>
