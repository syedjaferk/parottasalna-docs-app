# Chapter 7 · Single point of failure (SPOF)

## The big idea

A **single point of failure** is any one component that, if it breaks, **takes the whole system down**.

**Everyday example:** a house with exactly one key. Lose it and nobody gets in. Having a spare key
with a neighbour removes the single point of failure. Having two doors with two different locks
removes it even better.

## How to hunt for SPOFs

Walk the path of one request and ask **"if this dies, what happens?"** at every box.

```{raw} html
:file: ../diagrams/spof.html
```

Common SPOFs in a typical web system:

| Component | Why it is a SPOF | Fix |
|---|---|---|
| One load balancer | All traffic enters through it | Pair of balancers with a floating IP or DNS |
| One app server | Capacity and availability | Many servers behind the balancer |
| One database | All data and writes | Primary plus replicas, automatic promotion |
| One availability zone | Power or network loss takes everything | Spread over 2 or 3 zones |
| One region | Rare, but it happens | Multi-region for critical systems |
| One DNS provider | Nobody can find you | Two DNS providers |
| One person who knows the system | Not a computer, still a SPOF | Runbooks, on-call rotation |
| One config or secrets service | Every service reads it at start | Cache locally, replicate |

## Finding SPOFs with code

List each layer of the request path with its instances, mark which layers a request **cannot do without**, and
test every single failure: *if this one instance disappears, does any critical layer have nothing left?*

```python
layers = {
    "load balancer": ["lb1"],                  # one instance
    "app tier": ["app1", "app2", "app3"],
    "database": ["db-primary"],                # one instance
    "cache": ["cache1"],                       # one instance, but the database can serve without it (slower)
    "dns": ["dns-provider-a", "dns-provider-b"],
}
critical = {"load balancer", "app tier", "database", "dns"}

for layer, instances in layers.items():
    for failed in instances:
        left = [i for i in instances if i != failed]
        if not left and layer in critical:
            print(f"SPOF: {failed:<14} -> the whole service is down")
        elif not left:
            print(f"degraded: {failed:<10} -> still up, but slower (database takes the load)")
print("checked", sum(len(v) for v in layers.values()), "single failures")
```

**Output:**

```text
SPOF: lb1            -> the whole service is down
SPOF: db-primary     -> the whole service is down
degraded: cache1     -> still up, but slower (database takes the load)
checked 8 single failures
```

The cache is not a SPOF for **availability**, but losing it can still hurt: the database may not cope with
the full read load. Ask both questions about every component: "does the service stop?" and "can the rest carry the load?".

## Fixing a SPOF

1. **Duplicate it** (two or more).
2. Make the copies **independent** (different racks, zones, power, vendors).
3. Make switching **automatic** (health checks, failover).
4. **Test it** by killing the component in a controlled drill.

:::{admonition} Redundancy has to be independent
:class: warning
Two servers on the same rack, or two replicas using the same disk array, count as **one** failure
domain. A single event (power, a bad deploy, a cloud-zone outage) can still reach both.
:::

## Not every SPOF is a machine

| Hidden SPOF | Example |
|---|---|
| A **person** | Only one engineer knows how to deploy |
| A **process** | A manual step nobody has documented |
| A **vendor** | One DNS provider, one payment gateway |
| A **certificate** | It expires and every client fails |
| A **config or secret store** | Every service reads it at start-up |
| A **region** | Whole-region outage |
| A **bug in the code that is deployed everywhere** | Redundancy of identical code does not help |

## Common mistakes

:::{warning}
- Declaring "no SPOF" after duplicating only the app tier, leaving one database or one load balancer.
- Duplicating a component but keeping a shared dependency (same disk, same network switch).
- Never testing the failover.
- Forgetting the **monitoring system** itself: if it dies you cannot see anything else die.
:::

## Try it yourself

1. List five SPOFs in the request path of an online shop and a fix for each.
2. You run two app servers in the same availability zone. Is that redundant? What can still kill both?
3. Why is a certificate expiry a SPOF-style risk, and how do you remove it?

<details class="solution"><summary>Answers</summary>

1. Single load balancer (pair), single DB (primary + replica), single zone (multi-zone), single DNS provider (two), single payment provider (a fallback).
2. Partly. It protects against one server failing, but a zone-wide power, network or cooling failure takes both. Use two or three zones.
3. When it expires every client rejects the connection at once. Automate renewal (ACME/Let's Encrypt, cloud-managed certs) and alert weeks before expiry.

</details>

:::{admonition} Next
:class: important
Once you have a spare, you need to switch to it: [failover](08-failover.md).
:::
