# Chapter 2 · Back-of-envelope estimation

## The big idea

You cannot choose between "one database" and "a hundred shards" without knowing how much work the system must do.
Estimation turns a vague product into **numbers**: requests per second, storage, memory and bandwidth. The numbers do
not have to be exact. They have to be right to within a factor of two or three, because that is enough to pick an
architecture.

**Everyday example:** planning a wedding lunch. You do not need the exact number of rice grains. You need to know
whether you are cooking for 50 or for 5,000, because that decides whether you need one stove or a catering hall.

```{raw} html
:file: ../diagrams/estimation.html
```

## The few facts worth memorising

| Fact | Value |
|---|---|
| Seconds in a day | about 86,400 (call it 100,000 for quick maths) |
| Seconds in a month | about 2.6 million |
| Seconds in a year | about 31.5 million |
| 1 KB, 1 MB, 1 GB, 1 TB, 1 PB | 10^3, 10^6, 10^9, 10^12, 10^15 bytes |
| A character, an integer, a UUID | 1 byte (ASCII), 4 to 8 bytes, 16 bytes |
| Powers of 62 | 62^5 is 0.9 billion, 62^6 is 57 billion, 62^7 is 3.5 trillion |
| Peak versus average traffic | peak is usually 2 to 3 times the average |
| One server | 1,000 to 10,000 simple requests per second; one database primary 1,000 to 10,000 queries per second |

### Typical sizes

| Item | Size |
|---|---|
| A tweet or chat message (text) | 100 to 300 bytes |
| A database row with a few fields | 200 to 1,000 bytes |
| A web page (HTML) | 100 KB |
| A photo (compressed) | 200 KB to 3 MB |
| One minute of HD video | about 50 to 100 MB |

### Latency numbers (order of magnitude)

| Operation | Time |
|---|---|
| Memory read | 100 nanoseconds |
| SSD random read | 100 microseconds |
| Round trip inside a data centre | 0.5 milliseconds |
| Disk seek | 10 milliseconds |
| Round trip between continents | 150 milliseconds |

## The recipe

1. Start from **users or events per day**.
2. Convert to **requests per second**: divide by 86,400. Multiply by 2 to 3 for the **peak**.
3. Split into **reads and writes** with the read:write ratio.
4. **Storage** = records per day x bytes per record x days kept (x replicas).
5. **Bandwidth** = requests per second x bytes per response x 8 (to get bits).
6. **Cache memory** = hot share (often 20%) of one day's data or reads.
7. Say **"so this means ..."** after every number: that sentence is where the points are.

## A reusable estimator

```python
def estimate(daily_events, read_write_ratio, record_bytes, years, response_bytes,
             hot_share=0.2, peak_factor=3, replicas=3):
    writes_per_s = daily_events / 86_400
    reads_per_s = writes_per_s * read_write_ratio
    storage_tb = daily_events * 365 * years * record_bytes * replicas / 1e12
    bandwidth_mbit = (reads_per_s + writes_per_s) * response_bytes * 8 / 1e6
    cache_gb = reads_per_s * 86_400 * hot_share * record_bytes / 1e9
    return {"writes/s": writes_per_s, "reads/s": reads_per_s, "peak reads/s": reads_per_s * peak_factor,
            "storage TB (with replicas)": storage_tb, "bandwidth Mbit/s": bandwidth_mbit, "cache GB": cache_gb}

systems = {
    "URL shortener (3.3M new links/day)": dict(daily_events=3_300_000, read_write_ratio=100, record_bytes=500, years=5, response_bytes=500),
    "Chat app (1B messages/day)": dict(daily_events=1_000_000_000, read_write_ratio=2, record_bytes=200, years=3, response_bytes=300),
    "Photo sharing (10M uploads/day)": dict(daily_events=10_000_000, read_write_ratio=50, record_bytes=1_000_000, years=2, response_bytes=200_000),
}

for name, params in systems.items():
    print(name)
    for label, value in estimate(**params).items():
        print(f"   {label:<28} {value:>16,.1f}")
```

**Output:**

```text
URL shortener (3.3M new links/day)
   writes/s                                 38.2
   reads/s                               3,819.4
   peak reads/s                         11,458.3
   storage TB (with replicas)                9.0
   bandwidth Mbit/s                         15.4
   cache GB                                 33.0
Chat app (1B messages/day)
   writes/s                             11,574.1
   reads/s                              23,148.1
   peak reads/s                         69,444.4
   storage TB (with replicas)              657.0
   bandwidth Mbit/s                         83.3
   cache GB                                 80.0
Photo sharing (10M uploads/day)
   writes/s                                115.7
   reads/s                               5,787.0
   peak reads/s                         17,361.1
   storage TB (with replicas)           21,900.0
   bandwidth Mbit/s                      9,444.4
   cache GB                            100,000.0
```

Read the three profiles: the shortener is **read-heavy and tiny** (a cache solves it); the chat app has **enormous
write volume** (partition and use a write-optimised store); the photo app is dominated by **bytes** (object storage and
a CDN, because 2 PB of photos is a storage and bandwidth problem, not a database problem).

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

## Sanity checks

- **Units:** bits or bytes? MB or GB? A factor of 8 or 1,000 hides here.
- **Compare against known systems:** a single well-tuned database does thousands of queries per second, a good cache
  hundreds of thousands.
- **Cross-check two ways:** estimate storage from users and from events; they should agree within a factor of 3.
- **Ask what dominates:** requests, storage, bandwidth or memory. Design for the dominant one.

## Common mistakes

:::{warning}
- Chasing precision. "About 40" is as good as "38.6".
- Forgetting **peak** traffic, or the **replication factor** in storage.
- Mixing up bits and bytes, or MB and GB.
- Doing the maths and then not using it. Always finish with "so this means...".
:::

## Try it yourself

1. A chat app has 50 million daily users, each sending 40 messages of 150 bytes. How many messages per second, and how much new storage per day?
2. A video site streams 5 million hours a day at 3 Mbit/s. What is the average bandwidth in Gbit/s?
3. A service must handle 30,000 requests per second at peak and one server handles 2,500. How many servers with 30% spare?

<details class="solution"><summary>Answers</summary>

1. 50M x 40 = 2 billion a day, /86,400 = **about 23,000 messages per second**. Storage: 2 billion x 150 B = **300 GB per day**.
2. 5,000,000 hours x 3,600 seconds = 18 billion seconds of video a day; x 3 Mbit/s = 54 billion Mbit; divided by 86,400 seconds is **about 625,000 Mbit/s = 625 Gbit/s** on average.
3. 30,000 / 2,500 = 12; +30% = **16 servers**.

</details>

:::{admonition} Try it in the playground
:class: important
The [TinyURL problem](/system-design/tinyurl/) asks you to work out writes per second, reads per second, storage and
cache size before you design anything.
:::

:::{admonition} Next
:class: important
Numbers tell you what to build. Next, how clients and servers talk: [APIs and data models](03-api-and-data-model.md).
:::
