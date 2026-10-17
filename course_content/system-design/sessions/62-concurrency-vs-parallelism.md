# Chapter 62 · Concurrency vs parallelism

## The big idea

- **Concurrency** is **dealing with many things at once**: structuring a program so several tasks can **make
  progress by taking turns**, even on one CPU core.
- **Parallelism** is **doing many things at the same moment**: several tasks **literally run at the same time**
  on different cores or machines.

**Everyday example:** a **chef in a kitchen**. With one chef cooking dal, rice and sabzi, the chef starts the
rice, while it simmers chops vegetables, stirs the dal, returns to the rice. Many dishes progress, but only
**one thing is done at any instant**: that is **concurrency**. With **three chefs**, each cooks one dish at the
same time: that is **parallelism**. You can have concurrency without parallelism (one chef), parallelism
without much concurrency (three chefs each doing one long task), or both.

```{raw} html
:file: ../diagrams/concurrency-parallelism.html
```

## Two different problems

| | Concurrency | Parallelism |
|---|---|---|
| Goal | **Responsiveness and structure**: handle many tasks, hide waiting | **Speed**: finish heavy computation faster |
| Needs multiple cores? | **No** | **Yes** |
| Typical task | **I/O-bound** (waiting for network, disk, database) | **CPU-bound** (maths, encoding, compression) |
| Tools | Threads, **async/await**, event loops, coroutines | Processes, multiple cores, GPUs, clusters |
| Main danger | Race conditions, deadlocks | Overheads, uneven work, merging results |

## I/O-bound work: concurrency is the answer

Most web servers spend their time **waiting**: for a database, an API, a disk. While one request waits,
another can run. One core can juggle thousands of waiting requests.

```python
import asyncio, time

async def fetch(name, seconds):
    await asyncio.sleep(seconds)           # pretend network call: the program is waiting, not computing
    return name

async def main():
    start = time.perf_counter()
    for name in ("users", "orders", "prices"):            # one after another
        await fetch(name, 0.3)
    sequential = time.perf_counter() - start

    start = time.perf_counter()
    await asyncio.gather(fetch("users", 0.3), fetch("orders", 0.3), fetch("prices", 0.3))   # overlapped
    concurrent = time.perf_counter() - start
    print(f"sequential: {sequential:.1f}s")
    print(f"concurrent: {concurrent:.1f}s   (one thread, no extra cores)")

asyncio.run(main())
```

**Output:**

```text
sequential: 0.9s
concurrent: 0.3s   (one thread, no extra cores)
```

Three 0.3-second waits took 0.9 s one after another and only 0.3 s overlapped, with **one thread**. The
program did not compute faster; it **stopped wasting time waiting**.

## CPU-bound work: parallelism is the answer

If the CPU is busy computing, taking turns does not help: you need **more CPUs working at once**.

```python
import time
from concurrent.futures import ProcessPoolExecutor

def heavy(n):
    return sum(i * i for i in range(n))

def run_sequential(jobs):
    start = time.perf_counter()
    results = [heavy(n) for n in jobs]
    return time.perf_counter() - start, results

def run_parallel(jobs, workers=4):
    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(heavy, jobs))
    return time.perf_counter() - start, results

if __name__ == "__main__":
    jobs = [3_000_000] * 8
    t_seq, r_seq = run_sequential(jobs)
    t_par, r_par = run_parallel(jobs)
    print("same answers          :", r_seq == r_par)
    print("parallel was faster   :", t_par < t_seq)
```

**Output:**

```text
same answers          : True
parallel was faster   : True
```

Eight heavy jobs ran on several cores simultaneously. (The speed-up is below the core count because of process
start-up and result passing; this is Amdahl's law at work, see below.)

## Limits of parallelism: Amdahl's law

If a fraction **p** of the work can be parallelised across **n** workers, the best speed-up is

```text
speed-up = 1 / ((1 - p) + p / n)
```

```python
def amdahl(p, n):
    return 1 / ((1 - p) + p / n)

print("parallel share   2 cores   8 cores   64 cores   infinite")
for p in (0.50, 0.90, 0.99):
    print(f"{p:>13.0%}   {amdahl(p, 2):>7.2f}   {amdahl(p, 8):>7.2f}   {amdahl(p, 64):>8.2f}   {1 / (1 - p):>8.1f}")
```

**Output:**

```text
parallel share   2 cores   8 cores   64 cores   infinite
          50%      1.33      1.78       1.97        2.0
          90%      1.82      4.71       8.77       10.0
          99%      1.98      7.48      39.26      100.0
```

If 10% of a job is strictly sequential, **no number of cores gives more than a 10x speed-up**. This is why
the sequential parts (locks, one database, one leader) are the real bottleneck of scaling.

## The dangers of concurrency

Tasks that share data can interfere:

- **Race condition:** result depends on timing. Two threads do `count += 1` and one update is lost.
- **Deadlock:** A waits for B's lock while B waits for A's. Both stop forever.
- **Starvation:** one task never gets its turn.
- **Livelock:** tasks keep reacting to each other and make no progress.

```python
import threading

counter = 0
lock = threading.Lock()

def unsafe(n):
    global counter
    for _ in range(n):
        value = counter          # read
        counter = value + 1      # write: another thread may have changed it in between

def safe(n):
    global counter
    for _ in range(n):
        with lock:               # only one thread at a time may update
            counter += 1

counter = 0
threads = [threading.Thread(target=safe, args=(100_000,)) for _ in range(4)]
for t in threads: t.start()
for t in threads: t.join()
print("with a lock, expected 400000, got:", counter)
```

**Output:**

```text
with a lock, expected 400000, got: 400000
```

Remedies: **locks** (careful with ordering to avoid deadlock), **immutable data**, **message passing** instead
of sharing (queues, actors), **atomic operations**, and **single-writer designs**.

## Where each shows up in system design

| Scenario | Mechanism |
|---|---|
| A web server handling 10,000 connections | **Concurrency**: event loop (Node, nginx), async, or threads |
| Using all cores of one machine | **Parallelism**: worker processes/threads |
| MapReduce, Spark | **Parallelism** across many machines |
| Database serving many queries | Concurrency control (MVCC, locks) + parallel query execution |
| Video encoding | **Parallelism** (split the file, encode chunks in parallel) |
| Many microservice calls in a page | **Concurrency**: issue them in parallel, wait for all |

Related ideas: **Python's GIL** lets only one thread run Python bytecode at a time, so threads give
concurrency for I/O but not CPU parallelism (use processes); **Go** goroutines, **Erlang** actors and **async/await**
are concurrency models; **GPUs** are massively parallel.

## Common mistakes

:::{warning}
- Using threads for CPU-heavy Python code and expecting a speed-up (the GIL).
- Spawning one thread per request with no limit (memory exhaustion); use pools and queues.
- Sharing mutable state between tasks without locks.
- Assuming more cores always means proportionally faster (Amdahl).
:::

## Try it yourself

1. A job is 20% sequential. What is the maximum speed-up with unlimited cores?
2. You call three independent APIs, each 200 ms. How long if called one after another, and if concurrently?
3. A web server is slow because each request waits for the database. Do you need parallelism or concurrency?

<details class="solution"><summary>Answers</summary>

1. 1 / 0.20 = **5x** at most.
2. Sequential: **600 ms**. Concurrent: about **200 ms**.
3. **Concurrency**: the CPU is mostly idle, so overlap the waiting (async, threads, more connections). More cores would not help.

</details>

:::{admonition} Next
:class: important
Delivering live updates: [long polling vs WebSockets](63-long-polling-vs-websockets.md).
:::
