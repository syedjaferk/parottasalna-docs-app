# Chapter 74 · Design a content delivery network (CDN)

## Concepts to review first

This design is built from earlier chapters. Skim them if any term feels new:

- [CDN](43-cdn.md)
- [DNS](17-dns.md)
- [Caching strategies](40-caching-strategies.md)
- [Cache eviction policies](41-eviction-policies.md)
- [HTTP and HTTPS](19-http-and-https.md)
- [Latency, throughput and bandwidth](10-latency-throughput-and-bandwidth.md)

## The problem

Serve images, scripts and video to users around the world with low latency, so most requests never travel to the
customer's own servers (the **origin**). Think of Cloudflare, Akamai or CloudFront.

```{raw} html
:file: ../diagrams/cdn.html
```

## Step 1: clarify requirements

**Functional:** serve content from a server **near the user** (an **edge**); on a miss, fetch from the origin and keep a
copy; let owners **expire or purge** content; support private content with **signed URLs**.

**Non-functional:** latency of tens of milliseconds; very high availability (an edge failure must be invisible); huge
bandwidth; a very **high cache hit rate** so the origin stays calm.

**Out of scope:** video transcoding, billing, analytics dashboards, edge compute.

## Step 2: estimate and find the target hit rate

```python
daily_users, mb_per_user = 50_000_000, 2
peak_factor = 3
origin_capacity_gbit = 1.0                      # what one customer's origin can serve

total_tb_per_day = daily_users * mb_per_user / 1e6
avg_gbit = total_tb_per_day * 1e6 * 8 / 86_400 / 1000
peak_gbit = avg_gbit * peak_factor
needed_hit_rate = 1 - origin_capacity_gbit / peak_gbit

print(f"traffic            : {total_tb_per_day:.0f} TB per day")
print(f"average bandwidth  : {avg_gbit:.1f} Gbit/s")
print(f"peak bandwidth     : {peak_gbit:.1f} Gbit/s")
print(f"origin can serve   : {origin_capacity_gbit} Gbit/s")
print(f"required hit rate  : at least {needed_hit_rate:.1%}")
```

**Output:**

```text
traffic            : 100 TB per day
average bandwidth  : 9.3 Gbit/s
peak bandwidth     : 27.8 Gbit/s
origin can serve   : 1.0 Gbit/s
required hit rate  : at least 96.4%
```

**One origin cannot serve 28 Gbit/s**, so a CDN is not an optimisation, it is a necessity. And the origin can only
survive if about **96.4% or more of requests are answered at the edge**. That single number drives the design: long
TTLs, versioned file names, a shield cache and pre-warming.

## Step 3: routing a user to the nearest edge

1. The user looks up `cdn.example.com`. A **geo/latency-aware DNS** (or **anycast**, where every edge announces the same
   IP and the network delivers the packet to the nearest one) returns a **nearby, healthy** edge.
2. DNS TTLs are short (30 to 60 seconds) so users can be moved when an edge fails.
3. The edge terminates TLS close to the user, saving round trips.

## Step 4: the cache key and a cache that actually hits

The **cache key** decides when two requests count as "the same". Poor keys destroy the hit rate:

```python
from urllib.parse import urlsplit, parse_qsl, urlencode

IGNORE = {"utm_source", "utm_medium", "utm_campaign", "fbclid", "gclid"}

def cache_key(url):
    parts = urlsplit(url)
    query = sorted((k, v) for k, v in parse_qsl(parts.query) if k not in IGNORE)   # drop tracking, normalise order
    return f"{parts.netloc.lower()}{parts.path}?{urlencode(query)}"

urls = [
    "https://cdn.example.com/img/logo.png?utm_source=mail",
    "https://cdn.example.com/img/logo.png?fbclid=XYZ",
    "https://CDN.example.com/img/logo.png",
    "https://cdn.example.com/img/photo.jpg?w=200&h=100",
    "https://cdn.example.com/img/photo.jpg?h=100&w=200",
]
keys = [cache_key(u) for u in urls]
for u, k in zip(urls, keys):
    print(f"{k:<45} <- {u}")
print("\ndistinct cache entries:", len(set(keys)), "instead of", len(urls))
```

**Output:**

```text
cdn.example.com/img/logo.png?                 <- https://cdn.example.com/img/logo.png?utm_source=mail
cdn.example.com/img/logo.png?                 <- https://cdn.example.com/img/logo.png?fbclid=XYZ
cdn.example.com/img/logo.png?                 <- https://CDN.example.com/img/logo.png
cdn.example.com/img/photo.jpg?h=100&w=200     <- https://cdn.example.com/img/photo.jpg?w=200&h=100
cdn.example.com/img/photo.jpg?h=100&w=200     <- https://cdn.example.com/img/photo.jpg?h=100&w=200

distinct cache entries: 2 instead of 5
```

Five different-looking URLs collapse into **two** cache entries. Also respect `Vary` carefully: varying on
`Accept-Language` or `Cookie` multiplies entries and kills the hit rate.

## Step 5: two tiers, TTLs and request coalescing

Hundreds of edges all missing on the same new file would hit the origin hundreds of times. A **shield (regional)
cache** sits between the edges and the origin so the origin sees **one** request per file:

```python
import random
random.seed(11)

class Cache:
    def __init__(self, name, capacity):
        self.name, self.capacity, self.items, self.hits, self.misses = name, capacity, {}, 0, 0
    def get(self, key):
        if key in self.items:
            self.hits += 1
            self.items[key] = self.items.pop(key)             # mark as recently used
            return True
        self.misses += 1
        return False
    def put(self, key):
        if len(self.items) >= self.capacity:
            self.items.pop(next(iter(self.items)))             # evict the least recently used
        self.items[key] = True

files = [f"file{i}" for i in range(2000)]
weights = [1 / (rank + 1) for rank in range(len(files))]     # Zipf-like: a few files are very popular

def run(use_shield, edges=20, requests=60_000):
    edge_caches = [Cache(f"edge{i}", 150) for i in range(edges)]
    shield, origin_hits = Cache("shield", 600), 0
    for _ in range(requests):
        f = random.choices(files, weights)[0]
        edge = random.choice(edge_caches)
        if edge.get(f):
            continue
        edge.put(f)
        if use_shield:
            if shield.get(f):
                continue
            shield.put(f)
        origin_hits += 1
    return origin_hits, requests

for shield in (False, True):
    origin, total = run(shield)
    label = "edge + shield" if shield else "edges only  "
    print(f"{label}: origin saw {origin:>6,} of {total:,} requests = {origin / total:.1%}")
```

**Output:**

```text
edges only  : origin saw 26,473 of 60,000 requests = 44.1%
edge + shield: origin saw 12,688 of 60,000 requests = 21.1%
```

The shield absorbs misses that several edges would otherwise send separately. Also use **request coalescing**: if 1,000
users ask for the same uncached file at the same instant, the edge sends **one** request to the origin and serves all
1,000 from the answer.

**Freshness controls**

- Honour `Cache-Control: max-age`, `s-maxage` and `ETag` / `If-None-Match` (a `304` costs almost nothing).
- **Version your file names** (`app.3f9a.js`) and cache them for a year. A change is a new URL, so there is nothing to purge.
- Offer a **purge API** for emergencies; it must reach every edge within seconds.
- **Serve stale content** (`stale-while-revalidate`, `stale-if-error`) while the origin refreshes or is down.
- **Pre-warm** known hits (a launch at 8 pm) by fetching them into the edges beforehand.

## Step 6: private content with signed URLs

Paid videos must not be cached for anyone who knows the URL. The origin signs a link with an **expiry**; the edge
**verifies the signature locally**, with no call to any server:

```python
import hmac, hashlib, time

SECRET = b"cdn-signing-secret"

def sign(path, expires_at):
    digest = hmac.new(SECRET, f"{path}:{expires_at}".encode(), hashlib.sha256).hexdigest()[:16]
    return f"{path}?expires={expires_at}&sig={digest}"

def edge_check(url, now):
    path, query = url.split("?", 1)
    params = dict(p.split("=") for p in query.split("&"))
    expected = hmac.new(SECRET, f"{path}:{params['expires']}".encode(), hashlib.sha256).hexdigest()[:16]
    if not hmac.compare_digest(expected, params["sig"]):
        return "403 bad signature"
    if now > int(params["expires"]):
        return "403 expired"
    return "200 serve from cache"

now = 1_700_000_000
url = sign("/videos/premium/ep1.mp4", now + 3600)
print("fresh link   :", edge_check(url, now))
print("after expiry :", edge_check(url, now + 7200))
print("tampered path:", edge_check(url.replace("ep1", "ep2"), now))
```

**Output:**

```text
fresh link   : 200 serve from cache
after expiry : 403 expired
tampered path: 403 bad signature
```

## Step 7: failures and trade-offs

| Failure | What happens |
|---|---|
| An edge dies | DNS or anycast routes users to the next nearest edge; the hit rate dips, service continues |
| Origin down | Serve stale content (`stale-if-error`); the shield and edges keep answering |
| Origin overloaded by a cold start | Pre-warm, coalesce requests, rate-limit origin fetches |
| Cache poisoning (a bad response cached) | Strict cache keys; never cache `Set-Cookie` responses; purge quickly |
| DDoS | The edge network absorbs it; rate limiting and bot filtering at the edge |

| Choice | You gain | You pay |
|---|---|---|
| Long TTLs | High hit rate, low origin load | Stale content unless versioned or purged |
| Shield cache | One origin fetch per file | An extra hop on a miss |
| More edges | Lower latency everywhere | Lower hit rate per edge, more cost |
| Signed URLs | Private content cached safely | Short expiries mean refreshing links |

## Common mistakes

:::{warning}
- Caching personalised or authenticated responses at the edge (one user sees another's data).
- Reusing file names with long TTLs, then needing emergency purges.
- A cache key polluted by tracking parameters or cookies.
- No plan for a launch spike hitting the origin all at once.
:::

## Try it yourself

1. The origin can serve 2 Gbit/s and peak traffic is 40 Gbit/s. What hit rate is needed?
2. Why is a hash in the file name better than a purge?
3. How does the edge verify a signed URL without contacting the origin?

<details class="solution"><summary>Answers</summary>

1. 1 - 2/40 = **95%** at least.
2. A new name is a new URL, so old and new versions coexist and nothing needs invalidating. Purges are slow, can fail on some edges and race with clients.
3. It recomputes the HMAC of the path and expiry with the shared secret and compares it with the signature, then checks the expiry time, all locally.

</details>

:::{admonition} Try it in the playground
:class: important
Build it in [Design a CDN](/system-design/cdn/).
:::

:::{admonition} Next
:class: important
Next case study: [Design a parking garage](75-design-parking-garage.md).
:::
