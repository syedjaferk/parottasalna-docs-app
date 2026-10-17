# Chapter 46 · Change data capture (CDC)

## The big idea

**Change data capture** turns a database's changes into a **stream of events**. Every insert, update and
delete is captured **as it happens** and delivered to other systems (a search index, a cache, a
warehouse), so they stay in sync **without polling the database or changing application code**.

**Everyday example:** a **bank passbook** versus an **SMS alert**. Checking your passbook (polling the table)
tells you what changed only when you remember to look. CDC is the SMS: the moment money moves, a message
about **exactly what changed** is sent to whoever signed up.

```{raw} html
:file: ../diagrams/cdc.html
```

## The problem it solves

One database is the source of truth, but you also need the same data in:

- a **search index** (Elasticsearch) for text search,
- a **cache** (Redis) that must be invalidated,
- a **data warehouse** for analytics,
- another **microservice's** own database,
- an **audit trail**.

Common bad solutions:

| Approach | Problem |
|---|---|
| **Dual writes** (app writes to DB **and** to search) | If one write fails, they diverge. No transaction spans both. |
| **Polling** (`SELECT ... WHERE updated_at > ?` every minute) | Misses deletes, adds load, adds delay, clock-skew bugs |
| **Batch ETL nightly** | Data is a day old |

CDC fixes all of this by reading the **database's own commit log**.

## How it works: log-based CDC

Every serious database already writes every change to a **transaction log** first (PostgreSQL WAL, MySQL
binlog, MongoDB oplog) for **durability and replication**. A CDC tool **reads that same log**.

1. The app commits a change to the database as usual.
2. The change is appended to the **transaction log**.
3. A **CDC connector** (Debezium, AWS DMS) tails the log, converts entries into **events** (`before` and
   `after` values), and publishes them to a stream (Kafka).
4. **Consumers** apply the events to their own stores.

```text
{ "op": "u", "table": "products", "key": 42,
  "before": {"price": 120}, "after": {"price": 99}, "ts": 1718000000 }
```

Because it reads the log, it captures **everything committed, in commit order, including deletes**, with
**no extra load** on the tables and **no changes to application code**.

## A small simulation

```python
# The database applies changes and records each one in a log. CDC consumers read the log.
database = {}
log = []                                    # the transaction log (append-only)

def db_write(table, key, value):
    before = database.get((table, key))
    database[(table, key)] = value
    log.append({"op": "update" if before else "insert", "table": table, "key": key, "before": before, "after": value})

def db_delete(table, key):
    log.append({"op": "delete", "table": table, "key": key, "before": database.pop((table, key), None), "after": None})

search_index, cache = {}, {}

def cdc_consumer(position):
    """Read new log entries and update downstream systems. Returns the new position (offset)."""
    for event in log[position:]:
        k = (event["table"], event["key"])
        if event["op"] == "delete":
            search_index.pop(k, None); cache.pop(k, None)
        else:
            search_index[k] = event["after"]; cache.pop(k, None)       # keep search in sync, invalidate cache
    return len(log)

db_write("products", 42, "Masala Tea")
db_write("products", 43, "Filter Coffee")
pos = cdc_consumer(0)
db_write("products", 42, "Masala Chai")          # an update
db_delete("products", 43)                          # a delete: polling by updated_at would miss this
pos = cdc_consumer(pos)

print("database    :", dict(database))
print("search index:", dict(search_index))
print("log entries :", len(log), "| consumer offset:", pos)
```

**Output:**

```text
database    : {('products', 42): 'Masala Chai'}
search index: {('products', 42): 'Masala Chai'}
log entries : 4 | consumer offset: 4
```

The search index mirrors the database exactly, **including the delete**, and the consumer remembers its
**offset** so after a restart it resumes where it stopped.

## The outbox pattern: the safe way to publish events from your own code

Sometimes you want to publish a **business event** ("order placed") rather than raw row changes. If you
write the order to the database **and** then publish to Kafka, a crash between the two loses the event.

**Outbox:** in the **same database transaction**, insert the order **and** a row into an `outbox` table.
A CDC connector (or poller) reads the outbox and publishes. The event is published **if and only if**
the order committed.

```sql
BEGIN;
INSERT INTO orders (id, user_id, total) VALUES (9001, 17, 500);
INSERT INTO outbox (id, topic, payload) VALUES (gen_random_uuid(), 'order.placed', '{"order_id": 9001}');
COMMIT;      -- both happen, or neither does
```

## Guarantees and gotchas

- **Order:** preserved per key/partition, so partition events by primary key.
- **At-least-once** delivery: consumers must be **idempotent** (apply "set price = 99" twice, no harm).
- **Initial snapshot:** a new consumer first needs the current state (snapshot), then the stream.
- **Schema changes:** the event shape changes when columns change; use a schema registry.
- **Lag:** consumers are slightly behind; monitor **replication slot lag** (an unconsumed slot makes
  PostgreSQL keep WAL on disk and can fill the disk).
- **Eventual consistency:** downstream stores are seconds behind the source.

## Where CDC is used

| Use | How |
|---|---|
| Keep **search** in sync | DB changes to Elasticsearch |
| **Cache invalidation** | A change event deletes the cache key (avoids stale-cache races) |
| **Data warehouse / lake** | Stream changes into BigQuery/Snowflake, no nightly dump |
| **Microservice data sync, CQRS read models** | Build query-optimised views from events |
| **Audit and compliance** | A full history of changes |
| **Zero-downtime migration** | Replicate old DB to new, then cut over |

## Common mistakes

:::{warning}
- **Dual writes** to a database and a broker instead of CDC or an outbox.
- Polling with `updated_at` and missing hard deletes.
- Non-idempotent consumers (a replay applies changes twice).
- Ignoring slot or offset lag until the source database's disk fills.
:::

## Try it yourself

1. Why is "write to DB, then publish to Kafka" unsafe, and how does the outbox pattern fix it?
2. Why does CDC catch deletes when `WHERE updated_at > last_run` does not?
3. A consumer crashes and restarts. How does it avoid missing or repeating a lot of events?

<details class="solution"><summary>Answers</summary>

1. A crash between the two steps leaves the DB updated but no event published. With an outbox, the event row is written **in the same transaction**, so it exists if and only if the data change committed.
2. A deleted row no longer exists, so no `updated_at` can be read. CDC reads the **log**, which records the delete itself.
3. It stores its **offset** (log position). On restart it resumes there. Idempotent processing makes the small chance of a repeated event harmless.

</details>

:::{admonition} Next
:class: important
Time to see how many machines know whether each other is alive: [heartbeats](47-heartbeats.md).
:::
