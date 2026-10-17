# Chapter 17 · DNS (Domain Name System)

## The big idea

People remember **names** (`parottasalna.com`); computers route by **IP addresses**
(`203.0.113.7`). **DNS** is the distributed phone book that translates one into the other.

**Everyday example:** the contacts list on your phone. You tap "Amma", and the phone dials the number.
DNS is a contacts list shared by the whole planet, split into pieces so no single list has to hold
everything.

```{raw} html
:file: ../diagrams/dns-lookup.html
```

## How a lookup really works

When you open `www.shop.example.com`, your computer does not know where to go. It asks a chain of
servers. Most of the time the answer is already cached, so none of this happens.

1. **Browser and OS cache** are checked first. A hit costs nothing.
2. The OS asks the **recursive resolver** (your ISP's, or `8.8.8.8`, `1.1.1.1`). It does the legwork.
3. The resolver asks a **root server**: "who handles `.com`?" It answers with the **TLD** servers.
4. The resolver asks the **`.com` TLD server**: "who handles `shop.example.com`?" It returns the
   domain's **authoritative name servers**.
5. The resolver asks the **authoritative server**, which gives the real answer: an **A record** with an IP.
6. The resolver **caches** the answer for its **TTL** and returns it to you.

A cold lookup takes **20 to 120 ms**; a cached one under 1 ms.

## Record types you must know

| Record | Meaning | Example |
|---|---|---|
| **A** | name to IPv4 | `shop.example.com -> 203.0.113.7` |
| **AAAA** | name to IPv6 | |
| **CNAME** | name is an alias of another name | `www -> shop.example.com` |
| **NS** | which servers are authoritative | `example.com -> ns1.dnsprovider.com` |
| **MX** | where to deliver email | |
| **TXT** | free text: SPF, domain verification | |

(A CNAME cannot sit at the bare domain `example.com`. Cloud providers offer an `ALIAS` record for that.)

## TTL: the trade-off you control

The **TTL** (time to live) tells caches how long to keep an answer.

- **Long TTL (1 day):** fewer lookups, faster, cheaper. But a change takes up to a day to spread.
- **Short TTL (60 s):** changes (and failovers) spread quickly. More lookups, more load on your DNS.

Real playbook: lower the TTL to 60 seconds a day **before** a migration, switch over, then raise it again.

## DNS as a traffic tool

DNS can return different answers to different users:

- **Round robin:** several A records, rotated. Cheap load spreading, but no health checks.
- **Weighted:** 90% to the old version, 10% to the new (canary).
- **Latency-based or geo:** send users to the nearest region.
- **Failover:** if the health check on the primary fails, return the secondary's address.

Limits: caches ignore your wishes until the TTL expires, so DNS failover takes **minutes**, not seconds.
For fast failover use a load balancer or anycast.

## A toy resolver

```python
# A pretend DNS hierarchy: each level only knows who to ask next.
ROOT = {"com": "tld-com-server"}
TLD = {"tld-com-server": {"example.com": "ns1.example.com"}}
AUTH = {"ns1.example.com": {"www.shop.example.com": "203.0.113.7"}}

cache = {}

def resolve(name):
    if name in cache:
        return cache[name], "cache hit"
    steps = []
    tld = name.split(".")[-1]
    tld_server = ROOT[tld]; steps.append(f"root -> {tld_server}")
    domain = ".".join(name.split(".")[-2:])
    auth_server = TLD[tld_server][domain]; steps.append(f"{tld_server} -> {auth_server}")
    ip = AUTH[auth_server][name]; steps.append(f"{auth_server} -> {ip}")
    cache[name] = ip
    return ip, " | ".join(steps)

print(resolve("www.shop.example.com"))
print(resolve("www.shop.example.com"))
```

**Output:**

```text
('203.0.113.7', 'root -> tld-com-server | tld-com-server -> ns1.example.com | ns1.example.com -> 203.0.113.7')
('203.0.113.7', 'cache hit')
```

The second lookup is a cache hit. That asymmetry is why DNS scales to the whole world.

## Reliability and security

- **Run at least two authoritative name servers**, ideally with two providers. A DNS outage makes your
  site unreachable even if every server is healthy (a classic SPOF).
- **DNS caching** means errors and changes spread slowly: plan TTLs.
- **DNS poisoning** (a fake answer slipped into a cache) is countered by **DNSSEC** and by using
  HTTPS everywhere.
- **DNS over HTTPS/TLS** encrypts lookups so networks cannot see which names you ask for.

## Common mistakes

:::{warning}
- Planning an "instant" DNS failover with a 1-hour TTL.
- Putting a CNAME at the bare domain (`example.com`); use an ALIAS/ANAME record from your DNS provider.
- A single DNS provider.
- Hard-coding IPs instead of names; the IP will change, the name should not.
:::

## Try it yourself

1. You will move a website to a new server tomorrow. What do you do to the DNS TTL today, and why?
2. Why does a cold DNS lookup take much longer than a warm one?
3. How can DNS send Indian users to Mumbai and European users to Frankfurt?

<details class="solution"><summary>Answers</summary>

1. **Lower it** (for example to 60 s) so that after the switch, caches expire fast. Raise it again afterwards.
2. A cold lookup walks root, TLD and authoritative servers (several round trips). A warm lookup is answered from a nearby cache.
3. **Geo or latency-based routing**: the authoritative DNS looks at the resolver's location and returns the IP of the nearest region.

</details>

:::{admonition} Next
:class: important
Two kinds of middlemen sit between users and servers: [proxy vs reverse proxy](18-proxy-vs-reverse-proxy.md).
:::
