# Session 4 · Exception handling and logging

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube.com/embed/GDZsOr7H_fk"
  title="Session 3: Dictionary, Set, Tuple" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

## The big idea

Data is never perfect: a field is empty, a line is broken, an API times out. A good pipeline
**decides in advance** what to do with each kind of problem: skip the bad record, retry the call,
or stop loudly. And it **writes down** what happened, so at 3 AM you can tell *what* failed and
*why* without guessing.

- **Exceptions** are how Python reports problems, and how your code handles them.
- **Logging** is how your pipeline keeps a diary.

**Everyday example:** a delivery van. A wrong address means *set this parcel aside and carry on*. A
flat tyre means *stop and call for help*. The driver notes both in the logbook.

```{raw} html
:file: ../diagrams/s04-errors.html
```

## try / except / else / finally

```python
def to_int(text):
    try:
        value = int(text)
    except ValueError:
        print(f"  {text!r} is not a number")
        return None
    else:
        print(f"  {text!r} converted")         # runs only if no exception happened
        return value
    finally:
        print("  (checked)")                   # runs no matter what

print(to_int("20"))
print(to_int("twenty"))
```

```text
  '20' converted
  (checked)
20
  'twenty' is not a number
  (checked)
None
```

- `except` catches a **specific** exception type. Never write a bare `except:`, which also swallows
  typos (`NameError`) and Ctrl+C.
- `else` holds the code that should run only when nothing failed.
- `finally` is for cleanup that must always happen (closing a connection, removing a temp file).

## Exceptions you'll meet constantly

```python
samples = [
    lambda: int("1,200"),                      # ValueError: bad text for int
    lambda: {"city": "Chennai"}["pincode"],    # KeyError: missing dict key
    lambda: ["a", "b"][5],                     # IndexError: past the end of a list
    lambda: "Total: " + 900,                   # TypeError: str + int
    lambda: 10 / 0,                            # ZeroDivisionError
    lambda: open("data/missing.csv"),          # FileNotFoundError
]
for make_error in samples:
    try:
        make_error()
    except Exception as e:                     # broad catch is OK here: we only print and move on
        print(f"{type(e).__name__}: {e}")
```

```text
ValueError: invalid literal for int() with base 10: '1,200'
KeyError: 'pincode'
IndexError: list index out of range
TypeError: can only concatenate str (not "int") to str
ZeroDivisionError: division by zero
FileNotFoundError: [Errno 2] No such file or directory: 'data/missing.csv'
```

## Bad records: skip, keep, and count

Here's the classic data-engineering pattern on `events.jsonl`, which has one broken line on purpose.
Good records go on; bad ones are kept aside with the reason (a **dead-letter** list) instead of
crashing the whole run:

```python
import json

good, bad = [], []
with open("data/events.jsonl") as f:
    for line_no, line in enumerate(f, start=1):
        try:
            good.append(json.loads(line))
        except json.JSONDecodeError as e:
            bad.append({"line": line_no, "error": str(e), "raw": line.strip()})

print(len(good), "good,", len(bad), "bad")
print(bad[0])
```

```text
7 good, 1 bad
{'line': 7, 'error': 'Expecting value: line 1 column 1 (char 0)', 'raw': 'this line is broken {'}
```

In a real pipeline you'd write `bad` to a file or table and **alert** if it grows beyond a
threshold: 1 bad line in a million is noise, 30 % is an upstream bug.

## raise: report problems yourself

Use `raise` when the data breaks a rule your code depends on. Your own exception class makes it
easy for callers to catch exactly your errors:

```python
class DataValidationError(ValueError):
    """A record breaks a business rule."""

def validate(order):
    if order["quantity"] <= 0:
        raise DataValidationError(f"order {order['order_id']}: quantity must be positive")
    if order["status"] not in {"delivered", "returned", "cancelled"}:
        raise DataValidationError(f"order {order['order_id']}: unknown status {order['status']!r}")

for order in [{"order_id": 1, "quantity": 2, "status": "delivered"},
              {"order_id": 2, "quantity": 0, "status": "delivered"},
              {"order_id": 3, "quantity": 1, "status": "shipped"}]:
    try:
        validate(order)
        print(order["order_id"], "ok")
    except DataValidationError as e:
        print("rejected:", e)
```

```text
1 ok
rejected: order 2: quantity must be positive
rejected: order 3: unknown status 'shipped'
```

### raise … from …: keep the original cause

When you turn a low-level error into a meaningful one, chain them so the traceback shows both:

```python
def load_config(path):
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError as e:
        raise RuntimeError(f"config file {path!r} is missing; did you copy config.example?") from e

try:
    load_config("data/settings.toml")
except RuntimeError as e:
    print(e)
    print("caused by:", repr(e.__cause__))
```

```text
config file 'data/settings.toml' is missing; did you copy config.example?
caused by: FileNotFoundError(2, 'No such file or directory')
```

## Logging instead of print

`print` is for output; **logging** is for the story of what happened. Logging gives you **levels**
(filter out the noise), a **format** with timestamps and names, and **destinations** (console, file,
monitoring), all configured in one place.

| Level | Use it for |
|---|---|
| `DEBUG` | details while developing (row contents, intermediate values) |
| `INFO` | normal progress: *started*, *extracted 13 rows*, *finished* |
| `WARNING` | something odd, but the run continues: *row 5 has an empty city* |
| `ERROR` | a step failed: *couldn't reach the payments API* |
| `CRITICAL` | the whole pipeline can't continue |

```py
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)-7s %(name)s: %(message)s",
                    stream=sys.stdout, force=True)
log = logging.getLogger("orders_pipeline")

log.debug("not shown: level is INFO")
log.info("extracted %d rows from %s", 13, "orders.csv")
log.warning("row %d has an empty city", 5)
try:
    1 / 0
except ZeroDivisionError:
    log.exception("could not compute average order value")   # ERROR + the traceback
```

```text
INFO    orders_pipeline: extracted 13 rows from orders.csv
WARNING orders_pipeline: row 5 has an empty city
ERROR   orders_pipeline: could not compute average order value
Traceback (most recent call last):
  File "pipeline.py", line 12, in <module>
    1 / 0
ZeroDivisionError: division by zero
```

(Saved as `pipeline.py` and run with `python pipeline.py`.)

Notes:

- Pass values as arguments (`log.info("%d rows", n)`) rather than f-strings: the message is only built
  if that level is enabled, and log tools can group identical messages.
- `log.exception(...)` inside an `except` block logs at ERROR level **and** the full traceback.
- `getLogger("orders_pipeline")`, or `getLogger(__name__)` in a module, names each part of the
  pipeline, so you can see where a message came from.
- `force=True` resets any earlier setup (useful in notebooks). Configure logging **once**, at the
  start of your script, never inside library functions.

### A production setup: console + file, with timestamps

```py
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("pipeline.log")],
)
log = logging.getLogger("orders_pipeline")
log.info("pipeline started")
```

```text
2025-01-03 10:00:01,204 INFO    orders_pipeline: pipeline started
```

That's exactly the shape of `data/server.log` from the dataset. In Module 5, Airflow collects these
logs for every task run, and they're the first place you look when a task fails.

## Retrying, with logging

Putting it together: retry a flaky step a few times, log each failure, and give up loudly:

```python
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s", stream=sys.stdout, force=True)
log = logging.getLogger("extract")

calls = {"n": 0}
def fetch_payments():
    calls["n"] += 1
    if calls["n"] < 3:
        raise TimeoutError("payments API did not answer in 5s")
    return [{"order_id": 1001, "paid": True}]

def with_retries(func, attempts=4):
    for attempt in range(1, attempts + 1):
        try:
            return func()
        except TimeoutError as e:
            log.warning("attempt %d/%d failed: %s", attempt, attempts, e)
    raise RuntimeError(f"{func.__name__} failed after {attempts} attempts")

print(with_retries(fetch_payments))
```

```text
WARNING attempt 1/4 failed: payments API did not answer in 5s
WARNING attempt 2/4 failed: payments API did not answer in 5s
[{'order_id': 1001, 'paid': True}]
```

Only retry errors that might go away (timeouts, temporary network issues). Retrying a
`ValueError` from bad data just fails 4 times instead of once.

## Common mistakes

- **`except Exception: pass`.** The error disappears and the data silently goes wrong. At minimum, log it.
- **Catching too much in one `try`.** Wrap only the line that can fail, so you know what went wrong.
- **`print` for errors.** It has no level, no timestamp, and goes to stdout, mixed in with your data.
- **f-strings in log calls everywhere.** Fine for readability, but `log.info("%s", x)` is the
  convention and is cheaper when the level is off.
- **Retrying forever.** Always cap attempts, and wait longer between them (Session 2, Exercise 6).

## Hands-on exercises

**Exercise 1 · Safe float.** Write `to_float(text, default=None)` that returns the number, or the
default when the text isn't a valid number. Test `"9500"`, `"9,500"`, `""` and `None`.

<details class="solution"><summary>Solution</summary>

```python
def to_float(text, default=None):
    try:
        return float(text)
    except (TypeError, ValueError):     # None → TypeError, bad text → ValueError
        return default

print([to_float(t) for t in ["9500", "9,500", "", None]])    # [9500.0, None, None, None]
```

</details>

**Exercise 2 · Count bad orders.** Read `orders.csv`; for each line, try `int(quantity)` and
`float(unit_price)`. Count good and bad rows, keeping the bad line numbers.

<details class="solution"><summary>Solution</summary>

```python
good, bad = 0, []
with open("data/orders.csv") as f:
    next(f)
    for line_no, line in enumerate(f, start=2):
        fields = line.strip().split(",")
        try:
            int(fields[6]); float(fields[7])
            good += 1
        except (ValueError, IndexError):
            bad.append(line_no)
print(good, bad)        # 13 []: all numbers are clean in this file
```

</details>

**Exercise 3 · Your own error.** Create `MissingFieldError` and a function `require(record, *fields)`
that raises it with every missing or empty field named.

<details class="solution"><summary>Solution</summary>

```python
class MissingFieldError(ValueError):
    pass

def require(record, *fields):
    missing = [f for f in fields if not record.get(f)]
    if missing:
        raise MissingFieldError(f"missing: {', '.join(missing)}")

try:
    require({"order_id": 1005, "city": ""}, "order_id", "city", "status")
except MissingFieldError as e:
    print(e)          # missing: city, status
```

</details>

**Exercise 4 · Log, don't print.** Rewrite this with logging at the right levels: print "start",
print a warning for each row without a city, print "done, N rows".

<details class="solution"><summary>Solution</summary>

```python
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s", stream=sys.stdout, force=True)
log = logging.getLogger("cities")

log.info("start")
rows = 0
with open("data/orders.csv") as f:
    next(f)
    for line_no, line in enumerate(f, start=2):
        rows += 1
        if not line.split(",")[3]:
            log.warning("line %d has no city", line_no)
log.info("done, %d rows", rows)
```

</details>

**Exercise 5 · Log to a file.** Configure logging to write INFO and above to `pipeline.log` **and**
the console, then open the file and check the lines are there.

<details class="solution"><summary>Solution</summary>

```python
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                    handlers=[logging.StreamHandler(), logging.FileHandler("pipeline.log")], force=True)
logging.getLogger("demo").info("hello from the pipeline")
logging.shutdown()                       # flush and close the file
print(open("pipeline.log").read().strip().split(" ", 2)[-1])   # INFO hello from the pipeline
```

</details>

**Exercise 6 · Retry only what's worth retrying.** Change `with_retries` so it retries
`TimeoutError` and `ConnectionError`, but re-raises any other exception immediately.

<details class="solution"><summary>Solution</summary>

```python
def with_retries(func, attempts=4, retry_on=(TimeoutError, ConnectionError)):
    for attempt in range(1, attempts + 1):
        try:
            return func()
        except retry_on as e:
            print(f"attempt {attempt} failed: {e}")
    raise RuntimeError(f"{func.__name__} failed after {attempts} attempts")

def bad_data():
    raise ValueError("price is not a number")

try:
    with_retries(bad_data)
except ValueError as e:
    print("not retried:", e)          # fails straight away, once
```

</details>
