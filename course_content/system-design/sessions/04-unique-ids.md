# Chapter 4 · Generating unique short IDs

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

## Common mistakes

- Truncating a hash and assuming it is unique.
- Calling the database for every new code.
- A single coordinator instance: run a small replicated cluster.
- Ignoring custom aliases: they live in the same code space, so check them against existing codes.

:::{admonition} Try it in the playground
:class: important
The deep-dive steps of the [TinyURL problem](/system-design/tinyurl/) ask you to choose the approach and
then fix the guessability problem.
:::
