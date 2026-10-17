# Chapter 29 · ACID transactions

## The big idea

A **transaction** groups several database operations into **one all-or-nothing unit**. **ACID** is the
set of four guarantees a good database gives a transaction.

**Everyday example:** transferring Rs 500 from Asha to Ravi has two steps: take 500 from Asha, add 500
to Ravi. If the power fails between the steps, 500 rupees vanish. A transaction promises that either
**both** steps happen or **neither** does.

```{raw} html
:file: ../diagrams/acid.html
```

## The four letters

| Letter | Promise | Plain meaning | If it were missing |
|---|---|---|---|
| **A**tomicity | All or nothing | The transfer happens fully or not at all | Money disappears mid-way |
| **C**onsistency | Rules always hold | Balances never go negative, foreign keys stay valid | The data breaks its own rules |
| **I**solation | Transactions do not interfere | Two transfers at once behave as if one ran after the other | Wrong totals, double spending |
| **D**urability | Committed means permanent | After "success", a crash cannot lose it | Acknowledged writes disappear |

## Atomicity in action

```python
import sqlite3

db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE accounts (name TEXT PRIMARY KEY, balance INTEGER CHECK (balance >= 0))")
db.executemany("INSERT INTO accounts VALUES (?, ?)", [("asha", 1000), ("ravi", 200)])
db.commit()

def transfer(src, dst, amount):
    try:
        with db:                                    # one transaction: commit on success, rollback on error
            db.execute("UPDATE accounts SET balance = balance - ? WHERE name = ?", (amount, src))
            db.execute("UPDATE accounts SET balance = balance + ? WHERE name = ?", (amount, dst))
        return "committed"
    except sqlite3.IntegrityError as e:
        return f"rolled back ({e})"

def show():
    return dict(db.execute("SELECT name, balance FROM accounts"))

print("before            :", show())
print("asha -> ravi 300  :", transfer("asha", "ravi", 300), show())
print("asha -> ravi 5000 :", transfer("asha", "ravi", 5000), show())
```

**Output:**

```text
before            : {'asha': 1000, 'ravi': 200}
asha -> ravi 300  : committed {'asha': 700, 'ravi': 500}
asha -> ravi 5000 : rolled back (CHECK constraint failed: balance >= 0) {'asha': 700, 'ravi': 500}
```

The second transfer would have made Asha's balance negative. The `CHECK` constraint (**consistency**)
rejected the first update, and the whole transaction **rolled back**: Ravi did not receive anything.

## Isolation: what goes wrong without it

When transactions run **at the same time**, odd things can happen. The names to know:

| Anomaly | What happens |
|---|---|
| **Dirty read** | You read data another transaction has **not committed** (and may roll back) |
| **Non-repeatable read** | You read a row twice in one transaction and get **different values** (someone committed in between) |
| **Phantom read** | You run the same query twice and a **new row appears** |
| **Lost update** | Two transactions read the same value, both add to it, one write overwrites the other |
| **Write skew** | Two transactions each check a rule, both pass, together they break it (two doctors both go off-call) |

```python
# A lost update, step by step (two clients adding to the same counter)
counter = 100
a_reads = counter            # client A reads 100
b_reads = counter            # client B reads 100 (before A writes)
counter = a_reads + 10       # A writes 110
counter = b_reads + 20       # B writes 120   <- overwrites A's update
print("expected 130, got", counter)
```

**Output:**

```text
expected 130, got 120
```

### Isolation levels: pick your trade-off

| Level | Prevents | Cost |
|---|---|---|
| **Read uncommitted** | Nothing | Fastest, almost never used |
| **Read committed** (default in PostgreSQL) | Dirty reads | Good balance |
| **Repeatable read** (default in MySQL InnoDB) | Dirty + non-repeatable reads | More locking / versions |
| **Serializable** | Everything: acts as if one at a time | Slowest; transactions may abort and need retry |

Stronger isolation = more correctness, more waiting or aborts. Banking uses stronger levels;
a "like" counter does not.

### How databases provide isolation

- **Locks:** a transaction locks the rows it touches; others wait (pessimistic).
- **MVCC (multi-version concurrency control):** keep several versions of a row; readers see a consistent
  **snapshot** and never block writers. PostgreSQL, MySQL InnoDB and Oracle do this.
- **Optimistic concurrency:** do the work, then at commit check "did anyone change this row?" (a
  `version` column). If yes, retry.

```text
UPDATE products SET stock = stock - 1, version = version + 1
 WHERE id = 7 AND version = 12;          -- 0 rows updated means someone else got there first: retry
```

## Durability: the write-ahead log

The database first **appends the change to a log on disk** (the **write-ahead log, WAL**) and only
then updates data pages. If the machine crashes, on restart it **replays the log**, so every committed
transaction survives and uncommitted ones are undone. This is also the log that **replication** and
**change data capture** read from.

## Where ACID applies in system design

- **Money, inventory, bookings, orders:** need ACID. Use a relational database.
- **Across services:** you cannot hold one transaction across two databases cheaply. Use **sagas**
  (a sequence of local transactions with compensating steps), covered in the microservices chapter.
- **Distributed SQL (Spanner, CockroachDB):** offer ACID across nodes at higher latency.
- **BASE** (basically available, soft state, eventually consistent) is the NoSQL alternative: trade
  strict guarantees for scale and availability.

## Common mistakes

:::{warning}
- Doing read-modify-write in the application (`read balance`, `add`, `write`) instead of an atomic
  `UPDATE ... SET balance = balance + 100` or inside a transaction with the right isolation.
- Keeping a transaction open while calling an external API (it holds locks for seconds).
- Assuming **Serializable** everywhere: it is slow; apply it where correctness demands it.
- Forgetting that ACID is **per database**; microservices each own their own transaction.
:::

## Try it yourself

1. Which ACID letter is violated if a crash after "payment succeeded" loses the order?
2. Two users buy the last concert ticket at the same moment. Which anomaly can oversell it, and how do you prevent it?
3. Why can long-running transactions hurt a busy database?

<details class="solution"><summary>Answers</summary>

1. **Durability.**
2. A **lost update / write skew**. Prevent with an atomic conditional update (`UPDATE ... SET sold = true WHERE id = 5 AND sold = false`) or `SELECT ... FOR UPDATE`, or optimistic version checks.
3. They hold locks (or old row versions) for a long time, blocking other work and bloating storage.

</details>

:::{admonition} Next
:class: important
ACID is the signature of relational databases. How do they compare with the alternatives? [SQL vs
NoSQL](30-sql-vs-nosql.md).
:::
