# Chapter 10 · Latency, throughput and bandwidth

## The big idea

Three words people mix up:

- **Latency**: how long **one** thing takes (milliseconds).
- **Throughput**: how many things finish **per second**.
- **Bandwidth**: the **maximum** the pipe can carry (bits per second).

**Everyday example:** a water pipe. **Bandwidth** is the pipe's width. **Latency** is how long a
single drop takes to travel from the tap to the glass. **Throughput** is how much water actually
arrives per minute. A wide pipe can still be slow if it is very long (high latency), and a short pipe
can be narrow (low bandwidth).

A highway is the same: bandwidth is the number of lanes, latency is the travel time for one car,
throughput is how many cars pass a point per hour.

```{raw} html
:file: ../diagrams/latency-throughput-bandwidth.html
```

## They are linked: Little's Law

```text
concurrent requests in the system  =  throughput  x  latency
```

This is the most useful formula in the chapter. If your service takes **200 ms** per request and gets
**500 requests per second**, then on average **100 requests are in flight at once**
(500 x 0.2). If each server thread handles one request at a time, you need **100 threads** (across all
servers) or requests queue up.

```python
def in_flight(rps, latency_s):
    return rps * latency_s

def threads_needed(rps, latency_s, utilisation=0.7):
    return in_flight(rps, latency_s) / utilisation

for latency_ms in (50, 200, 1000):
    n = in_flight(500, latency_ms / 1000)
    t = threads_needed(500, latency_ms / 1000)
    print(f"{latency_ms:>5} ms latency at 500 rps -> {n:>5.0f} in flight, ~{t:>4.0f} threads at 70% load")
```

**Output:**

```text
   50 ms latency at 500 rps ->    25 in flight, ~  36 threads at 70% load
  200 ms latency at 500 rps ->   100 in flight, ~ 143 threads at 70% load
 1000 ms latency at 500 rps ->   500 in flight, ~ 714 threads at 70% load
```

When a dependency gets slow (50 ms becomes 1 s), the number of threads you need grows **20 times**,
and the service falls over even though traffic did not change. That is how a slow database becomes
an outage.

## Latency numbers worth remembering

Order of magnitude is what matters:

| Operation | Time | Feels like |
|---|---|---|
| CPU cache read | 1 ns | |
| RAM read | 100 ns | |
| SSD random read | 100 microseconds | |
| Same data centre round trip | 0.5 ms | |
| Redis or Memcached get (network) | 0.5 to 1 ms | |
| Database query (indexed) | 1 to 10 ms | |
| Disk (spinning) seek | 10 ms | |
| Same-continent round trip | 30 to 80 ms | |
| Cross-ocean round trip | 150 to 250 ms | **Light in fibre cannot go faster** |

Lessons you can use: memory is about 1,000 times faster than SSD; one cross-ocean call costs more
than 300 in-data-centre calls; **calls over the network, not computation, usually dominate**. This is
why caches, CDNs and keeping services in one region matter.

## Averages lie: percentiles

If 99 requests take 100 ms and 1 takes 10 seconds, the **average** is about 200 ms, which looks fine.
But 1 user in 100 waited 10 seconds. Look at **percentiles**:

- **p50** (median): half of requests are faster.
- **p95, p99**: the slow tail. Real users hit the tail often.

```python
import random
random.seed(3)

# 98% normal requests around 100 ms, 2% slow (a cache miss or a GC pause) around 2 s
samples = [random.gauss(100, 15) for _ in range(9800)] + [random.gauss(2000, 300) for _ in range(200)]
samples.sort()

def pct(p):
    return samples[int(len(samples) * p / 100) - 1]

print(f"average: {sum(samples) / len(samples):6.0f} ms")
print(f"p50    : {pct(50):6.0f} ms")
print(f"p95    : {pct(95):6.0f} ms")
print(f"p99    : {pct(99):6.0f} ms")
```

**Output:**

```text
average:    137 ms
p50    :    100 ms
p95    :    128 ms
p99    :   1956 ms
```

The average hides the 2-second tail completely. Always quote **p99** (or p99.9) in an interview.

### Tail latency amplification

A page that calls **20 services in parallel** is only as fast as the **slowest** one. If each service
is slow 1% of the time, the chance that *at least one* is slow is `1 - 0.99^20` = **18%**. So fan-out
turns a rare problem into a common one. Defences: timeouts, **hedged requests** (send a second copy
after a short wait), caching, and fewer dependencies.

## Throughput and bandwidth in practice

Bandwidth is measured in **bits**; file sizes in **bytes**. Multiply bytes by 8.

```python
def transfer_seconds(size_mb, bandwidth_mbit):
    return size_mb * 8 / bandwidth_mbit

print(f"2 MB image on a 20 Mbit/s phone link : {transfer_seconds(2, 20):.2f} s")
print(f"2 MB image on a 1 Gbit/s server link : {transfer_seconds(2, 1000) * 1000:.0f} ms")
print(f"100 TB a day needs {100e6 * 8 / 86_400 / 1000:.1f} Gbit/s on average")
```

**Output:**

```text
2 MB image on a 20 Mbit/s phone link : 0.80 s
2 MB image on a 1 Gbit/s server link : 16 ms
100 TB a day needs 9.3 Gbit/s on average
```

That last line is how you size a CDN or an egress bill: **total bytes x 8 / seconds**.

## Trading latency against throughput

You often cannot improve both at once:

| Technique | Throughput | Latency |
|---|---|---|
| **Batching** (write 100 rows at once) | Much higher | Each item waits for the batch |
| **Caching** | Higher | Lower |
| **Compression** | Saves bandwidth | Adds CPU time |
| **Queues** | Smooth bursts | Adds waiting time |
| **More parallelism** | Higher | Unchanged (or worse under contention) |

A good target is **high throughput with *acceptable* latency**, not the lowest latency at any cost.

## Common mistakes

:::{warning}
- Quoting only the **average** latency.
- Confusing **Mbps** (bits) with **MBps** (bytes): a factor of 8.
- Adding servers to fix a latency problem caused by a slow **dependency** or by distance.
- Forgetting that **retries** add load exactly when the system is already slow.
:::

## Try it yourself

1. A service handles 800 requests per second with a 250 ms average latency. How many requests are in flight on average?
2. You must deliver a 500 MB file to users on 50 Mbit/s links. How long does it take, at best?
3. A page waits for 10 parallel calls. Each is slow 2% of the time. How often is the page slow?

<details class="solution"><summary>Answers</summary>

1. 800 x 0.25 = **200** in flight.
2. 500 x 8 / 50 = **80 seconds**.
3. 1 - 0.98^10 = **18%** of page loads.

</details>

:::{admonition} Next
:class: important
To spread data across machines without reshuffling everything when machines come and go, the key
trick is [consistent hashing](11-consistent-hashing.md).
:::
