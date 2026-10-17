# Chapter 50 · Distributed locking

## The big idea

A **distributed lock** makes sure that **only one process across many machines** does a particular thing at a
time (run a cron job, update a shared record, be the leader).

**Everyday example:** a **single key to the meeting room**, hung on a hook in the lobby. Whoever takes the key
may use the room. Everyone else waits. If someone walks off with the key and disappears, the room is stuck,
so the key has an **expiry**: after two hours the receptionist hands out a new key. That fixes the stuck room
but creates a new danger: the first person may still be inside when the second walks in.

```{raw} html
:file: ../diagrams/distributed-locking.html
```

## Why you need one

Local locks (`threading.Lock`) only work inside one process. With many servers you face:

- Two servers run the **same nightly job** twice.
- Two requests update the same **inventory** record at once.
- Only one instance should be the **leader** or **consumer of a partition**.

Often a **database row lock** or a **unique constraint** is enough (`SELECT ... FOR UPDATE`,
`INSERT ... ON CONFLICT DO NOTHING`). Use a separate distributed lock only when the shared resource is not
protected by a database transaction.

## Requirements of a good lock

1. **Mutual exclusion:** at most one holder at a time.
2. **Deadlock freedom:** a crashed holder must not block everyone forever, so locks need a **lease (TTL)**.
3. **Fault tolerance:** the lock service must survive failures.
4. **Fairness / no starvation** (nice to have).

## The simple Redis lock

```text
SET lock:invoice-job  <random-token>  NX  PX 30000
```

- `NX`: set only if it does **not** exist (acquire).
- `PX 30000`: expire in 30 seconds (the lease).
- **Release** only if the stored token is **yours** (use a small Lua script so check-and-delete is atomic);
  otherwise you might delete someone else's lock.

```python
import time, uuid

class LockServer:
    """A toy lock service with leases, like SET key token NX PX ttl."""
    def __init__(self):
        self.locks = {}                                   # name -> (token, expires_at)

    def acquire(self, name, ttl, now):
        holder = self.locks.get(name)
        if holder and holder[1] > now:
            return None                                   # still held by someone
        token = str(uuid.uuid4())[:8]
        self.locks[name] = (token, now + ttl)
        return token

    def release(self, name, token):
        holder = self.locks.get(name)
        if holder and holder[0] == token:                 # only the owner may release
            del self.locks[name]
            return True
        return False

server = LockServer()
a = server.acquire("report", ttl=10, now=0)
b = server.acquire("report", ttl=10, now=3)               # A still holds it
print("A acquired:", a is not None, "| B acquired while A holds:", b is not None)
print("B releases with a wrong token:", server.release("report", "wrong"))
print("A releases:", server.release("report", a))
c = server.acquire("report", ttl=10, now=4)
print("C acquired after release:", c is not None)
d = server.acquire("report", ttl=10, now=20)              # C crashed and never released; its lease expired
print("D acquired after C's lease expired:", d is not None)
```

**Output:**

```text
A acquired: True | B acquired while A holds: False
B releases with a wrong token: False
A releases: True
C acquired after release: True
D acquired after C's lease expired: True
```

Leases prevent a crashed holder from blocking forever.

## The danger: a lease that expires while you are still working

```text
t=0   Client A acquires the lock (lease 10 s)
t=1   A hits a long GC pause (or network delay) ... 12 seconds
t=10  A's lease expires
t=11  Client B acquires the lock and starts writing
t=13  A wakes up, still believes it holds the lock, and writes  --> A and B overlap: DATA CORRUPTION
```

This is the core problem Martin Kleppmann describes in *How to do distributed locking*. A lock with a TTL
cannot **by itself** guarantee mutual exclusion, because processes can pause and clocks can drift.

### The fix: fencing tokens

Every time the lock is granted the lock service hands out a **monotonically increasing number**. The
**resource** (database, storage) **rejects any write with a smaller token than one it has already seen**.

```python
class Storage:
    def __init__(self):
        self.value, self.highest_token = None, 0
    def write(self, token, value):
        if token < self.highest_token:
            return f"REJECTED (stale token {token} < {self.highest_token})"
        self.highest_token, self.value = token, value
        return f"accepted with token {token}"

storage = Storage()
print("client A (token 33) writes first :", storage.write(33, "A's data"))
# A pauses; lease expires; B acquires the lock and receives token 34
print("client B (token 34) writes       :", storage.write(34, "B's data"))
# A wakes up and tries to write with its old token
print("client A wakes up, token 33      :", storage.write(33, "A's late data"))
print("final value:", storage.value)
```

**Output:**

```text
client A (token 33) writes first : accepted with token 33
client B (token 34) writes       : accepted with token 34
client A wakes up, token 33      : REJECTED (stale token 33 < 34)
final value: B's data
```

The late write from the paused client was rejected. The lock narrows the chance of overlap, and the **fencing
token makes correctness safe even when it happens**.

## Choosing the lock service

| Option | Safety | Notes |
|---|---|---|
| **Database row lock / unique constraint** | Strong (inside the DB transaction) | Simplest. Use first. |
| **Redis `SET NX PX`** (single instance) | Good for efficiency locks | Failover can lose the lock; no fencing token |
| **Redlock** (several Redis instances) | Debated: timing assumptions | Fine for "avoid duplicate work", not for strict correctness |
| **ZooKeeper / etcd / Consul** | **Strongest**: consensus-backed, sessions, ephemeral nodes, fencing via zxid/revision | Heavier |

Two kinds of locks:

- **Efficiency lock:** avoid doing duplicate work (sending a job twice is wasteful but harmless). A Redis
  lock is fine.
- **Correctness lock:** protects data integrity. Needs **consensus plus fencing tokens**, or avoid the lock
  entirely using database constraints, optimistic concurrency or idempotency.

## Alternatives to locking

- **Optimistic concurrency:** `UPDATE ... WHERE version = 7`.
- **Idempotent operations** so duplicates are harmless.
- **Single writer per partition** (assign each key to exactly one worker via sharding/leader).
- **Queues:** serialise work by putting it on one queue consumed by one worker.

## Common mistakes

:::{warning}
- A lock with **no expiry**: a crashed holder blocks everyone forever.
- Releasing a lock you no longer own (delete without checking the token).
- Assuming a TTL lock gives safety when the holder can pause (use **fencing tokens**).
- Holding locks across slow external calls, or for the entire request.
- Using a lock where a unique constraint or an atomic update would do.
:::

## Try it yourself

1. A job takes 40 seconds but the lock lease is 30 seconds. What can go wrong, and what are two remedies?
2. Why must release check that the token matches?
3. Why do you prefer a database unique constraint over a Redis lock for "only one active subscription per user"?

<details class="solution"><summary>Answers</summary>

1. The lease expires while the job runs, a second worker starts the same job: overlap. Remedies: **renew the lease** (heartbeat/watchdog) while working, and use **fencing tokens** so late writes are rejected.
2. Otherwise a slow client whose lease expired could delete the lock now owned by someone else.
3. The constraint is enforced **atomically by the database where the data lives**, so it is correct with no timing assumptions.

</details>

:::{admonition} Next
:class: important
So far membership and agreement have been central. A different, scalable way to spread information: the
[gossip protocol](51-gossip-protocol.md).
:::
