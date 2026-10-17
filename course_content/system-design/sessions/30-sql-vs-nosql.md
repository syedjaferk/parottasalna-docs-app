# Chapter 30 · SQL vs NoSQL

## The big idea

- **SQL (relational) databases** store data in **tables with a fixed structure** and let you combine
  tables with **joins**. They give strong guarantees (ACID).
- **NoSQL databases** ("not only SQL") store data in **other shapes**, such as key-value, documents,
  wide columns or graphs. They trade some of the guarantees for **scale, flexibility and speed** for
  specific access patterns.

**Everyday example:** SQL is an **accountant's ledger**: columns are fixed, entries are linked, totals
must balance. NoSQL is a **filing cabinet of folders**: each folder can hold whatever you like, it is
quick to grab one folder by its label, but cross-referencing two folders is on you.

```{raw} html
:file: ../diagrams/sql-vs-nosql.html
```

## The same data in both worlds

An order with items:

```python
import sqlite3, json

# --- SQL: normalised into tables, joined on demand ---
db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT);
CREATE TABLE orders    (id INTEGER PRIMARY KEY, customer_id INTEGER REFERENCES customers(id));
CREATE TABLE items     (order_id INTEGER REFERENCES orders(id), sku TEXT, qty INTEGER, price INTEGER);
INSERT INTO customers VALUES (1, 'Asha');
INSERT INTO orders    VALUES (100, 1);
INSERT INTO items     VALUES (100, 'TEA-250', 2, 120), (100, 'CUP-1', 1, 80);
""")
rows = db.execute("""
    SELECT c.name, i.sku, i.qty * i.price AS line_total
      FROM orders o JOIN customers c ON c.id = o.customer_id
                    JOIN items i     ON i.order_id = o.id
     WHERE o.id = 100
""").fetchall()
print("SQL joined rows:", rows)

# --- NoSQL document: the whole order is one self-contained document ---
document = {"_id": 100, "customer": {"id": 1, "name": "Asha"},
            "items": [{"sku": "TEA-250", "qty": 2, "price": 120}, {"sku": "CUP-1", "qty": 1, "price": 80}]}
print("Document read  :", json.dumps(document)[:70], "...")
print("Order total    :", sum(i["qty"] * i["price"] for i in document["items"]))
```

**Output:**

```text
SQL joined rows: [('Asha', 'TEA-250', 240), ('Asha', 'CUP-1', 80)]
Document read  : {"_id": 100, "customer": {"id": 1, "name": "Asha"}, "items": [{"sku":  ...
Order total    : 320
```

SQL stores each fact **once** (no duplication) and rebuilds the order with **joins**. The document stores
the whole order **together**, so one read gets everything, but the customer's name is **copied** into
every order (denormalised).

## Comparison

| | SQL (relational) | NoSQL |
|---|---|---|
| Structure | Fixed schema, tables, rows | Flexible: documents, key-value, wide columns, graph |
| Relationships | **Joins**, foreign keys | Embed or reference manually |
| Transactions | **ACID** across rows and tables | Often per record; multi-record varies |
| Consistency | Strong by default | Often eventual (tunable) |
| Scaling reads | Replicas | Replicas |
| Scaling writes | Vertical first; sharding is hard | **Designed to shard horizontally** |
| Query power | Ad-hoc queries, aggregations, SQL | Strong on key/known patterns, weaker ad hoc |
| Schema changes | Migrations | Easy to add fields; messy long term |
| Examples | PostgreSQL, MySQL, Oracle, SQL Server | MongoDB, Cassandra, DynamoDB, Redis, Neo4j |

## When to pick which

**Choose SQL when:**

- Data is **structured and related** (users, orders, payments, inventory).
- You need **transactions** and strong consistency.
- You need **ad-hoc queries** and reporting.
- The scale fits a primary with replicas (this covers most companies!).

**Choose NoSQL when:**

- **Huge scale or write throughput** that one machine cannot handle (millions of writes per second).
- The access pattern is **simple and known**: get by key, time-series, session lookup.
- **Flexible, evolving shape**: product catalogue with different attributes per category.
- **Low-latency global distribution** with tolerance for eventual consistency.
- A natural **graph** (social network, recommendations) or **cache** (Redis).

:::{admonition} A strong default
:class: tip
"I would start with PostgreSQL. It handles our 4,000 reads/s and 40 writes/s with replicas. If
writes grow past what one primary can handle, or the access pattern becomes pure key lookups, I would
move that dataset to a sharded NoSQL store." Reasoning like this beats naming a trendy database.
:::

## Polyglot persistence

Real systems use **several databases**, each for what it is best at:

| Need | Typical store |
|---|---|
| Orders, payments | PostgreSQL |
| Sessions, cache, rate-limit counters | Redis |
| Product catalogue | Document database |
| Full-text search | Elasticsearch / OpenSearch |
| Time-series metrics | InfluxDB, TimescaleDB |
| Images, videos | Object storage (S3) |
| Social graph | Graph database |

The cost: keeping them in sync (use **change data capture**) and operating several systems.

## Modelling mindset

- **SQL:** model the **data** first (normalise), then query it any way you like.
- **NoSQL:** model the **queries** first (what will I ask?), then shape the data to answer each one
  quickly, accepting duplication.

## Common mistakes

:::{warning}
- Picking NoSQL "because it scales" when a single PostgreSQL would be fine for years.
- Picking NoSQL and then needing joins and transactions everywhere.
- Treating "schemaless" as "no design": the schema moves into your application code.
- Believing SQL cannot scale. It scales further than most products ever need; it just needs more thought beyond one primary.
:::

## Try it yourself

1. A bank ledger versus a user-activity feed with 500,000 writes per second. Which database for each, and why?
2. Your product catalogue has books, laptops and shirts, each with different attributes. Which fits?
3. Why does a document database duplicate data, and what is the risk?

<details class="solution"><summary>Answers</summary>

1. Ledger: **SQL** (ACID, auditing). Activity feed: a **wide-column or key-value store** like Cassandra or DynamoDB that shards writes horizontally.
2. A **document database** (each product is a document with its own fields), or a relational table with JSON columns.
3. Embedding related data makes reads fast with one lookup. The risk is copies going out of date (customer renames themselves, old orders still show the old name), so you must update or accept it.

</details>

:::{admonition} Next
:class: important
Whatever you pick, queries must be fast. The tool that makes them fast: [database indexes](31-database-indexes.md).
:::
