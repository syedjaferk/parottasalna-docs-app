# Chapter 36 · Bloom filters

## The big idea

A **Bloom filter** is a tiny, fast structure that answers: *"Have I **definitely not** seen this item?"*
or *"I **might** have seen it."* It uses very little memory and never says "no" wrongly, but it can
sometimes say "maybe" when the answer is really "no" (a **false positive**).

**Everyday example:** a **club bouncer** with a rough memory. If he says "I have never seen you before",
that is certainly true. If he says "you look familiar", you might be a member, or he might be mixing you
up with someone else. Checking the real member list (a slow database lookup) is only needed in the
second case.

```{raw} html
:file: ../diagrams/bloom-filter.html
```

## Why it exists

Imagine 1 billion usernames in a database, and you want to check "is `asha123` taken?". A database lookup
costs milliseconds and load. A Bloom filter in memory answers in **microseconds**, and for names that
**do not exist** (most requests) it can answer "no" without touching the database at all.

## How it works

1. Start with an array of **m bits**, all zero.
2. Choose **k independent hash functions**, each mapping an item to a bit position.
3. **Add** an item: compute its k positions and set those bits to 1.
4. **Query** an item: compute its k positions. If **any** bit is 0 it was **definitely never added**. If
   **all** are 1, it is **probably** there.

False positives happen when other items happened to set all of this item's bits. **False negatives never
happen** (as long as you never delete).

## A working implementation

```python
import hashlib

class BloomFilter:
    def __init__(self, size_bits, hashes):
        self.size, self.hashes = size_bits, hashes
        self.bits = bytearray(size_bits)           # one byte per bit for clarity

    def _positions(self, item):
        for i in range(self.hashes):
            digest = hashlib.sha256(f"{i}:{item}".encode()).hexdigest()
            yield int(digest, 16) % self.size

    def add(self, item):
        for p in self._positions(item):
            self.bits[p] = 1

    def might_contain(self, item):
        return all(self.bits[p] for p in self._positions(item))

bf = BloomFilter(size_bits=10_000, hashes=4)
members = [f"user{i}" for i in range(1_000)]
for m in members:
    bf.add(m)

print("added users all found (no false negatives):", all(bf.might_contain(m) for m in members))

strangers = [f"stranger{i}" for i in range(10_000)]
false_positives = sum(bf.might_contain(s) for s in strangers)
print(f"false positives among 10,000 strangers: {false_positives} ({false_positives / 100:.2f}%)")
print("memory used: about", bf.size // 8, "bytes for 1,000 items")
```

**Output:**

```text
added users all found (no false negatives): True
false positives among 10,000 strangers: 134 (1.34%)
memory used: about 1250 bytes for 1,000 items
```

All 1,000 real members were found (never a false negative), and only a small share of strangers were
wrongly reported as "maybe". 1,250 bytes held 1,000 items.

## Tuning: size, hashes and error rate

Given `n` items, `m` bits and `k` hashes, the false-positive rate is about `(1 - e^(-kn/m))^k`. The
best `k` is `(m/n) x ln 2`.

```python
import math

def false_positive_rate(n, m, k):
    return (1 - math.exp(-k * n / m)) ** k

def design(n, target):
    m = math.ceil(-n * math.log(target) / (math.log(2) ** 2))
    k = round(m / n * math.log(2))
    return m, k

for target in (0.01, 0.001):
    m, k = design(1_000_000, target)
    print(f"1M items at {target:.1%} false positives -> {m / 8 / 1024 / 1024:5.2f} MB, {k} hashes")
```

**Output:**

```text
1M items at 1.0% false positives ->  1.14 MB, 7 hashes
1M items at 0.1% false positives ->  1.71 MB, 10 hashes
```

About **10 bits per item gives 1% errors**, and 14 bits give 0.1%: roughly **1 to 2 MB** for a million items,
versus tens of MB for storing the items themselves.

## Where Bloom filters are used

| System | Use |
|---|---|
| **Cassandra, HBase, RocksDB, LevelDB** | Before reading an SSTable file from disk, ask the filter "could this key be in this file?" and skip files that say no |
| **Chrome (historically)** | Check URLs against a list of malicious sites without downloading the whole list |
| **CDNs (Akamai)** | Do not cache one-hit wonders: cache an object only on its second request |
| **Medium / recommendations** | "Have I already shown this article to the user?" |
| **Username / email checks** | Quickly reject names that definitely are not taken |
| **Distributed caches** | Stop **cache penetration**: requests for keys that never exist hit the database every time; the filter blocks them |
| **Databases and joins** | Filter rows before an expensive join |

## Limits and variants

- **No deletion** in the basic form (clearing a bit could remove other items). **Counting Bloom
  filters** keep counters instead of bits and support deletion.
- **Cannot list or count items**, and cannot return a value (it is a set, not a map).
- The filter must be **sized for the expected item count**. Overfill it and false positives soar.
  **Scalable Bloom filters** chain several filters.
- **Cuckoo filters** support deletion and often use less space.
- Related structures: **HyperLogLog** (count distinct items), **Count-Min Sketch** (approximate frequencies).

## Common mistakes

:::{warning}
- Treating "maybe" as "yes". A positive result still needs a real lookup if the answer matters.
- Using it where false positives are unacceptable and there is no backing store to confirm.
- Under-sizing the filter, then watching the error rate climb as items are added.
- Trying to delete from a plain Bloom filter.
:::

## Try it yourself

1. A filter says "no" for a key. What does that tell you with certainty? What if it says "yes"?
2. Why does Cassandra use a Bloom filter for each SSTable?
3. You need to store 10 million emails at a 1% false-positive rate. About how much memory?

<details class="solution"><summary>Answers</summary>

1. "No" means **definitely not present**. "Yes" means **probably present** (verify against the source of truth if it matters).
2. A read might otherwise open many on-disk files. The filter lets Cassandra skip almost every file that cannot contain the key, saving disk reads.
3. About 9.6 bits per item: 10,000,000 x 9.6 / 8 = **about 12 MB** (roughly 7 hashes).

</details>

:::{admonition} Next
:class: important
Bigger picture: how whole database *deployments* are arranged across data centres:
[database architectures](37-database-architectures.md).
:::
