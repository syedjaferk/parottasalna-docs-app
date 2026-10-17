# Chapter 11 · Design autocomplete for a search engine

## The problem

As a user types `how t`, show the 5 most useful completions, fast enough to feel instant (under
100 ms). Think of the suggestion box on Google or on an e-commerce site.

```{raw} html
:file: ../diagrams/autocomplete.html
```

## Requirements

- **Functional:** given a prefix, return the top 5 suggestions ranked by popularity; support
  updates as trends change.
- **Non-functional:** very low latency, highly available, suggestions may be a few hours old
  (eventual consistency is fine).
- **Scale:** 10 million users, about 10 searches each a day, each search types about 5 characters
  that fire requests. That is about **500 million requests a day, roughly 6,000 per second, 15,000
  at peak**.

## The trie

A **trie** (prefix tree) stores words one character per node. Everything under the node for `ho`
starts with `ho`. Walking a trie to a prefix takes time proportional to the prefix length, not to the
number of words.

```text
root
 ├─ h ─ o ─ w          (how)       count 90
 │       └ t ─ e ─ l  (hotel)     count 70
 └─ i ─ n ─ d ─ i ─ a (india)      count 120
```

**Make lookups O(prefix length):** store the **top-k suggestions inside each node** (precomputed), so
you never walk the whole subtree at query time.

## Serving path (read-only and fast)

1. Browser sends the prefix after a short **debounce** (about 100-200 ms of no typing).
2. The suggestion service checks a **prefix cache**. Short prefixes (`a`, `ho`) are extremely hot.
3. On a miss it reads the trie (kept in memory, replicated), returns the top 5 and fills the cache.
4. Add a CDN or browser cache for the most common prefixes.

## Data pipeline (offline)

Searches are logged, aggregated (a count per query per day or week), then a **trie builder** creates
a new trie and publishes it, and servers swap it in. Rebuilding offline keeps the serving path
simple. For fresh trends add a small real-time layer on top.

## Scaling and trade-offs

- **Shard the trie by prefix range** (a-g, h-m, ...). Watch for hot shards (`s` is more common than
  `x`) and split by two letters if needed.
- **Update cadence:** hourly or daily rebuild, versus real-time (more complex, rarely needed).
- **Personalisation, typo tolerance and filtering offensive terms** are extensions. Mention them, do
  not build them first.

## Common mistakes

- Querying a SQL `LIKE 'ho%'` on every keystroke.
- Sending a request for every character with no debounce.
- Updating the live trie in place under read traffic.

:::{admonition} Try it in the playground
:class: important
Build it step by step in [Design Autocomplete](/system-design/autocomplete/).
:::
