# Chapter 43 · Content Delivery Network (CDN)

## The big idea

A **CDN** is a **worldwide network of cache servers** that keep copies of your files **close to your
users**, so a visitor in Chennai gets the image from a server in Chennai instead of one in Virginia.

**Everyday example:** a newspaper printed in one city and flown to every reader would arrive late. Instead,
the paper is printed at **regional presses** and delivered by local vans. Readers get it in minutes. The
regional presses are the CDN's **edge servers**; the original press is the **origin**.

```{raw} html
:file: ../diagrams/cdn.html
```

## The problem: distance is latency

Light in fibre travels about 200,000 km/s. A round trip between Chennai and a US data centre takes at
least **200 ms** before any server work, and a page loads dozens of files, many sequentially. No server
tuning can fix physics. The only fix is to **move the data closer**.

```python
def one_way_ms(km, speed_km_s=200_000):
    return km / speed_km_s * 1000

routes = {"Chennai -> Chennai edge (20 km)": 20, "Chennai -> Singapore (3,300 km)": 3_300,
          "Chennai -> Frankfurt (7,300 km)": 7_300, "Chennai -> Virginia (13,500 km)": 13_500}
for name, km in routes.items():
    rtt = 2 * one_way_ms(km)
    print(f"{name:<34} best-case round trip: {rtt:6.1f} ms   (10 sequential files: {10 * rtt:7.0f} ms)")
```

**Output:**

```text
Chennai -> Chennai edge (20 km)    best-case round trip:    0.2 ms   (10 sequential files:       2 ms)
Chennai -> Singapore (3,300 km)    best-case round trip:   33.0 ms   (10 sequential files:     330 ms)
Chennai -> Frankfurt (7,300 km)    best-case round trip:   73.0 ms   (10 sequential files:     730 ms)
Chennai -> Virginia (13,500 km)    best-case round trip:  135.0 ms   (10 sequential files:    1350 ms)
```

This is the **theoretical minimum**. Real latency is higher, which is why nearby edges matter so much.

## How a request flows

1. The browser asks DNS for `cdn.example.com`. DNS (geo/latency based) or **anycast** returns the nearest
   **edge**.
2. The edge looks in its cache.
   - **Hit:** answer immediately.
   - **Miss:** ask the **origin** (often through a **regional/shield cache**), return the file to the user
     and **keep a copy** for the next visitor.
3. Edge keeps the copy until its **TTL** expires, then revalidates.

## What a CDN does for you

- **Latency:** content from a nearby city.
- **Origin offload:** the origin sees only misses. A 97% hit rate means 3% of the traffic.
- **Bandwidth cost and capacity:** the CDN absorbs traffic spikes no single server could.
- **Availability:** serve stale content if the origin is down; many edges, no SPOF.
- **Security:** TLS termination near the user, **DDoS absorption**, WAF, bot filtering.
- **Optimisation:** compression, image resizing, HTTP/2 and HTTP/3, TLS session reuse.

## Push CDN vs pull CDN

| | **Pull** (origin pull) | **Push** |
|---|---|---|
| Who fills the edge | Edge fetches from origin on the first request | You upload files to the CDN ahead of time |
| Setup | Nearly none (point at your origin) | Upload and manage content |
| First request | Slower (miss) | Fast (already there) |
| Storage use | Only what is requested | Everything you push, even if unused |
| Best for | Websites, many files, unpredictable demand | Big known launches, software releases, video libraries |

Combine them: **pull by default, pre-warm (push) known hits** before a launch.

## Controlling freshness

- `Cache-Control: public, max-age=31536000, immutable` for **versioned** files (`app.3f9a.js`): cached a year.
- `Cache-Control: no-store` for private data; `private` for per-user pages (not shared caches).
- `ETag` / `If-None-Match` to revalidate cheaply (304 with no body).
- **Purge/invalidate API:** emergency removal; propagates in seconds.
- **Best practice:** **version your file names** (hash in the name) so you never purge. New content, new URL.

```python
import hashlib

def versioned_name(filename, content):
    digest = hashlib.sha256(content).hexdigest()[:8]
    stem, dot, ext = filename.rpartition(".")
    return f"{stem}.{digest}.{ext}"

print(versioned_name("app.js", b"console.log('v1')"))
print(versioned_name("app.js", b"console.log('v2')"))        # new content -> new URL -> no purge needed
```

**Output:**

```text
app.fc787e30.js
app.a23d0f93.js
```

## Sizing the benefit

```python
daily_users, mb_per_user = 50_000_000, 2
total_tb = daily_users * mb_per_user / 1e6
avg_gbit = total_tb * 1e6 * 8 / 86_400 / 1000
print(f"traffic: {total_tb:.0f} TB/day = {avg_gbit:.1f} Gbit/s average")

origin_capacity_gbit = 1
peak_gbit = avg_gbit * 3
needed_hit_rate = 1 - origin_capacity_gbit / peak_gbit
print(f"origin can serve {origin_capacity_gbit} Gbit/s; peak is {peak_gbit:.0f} Gbit/s -> hit rate must be at least {needed_hit_rate:.1%}")
```

**Output:**

```text
traffic: 100 TB/day = 9.3 Gbit/s average
origin can serve 1 Gbit/s; peak is 28 Gbit/s -> hit rate must be at least 96.4%
```

## Dynamic content, streaming, and security

- **Dynamic and API traffic** can use the CDN too (TLS termination, connection reuse over the CDN's fast
  backbone, short TTL caching, edge compute/workers).
- **Video:** split into small segments (HLS/DASH) in several bitrates; edges cache segments, so a popular video
  is served almost entirely from the edge.
- **Private content:** **signed URLs or cookies** with an expiry that the edge verifies, with no call to your server.
- **Request coalescing:** if 1,000 users ask for an uncached file at once, the edge sends **one** request
  to the origin.

## Trade-offs

- **Staleness:** content can be out of date until the TTL or a purge.
- **Cost:** per GB transferred and per request; usually cheaper than serving it yourself.
- **Complexity:** cache keys, headers, purging, debugging "which version did the user get?".
- **Cache pollution:** accidentally caching personalised pages in a shared cache.
- **Vendor dependence:** a CDN outage can take your site down; consider a multi-CDN setup for critical sites.

## Common mistakes

:::{warning}
- Caching personalised or authenticated responses at the edge (one user sees another's data).
- Reusing file names with long TTLs and then needing urgent purges.
- No plan for a cold start of a big launch (the origin is crushed by simultaneous misses).
- Forgetting that the origin must still handle all cache misses at peak.
:::

## Try it yourself

1. Why is a hash in the file name better than purging the CDN?
2. A launch is expected at 8 pm with millions of users and an uncached video. What do you do beforehand?
3. Why can CDNs make even dynamic, uncacheable API calls faster?

<details class="solution"><summary>Answers</summary>

1. A new name is a new URL, so there is nothing to invalidate; old and new versions coexist and every client gets a consistent set. Purging is slow, racy and can fail on some edges.
2. **Pre-warm** the popular files onto the edges (push or scripted requests) and enable **request coalescing** so simultaneous first requests reach the origin once.
3. The user terminates TLS and the TCP handshake at a nearby edge, and the edge reuses warm, persistent connections over a fast private backbone to the origin, removing several long round trips.

</details>

:::{admonition} Next
:class: important
Caching is done. Now work that should not make the user wait: [message queues](44-message-queues.md) and
[publish/subscribe](45-pub-sub.md).
:::
