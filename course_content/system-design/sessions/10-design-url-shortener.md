# Chapter 10 · Design a URL shortener (TinyURL)

## The problem

Turn `https://www.example.com/blog/2024/a-very-long-title?utm=42` into `https://tiny.example/aZ3k9Qp`
and redirect anyone who opens the short link. This is the "hello world" of system design because it
touches every building block.

```{raw} html
:file: ../diagrams/shortener.html
```

## Where each earlier chapter shows up

| Question | Answer | Chapter |
|---|---|---|
| What do we build? | Create, redirect, custom alias, expiry | [1](01-interview-framework.md) |
| How big? | 40 writes/s, 4,000 reads/s (10,000 at peak), about 3 TB in 5 years | [2](02-back-of-envelope.md) |
| API and data? | `POST /api/v1/urls`, `GET /{code}`, key-value store keyed by code | [3](03-api-and-data-model.md) |
| Unique short codes? | Counter ranges per server, scrambled, then base62 (7 characters) | [4](04-unique-ids.md) |
| Fast reads? | Cache-aside with LRU, 302 redirect | [5](05-caching.md) |
| Scale and survive? | Shard by hash of code, replicate across zones | [6](06-scaling-data.md) |

## Three ways to make a code (and the winner)

1. **Hash the long URL** and keep 7 characters: collisions need a check on every write.
2. **Random code** and retry on collision: simple, but a lookup per write.
3. **Counter ranges + base62**: no collisions, no lookup. Scramble the number if codes must not be guessable.

## Extra points that impress

- **301 vs 302:** 301 is cached by browsers (less load, no click counting); 302 keeps control.
- **Abuse:** scan for malware, rate-limit creation per user.
- **Expiry:** a lazy check on read plus a background cleaner.

:::{admonition} Try it in the playground
:class: important
Work through the full [TinyURL problem](/system-design/tinyurl/).
:::
