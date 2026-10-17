# Chapter 14 · IP addresses

## The big idea

An **IP address** is the number that identifies a machine on a network, so packets know where to go.

**Everyday example:** a postal address. A letter needs a street, a number and a pincode. A packet needs
an IP address. Routers are the sorting offices: each looks at the address and decides which direction to
forward it.

```{raw} html
:file: ../diagrams/ip-addresses.html
```

## IPv4 and IPv6

| | IPv4 | IPv6 |
|---|---|---|
| Size | 32 bits | 128 bits |
| Written as | `192.168.1.10` (four numbers 0-255) | `2001:0db8::1` (eight hex groups) |
| Count | about 4.3 billion (ran out) | about 3.4 x 10^38 |
| Today | Still dominant, shared via NAT | Growing, required in many mobile networks |

## Public vs private addresses

Three ranges are **private**: usable inside a home, office or cloud network, but **not routable on the
public internet**:

| Range | Notes |
|---|---|
| `10.0.0.0/8` | Large networks, cloud VPCs |
| `172.16.0.0/12` | |
| `192.168.0.0/16` | Home routers |

Your laptop at `192.168.1.10` reaches the internet through **NAT** (network address translation):
your router rewrites outgoing packets to use its single **public** address and remembers which inner
machine each reply belongs to.

## CIDR: network and host parts

`10.0.1.0/24` means **the first 24 bits are the network, the remaining 8 bits are hosts**.

- Hosts available: `2^(32 - prefix)` addresses. `/24` = 256, `/16` = 65,536, `/28` = 16.
- Cloud providers reserve a few addresses per subnet, so usable is slightly less.

```python
import ipaddress

net = ipaddress.ip_network("10.0.1.0/24")
print("network     :", net)
print("addresses   :", net.num_addresses)
print("first usable:", next(net.hosts()))
print("is 10.0.1.77 inside?", ipaddress.ip_address("10.0.1.77") in net)
print("is 10.0.2.5  inside?", ipaddress.ip_address("10.0.2.5") in net)
print("private?", ipaddress.ip_address("192.168.1.10").is_private)

# split a /24 into four /26 subnets, e.g. one per availability zone
for sub in net.subnets(new_prefix=26):
    print("subnet", sub, "->", sub.num_addresses, "addresses")
```

**Output:**

```text
network     : 10.0.1.0/24
addresses   : 256
first usable: 10.0.1.1
is 10.0.1.77 inside? True
is 10.0.2.5  inside? False
private? True
subnet 10.0.1.0/26 -> 64 addresses
subnet 10.0.1.64/26 -> 64 addresses
subnet 10.0.1.128/26 -> 64 addresses
subnet 10.0.1.192/26 -> 64 addresses
```

## How a router chooses: longest prefix match

A router has a **routing table** of prefixes. For a destination it picks the **most specific** (longest
prefix) matching route.

```python
import ipaddress

routes = {
    "0.0.0.0/0": "internet gateway",        # default route: anything
    "10.0.0.0/16": "VPC core",
    "10.0.1.0/24": "web subnet",
    "10.0.1.128/25": "special cache hosts",
}

def route(destination):
    ip = ipaddress.ip_address(destination)
    matches = [(ipaddress.ip_network(p), hop) for p, hop in routes.items() if ip in ipaddress.ip_network(p)]
    best = max(matches, key=lambda m: m[0].prefixlen)
    return f"{destination:<12} -> {best[1]}  (matched {best[0]})"

for dest in ("10.0.1.200", "10.0.1.20", "10.0.9.9", "8.8.8.8"):
    print(route(dest))
```

**Output:**

```text
10.0.1.200   -> special cache hosts  (matched 10.0.1.128/25)
10.0.1.20    -> web subnet  (matched 10.0.1.0/24)
10.0.9.9     -> VPC core  (matched 10.0.0.0/16)
8.8.8.8      -> internet gateway  (matched 0.0.0.0/0)
```

This is the rule behind every cloud route table and VPN.

## Static, dynamic, elastic

- **Static IP:** fixed, does not change (servers behind DNS, allow-lists).
- **Dynamic IP:** assigned by **DHCP** when a device joins, may change.
- **Elastic/floating IP (cloud):** a static public address you can **move between machines**, which is
  how many failover setups work.

## Ports: the second half of an address

An IP picks the **machine**; a **port** picks the **program**. `203.0.113.7:443` = machine
203.0.113.7, HTTPS service. Well-known ports: `22` SSH, `80` HTTP, `443` HTTPS, `5432` PostgreSQL,
`6379` Redis, `3306` MySQL.

## Designing a cloud network (typical interview sketch)

```text
VPC 10.0.0.0/16
 ├─ public subnet  10.0.1.0/24  (load balancer, NAT gateway)   -> route to internet gateway
 ├─ private subnet 10.0.2.0/24  (app servers)                   -> route out via NAT only
 └─ private subnet 10.0.3.0/24  (databases)                     -> no internet route at all
```

Put only what must be reachable from the internet in the public subnet. Databases never get a
public address.

## Common mistakes

:::{warning}
- Overlapping CIDR ranges between two networks you later want to connect (VPN or peering fails). Plan ranges early.
- Choosing a subnet too small (`/28`) and running out of addresses when you scale.
- Giving databases public IPs.
- Treating an IP as a stable identity for a user: NAT shares one address among thousands.
:::

## Try it yourself

1. How many hosts can a `/22` network hold?
2. Which route wins for destination `10.0.1.200` if the table has `10.0.0.0/16` and `10.0.1.0/24`?
3. Why do thousands of users in one office appear to come from one IP, and what does that mean for per-IP rate limiting?

<details class="solution"><summary>Answers</summary>

1. 2^(32-22) = **1,024** addresses.
2. `10.0.1.0/24`: the **longest prefix** is the most specific.
3. **NAT** shares the router's public address. Per-IP limits can punish a whole office or school. Combine IP limits with per-account limits.

</details>

:::{admonition} Next
:class: important
Machines have addresses. How do they exchange data reliably, or quickly? [TCP vs UDP](15-tcp-vs-udp.md).
:::
