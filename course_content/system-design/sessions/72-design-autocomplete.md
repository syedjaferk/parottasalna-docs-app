# Chapter 72 · Design autocomplete for a search engine

## Concepts to review first

This design is built from earlier chapters. Skim them if any term feels new:

- [Caching 101](39-caching-101.md)
- [Distributed caching](42-distributed-caching.md)
- [CDN](43-cdn.md)
- [Data replication](33-replication.md)
- [Batch vs stream processing](64-batch-vs-stream-processing.md)
- [Message queues](44-message-queues.md)

## The problem

As a user types `how t`, show the five most useful completions fast enough to feel instant. Think of the suggestion
box on a search engine or an e-commerce site.

```text
user types:  how t
suggestions: how to tie a tie
             how to train your dragon
             how to take a screenshot
             how to tie a saree
             how to turn off an iphone
```

```{raw} html
:file: ../diagrams/autocomplete.html
```

## Step 1: clarify requirements

**Functional:** given a prefix, return the top 5 completions ranked by popularity; suggestions follow changing trends.

**Out of scope:** spell correction, personalised suggestions, semantic search, the results page itself.

**Non-functional:** very low latency (the response must arrive **before the next keystroke**, so well under 100 ms),
highly available (search must work even if suggestions do not), and **eventual consistency is fine**: suggestions that
are a few hours old are perfectly acceptable.

## Step 2: estimate the load

Given: **10 million users**, about **10 searches each a day**, each search typed in about **5 requests** (one per
key after a short pause), **100 million distinct queries** of about **30 bytes**.

```python
users, searches_per_user, requests_per_search = 10_000_000, 10, 5
distinct_queries, bytes_per_query = 100_000_000, 30

requests_per_day = users * searches_per_user * requests_per_search
avg_rps = requests_per_day / 86_400
peak_rps = avg_rps * 3

raw_gb = distinct_queries * bytes_per_query / 1e9
trie_gb = raw_gb * 8                      # a trie with top-5 lists in every node is roughly 5 to 10 times the raw text

print(f"requests per day : {requests_per_day:,}")
print(f"average          : {avg_rps:,.0f} requests per second")
print(f"peak             : {peak_rps:,.0f} requests per second")
print(f"raw query text   : {raw_gb:.0f} GB")
print(f"trie in memory   : about {trie_gb:.0f} GB")
```

**Output:**

```text
requests per day : 500,000,000
average          : 5,787 requests per second
peak             : 17,361 requests per second
raw query text   : 3 GB
trie in memory   : about 24 GB
```

Conclusions: about **6,000 requests per second (about 17,000 at peak)** is far too much for a database query per keystroke, and
about **24 GB** fits in the memory of **one machine**. So the bottleneck is **request rate**, not data size: we
replicate the whole structure for traffic and only shard if memory ever becomes a problem.

## Step 3: API

```text
GET /v1/suggest?q=how%20t&limit=5

200 OK
Cache-Control: public, max-age=60
{"query": "how t", "suggestions": ["how to tie a tie", "how to train your dragon", "how to take a screenshot", ...]}
```

`Cache-Control` lets the browser and a CDN cache popular prefixes, so a large share of requests never reach us.

## Step 4: the data structure, a trie with top-k in every node

A **trie** (prefix tree) has one node per prefix. Walking `h`, `o`, `w` takes **three steps** whatever the dictionary
size. The speed trick: store the **top 5 completions inside every node**, pre-computed, so a lookup does no ranking.

```python
K = 5

class Node:
    def __init__(self):
        self.children = {}
        self.top = []                      # up to K entries of (count, query), best first

class Trie:
    def __init__(self):
        self.root = Node()

    def insert(self, query, count):
        node = self.root
        for ch in query:
            node = node.children.setdefault(ch, Node())
            node.top.append((count, query))
            node.top.sort(key=lambda item: (-item[0], item[1]))
            del node.top[K:]                # keep only the best K at every prefix

    def suggest(self, prefix):
        node, steps = self.root, 0
        for ch in prefix:
            node, steps = node.children.get(ch), steps + 1
            if node is None:
                return [], steps
        return [query for _, query in node.top], steps

popular = {"how to tie a tie": 9000, "how to train your dragon": 7000, "how to take a screenshot": 8000,
           "how to tie a saree": 6500, "how to turn off an iphone": 6000, "how to lose weight": 5000,
           "hotel near me": 8500, "hotels in goa": 7500, "house for rent": 4000, "india vs australia": 12000}

trie = Trie()
for query, count in popular.items():
    trie.insert(query, count)

for prefix in ("how t", "ho", "hot", "zzz"):
    suggestions, steps = trie.suggest(prefix)
    print(f"{prefix!r:<8} ({steps} steps) -> {suggestions}")
```

**Output:**

```text
'how t'  (5 steps) -> ['how to tie a tie', 'how to take a screenshot', 'how to train your dragon', 'how to tie a saree', 'how to turn off an iphone']
'ho'     (2 steps) -> ['how to tie a tie', 'hotel near me', 'how to take a screenshot', 'hotels in goa', 'how to train your dragon']
'hot'    (3 steps) -> ['hotel near me', 'hotels in goa']
'zzz'    (1 steps) -> []
```

Notice `ho` returns the five most popular completions across `how ...`, `hotel ...` and `house ...`, with no
sorting at query time. Compare the work against the naive SQL approach `WHERE query LIKE 'ho%' ORDER BY count DESC LIMIT 5`:

```python
import random
random.seed(4)

words = ["how", "hotel", "house", "horse", "home", "honey", "hockey", "hobby", "host", "hold"]
tails = [f"{a} {b}" for a in ("to", "in", "near", "for", "with", "tips") for b in ("kids", "free", "work", "today", "online", "fast", "cheap", "best")]
queries = [f"{w} {t}" for w in words for t in tails for _ in range(1000)]          # 4.8 million rows
print("rows in the table:", f"{len(queries):,}")

prefix = "ho"
examined_naive = len(queries)                                  # a LIKE 'ho%' without a good index scans the table
print(f"naive scan examines   : {examined_naive:,} rows, then sorts the matches")
print(f"trie examines         : {len(prefix)} nodes and returns the stored top 5")
```

**Output:**

```text
rows in the table: 480,000
naive scan examines   : 480,000 rows, then sorts the matches
trie examines         : 2 nodes and returns the stored top 5
```

## Step 5: keep the client and the network quiet

Most requests can be avoided before they reach any server:

```python
def requests_sent(keystroke_times_ms, debounce_ms):
    """Send a request only when the user pauses for `debounce_ms` after a key."""
    sent = 0
    for i, t in enumerate(keystroke_times_ms):
        next_key = keystroke_times_ms[i + 1] if i + 1 < len(keystroke_times_ms) else float("inf")
        if next_key - t >= debounce_ms:
            sent += 1
    return sent

typing = [0, 110, 230, 340, 800, 905, 1010, 1130, 1700, 1810, 1925]    # 11 keystrokes with a few natural pauses
print("keystrokes                    :", len(typing))
print("requests with no debounce     :", len(typing))
print("requests with 200 ms debounce :", requests_sent(typing, 200))
```

**Output:**

```text
keystrokes                    : 11
requests with no debounce     : 11
requests with 200 ms debounce : 3
```

Also **cancel the previous in-flight request** when a new key arrives (so a slow old answer never overwrites a newer
one), **cache answers in the browser** (backspacing reuses them), and let the **CDN cache hot prefixes** like `a`,
`ho` and `how`. Short prefixes are extremely popular and therefore extremely cacheable.

## Step 6: the serving path

```text
Browser -> (debounce, local cache) -> CDN -> Load balancer -> Suggestion service
   Suggestion service: 1. prefix cache (Redis)    hit -> answer
                       2. trie in memory          -> answer, and fill the prefix cache
```

The suggestion service holds the **whole trie in memory** and is **read-only**, so it needs no locking and scales by
adding identical servers behind the load balancer.

## Step 7: keeping suggestions fresh (the data pipeline)

Never update the live trie in place under read traffic. Rebuild it **offline** and swap it in:

```python
# continues from the earlier examples (the Trie class and `trie` object)
from collections import Counter

search_log = ["india vs australia", "how to tie a tie", "india vs australia", "hotel near me",
              "how to tie a tie", "india vs australia", "hotel near me", "how to train your dragon"]

counts = Counter(search_log)                      # the aggregator: query -> how many times
print("aggregated counts:", dict(counts))

new_trie = Trie()                                  # the builder: a fresh trie from the counts
for query, count in counts.items():
    new_trie.insert(query, count)

live = {"trie": trie}                              # the serving process holds a reference to the current trie
live["trie"] = new_trie                            # atomic swap: readers see the old or the new one, never half of each
print("after the swap, 'in' suggests:", live["trie"].suggest("in")[0])
```

**Output:**

```text
aggregated counts: {'india vs australia': 3, 'how to tie a tie': 2, 'hotel near me': 2, 'how to train your dragon': 1}
after the swap, 'in' suggests: ['india vs australia']
```

1. Searches are written to a **log** (a stream such as Kafka).
2. An **aggregator** counts queries per day or week (and applies a decay so old trends fade).
3. A **trie builder** creates the new trie, **validates** it (size sane, top suggestions plausible, offensive terms
   filtered) and writes it to object storage.
4. Servers **download and atomically swap** the new version. If a build looks wrong, the old trie keeps serving.

For breaking news, add a small **real-time layer** (a stream processor counting the last 10 minutes) merged with the
trie results.

## Step 8: scaling, failures and trade-offs

- **Replicate** the full trie on many servers for traffic. Shard by prefix range only if memory becomes the limit, and
  split by observed traffic (`s` is far busier than `x`).
- **Failure:** autocomplete is optional. If it times out, the search box still works. Return `[]` instead of an error.
- **Cold start:** load the trie from the snapshot before joining the load balancer.

| Choice | You gain | You pay |
|---|---|---|
| Offline rebuild | Simple, safe, fast reads | Suggestions lag by minutes or hours |
| Top-k stored in every node | Constant-time lookups | Several times more memory |
| Replicas before shards | Easy scaling, no cross-node hops | Each server holds the whole trie |
| Browser, CDN and Redis caching | Most traffic never reaches the trie | Slightly stale answers |

## Common mistakes

:::{warning}
- Querying the database with `LIKE 'ho%'` on every keystroke.
- No debounce: three times the load for nothing.
- Updating the live trie in place under read traffic.
- Sharding a trie that fits comfortably in one machine's memory.
- Showing an error when suggestions fail instead of failing quietly.
:::

## Try it yourself

1. Why store the top 5 inside each trie node rather than collecting the subtree at query time?
2. Peak load is 15,000 requests per second and one server handles 3,000. How many servers, with one spare?
3. A viral topic appears. Why would an hourly rebuild feel too slow, and what would you add?

<details class="solution"><summary>Answers</summary>

1. A short prefix such as `a` has millions of descendants, so collecting and sorting them at query time is far too slow. Pre-computing the top 5 turns every lookup into a few pointer hops.
2. 15,000 / 3,000 = 5 servers, plus 1 spare = **6**.
3. The topic would not appear for up to an hour. Add a **real-time layer** that counts the last few minutes of searches in a stream processor and merges those trending queries into the results.

</details>

:::{admonition} Try it in the playground
:class: important
Build it step by step in [Design Autocomplete](/system-design/autocomplete/).
:::

:::{admonition} Next
:class: important
Next case study: [Design a load balancer](73-design-load-balancer.md).
:::
