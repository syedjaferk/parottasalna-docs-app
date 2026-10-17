# Chapter 71 · Design a URL shortener (TinyURL)

## Concepts to review first

This design is built from earlier chapters. Skim them if any term feels new:

- [Generating unique short IDs](38-unique-ids.md)
- [Consistent hashing](11-consistent-hashing.md)
- [Caching strategies](40-caching-strategies.md)
- [Database sharding](32-sharding.md)
- [Data replication](33-replication.md)
- [HTTP and HTTPS](19-http-and-https.md)
- [Rate limiting](28-rate-limiting.md)

## The problem

A user pastes a long link and gets back a short one:

```text
https://www.example.com/blog/2024/a-very-long-article-title?utm_source=newsletter&ref=42
                     becomes
https://tiny.example/aZ3k9Qp
```

Anyone who opens the short link is sent to the original page. This is the "hello world" of system design because
it touches ID generation, caching, storage, scaling and failure handling, all with small, clear numbers.

```{raw} html
:file: ../diagrams/shortener.html
```

## Step 1: clarify requirements

**Functional (in scope):** create a short link from a long URL; redirect a short link to the long URL; optional
custom alias (`tiny.example/my-sale`); optional expiry date; a click count is enough for analytics.

**Not in scope (say it out loud):** user accounts and billing, analytics dashboards, spam-detection internals.

**Non-functional:**

| Requirement | Target | Why |
|---|---|---|
| Redirect latency | Under 100 ms at p99 | Users are waiting on a click |
| Availability | 99.99% for redirects | A dead link is a broken web page somewhere |
| Durability | Never lose a mapping | A lost link cannot be recreated |
| Unpredictable codes | Not guessable | Private documents are shared by short link |
| Consistency | Eventual is fine for reads | A new link may take a moment to appear everywhere |

## Step 2: estimate the load

Given: **100 million new links a month**, **100 redirects for every link created**, links kept **5 years**, about
**500 bytes** per record.

```python
SECONDS_PER_MONTH = 30 * 24 * 3600

new_links_per_month = 100_000_000
read_write_ratio = 100
years = 5
record_bytes = 500

writes_per_s = new_links_per_month / SECONDS_PER_MONTH
reads_per_s = writes_per_s * read_write_ratio
peak_reads = reads_per_s * 3

records = new_links_per_month * 12 * years
storage_tb = records * record_bytes / 1e12

# cache the hottest 20% of one day's redirects
daily_reads = reads_per_s * 86_400
cache_gb = daily_reads * 0.20 * record_bytes / 1e9

print(f"writes        : {writes_per_s:,.0f} per second")
print(f"reads         : {reads_per_s:,.0f} per second average, {peak_reads:,.0f} at peak")
print(f"records       : {records / 1e9:.1f} billion in {years} years")
print(f"storage       : {storage_tb:.1f} TB")
print(f"cache for 20% : {cache_gb:.0f} GB")
```

**Output:**

```text
writes        : 39 per second
reads         : 3,858 per second average, 11,574 at peak
records       : 6.0 billion in 5 years
storage       : 3.0 TB
cache for 20% : 33 GB
```

What the numbers tell us:

- **40 writes per second** is tiny: one ordinary database handles it. Writes will not force a complicated design.
- **4,000 reads per second (10,000 at peak)** and a 100:1 ratio: this is a **read-heavy** problem. Optimise the
  redirect path.
- **3 TB** fits on a handful of machines but is too much to want on one primary forever, so plan to partition.
- **About 33 GB** of hot data fits in the memory of a small cache cluster.

## Step 3: how long should the code be?

We need to name about **6 billion** links without ever repeating a name. Use the 62 characters `a-z A-Z 0-9` (**base62**).

```python
for length in range(5, 9):
    print(f"{length} characters -> {62 ** length:>20,} codes")
print()
print("links needed in 5 years:", f"{100_000_000 * 12 * 5:,}")
```

**Output:**

```text
5 characters ->          916,132,832 codes
6 characters ->       56,800,235,584 codes
7 characters ->    3,521,614,606,208 codes
8 characters ->  218,340,105,584,896 codes

links needed in 5 years: 6,000,000,000
```

6 characters give 56.8 billion codes (enough for 6 billion with room to spare) and **7 characters give 3.5 trillion**,
which leaves the code space mostly empty. That sparseness matters for security: if only 0.2% of codes exist, a guess
almost never hits a real link. **Choose 7 characters.**

## Step 4: API and data model

```text
POST   /api/v1/urls
       body: {"long_url": "https://...", "custom_alias": "my-sale", "expires_at": "2026-01-01T00:00:00Z"}
       -> 201 Created   {"short_url": "https://tiny.example/aZ3k9Qp", "expires_at": "..."}
       -> 409 Conflict  if the alias is taken        -> 400 if the URL is not valid or is blocked

GET    /{code}            -> 302 Found, Location: <long_url>      (or 404 / 410 Gone if expired)
DELETE /api/v1/urls/{code} -> 204 No Content                      (owner only)
```

The only query we ever need is **"given a code, find the URL"**. That is a perfect **key-value** access pattern:

```sql
-- the logical schema (works in SQL or as the value of a key-value store)
CREATE TABLE urls (
  short_code  VARCHAR(10) PRIMARY KEY,      -- the key we look up by
  long_url    TEXT        NOT NULL,
  created_at  TIMESTAMP   NOT NULL,
  expires_at  TIMESTAMP,                    -- NULL = never
  owner_id    BIGINT                        -- optional
);
```

Choice of store: a **key-value / wide-column** store (DynamoDB, Cassandra) scales horizontally for this pattern. A
sharded PostgreSQL also works and is fine at our numbers. Say which, and why.

## Step 5: the hard part, generating unique codes

Three approaches, and why one wins:

| Approach | How | Problem |
|---|---|---|
| **Hash the long URL** | `md5(url)`, keep the first 7 base62 characters | **Collisions**: different URLs map to the same code, so every write needs a lookup and a retry |
| **Random code** | Pick 7 random characters, retry if taken | A database lookup on every write, and collisions grow as the table fills |
| **Counter + base62** | Take the next number, convert to base62 | **No collisions**. But sequential codes are guessable |

### Counter ranges, scrambled

1. A small **coordinator** (a database row, ZooKeeper or etcd) hands each app server a **block of numbers**
   (server A takes 1,000,000 to 1,999,999, server B takes 2,000,000 to 2,999,999). The server uses its block with
   **no further coordination**, so the coordinator is almost never on the hot path.
2. Each number is passed through a **reversible scramble** so neighbouring numbers look unrelated (and are
   therefore unguessable), then converted to base62.

```python
ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
SPACE = 62 ** 7                      # 3.5 trillion codes
K = 2_654_435_761                    # odd and not a multiple of 31, so it shares no factor with 62^7

def scramble(n):
    return (n * K) % SPACE           # a bijection: different n always give different results

def to_base62(n):
    out = []
    for _ in range(7):               # always exactly 7 characters
        n, r = divmod(n, 62)
        out.append(ALPHABET[r])
    return "".join(reversed(out))

sequential = [1_000_000 + i for i in range(5)]
print("plain counter :", [to_base62(n) for n in sequential])
print("scrambled     :", [to_base62(scramble(n)) for n in sequential])

codes = {to_base62(scramble(n)) for n in range(2_000_000, 2_200_000)}
print("200,000 consecutive ids -> unique codes:", len(codes))
```

**Output:**

```text
plain counter : ['0004c92', '0004c93', '0004c94', '0004c95', '0004c96']
scrambled     : ['KPt1G92', 'KSmFq93', 'KVgja94', 'KY9WU95', 'L13AE96']
200,000 consecutive ids -> unique codes: 200000
```

The plain counter produces `0004c92`, `0004c93`, ... a stranger can **enumerate every link**. The scrambled version
looks random yet **never repeats**, because multiplying by a number coprime with the space is a one-to-one mapping.
Custom aliases are different: check for a clash with an atomic conditional write (`INSERT ... IF NOT EXISTS`) and return
`409`.

## Step 6: the redirect path

```text
1. Browser:  GET https://tiny.example/aZ3k9Qp
2. DNS + load balancer send it to any stateless app server
3. App server: look up "aZ3k9Qp" in the CACHE (Redis)
      hit  -> answer immediately
      miss -> read the key-value store, put the result in the cache, answer
4. If expires_at is in the past -> 410 Gone.  Otherwise: HTTP 302 with Location: <long_url>
```

### 301 or 302?

| | 301 Moved Permanently | 302 Found |
|---|---|---|
| Browser caches the redirect | **Yes** (later clicks never reach us) | No (every click reaches us) |
| Server load | Lower | Higher |
| Click counting, expiry, edits | **Broken** after the first visit | Work |

Because we want **click counts, expiry and the ability to edit or delete a link**, choose **302**. The cost is more
traffic to the cache, which we sized for.

### Cache design

**Cache-aside** with **LRU** eviction, a **TTL no longer than the link's expiry**, and a **delete on update or delete**
so nobody is served stale data. Aim for a hit rate above 90%: at 4,000 reads per second that means fewer than 400
reads per second reach the database.

## Step 7: scale and survive

| Layer | Scale | Failure handling |
|---|---|---|
| **App servers** | Stateless, many, behind a load balancer | Lose one, the rest carry on (size for N+1) |
| **Cache** | Redis cluster, consistent hashing on the code | Replicas; on a node loss only that node's keys miss |
| **Database** | Shard by `hash(short_code)` with consistent hashing, **3 replicas across zones** | Automatic failover; backups with tested restores |
| **ID coordinator** | 3 or 5 nodes with consensus (etcd) | If it is briefly down, servers keep using their current blocks |

**When the cache dies:** every request falls to the database (a stampede). Protect it with request coalescing (one
request refills a key while others wait), a rate limit on the database path, and a warm replacement node.

**Abuse:** rate limit link creation per user and per IP; scan new URLs against a malware blocklist; block redirect
loops (a short link pointing to a short link).

## Step 8: trade-offs to say out loud

| Choice | You gain | You pay |
|---|---|---|
| 302 instead of 301 | Click counts, expiry and edits keep working | More traffic reaches your servers |
| Key-value store | Simple scaling, fast lookups | No flexible queries or joins |
| Counter ranges + scramble | No collisions, no per-write lookup | A coordinator to run; wasted numbers if a server crashes |
| Eventual consistency | Fast, always available | A new link may be briefly unavailable in another region |

## Common mistakes

:::{warning}
- Hashing the URL and ignoring collisions.
- Sequential codes that let strangers list every private link.
- Choosing 301 and then wondering why click counts are wrong.
- Sharding on day one without the numbers to justify it.
- No plan for a cold or failed cache.
:::

## Try it yourself

1. With 8-character codes, how many codes exist? Is 8 better than 7 for this product?
2. Why must the cache TTL never exceed a link's expiry?
3. Two app servers get the same block of ids by a bug. What happens, and how would you notice?

<details class="solution"><summary>Answers</summary>

1. 62^8 = about 218 trillion. It is overkill: 7 characters already give 3.5 trillion codes for 6 billion links, and shorter links are nicer to share.
2. Otherwise the cache could keep serving a link after it expired, when the correct answer is `410 Gone`.
3. They would generate identical codes: the second write to a code that exists would be rejected or would overwrite another user's link. Use unique constraints on `short_code` (writes fail loudly) and monitor for duplicate-key errors.

</details>

:::{admonition} Try it in the playground
:class: important
Work through the full [TinyURL problem](/system-design/tinyurl/): 16 guided steps, with numbers, trade-offs and a scorecard.
:::

:::{admonition} Next
:class: important
Next case study: [Design autocomplete for search](72-design-autocomplete.md).
:::
