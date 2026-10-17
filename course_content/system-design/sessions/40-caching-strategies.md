# Chapter 40 · Caching strategies

## The big idea

"Use a cache" is not a design. You must decide **who talks to the cache and the database, and in what
order** for reads and writes. Each pattern trades **freshness, speed, simplicity and risk of data loss**.

**Everyday example:** a school office. Parents ask the clerk (cache) for a student's record. Cache-aside:
the clerk says "not here, go to the archive yourself and bring a copy back". Read-through: the clerk
goes to the archive for you. Write-through: whenever a record changes, the clerk updates both the desk
copy and the archive before telling you it is done. Write-behind: the clerk updates the desk copy and
promises to update the archive later.

```{raw} html
:file: ../diagrams/caching-strategies.html
```

## 1. Cache-aside (lazy loading)

The **application** manages the cache.

**Read:** check the cache. **Hit** return. **Miss** read the database, **store in the cache**, return.
**Write:** update the database, then **delete** (or update) the cache entry.

- **Pro:** only requested data is cached; a cache failure does not break the app (just slower); the
  most common pattern.
- **Con:** the first request for each key is slow; stale data possible between a database change and
  the invalidation; app code owns the logic.

## 2. Read-through

The **cache** loads data itself from the database on a miss. The app only talks to the cache.

- **Pro:** simpler app code; consistent loading logic in one place.
- **Con:** needs a cache that supports loaders; first read still slow; data model must match the cache.

## 3. Write-through

Every write goes to the **cache and the database together**, synchronously, and succeeds only when both do.

- **Pro:** the cache is always fresh; reads after writes are fast and consistent.
- **Con:** **writes are slower** (two stores); you cache data that may never be read; needs coordination.
- Often combined with read-through.

## 4. Write-behind (write-back)

Write to the **cache only**, acknowledge, and **flush to the database later** (asynchronously, in batches).

- **Pro:** very fast writes; batching reduces database load; absorbs bursts.
- **Con:** **risk of data loss** if the cache dies before flushing; harder to debug; the database is
  temporarily stale.
- Good for: counters, view counts, analytics, logs. Not for money.

## 5. Write-around

Write **directly to the database** and **skip the cache**; the cache fills only on a later read.

- **Pro:** avoids filling the cache with data written once and rarely read.
- **Con:** a read right after a write is a miss (slow).

## 6. Refresh-ahead

The cache **refreshes popular entries before they expire**, predicting they will be requested again.

- **Pro:** hot keys never expire under load; no stampede, consistent latency.
- **Con:** wasted refreshes of items that were not needed; harder to predict.

## The strategies in code

```python
db = {"p1": "Tea"}                     # the slow source of truth
cache = {}
log = []

def db_read(k):  log.append(f"DB read {k}");  return db.get(k)
def db_write(k, v): log.append(f"DB write {k}"); db[k] = v

# cache-aside
def aside_read(k):
    if k in cache:
        log.append(f"cache hit {k}"); return cache[k]
    v = db_read(k); cache[k] = v; return v
def aside_write(k, v):
    db_write(k, v); cache.pop(k, None)                 # invalidate

# write-through
def through_write(k, v):
    db_write(k, v); cache[k] = v                       # both, synchronously

# write-behind
dirty = {}
def behind_write(k, v):
    cache[k] = v; dirty[k] = v                         # cache only for now
def flush():
    for k, v in list(dirty.items()):
        db_write(k, v); del dirty[k]

print("cache-aside :", aside_read("p1"), aside_read("p1"))
aside_write("p1", "Masala Tea"); print("after write :", aside_read("p1"))
through_write("p2", "Coffee");   print("write-through: DB has p2 =", db["p2"], "| cache has p2 =", cache["p2"])
behind_write("p3", "Juice");     print("write-behind : DB has p3? ", "p3" in db, "| dirty queue:", dirty)
flush();                          print("after flush  : DB has p3? ", "p3" in db)
print("operations   :", log)
```

**Output:**

```text
cache-aside : Tea Tea
after write : Masala Tea
write-through: DB has p2 = Coffee | cache has p2 = Coffee
write-behind : DB has p3?  False | dirty queue: {'p3': 'Juice'}
after flush  : DB has p3?  True
operations   : ['DB read p1', 'cache hit p1', 'DB write p1', 'DB read p1', 'DB write p2', 'DB write p3']
```

Notice: write-behind returned before the database had the data (the risky window), and cache-aside's
second read was a pure cache hit.

## Choosing

| Workload | Pattern |
|---|---|
| Read-heavy, general purpose | **Cache-aside** |
| Read-heavy, simple app code, cache supports loaders | Read-through |
| Must read your own writes, can afford slower writes | Write-through (+ read-through) |
| Write-heavy, losing a few seconds of data is acceptable | Write-behind |
| Data written once, rarely read (logs, uploads) | Write-around |
| A few very hot, expensive keys | Refresh-ahead |

## The classic race: stale cache after a write

Cache-aside has a subtle race. Two requests at the same time:

1. Reader misses, reads old value `A` from the database.
2. Writer updates the database to `B`, **deletes** the cache key.
3. Reader (slow) now **stores `A`** in the cache.

The cache now holds stale `A` until its TTL expires. Mitigations: **short TTLs as a safety net**,
version numbers, or invalidate **after a short delay** (delayed double delete). This is exactly why
TTLs matter even when you invalidate explicitly.

## Stampede protection

When a hot key expires, thousands of requests miss together:

- **Request coalescing / single flight:** one request rebuilds; the others wait for its result.
- **Lock per key** with a short timeout.
- **TTL jitter:** add random seconds so many keys do not expire together.
- **Serve stale while revalidating:** return the old value and refresh in the background.

## Common mistakes

:::{warning}
- Write-behind for important data with no replication or durability on the cache.
- Updating the cache on write instead of deleting it when two writers can race.
- No TTL: stale data lives forever after a missed invalidation.
- Caching a database **miss** forever (a new row never appears); cache "not found" briefly.
:::

## Try it yourself

1. Which strategy for: a user's profile page, a video view counter, and a bank balance?
2. Why is deleting the cache key on write usually safer than updating it?
3. Write-behind acknowledged a write and then the cache node crashed. What was lost?

<details class="solution"><summary>Answers</summary>

1. Profile: **cache-aside**. View counter: **write-behind** (batch the updates). Bank balance: don't cache it, or **write-through** with the database as the truth.
2. With two concurrent writers, updating the cache can leave the **older** value last. Deleting forces the next reader to load the current database value.
3. Any updates that were in the cache but not yet flushed to the database.

</details>

:::{admonition} Next
:class: important
Caches are finite. What gets thrown out when it fills up? [Cache eviction policies](41-eviction-policies.md).
:::
