# Chapter 6 · Scaling the data layer

## The big idea

One machine only holds so much and answers so many requests. Beyond that you spread the data in two ways:
**replication** (several copies) and **sharding** (splitting the data into parts).

**Everyday example:** a library. Photocopies of a popular book let many people read at once (replication).
Splitting the shelves A-M and N-Z across two rooms lets the library grow (sharding).

## Replication

- Keep **copies** of each piece of data on different machines or zones.
- Gives **durability** (a machine can die) and **more read capacity**.
- Cost: copies can briefly disagree (**eventual consistency**). For a link shortener that is acceptable.

## Sharding

Choose a **shard key**, hash it and use the result to decide which machine owns the row.

| Candidate key | Verdict for a shortener |
|---|---|
| hash(short_code) | **Best.** Every read knows the code; load spreads evenly |
| User id | Reads do not know the user; one heavy user makes a hot shard |
| Creation date | New links and recent reads all hit one shard |
| First letter | Uneven and limited |

Rules of thumb for a shard key: it should be **known at read time**, **spread load evenly** and avoid
**hot spots**. Use **consistent hashing** so adding a shard moves only a small share of the data.

## Reliability checklist

- Remove every single point of failure: several load balancers and app servers across zones.
- Replicate each shard with automatic failover.
- Add **timeouts, retries with backoff** and **circuit breakers** so a slow dependency cannot drag everyone down.
- Take backups **and test the restore**.
- Monitor latency, error rate, cache hit rate and replication lag; alert on them.

## Trade-offs to say out loud

- Eventual consistency buys availability and low latency; it costs briefly stale reads.
- Sharding scales storage but gives up cross-shard queries and transactions.
- More replicas mean more durability and more cost.

## Common mistakes

- Sharding too early, before the numbers need it.
- A shard key that makes one shard hot.
- Replicas in the same rack or zone.
- Backups that were never restored.

:::{admonition} Try it in the playground
:class: important
Finish the [TinyURL problem](/system-design/tinyurl/): choose the shard key, harden the design against
failures and defend your trade-offs.
:::
