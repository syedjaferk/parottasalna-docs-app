# Chapter 5 · Caching and serving reads

## The big idea

A **cache** is fast memory that remembers answers you already worked out. If a few popular items cause
most of the traffic, remembering them saves the slow, expensive trip to the database.

**Everyday example:** a tea stall keeps the most-ordered snacks on the counter instead of walking to
the storeroom each time.

```{raw} html
:file: ../diagrams/cache-aside.html
```

## Where can you cache?

| Layer | Example | Good for |
|---|---|---|
| Client | Browser cache (a 301 redirect) | Zero server load |
| CDN / edge | Content close to the user | Static files, popular redirects |
| Application | In-process map | Tiny, very hot data |
| Shared cache | Redis or Memcached | Hot rows shared by all servers |
| Database | Buffer pool | Automatic |

## Cache-aside, step by step

1. The app asks the cache for the key.
2. **Hit:** answer from memory.
3. **Miss:** read the database, **store the result in the cache**, answer.

Other patterns: **write-through** (write both at once), **write-back** (write the cache, flush later:
fast but risky).

## Eviction and invalidation

- **LRU** (least recently used) throws out what has not been used for the longest time. It is a good default.
- Give every entry a **TTL**. For expiring links, never let the TTL outlive the link.
- When a link is edited or deleted, **delete the cache entry** so nobody is served stale data.

## Sizing the cache

Hot 20% of one day's reads at 500 bytes: about 35 GB for a shortener with 4,000 reads per second.
That fits in memory, so a small Redis cluster handles most of the load.

## When the cache fails

If the cache dies, every request falls through to the database and may overwhelm it (a **cache
stampede**). Protect it with **request coalescing** (one request fills the cache while others wait),
rate limits, and warm replacement nodes.

## Common mistakes

- Caching without saying what the **hit rate** should be.
- Forgetting invalidation and TTLs.
- Treating the cache as the only copy of data.
- No plan for a cold or failed cache.

:::{admonition} Try it in the playground
:class: important
The [TinyURL problem](/system-design/tinyurl/) has you size the cache and decide between 301 and 302
redirects, a choice that decides how much traffic ever reaches your cache.
:::
