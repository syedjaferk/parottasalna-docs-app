# Chapter 31 · Database indexes

## The big idea

An **index** is a separate, sorted structure that lets the database **jump straight to matching rows**
instead of reading the whole table.

**Everyday example:** the **index at the back of a textbook**. To find "photosynthesis" you do not read
all 600 pages. You look in the alphabetical index, see "page 214", and open that page. A database index
does the same for a column.

```{raw} html
:file: ../diagrams/database-indexes.html
```

## Without an index: a full table scan

If you ask `WHERE email = 'asha@example.com'` and there is no index, the database must check **every
row**. 10 million rows means reading 10 million rows. With an index it reads **about 4 to 5 pages**.

## Seeing the difference with a real database

```python
import sqlite3, time, random

db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT, city TEXT)")
random.seed(1)
db.executemany("INSERT INTO users (email, city) VALUES (?, ?)",
               [(f"user{i}@example.com", random.choice(["Chennai", "Pune", "Delhi"])) for i in range(300_000)])
db.commit()

query = "SELECT id FROM users WHERE email = 'user250000@example.com'"

print("plan without index:", db.execute("EXPLAIN QUERY PLAN " + query).fetchone()[3])
start = time.perf_counter()
for _ in range(20):
    db.execute(query).fetchall()
slow = (time.perf_counter() - start) / 20

db.execute("CREATE INDEX idx_users_email ON users (email)")

print("plan with index   :", db.execute("EXPLAIN QUERY PLAN " + query).fetchone()[3])
start = time.perf_counter()
for _ in range(20):
    db.execute(query).fetchall()
fast = (time.perf_counter() - start) / 20

print("index at least 50x faster than the scan:", slow / fast > 50)
```

**Output:**

```text
plan without index: SCAN users
plan with index   : SEARCH users USING COVERING INDEX idx_users_email (email=?)
index at least 50x faster than the scan: True
```

`SCAN` means reading every row; `SEARCH ... USING INDEX` means jumping directly to the match.

## How an index works: the B-tree

Most indexes are **B-trees** (balanced trees):

- Keys are kept **sorted** in pages (nodes); each page points to child pages.
- Lookup starts at the root and picks a child at each level.
- With a page holding hundreds of keys, a tree of 3 to 4 levels covers **hundreds of millions of rows**.
  So any lookup costs **3 to 4 page reads**, regardless of table size: **O(log n)**.
- Because keys are sorted, the index also serves **range queries** (`BETWEEN`), **ORDER BY** and
  **prefix matches** (`LIKE 'abc%'`).

```python
import math

for rows in (1_000, 1_000_000, 100_000_000, 10_000_000_000):
    fanout = 200                                         # keys per page
    levels = math.ceil(math.log(rows, fanout))
    print(f"{rows:>14,} rows -> about {levels} page reads per lookup")
```

**Output:**

```text
         1,000 rows -> about 2 page reads per lookup
     1,000,000 rows -> about 3 page reads per lookup
   100,000,000 rows -> about 4 page reads per lookup
10,000,000,000 rows -> about 5 page reads per lookup
```

Ten billion rows, only five page reads. That is why indexes are so powerful.

## Index types

| Type | Good for | Notes |
|---|---|---|
| **B-tree** (default) | Equality, ranges, sorting | General purpose |
| **Hash** | Exact equality only | Very fast `=`, no range queries |
| **Composite (multi-column)** | Queries that filter on several columns | **Column order matters** |
| **Unique** | Enforcing uniqueness (email) | Also speeds lookups |
| **Covering** | Query answered **from the index alone** | Avoids visiting the table |
| **Partial** | Only some rows (`WHERE active = true`) | Smaller and faster |
| **Full-text** | Words inside text | Search engines |
| **Geospatial (GiST, R-tree)** | "Within 5 km" | Maps |

### Composite index: order matters

An index on `(city, created_at)` helps queries that filter by `city`, or by `city` **and** `created_at`.
It does **not** help a query filtering only by `created_at` (the leftmost-prefix rule). Think of a phone
book sorted by last name then first name: great for "Sharma", useless for "everyone named Ravi".

## The cost: nothing is free

Every index:

- **Slows writes**: each `INSERT`, `UPDATE`, `DELETE` must update the table **and** every index on it.
- **Uses storage**: sometimes as large as the table.
- **Needs maintenance**: fragmentation, rebuilds.

So **do not index everything**. Index columns used in `WHERE`, `JOIN`, `ORDER BY` of **frequent and slow**
queries. A table that is mostly written (logs) wants few indexes; a table that is mostly read wants more.

## When an index is not used

- Applying a **function to the column**: `WHERE LOWER(email) = ...` (create an expression index instead).
- **Leading wildcards**: `LIKE '%sharma'` cannot use a normal index.
- **Low selectivity**: indexing a column with two values (`gender`) rarely helps, since half the table matches.
- **Implicit type conversion** (comparing a string column to a number).
- Very small tables: scanning is faster than using the index.

## Reading a query plan

Always check with `EXPLAIN` (or `EXPLAIN ANALYZE` in PostgreSQL). Look for **sequential/full scans** on
big tables, and **estimated vs actual rows** for stale statistics.

## Indexes in NoSQL

The same ideas appear everywhere: DynamoDB's **partition and sort keys**, MongoDB's secondary indexes,
Cassandra's **clustering key** inside a partition, Elasticsearch's **inverted index** for text. Whatever
the engine, "how is the data sorted, and what can I look up quickly?" is the key question.

## Common mistakes

:::{warning}
- No index on a foreign key or frequent filter column, so every request scans the table.
- Indexing every column "just in case" and slowing every write.
- Composite index with the columns in the wrong order.
- Never looking at the query plan; guessing instead.
:::

## Try it yourself

1. A table has 50 million rows. Roughly how many page reads for a B-tree lookup with 200 keys per page?
2. You query `WHERE city = 'Pune' AND created_at > '2024-01-01'`. Which composite index order is better, `(city, created_at)` or `(created_at, city)`?
3. Why does adding five indexes to a table that receives 20,000 writes per second hurt?

<details class="solution"><summary>Answers</summary>

1. log base 200 of 50,000,000 is about 3.3, so **4 page reads**.
2. `(city, created_at)`: equality on `city` narrows to a range, then the range on `created_at` is a contiguous slice.
3. Every write must update the table plus all five index trees, multiplying the I/O and lock contention per write.

</details>

:::{admonition} Next
:class: important
When one machine holds too much data, split it across machines: [database sharding](32-sharding.md).
:::
