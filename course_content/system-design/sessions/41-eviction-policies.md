# Chapter 41 · Cache eviction policies

## The big idea

A cache is **smaller than the data it fronts**. When it is full and a new item arrives, something must be
**evicted** (thrown out). The **eviction policy** decides *what*. A good policy keeps the items that will
be used soon; a bad one throws out what you are about to need.

**Everyday example:** a small desk with space for 5 books. When you need a 6th, which do you put back on
the shelf? The one you have not touched for days (**LRU**)? The one you have used least overall (**LFU**)?
The one you put on the desk first (**FIFO**)? Each rule suits a different habit.

```{raw} html
:file: ../diagrams/eviction-policies.html
```

## The policies

### LRU: Least Recently Used

Evict the entry **not used for the longest time**. Assumes recent use predicts future use (it usually does).
The default choice.

### LFU: Least Frequently Used

Evict the entry with the **fewest accesses**. Good when popularity is stable. Weakness: old items that
were popular once keep a high count and stay forever; counts need ageing.

### FIFO: First In, First Out

Evict the **oldest inserted** entry, regardless of use. Simple, ignores popularity. Rarely best.

### LIFO / MRU: Most Recently Used

Evict the **newest**. Useful in odd patterns such as a one-pass scan over data.

### Random

Evict a random entry. Surprisingly decent, and **cheap** (no bookkeeping). Redis uses **sampled LRU**:
pick a few random keys and evict the least recently used among them.

### TTL-based

Entries expire after a fixed time, regardless of space. Used **together** with the above to bound staleness.

### Newer policies

- **TinyLFU / W-TinyLFU (Caffeine):** a small frequency sketch decides whether a new item is even worth
  admitting. Excellent hit rates.
- **ARC / 2Q / SLRU:** combine recency and frequency adaptively.
- **Belady's optimal:** evict what will be used **furthest in the future**. Impossible to implement (needs the
  future) but the benchmark all policies are measured against.

## LRU in O(1): the classic interview question

A **hash map** (key to node) plus a **doubly linked list** (order of use). Access moves a node to the front;
eviction removes the tail.

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.capacity, self.data = capacity, OrderedDict()
    def get(self, key):
        if key not in self.data:
            return None
        self.data.move_to_end(key)                  # now the most recently used
        return self.data[key]
    def put(self, key, value):
        self.data[key] = value
        self.data.move_to_end(key)
        if len(self.data) > self.capacity:
            evicted, _ = self.data.popitem(last=False)   # drop the least recently used
            return evicted

cache = LRUCache(3)
for k in "ABC":
    cache.put(k, k.lower())
cache.get("A")                      # touch A: order is now B, C, A
evicted = cache.put("D", "d")        # cache full -> evict the least recent (B)
print("evicted :", evicted)
print("contents:", list(cache.data))
```

**Output:**

```text
evicted : B
contents: ['C', 'A', 'D']
```

`A` was used recently so it survived; `B` had gone longest untouched and was evicted.

## Comparing policies on the same workload

```python
import random
from collections import OrderedDict, Counter, deque

random.seed(21)
# 80% of requests go to 20 hot keys; 20% to 400 cold keys; cache holds 40 keys
requests = [random.randrange(20) if random.random() < 0.8 else random.randrange(20, 420) for _ in range(30_000)]
CAPACITY = 40

def run(policy):
    cache, hits = {}, 0
    order = OrderedDict(); freq = Counter(); fifo = deque()
    for k in requests:
        if k in cache:
            hits += 1
            order.move_to_end(k); freq[k] += 1
            continue
        if len(cache) >= CAPACITY:
            if policy == "LRU":
                victim, _ = order.popitem(last=False)
            elif policy == "LFU":
                victim = min(cache, key=lambda x: freq[x])
            elif policy == "FIFO":
                victim = fifo.popleft()
            else:
                victim = random.choice(list(cache))
            cache.pop(victim); order.pop(victim, None)
        cache[k] = True; order[k] = None; freq[k] += 1; fifo.append(k)
    return hits / len(requests)

for p in ("LRU", "LFU", "FIFO", "RANDOM"):
    print(f"{p:<7} hit rate: {run(p):.1%}")
```

**Output:**

```text
LRU     hit rate: 79.1%
LFU     hit rate: 80.5%
FIFO    hit rate: 67.7%
RANDOM  hit rate: 67.4%
```

With a clearly popular set, LFU and LRU do well; FIFO and random waste space on one-time cold keys. The best
policy depends on the **access pattern**, so measure with real traffic.

## Choosing

| Pattern | Best fit |
|---|---|
| General web traffic | **LRU** (or W-TinyLFU) |
| Stable, long-lived popularity (top products) | LFU |
| Time-bound data (sessions, tokens) | TTL (plus LRU for memory) |
| One big scan that should not pollute the cache | Scan-resistant: 2Q, ARC, TinyLFU |
| Need very cheap bookkeeping at huge scale | Random / sampled LRU |

## Eviction in real systems

- **Redis:** `maxmemory-policy` options: `allkeys-lru`, `volatile-lru` (only keys with a TTL),
  `allkeys-lfu`, `allkeys-random`, `volatile-ttl`, `noeviction` (reject writes when full).
- **Memcached:** LRU per slab class.
- **CPU and OS page caches:** approximations of LRU (CLOCK).
- **CDNs:** LRU plus admission control (cache only on the second request).

## Common mistakes

:::{warning}
- No eviction policy (`noeviction`) so the cache starts rejecting writes when full.
- A big one-off scan (an export) pollutes an LRU cache and throws out all the hot data.
- Choosing LFU without ageing: yesterday's viral item squats forever.
- Forgetting the TTL: eviction frees memory but does not guarantee freshness.
:::

## Try it yourself

1. A cache of size 3 receives A, B, C, A, D. With LRU, which item is evicted when D arrives?
2. Why is plain LFU risky for trending content?
3. What two data structures give O(1) get and put for LRU?

<details class="solution"><summary>Answers</summary>

1. The order of use is B, C, A (A was just used). **B** is the least recently used, so B is evicted.
2. An item that was extremely popular last week keeps a huge count and is never evicted, while a new viral item with a low count is evicted first. Use **ageing/decay**.
3. A **hash map** and a **doubly linked list**.

</details>

:::{admonition} Next
:class: important
One cache server is not enough for a big site: [distributed caching](42-distributed-caching.md).
:::
