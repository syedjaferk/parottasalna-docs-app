# Chapter 2 · Back-of-envelope estimation

## The big idea

You cannot choose between "one database" and "a hundred shards" without knowing how much work the
system must do. Estimation turns a vague product into **numbers**: requests per second, storage and
memory. The numbers do not have to be exact. They have to be right to within a factor of two or three.

**Everyday example:** planning a wedding lunch. You do not need the exact number of rice grains. You
need to know whether you are cooking for 50 or for 5,000.

## The few facts worth memorising

| Fact | Value |
|---|---|
| Seconds in a day | about 86,400 (call it 100,000 for quick math) |
| Seconds in a month | about 2.6 million |
| 1 KB, 1 MB, 1 GB, 1 TB | 10^3, 10^6, 10^9, 10^12 bytes |
| Powers of 62 | 62^5 is about 0.9 billion, 62^6 is about 57 billion, 62^7 is about 3.5 trillion |
| Peak versus average traffic | peak is usually 2 to 3 times the average |

## The recipe

1. Start from **users or events per day**.
2. Convert to **requests per second**: divide by 86,400. Multiply by 2-3 for peak.
3. Split into **reads and writes** using the read:write ratio.
4. **Storage** = records per year x bytes per record x years.
5. **Cache memory** = hot share of one day's reads x bytes per record.

## Worked example: a URL shortener

Given: 100 million new links a month, 100 reads for every write, 500 bytes per record, kept 5 years.

| Question | Working | Answer |
|---|---|---|
| Writes per second | 100,000,000 / 2,600,000 | about **40/s** |
| Reads per second | 40 x 100 | about **4,000/s** (peak about 10,000/s) |
| Records in 5 years | 100M x 12 x 5 | **6 billion** |
| Storage | 6 billion x 500 B | about **3 TB** |
| Cache for the hot 20% of a day | 4,000 x 86,400 x 20% x 500 B | about **35 GB** |

What the numbers tell us:

- **40 writes/s is small.** Writes will not force a complicated design.
- **4,000 to 10,000 reads/s** is where a single database starts to struggle: use a **cache**.
- **3 TB** is a lot for one machine: plan to **partition** the data.
- **35 GB** fits in memory, so caching the hot links is cheap.

## Common mistakes

- Chasing precision. "About 40" is as good as "38.6".
- Forgetting **peak** traffic.
- Mixing up bits and bytes, or MB and GB.
- Doing the math and then not using it. Always finish with "so this means...".

:::{admonition} Try it in the playground
:class: important
The [TinyURL problem](/system-design/tinyurl/) asks you to work out writes per second, reads per second,
storage and cache size before you design anything.
:::
