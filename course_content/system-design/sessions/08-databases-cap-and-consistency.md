# Chapter 8 · Databases, CAP and consistency

## The big idea

Every design needs a place to keep data safely, and every choice of database trades something away.
This chapter gives you the vocabulary to say **why** you picked one.

**Everyday example:** a bank keeps one official ledger (strong consistency) while a shop keeps a
quick notebook of today's orders that is copied to the main book each night (eventual consistency).

## SQL or NoSQL?

| | Relational (SQL) | NoSQL |
|---|---|---|
| Shape | Tables, rows, joins | Key-value, document, wide-column, graph |
| Guarantees | **ACID** transactions | Often **BASE**: basically available, soft state, eventually consistent |
| Scaling | Vertical first, shard with effort | Built to spread over many machines |
| Pick it when | Relationships and transactions matter (money, orders) | Huge scale, simple access by key, flexible shape |

**ACID:** Atomicity (all or nothing), Consistency (rules always hold), Isolation (concurrent
transactions do not trip each other), Durability (committed data survives a crash).

:::{admonition} Say it simply
:class: tip
Start with a relational database unless the numbers or the access pattern say otherwise. "I would use
Postgres until X" is a strong sentence.
:::

## Indexes

An **index** is a sorted lookup structure (usually a B-tree) so the database does not scan every row.
It makes reads fast and writes slower, and costs storage. Index the columns you filter and sort by.

## Replication

```{raw} html
:file: ../diagrams/replication.html
```

- **Primary-replica:** writes to one primary, copied to replicas that serve reads. If the primary
  dies, promote a replica (**failover**).
- **Primary-primary:** both accept writes. More availability, but you must resolve conflicts.
- **Replication lag:** replicas are slightly behind, so a user may not see their own write at once.
  Fix with "read your own writes" (read from the primary for a moment after a write).

## Sharding

Split one big dataset across machines. The **shard key** decides where a row lives. Good keys spread
load evenly and let most queries touch one shard. **Consistent hashing** lets you add shards while
moving only a small part of the data. The cost: cross-shard joins and transactions get hard.

## Federation and denormalization

- **Federation:** separate databases by function (users, orders, products).
- **Denormalization:** store some data twice so a hot read needs no join. Faster reads, harder writes.

## CAP theorem

In a network **partition** (nodes cannot talk), a distributed store can keep only one of:

- **Consistency (C):** every read sees the latest write.
- **Availability (A):** every request gets an answer.

Partitions do happen, so the real choice is **CP** (refuse some requests to stay correct, such as
a bank balance) or **AP** (always answer, maybe with slightly old data, such as a social feed).

## Consistency patterns

- **Strong:** after a write, every reader sees it. Slower, needs coordination.
- **Eventual:** readers see it *soon*. Fast and available.
- **Weak:** readers may or may not (live video, games).

## Availability in numbers

"Nines": 99.9% is about **8.8 hours** of downtime a year, 99.99% about **53 minutes**. Components in
**sequence** multiply (two 99.9% parts give about 99.8%); components in **parallel** improve it
(two 99.9% parts give 99.9999%). This is why redundancy beats a single fancy machine.

## Common mistakes

- "NoSQL because it scales" with no access pattern in mind.
- Sharding before a single node is actually the bottleneck.
- Saying "CA" for a distributed system.
- Ignoring replication lag in the user experience.

:::{admonition} Try it in the playground
:class: important
The [Distributed Key-Value Store](/system-design/key-value-store/) problem puts replication, quorums and
CAP into practice.
:::
