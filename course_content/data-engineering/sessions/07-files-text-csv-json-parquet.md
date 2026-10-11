# Session 7 · Files: text, CSV, JSON and Parquet

## The big idea

Files are where most pipelines start and end. Each format has a job:

| Format | Looks like | Good for | Watch out for |
|---|---|---|---|
| **Text / logs** | free-form lines | logs, simple exports | you parse everything yourself |
| **CSV** | rows of comma-separated values | exchanging tables with anyone (Excel, databases) | no types, commas inside values, encodings |
| **JSON** | nested `{}` and `[]` | API responses, config, nested records | whole file in memory; no schema |
| **JSON Lines** | one JSON object per line | event streams, logs, big exports | one bad line shouldn't stop the file |
| **Parquet** | binary, column by column | analytics and data lakes (Spark, Databricks) | not human-readable; needs a library |

**Everyday example:** CSV is a printed register: anyone can read it, but "1,200" could be a number
or two columns. Parquet is a sorted filing cabinet with labelled drawers: you can't read it by eye,
but finding "every price" is instant.

Run the examples in order, from your project folder (so `data/...` paths work).

## Paths with pathlib

```python
from pathlib import Path

data = Path("data")
for path in sorted(data.glob("*")):
    print(f"{path.name:<15} {path.suffix:<7} {path.stat().st_size:>5} bytes")

out = Path("output")
out.mkdir(exist_ok=True)                  # no error if it already exists
print((out / "clean_orders.csv").as_posix())
```

```text
customers.json  .json    1024 bytes
events.jsonl    .jsonl    683 bytes
orders.csv      .csv      895 bytes
server.log      .log      370 bytes
output/clean_orders.csv
```

`Path("data") / "orders.csv"` builds paths that work on Windows, macOS and Linux. Prefer it over
gluing strings with `"/"`.

## Text files

Always say the **encoding**; `utf-8` handles English, Tamil and ₹ alike:

```python
counts = {}
with open("data/server.log", encoding="utf-8") as f:     # `with` closes the file for you
    for line in f:
        day, time, level, message = line.rstrip("\n").split(maxsplit=3)
        counts[level] = counts.get(level, 0) + 1
        if level == "ERROR":
            print(time, message)
print(counts)
```

```text
10:00:03 could not reach payments API (timeout)
{'INFO': 5, 'WARN': 1, 'ERROR': 1}
```

`split(maxsplit=3)` splits on whitespace at most 3 times, so the message keeps its spaces.

Writing: mode `"w"` replaces the file, `"a"` appends to it:

```python
with open("output/errors.txt", "w", encoding="utf-8") as f:
    f.write("10:00:03 could not reach payments API\n")
with open("output/errors.txt", "a", encoding="utf-8") as f:
    f.write("10:07:41 warehouse write timed out\n")
print(Path("output/errors.txt").read_text(encoding="utf-8"), end="")
```

```text
10:00:03 could not reach payments API
10:07:41 warehouse write timed out
```

## CSV with the csv module

Don't split CSV lines on commas yourself: a value like `"Lamp, desk"` contains a comma. The `csv`
module handles quoting for you.

```python
import csv

with open("data/orders.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)                    # each row is a dict keyed by the header
    rows = list(reader)

print(reader.fieldnames)
print(rows[4])
```

```text
['order_id', 'order_date', 'customer_id', 'city', 'product', 'category', 'quantity', 'unit_price', 'status']
{'order_id': '1005', 'order_date': '2025-01-05', 'customer_id': 'C04', 'city': '', 'product': 'Pen', 'category': 'Stationery', 'quantity': '20', 'unit_price': '10', 'status': 'delivered'}
```

Every value is still a **string**; CSV has no types. Now write a cleaned file, including a value
that contains a comma:

```python
clean = []
for r in rows:
    if r["status"] != "delivered":
        continue
    clean.append({"order_id": r["order_id"], "city": r["city"] or "UNKNOWN",
                  "product": r["product"], "amount": int(r["quantity"]) * float(r["unit_price"])})
clean[0]["product"] = "Laptop, 15 inch"           # a comma inside a value

with open("output/clean_orders.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["order_id", "city", "product", "amount"])
    writer.writeheader()
    writer.writerows(clean)

print(Path("output/clean_orders.csv").read_text().splitlines()[:3])
```

```text
['order_id,city,product,amount', '1001,Chennai,"Laptop, 15 inch",55000.0', '1002,Coimbatore,Mouse,900.0']
```

The writer put quotes around `"Laptop, 15 inch"` automatically, and the reader will remove them.
Always open CSV files with `newline=""`, or you'll get blank lines between rows on Windows.

## JSON

```python
import json

with open("data/customers.json", encoding="utf-8") as f:
    customers = json.load(f)                          # file → Python lists/dicts

c = customers[0]
print(type(customers).__name__, len(customers))
print(c["name"], c["address"]["city"], c["tags"])    # nested access
print(customers[3]["email"])                          # JSON null → Python None
```

```text
list 6
Arun Chennai ['prime']
None
```

Writing JSON: `indent` makes it readable; `ensure_ascii=False` keeps Tamil and ₹ as they are instead
of `\u0b9a…` escapes:

```python
summary = {"city": "சென்னை", "orders": 5, "revenue": "₹121,700", "ok": True, "note": None}
print(json.dumps(summary, ensure_ascii=False))
print(json.dumps(summary))
with open("output/summary.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
```

```text
{"city": "சென்னை", "orders": 5, "revenue": "₹121,700", "ok": true, "note": null}
{"city": "\u0b9a\u0bc6\u0ba9\u0bcd\u0ba9\u0bc8", "orders": 5, "revenue": "\u20b9121,700", "ok": true, "note": null}
```

`json.dump`/`json.load` work with files; `json.dumps`/`json.loads` (with **s**) work with
**s**trings.

## JSON Lines: one record per line

Big exports and event streams use JSON Lines, so you can read them one line at a time, and one bad
line doesn't ruin the file:

```python
purchases = []
with open("data/events.jsonl", encoding="utf-8") as f:
    for line_no, line in enumerate(f, start=1):
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            print("skipping broken line", line_no)
            continue
        if event["event"] == "purchase":
            purchases.append({"user": event["user"], "amount": event["amount"]})

with open("output/purchases.jsonl", "w", encoding="utf-8") as f:
    for p in purchases:
        f.write(json.dumps(p) + "\n")
print(Path("output/purchases.jsonl").read_text(), end="")
```

```text
skipping broken line 7
{"user": "C01", "amount": 55000}
{"user": "C02", "amount": 900}
{"user": "C03", "amount": 400}
```

## Parquet: the data-lake format

Parquet stores data **column by column**, with **types** and **compression**. That's why Spark,
Databricks and BigQuery love it: a query that needs only `unit_price` reads only that column.

```{raw} html
:file: ../diagrams/s07-columnar.html
```

The easiest way to write Parquet is with pandas (which uses `pyarrow`; we cover pandas properly in
Sessions 11–12):

```python
import pandas as pd

df = pd.read_csv("data/orders.csv")
df.to_parquet("output/orders.parquet", index=False)

back = pd.read_parquet("output/orders.parquet", columns=["order_id", "unit_price"])   # read 2 columns only
print(back.head(3))
print(back.dtypes.to_dict())
```

```text
   order_id  unit_price
0      1001       55000
1      1002         450
2      1003          40
{'order_id': dtype('int64'), 'unit_price': dtype('int64')}
```

Unlike CSV, the types travel **with** the file. Look at the schema stored inside it:

```python
import pyarrow.parquet as pq

for field in pq.read_schema("output/orders.parquet"):
    print(f"{field.name:<12} {field.type}")
```

```text
order_id     int64
order_date   string
customer_id  string
city         string
product      string
category     string
quantity     int64
unit_price   int64
status       string
```

| | CSV | Parquet |
|---|---|---|
| Types | none: everything is text | stored in the file |
| Read one column | must read every row fully | reads just that column |
| Size | big | compressed: often 5–10× smaller |
| Human-readable | yes | no |

## Common mistakes

- **No `encoding="utf-8"`.** Windows may default to another encoding and garble ₹ or Tamil text.
- **Splitting CSV on commas yourself.** Quoted values with commas break it. Use `csv` (or pandas).
- **CSV without `newline=""`** gives extra blank lines on Windows.
- **`json.load` on a JSON Lines file** fails with `Extra data`. Read it line by line.
- **Writing into the input folder.** Keep raw input read-only and write to a separate `output/`
  (later, `bronze/silver/gold` in Module 7).

## Hands-on exercises

**Exercise 1 · Log summary.** From `server.log`, print the first and last timestamps and how many
lines are INFO.

<details class="solution"><summary>Solution</summary>

```python
lines = Path("data/server.log").read_text(encoding="utf-8").splitlines()
first, last = lines[0].split()[:2], lines[-1].split()[:2]
info = sum(1 for line in lines if line.split()[2] == "INFO")
print(" ".join(first), "→", " ".join(last), "|", info, "INFO lines")
```

```text
2025-01-03 10:00:01 → 2025-01-03 10:00:06 | 5 INFO lines
```

</details>

**Exercise 2 · CSV to JSON Lines.** Convert `orders.csv` to `output/orders.jsonl`, with `quantity` and
`unit_price` as numbers. Print the second line of the result.

<details class="solution"><summary>Solution</summary>

```python
with open("data/orders.csv", newline="", encoding="utf-8") as src, \
     open("output/orders.jsonl", "w", encoding="utf-8") as dst:
    for row in csv.DictReader(src):
        row["quantity"], row["unit_price"] = int(row["quantity"]), float(row["unit_price"])
        dst.write(json.dumps(row) + "\n")
print(Path("output/orders.jsonl").read_text().splitlines()[1])
```

```text
{"order_id": "1002", "order_date": "2025-01-03", "customer_id": "C02", "city": "Coimbatore", "product": "Mouse", "category": "Electronics", "quantity": 2, "unit_price": 450.0, "status": "delivered"}
```

</details>

**Exercise 3 · Flatten customers to CSV.** Write `output/customers.csv` with columns `customer_id,
name, city, pincode, tags`, with the tags joined by `|`.

<details class="solution"><summary>Solution</summary>

```python
with open("output/customers.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["customer_id", "name", "city", "pincode", "tags"])
    for c in customers:
        w.writerow([c["customer_id"], c["name"], c["address"]["city"], c["address"]["pincode"], "|".join(c["tags"])])
print(Path("output/customers.csv").read_text().splitlines()[5])
```

```text
C05,Ravi,Chennai,600020,prime|student
```

</details>

**Exercise 4 · Every file in a folder.** Print the number of lines in every file in `data/` using
`Path.glob`.

<details class="solution"><summary>Solution</summary>

```python
for p in sorted(Path("data").glob("*")):
    print(p.name, len(p.read_text(encoding="utf-8").splitlines()))
```

```text
customers.json 8
events.jsonl 8
orders.csv 14
server.log 7
```

</details>

**Exercise 5 · Parquet round trip.** Save only the delivered orders to `output/delivered.parquet`,
read it back, and print the number of rows and the distinct statuses.

<details class="solution"><summary>Solution</summary>

```python
df = pd.read_csv("data/orders.csv")
df[df["status"] == "delivered"].to_parquet("output/delivered.parquet", index=False)
back = pd.read_parquet("output/delivered.parquet")
print(len(back), back["status"].unique().tolist())
```

```text
11 ['delivered']
```

</details>
