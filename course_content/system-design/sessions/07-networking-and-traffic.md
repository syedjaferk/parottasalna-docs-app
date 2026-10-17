# Chapter 7 · DNS, CDNs, load balancers and proxies

## The big idea

Before a request reaches your code it passes through several helpers. Knowing what each one does
(and what it can answer **without bothering your servers**) is how you handle huge traffic cheaply.

**Everyday example:** a railway station. The enquiry board tells you the platform (DNS), the nearby
ticket kiosks sell the common tickets (CDN), and the staff at the gate send people down different
corridors so no corridor jams (load balancer).

```{raw} html
:file: ../diagrams/request-path.html
```

## Performance, scalability, latency, throughput

- **Performance problem:** the system is slow for a *single* user.
- **Scalability problem:** it is fast for one user but slow under load.
- **Latency** is the time one action takes. **Throughput** is how many actions finish per second.
  Aim for high throughput with *acceptable* latency, not the lowest latency at any cost.

## DNS: names to addresses

DNS turns `example.com` into an IP address. Records you should know: **A** (name to IPv4), **CNAME**
(name to another name), **NS** (who answers for this domain), **MX** (mail). DNS answers are cached
for a time called the **TTL**, so changes spread slowly. DNS can also *route*: weighted (send 10% to
the new version), latency-based (nearest region) and geolocation (users in India to the India region).

## CDN: copies close to the user

A **content delivery network** keeps copies of files in many cities ("edge" servers).

| | Push CDN | Pull CDN |
|---|---|---|
| Who fills it | You upload ahead of time | The edge fetches on the first request |
| Good for | Few, rarely changing files | Many files, unpredictable demand |
| Cost | Storage for everything | Slow first request per edge |

Control freshness with `Cache-Control` headers and with **versioned file names**
(`app.3f9a.js`), so you never have to ask the CDN to forget something.

## Load balancers

A **load balancer** spreads requests over many servers and stops sending to servers that fail.

- **Layer 4** (TCP/UDP): fast, sees only IPs and ports.
- **Layer 7** (HTTP): can route by URL, header or cookie, and terminate TLS.
- Algorithms: **round robin**, **least connections**, **IP hash** (same client, same server) and
  **weighted** variants for servers of different size.
- Run at least **two** load balancers; otherwise the balancer is itself a single point of failure.

## Reverse proxy

A **reverse proxy** sits in front of your servers and handles chores for them: TLS termination,
compression, caching, rate limiting and hiding the internal layout. A load balancer is a reverse
proxy that has more than one server behind it. (A *forward* proxy is the other way round: it sits in
front of *clients*.)

## Stateless servers

If any server can serve any request, you can add or remove servers freely. Keep **session data in a
shared store** (a database or Redis) instead of in server memory. Statelessness is what makes
horizontal scaling easy.

## Common mistakes

- Saying "add a load balancer" and not saying **which layer** or **which algorithm**.
- A load balancer with no standby.
- Forgetting DNS TTL when planning a failover.
- Caching user-specific pages in a shared CDN.

:::{admonition} Try it in the playground
:class: important
Design the [Load Balancer](/system-design/load-balancer/) and the [CDN](/system-design/cdn/) from scratch.
:::
