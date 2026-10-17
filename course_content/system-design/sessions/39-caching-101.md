# Chapter 39 · Caching 101

## The big idea

A **cache** is a small, fast storage that keeps **copies of data you will probably need again**, so
you do not repeat the slow work of fetching or computing it.

**Everyday example:** a tea stall keeps the **most-ordered snacks on the counter** instead of walking to
the storeroom each time. The counter is small and close (the cache); the storeroom is big and far (the
database). Most customers order the same few things, so the counter answers most requests instantly.

```{raw} html
:file: ../diagrams/caching-101.html
```

## Why caching works: two ideas

1. **Locality of reference:** data used recently is likely to be used again soon (**temporal**), and data
   near it is likely to be used next (**spatial**).
2. **The 80/20 rule:** a small share of items (often 10 to 20%) gets most of the traffic. Cache that
   share and you serve most requests from memory.

## The numbers that justify it

| Where the data is | Typical access time |
|---|---|
| CPU cache | 1 ns |
| RAM | 100 ns |
| Redis over the network | 0.5 to 1 ms |
| Database (indexed query) | 5 to 50 ms |
| Another region | 100+ ms |

A cache read is **10 to 100 times faster** than a database read **and** it relieves the database.

```python
import random
random.seed(8)

DB_MS, CACHE_MS = 20, 1
cache, hits, total_ms = {}, 0, 0

# a skewed workload: 20% of the keys receive about 80% of the requests
popular = list(range(200))
rare = list(range(200, 1000))
requests = [random.choice(popular) if random.random() < 0.8 else random.choice(rare) for _ in range(20_000)]

for key in requests:
    if key in cache:
        hits += 1
        total_ms += CACHE_MS
    else:
        total_ms += DB_MS          # miss: read the database...
        cache[key] = True          # ...and remember it (the cache is big enough here)

n = len(requests)
print(f"hit rate    : {hits / n:.1%}")
print(f"avg latency : {total_ms / n:.2f} ms (without cache: {DB_MS} ms)")
print(f"DB queries  : {n - hits:,} of {n:,} requests")
```

**Output:**

```text
hit rate    : 95.0%
avg latency : 1.95 ms (without cache: 20 ms)
DB queries  : 998 of 20,000 requests
```

A cache that holds all 1,000 keys serves 95%+ of requests from memory and cuts database queries from 20,000
to about 1,000.

### The formula

```text
average latency = hit_rate x cache_time + (1 - hit_rate) x slow_time
```

At 90% hit rate with a 1 ms cache and a 20 ms database: `0.9 x 1 + 0.1 x 20 = 2.9 ms`, almost 7 times better.
The last few percent of hit rate matter most: going from 90% to 99% cuts database load **10 times**.

## What to cache

| Good candidates | Poor candidates |
|---|---|
| Read-heavy data (product pages, profiles) | Data that changes every request |
| Expensive computations (a recommendation list, a report) | Rarely repeated data (one-off queries) |
| Results of slow external API calls | Highly personalised, unique responses |
| Static assets (images, JS, CSS) | Data that must be perfectly fresh (a bank balance) |
| Session data, configuration | |

## Where caches live (layers)

```text
Browser cache -> CDN -> reverse proxy -> application cache (in process) -> shared cache (Redis) -> database buffer pool -> disk
```

| Layer | Example | Speed | Shared? |
|---|---|---|---|
| Browser | `Cache-Control` | Instant, zero server load | Per user |
| CDN | Cloudflare, CloudFront | Tens of ms | Per region |
| Application (in process) | Python dict, Guava, Caffeine | Nanoseconds | Per server |
| Shared cache | Redis, Memcached | About 1 ms | All servers |
| Database | Buffer pool, query cache | Automatic | The DB |

## The hard part: invalidation

> "There are only two hard things in computer science: cache invalidation and naming things."

When the source data changes, the cached copy becomes **stale**. Options:

- **TTL (time to live):** entries expire after N seconds. Simple; bounded staleness.
- **Explicit invalidation:** delete or update the cache key when the data changes.
- **Versioned keys:** `product:42:v17`; change the version, old entries are simply never read again.
- **Write-through:** update the cache on every write (see caching strategies).

## What can go wrong

- **Stale data:** users see old information.
- **Cache stampede:** a hot key expires and thousands of requests hit the database at once.
- **Cold cache:** after a restart, every request misses and the database melts.
- **Memory pressure:** cache full, evictions drop useful entries (see eviction policies).
- **Inconsistency between cache and database:** if the cache is the only copy, you can lose data.
- **Hot keys:** one key getting so much traffic one cache node struggles.

## Common mistakes

:::{warning}
- Caching without saying the target **hit rate** or the **TTL**.
- Treating the cache as the **source of truth** (it is a copy and may vanish).
- Caching user-specific data under a shared key (one user sees another's page).
- No plan for a cold or failed cache.
:::

## Try it yourself

1. Cache time 1 ms, database 30 ms, hit rate 95%. What is the average latency?
2. A hot key with a 60-second TTL expires. What happens next without protection, and what is the fix?
3. List three things that make poor cache candidates in a banking app.

<details class="solution"><summary>Answers</summary>

1. 0.95 x 1 + 0.05 x 30 = **2.45 ms**.
2. Many requests miss simultaneously and stampede the database. Fix: **request coalescing** (one request refills, others wait), a lock, or refresh before expiry.
3. Live account balances, one-time OTPs, and per-user transaction lists that must be exactly current.

</details>

:::{admonition} Next
:class: important
How the app and the cache cooperate on reads and writes: [caching strategies](40-caching-strategies.md).
:::
