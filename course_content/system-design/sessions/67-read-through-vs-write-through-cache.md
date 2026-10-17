# Chapter 67 · Read-through vs write-through cache

## The big idea

Both patterns put the **cache in the middle**, between your application and the database, so the app talks to
**one place**. They differ in **which direction** they handle:

- **Read-through:** on a **read miss**, the **cache itself loads** the value from the database, stores it and
  returns it.
- **Write-through:** on a **write**, the data is written to the **cache and the database together**,
  synchronously, before the write is acknowledged.

**Everyday example:** a **bookshop with a front-desk assistant**. *Read-through:* you ask the assistant for a
book; if it is not on the desk, **the assistant** fetches it from the warehouse, keeps a copy on the desk and
hands it to you. *Write-through:* when new stock or a price change arrives, the assistant updates **both** the
desk list and the warehouse ledger **before** telling you it is done.

```{raw} html
:file: ../diagrams/read-write-through.html
```

## Read-through

```text
app --get(key)--> CACHE
                   hit : return value
                   miss: CACHE loads from the DB, stores it, returns it
```

- The application **never talks to the database for reads**; only to the cache.
- The loading logic lives **in the cache layer** (a "loader" or "cache provider").
- Contrast with **cache-aside**: there, **the application** checks the cache and, on a miss, loads from the
  database and fills the cache itself.

## Write-through

```text
app --put(key, value)--> CACHE --writes to DB (synchronously)--> DB
                          both succeed -> acknowledged to the app
```

- The cache and database are **always in step** for data that was written through the cache.
- Writes are **slower**: two stores must acknowledge.
- You cache data that may **never be read** (wasted memory), unless combined with expiry.

## The patterns in code

```python
db = {"p1": "Tea"}
log = []

class ReadThroughCache:
    def __init__(self, loader):
        self.data, self.loader = {}, loader
    def get(self, key):
        if key in self.data:
            log.append(f"  cache hit  {key}")
            return self.data[key]
        log.append(f"  cache miss {key} -> cache loads from DB")
        self.data[key] = self.loader(key)              # the CACHE fetches; the app does not know about the DB
        return self.data[key]

class WriteThroughCache:
    def __init__(self, store):
        self.data, self.store = {}, store
    def put(self, key, value):
        self.store[key] = value                         # 1. write to the database first (source of truth)...
        self.data[key] = value                          # 2. ...then the cache, so they are always in step
        log.append(f"  wrote {key} to DB and cache")

reader = ReadThroughCache(loader=lambda k: db[k])
print("read-through:")
print(" ", reader.get("p1")); print(" ", reader.get("p1"))
print("\n".join(log)); log.clear()

writer = WriteThroughCache(db)
writer.put("p2", "Coffee")
print("\nwrite-through:")
print("\n".join(log))
print("DB has p2:", db["p2"], "| cache has p2:", writer.data["p2"])
```

**Output:**

```text
read-through:
  Tea
  Tea
  cache miss p1 -> cache loads from DB
  cache hit  p1

write-through:
  wrote p2 to DB and cache
DB has p2: Coffee | cache has p2: Coffee
```

## Side by side

| | **Read-through** | **Write-through** |
|---|---|---|
| Triggered by | A **read miss** | A **write** |
| Who loads or writes | The **cache layer** | The **cache layer** |
| Freshness | Stale until TTL or invalidation if the DB changes elsewhere | Cache is **fresh** for writes that go through it |
| First read | **Slow** (miss) | Fast after a write (already cached) |
| Write latency | Unaffected | **Higher** (cache + DB) |
| Wasted memory | Only data requested | Data written but never read |
| Data-loss risk | None added | None (DB is written synchronously) |
| Complexity | Cache must support loaders | Cache must be able to write to the DB |

They are **complementary**: the most common pairing is **read-through + write-through**. Reads populate the cache
on demand; writes keep it current; so a read after a write is always a hit and always consistent.

## Where the other strategies fit

| Strategy | Read path | Write path |
|---|---|---|
| **Cache-aside** | App checks cache, on miss loads from the DB and fills the cache | App writes the DB, then **deletes** the cache key |
| **Read-through** | **Cache** loads on miss | (any) |
| **Write-through** | (any) | **Cache** writes cache and DB together, synchronously |
| **Write-behind** | (any) | Cache acknowledges immediately and flushes to the DB **later** |
| **Write-around** | (any) | Write straight to the DB, skipping the cache |

## Choosing

| Situation | Choice |
|---|---|
| General web app, you control the code, simple infrastructure | **Cache-aside** (most common) |
| Want simple app code and your cache/library supports loaders (Caffeine, Hazelcast, NCache, DynamoDB DAX) | **Read-through** |
| Read-after-write consistency matters and writes are moderate | **Write-through** (+ read-through) |
| Heavy write bursts, tolerate small loss (counters) | Write-behind |
| Write-once, rarely read | Write-around |

## Gotchas

- **Read-through:** the **first request pays the miss**; a cold cache after a restart causes a **load spike** on
  the database (pre-warm). The loader is a single place to add **stampede protection**.
- **Write-through:** doubles the write path; if the DB write succeeds but the cache update fails (or vice
  versa) you must **order the operations and retry** (write DB first; on cache failure, delete the key).
- Both can be bypassed if other writers update the database directly: **use a TTL** as a safety net.
- Negative caching: a missing key may be loaded and cached as "not found" briefly to avoid repeated DB hits.

## Common mistakes

:::{warning}
- Calling it "write-through" while actually writing the cache first and the database later (that is write-behind, which can lose data).
- Using write-through for data that is written often but almost never read.
- No TTL, so data changed directly in the database stays stale forever.
- Forgetting the cold-start spike after a restart or deploy.
:::

## Try it yourself

1. A product page is read 1,000 times for each update. Which pattern matters more, and why?
2. What is the difference between cache-aside and read-through, in one sentence?
3. Why write the database first, then the cache, in write-through?

<details class="solution"><summary>Answers</summary>

1. **Read-through (or cache-aside)**: the workload is read-heavy, so a high hit rate on reads matters most; write cost is rare.
2. In cache-aside the **application** loads from the DB and fills the cache; in read-through the **cache** does that itself.
3. The database is the source of truth. If the cache write fails afterwards, the data is still safe and you can retry or invalidate; the reverse order could leave a cache entry for data that never reached the database.

</details>

:::{admonition} Next
:class: important
Who initiates data movement, the producer or the consumer? [Push vs pull architecture](68-push-vs-pull-architecture.md).
:::
