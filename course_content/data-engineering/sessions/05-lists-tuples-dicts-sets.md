# Session 5 · Lists, tuples, dictionaries and sets

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube.com/embed/sHWDumBI03M"
  title="Session 1: Introduction to Python Variables, List" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

<br>

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube.com/embed/GDZsOr7H_fk"
  title="Session 3: Dictionary, Set, Tuple" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

## The big idea

Choosing the right container makes code both **simpler** and **faster**:

| Structure | Think of it as | Data-engineering use |
|---|---|---|
| `list` `[...]` | a queue of items, in order | a batch of records, rows to load |
| `tuple` `(...)` | a fixed, sealed record | a composite key like `(city, month)`, a returned pair |
| `dict` `{k: v}` | a lookup table | one record (`column → value`), an index (`id → record`) |
| `set` `{...}` | a bag of unique things | de-duplicating, fast "have I seen this?", comparing two systems |

**Everyday example:** a warehouse. Parcels on a conveyor are a **list**; a shelf label like
*(Aisle 4, Rack B)* is a **tuple**; the stock register *product → quantity* is a **dict**; the set of
products *currently in stock* is a **set**.

Run the examples **in order, in one session** (a Jupyter notebook is ideal): later examples
reuse earlier variables. We'll use this list of records all session (parsed from `orders.csv` with the `parse_order`
function from Session 3):

```python
HEADER = "order_id,order_date,customer_id,city,product,category,quantity,unit_price,status".split(",")

def parse_order(line):
    r = dict(zip(HEADER, line.strip().split(",")))
    r["order_id"], r["quantity"], r["unit_price"] = int(r["order_id"]), int(r["quantity"]), float(r["unit_price"])
    return r

with open("data/orders.csv") as f:
    next(f)
    orders = [parse_order(line) for line in f]

print(len(orders), type(orders).__name__, type(orders[0]).__name__)
```

```text
13 list dict
```

## Lists: ordered batches

```python
batch = [1001, 1002, 1003]
batch.append(1004)                    # one item at the end
batch.extend([1005, 1006])            # many items
print(batch, len(batch))
print(batch[0], batch[-1], batch[1:3])    # index, last item, slice
print(1003 in batch)
```

```text
[1001, 1002, 1003, 1004, 1005, 1006] 6
1001 1006 [1002, 1003]
True
```

Loading a database in **chunks** is an everyday list task:

```python
ids = list(range(1001, 1014))
size = 5
chunks = [ids[i:i + size] for i in range(0, len(ids), size)]
for chunk in chunks:
    print(chunk)
```

```text
[1001, 1002, 1003, 1004, 1005]
[1006, 1007, 1008, 1009, 1010]
[1011, 1012, 1013]
```

## Tuples: fixed records and composite keys

A tuple can't be changed, so it's safe to use as a **dictionary key**: perfect for "group by
several columns":

```python
monthly = {}
for o in orders:
    key = (o["city"] or "UNKNOWN", o["order_date"][:7])       # (city, "YYYY-MM")
    monthly[key] = monthly.get(key, 0) + o["quantity"] * o["unit_price"]

for (city, month), amount in sorted(monthly.items()):
    print(f"{city:<11} {month}  ₹{amount:>9,.0f}")
```

```text
Chennai     2025-01  ₹   58,000
Chennai     2025-02  ₹   10,000
Coimbatore  2025-01  ₹    2,400
Madurai     2025-01  ₹      400
Madurai     2025-02  ₹   52,000
Salem       2025-02  ₹      200
Trichy      2025-01  ₹    1,500
UNKNOWN     2025-01  ₹      200
```

(These totals include *every* status and the duplicate row. Cleaning comes in Session 12.)

Functions often **return a tuple** when they have two answers. Unpack it on the way out:

```python
def min_max_price(rows):
    prices = [r["unit_price"] for r in rows]
    return min(prices), max(prices)

low, high = min_max_price(orders)
print(low, high)
```

```text
10.0 55000.0
```

## Dictionaries: records, lookups and groups

### A record

```python
order = orders[4]
print(order["product"], order.get("coupon"), order.get("coupon", "NONE"))
order["amount"] = order["quantity"] * order["unit_price"]       # add a field
print(sorted(order))                                            # its keys, sorted
```

```text
Pen None NONE
['amount', 'category', 'city', 'customer_id', 'order_date', 'order_id', 'product', 'quantity', 'status', 'unit_price']
```

`d[key]` raises `KeyError` if the key is missing; `d.get(key, default)` doesn't. Use `[]` when the
field **must** exist (missing is a bug), and `.get` when it's optional.

### An index: a lookup "join"

Joining orders to customers by looping over both lists checks every pair, which is slow. Build a
**dict index** once, and each lookup is instant. Databases call this a **hash join**:

```{raw} html
:file: ../diagrams/s05-lookup.html
```

```python
import json

with open("data/customers.json") as f:
    customers = json.load(f)

by_id = {c["customer_id"]: c for c in customers}          # the index: id → customer

for o in orders[:3]:
    c = by_id.get(o["customer_id"])
    print(o["order_id"], o["product"], "→", c["name"] if c else "?")
```

```text
1001 Laptop → Arun
1002 Mouse → Priya
1003 Notebook → Karthik
```

### Grouping and counting: defaultdict and Counter

```python
from collections import Counter, defaultdict

products_by_category = defaultdict(list)          # missing keys start as an empty list
for o in orders:
    products_by_category[o["category"]].append(o["product"])
print(dict(products_by_category))

status_counts = Counter(o["status"] for o in orders)
print(status_counts)
print(status_counts.most_common(1))
```

```text
{'Electronics': ['Laptop', 'Mouse', 'Headphones', 'Keyboard', 'Laptop', 'Monitor'], 'Stationery': ['Notebook', 'Pen', 'Notebook', 'Pen'], 'Home': ['Desk Lamp', 'Water Bottle', 'Water Bottle']}
Counter({'delivered': 11, 'returned': 1, 'cancelled': 1})
[('delivered', 11)]
```

## Sets: unique values and comparisons

```python
order_ids = [o["order_id"] for o in orders]
unique_ids = set(order_ids)
print(len(order_ids), len(unique_ids))             # 13 rows, 12 unique: one duplicate

seen, duplicates = set(), set()
for oid in order_ids:
    (duplicates if oid in seen else seen).add(oid)
print("duplicates:", duplicates)
```

```text
13 12
duplicates: {1008}
```

### Reconciling two systems

After a load, compare what the **source** had with what the **target** received:

```python
source_ids = {1001, 1002, 1003, 1004, 1005}
warehouse_ids = {1001, 1002, 1004, 1099}

print("missing in warehouse:", sorted(source_ids - warehouse_ids))
print("unexpected in warehouse:", sorted(warehouse_ids - source_ids))
print("in both:", sorted(source_ids & warehouse_ids))
print("in either:", len(source_ids | warehouse_ids))
```

```text
missing in warehouse: [1003, 1005]
unexpected in warehouse: [1099]
in both: [1001, 1002, 1004]
in either: 6
```

This check catches lost or extra rows: run it after every important load.

## Why sets and dicts are fast

Checking `x in some_list` looks at items one by one: the bigger the list, the slower. Sets and
dicts use **hashing** to jump straight to the answer, no matter how big they are:

```py
import timeit

ids_list = list(range(1_000_000))
ids_set = set(ids_list)
print(timeit.timeit(lambda: 999_999 in ids_list, number=100))
print(timeit.timeit(lambda: 999_999 in ids_set, number=100))
```

```text
1.1453              ← list: scans a million items, 100 times
0.0000083           ← set: about 100,000× faster
```

(Exact numbers depend on your computer.) The rule: **if you check membership often, use a set or
a dict.**

## Common mistakes

- **`list.remove` / `in` inside a big loop**: slow (quadratic) on large data. Use a set or dict.
- **Using a list as a dict key**: `TypeError: unhashable type: 'list'`. Use a tuple.
- **Copying by assignment.** `b = a` shares one list; use `a.copy()` (or `copy.deepcopy` for nested
  records) before changing records you didn't create.
- **Expecting sets to keep order.** They don't. `sorted(s)` when the order matters; to de-duplicate
  *and* keep the order use `list(dict.fromkeys(items))`.

## Hands-on exercises

**Exercise 1 · Products sold.** Print the sorted list of **distinct** product names in `orders`.

<details class="solution"><summary>Solution</summary>

```python
HEADER = "order_id,order_date,customer_id,city,product,category,quantity,unit_price,status".split(",")
with open("data/orders.csv") as f:
    next(f)
    orders = [dict(zip(HEADER, line.strip().split(","))) for line in f]
print(sorted({o["product"] for o in orders}))
```

</details>

**Exercise 2 · Revenue by category.** Sum `quantity × unit_price` per category for **delivered**
orders only, using a dict.

<details class="solution"><summary>Solution</summary>

```python
HEADER = "order_id,order_date,customer_id,city,product,category,quantity,unit_price,status".split(",")
revenue = {}
with open("data/orders.csv") as f:
    next(f)
    for line in f:
        o = dict(zip(HEADER, line.strip().split(",")))
        if o["status"] == "delivered":
            revenue[o["category"]] = revenue.get(o["category"], 0) + int(o["quantity"]) * float(o["unit_price"])
print(revenue)    # {'Electronics': 118900.0, 'Stationery': 1300.0, 'Home': 1500.0}
```

(Home includes the duplicate water-bottle row twice.)

</details>

**Exercise 3 · Enrich orders.** Add the customer's `name` and `pincode` (from the nested `address`)
to each of the first three orders.

<details class="solution"><summary>Solution</summary>

```python
import json

with open("data/customers.json") as f:
    by_id = {c["customer_id"]: c for c in json.load(f)}

orders = [{"order_id": 1001, "customer_id": "C01"}, {"order_id": 1002, "customer_id": "C02"},
          {"order_id": 1003, "customer_id": "C03"}]
for o in orders:
    c = by_id[o["customer_id"]]
    o["name"], o["pincode"] = c["name"], c["address"]["pincode"]
print(orders[0])    # {'order_id': 1001, 'customer_id': 'C01', 'name': 'Arun', 'pincode': '600001'}
```

</details>

**Exercise 4 · Customers who never ordered.** Using sets, list customers in `customers.json` with no
orders in `orders.csv`.

<details class="solution"><summary>Solution</summary>

```python
import json

with open("data/customers.json") as f:
    all_customers = {c["customer_id"] for c in json.load(f)}
with open("data/orders.csv") as f:
    next(f)
    ordered = {line.split(",")[2] for line in f}
print(sorted(all_customers - ordered))     # []: every customer has ordered
```

An empty result is still a useful answer: the check passed.

</details>

**Exercise 5 · Tag counts.** Count how many customers have each tag (`prime`, `student`) with a
`Counter`.

<details class="solution"><summary>Solution</summary>

```python
import json
from collections import Counter

with open("data/customers.json") as f:
    customers = json.load(f)
print(Counter(tag for c in customers for tag in c["tags"]))   # prime: 2, student: 2
```

</details>

**Exercise 6 · De-duplicate, keeping order.** Remove duplicate rows (identical lines) from
`orders.csv`, keeping the first one of each and the original order, and print how many lines are
left.

<details class="solution"><summary>Solution</summary>

```python
with open("data/orders.csv") as f:
    header, *rows = f.read().splitlines()
unique_rows = list(dict.fromkeys(rows))       # dict keys keep insertion order
print(len(rows), "→", len(unique_rows))       # 13 → 12
```

</details>
