# Chapter 38 · Generating unique short IDs

## The big idea

Many servers create IDs at the same moment, and **no two items may get the same ID**. Making unique
IDs without slowing everything down is one of the classic hard parts of system design.

**Everyday example:** a hospital token counter. One person handing out tokens is simple but slow. Give
each desk a **block** of numbers (desk A takes 1-100, desk B takes 101-200) and everyone works in
parallel without clashing.

## Base62 in one minute

Short links use 62 symbols: `a-z`, `A-Z`, `0-9`. Treat a number as "digits" in base 62 and you get
a short string. Capacity by length: 6 characters is about **57 billion** codes, 7 is about **3.5 trillion**.

```python
ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def to_base62(n: int) -> str:
    if n == 0:
        return ALPHABET[0]
    out = []
    while n:
        n, r = divmod(n, 62)
        out.append(ALPHABET[r])
    return "".join(reversed(out))

print(to_base62(125))        # 21
print(to_base62(3_500_000))  # eGvC
```

## Four ways to make a code

| Approach | Good | Bad |
|---|---|---|
| **Hash the URL**, keep 7 chars | Stateless | Collisions after truncation, so check and retry; same URL gives same code |
| **Random code**, retry on clash | Hard to guess | A database check on every write; retries grow as the table fills |
| **One database auto-increment** | Simple, no clashes | One machine is a bottleneck and a single point of failure |
| **Counter ranges + base62** | No clashes, no lookup per write | Needs a small coordinator; unused numbers lost on a crash |

```{raw} html
:file: ../diagrams/id-ranges.html
```

**Winner for most designs: counter ranges.** Each app server asks a tiny coordinator (etcd, ZooKeeper
or a one-row table) for a block, such as one million numbers. It hands them out from memory and
converts each to base62. The coordinator is contacted once per million links.

## Making codes hard to guess

Counters give `aaaaab`, `aaaaac`, ... Anyone can walk through them. Keep the counter for
**uniqueness** and pass the number through a **reversible scramble** (a Feistel network, or XOR and
bit shuffling with a secret) before encoding. A one-to-one mapping cannot create duplicates, yet the
output looks random. An alternative is a **key generation service** that pre-fills a table with random
unused codes.

## Snowflake-style IDs: no coordinator at all

Twitter's **Snowflake** packs a 64-bit ID from three parts, so every machine can create IDs on its own:

```{raw} html
:file: ../diagrams/snowflake.html
```

```python
import threading
import time

EPOCH_MS = 1_700_000_000_000          # a custom start date keeps the 41 time bits lasting for ~69 years

class Snowflake:
    def __init__(self, machine_id, clock=lambda: int(time.time() * 1000)):
        assert 0 <= machine_id < 1024                      # 10 bits
        self.machine_id, self.clock = machine_id, clock
        self.last_ms, self.sequence, self.lock = -1, 0, threading.Lock()

    def next_id(self):
        with self.lock:
            now = self.clock()
            if now < self.last_ms:
                raise RuntimeError("clock moved backwards: refuse to issue ids")
            if now == self.last_ms:
                self.sequence = (self.sequence + 1) & 0xFFF           # 12 bits: 4,096 ids per millisecond
                if self.sequence == 0:                                 # exhausted this millisecond: wait for the next
                    while now <= self.last_ms:
                        now = self.clock()
            else:
                self.sequence = 0
            self.last_ms = now
            return ((now - EPOCH_MS) << 22) | (self.machine_id << 12) | self.sequence

fake_ms = [EPOCH_MS + 5_000]
a, b = Snowflake(1, lambda: fake_ms[0]), Snowflake(2, lambda: fake_ms[0])

ids = [a.next_id(), a.next_id(), b.next_id()]
fake_ms[0] += 1
ids.append(a.next_id())
for i in ids:
    print(f"{i}   time bits={i >> 22:>5}   machine={(i >> 12) & 0x3FF}   sequence={i & 0xFFF}")
print("all unique:", len(set(ids)) == len(ids), "| sorted by creation time:", ids == sorted(ids) or "roughly (ties broken by machine id)")
```

**Output:**

```text
20971524096   time bits= 5000   machine=1   sequence=0
20971524097   time bits= 5000   machine=1   sequence=1
20971528192   time bits= 5000   machine=2   sequence=0
20975718400   time bits= 5001   machine=1   sequence=0
all unique: True | sorted by creation time: True
```

Two machines issued ids in the **same millisecond** and never clashed (different machine bits), and each machine's
own ids increase. Compared with counter ranges, Snowflake needs **no coordinator per block** but needs unique machine
ids and a trustworthy clock (if the clock jumps backwards the generator must refuse to issue ids).

| Approach | Needs a coordinator? | Sortable by time? | Guessable? |
|---|---|---|---|
| UUID v4 (random 128 bit) | No | No | No |
| Counter ranges + base62 | A little (blocks) | Roughly | Yes, unless scrambled |
| Snowflake | Only machine ids | **Yes** | Somewhat |
| Database auto-increment | Yes (one machine) | Yes | Yes |

## Common mistakes

- Truncating a hash and assuming it is unique.
- Calling the database for every new code.
- A single coordinator instance: run a small replicated cluster.
- Ignoring custom aliases: they live in the same code space, so check them against existing codes.

## Try it yourself

1. How many IDs can one Snowflake machine create per second, and how many machines can there be?
2. Why must a Snowflake generator refuse to issue IDs when the clock goes backwards?
3. You need unguessable short codes for 6 billion links. Which approach, and how long should the code be?

<details class="solution"><summary>Answers</summary>

1. 4,096 per millisecond = about **4 million per second per machine**; 2^10 = **1,024 machines**.
2. It could repeat a (time, machine, sequence) combination it already issued, creating a duplicate id.
3. Counter ranges with a **reversible scramble**, converted to base62, **7 characters** (3.5 trillion codes, so the space stays sparse).

</details>

:::{admonition} Try it in the playground
:class: important
The deep-dive steps of the [TinyURL problem](/system-design/tinyurl/) ask you to choose the approach and
then fix the guessability problem.
:::

:::{admonition} Next
:class: important
Databases are covered. Now the biggest lever for speed: [caching 101](39-caching-101.md).
:::
