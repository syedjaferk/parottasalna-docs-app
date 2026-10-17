# Chapter 13 · Design a content delivery network (CDN)

## The problem

Serve images, videos and web files to users all over the world quickly and cheaply, without every
request travelling back to one origin server.

```{raw} html
:file: ../diagrams/cdn.html
```

## Requirements

- **Functional:** cache and serve content from servers near the user; fetch from the origin on a
  miss; let owners purge or expire content.
- **Non-functional:** low latency (tens of ms), very high availability, huge bandwidth.
- **Scale:** say 50 million daily users, each loading 2 MB from the CDN: **100 TB/day, about 10 Gbit/s
  on average**, several times that at peak. No origin can carry that.

## Request flow

1. The user asks DNS for `cdn.example.com`. DNS (latency-based or **anycast**) returns the **nearest
   healthy edge**.
2. The edge looks in its cache. **Hit:** answer. **Miss:** ask the **regional / shield cache**, then
   the **origin**; store the file with a TTL; answer.
3. A shield layer means many edges ask one cache, so the origin sees one request, not hundreds.

## Cache control

- Honour `Cache-Control: max-age`, `ETag` and `Last-Modified`; revalidate with `If-None-Match`.
- **Versioned URLs** (`logo.9fd2.png`) beat purging.
- **Purge API** for emergencies. It must reach all edges in seconds.
- **Eviction:** LRU per edge; keep rarely requested "long tail" files out of small edges.

## Push or pull?

Pull is the default: no setup, fill on demand. Use push to **pre-warm** a big launch (a new episode
at 8pm) so the first viewers do not all miss.

## Video

Split into small segments (HLS/DASH) in several bitrates. Edges cache segments, so a popular video
is served almost entirely from the edge.

## Failure and trade-offs

- An edge dies: DNS/anycast routes users to the next nearest.
- Origin dies: serve **stale** content (`stale-if-error`) while it recovers.
- More edges mean lower latency but lower hit rate each and more cost.
- Private content needs **signed URLs** with expiry.

## Common mistakes

- Caching personalised responses in a shared cache.
- No story for purge or for the origin being overwhelmed on a cold start.
- Not mentioning TLS at the edge.

:::{admonition} Try it in the playground
:class: important
Build it in [Design a CDN](/system-design/cdn/).
:::
