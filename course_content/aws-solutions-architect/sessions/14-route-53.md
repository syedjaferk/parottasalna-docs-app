# Session 14 · Amazon Route 53

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/EXbcDwvIdu0"
  title="Session 14: Amazon Route 53" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 **Session 14** of the [AWS Solutions Architect playlist](https://www.youtube.com/playlist?list=PLYmjGMwZ9N88) (Tamil) · [watch on YouTube](https://www.youtube.com/watch?v=EXbcDwvIdu0)

## The big idea

**Route 53** is AWS's DNS service: it registers domains, hosts their DNS records, checks the
health of your servers, and can answer the same question differently based on location,
latency or failures. It's how `www.yourdomain.com` reaches your load balancer. (The name: DNS runs
on port **53**.)

**Everyday example:** a phone directory with smart operators. Ask for "Parottasalna" and the
operator gives you the nearest branch's number, or the backup branch's number if the main one
isn't answering.

```{raw} html
:file: ../diagrams/s14-route53.html
```

## 1. Registrar vs DNS hosting

These are two separate jobs that people often mix up:

- **Registrar:** where you *buy* the domain (Route 53, GoDaddy, Namecheap…). It tells the `.com`
  servers which **name servers** are in charge of your domain.
- **DNS hosting:** the name servers that *answer* with your records. In Route 53 this is a
  **hosted zone**.

If you bought the domain elsewhere, create a hosted zone in Route 53 and copy its **4 NS records**
into the registrar's "custom name servers" setting. That's the step from the live demo.

## 2. Hosted zones

| | Public hosted zone | Private hosted zone |
|---|---|---|
| Answers | the whole internet | only VPCs you associate with it |
| Example | `parottasalna.com` | `internal.corp` → `db.internal.corp` → `10.0.2.15` |
| Cost | about $0.50 per zone per month + queries | same |

## 3. Record types (and Alias)

| Record | Points to | Notes |
|---|---|---|
| **A / AAAA** | IPv4 / IPv6 | |
| **CNAME** | another name | **not allowed at the zone apex** (`example.com` itself) |
| **Alias** (Route 53 special) | AWS resources: ALB, CloudFront, S3 website, API Gateway, another record | **works at the apex**, follows the resource's changing IPs, **free queries** to AWS targets |
| **MX** | mail servers | priority + host |
| **TXT** | text | domain verification, SPF/DKIM |
| **NS / SOA** | the zone's own servers | created automatically |

:::{important}
For `example.com → ALB`, use an **A record with Alias = on**, not a CNAME. CNAMEs can't sit at the
apex, and an ALB's IP addresses change, so you can't use a plain A record with an IP either.
:::

## 4. Routing policies

| Policy | Answers with… | Use |
|---|---|---|
| **Simple** | one record (can hold several values, returned in random order) | a single resource |
| **Weighted** | records in proportion to weights (e.g. 90 / 10) | canary releases, A/B tests |
| **Latency-based** | the Region with the lowest latency for this user | multi-Region apps |
| **Failover** | primary while its **health check** passes, else secondary | active–passive disaster recovery |
| **Geolocation** | by the user's continent / country / state | content or legal rules per country |
| **Geoproximity** | by distance, adjustable with a *bias* | shifting traffic between Regions |
| **Multivalue answer** | up to 8 healthy records at random | simple client-side load spreading |
| **IP-based** | by the user's IP range (CIDR) | ISP-specific routing |

**Health checks** test an endpoint (HTTP/HTTPS/TCP) from many locations, or watch a CloudWatch
alarm, and remove unhealthy records from answers.

## 5. Hands-on: point a real domain at AWS

1. *Route 53 → Hosted zones → Create*: `yourdomain.com`, public.
2. Copy the 4 **NS** values into your registrar (skip if the domain is registered in Route 53).
   Propagation can take minutes to hours, because of the old NS records' TTL.
3. Create records:
   - `yourdomain.com` → **A, Alias** → your Application Load Balancer.
   - `www.yourdomain.com` → **CNAME** → `yourdomain.com` (or another Alias).
4. Check it:

```bash
dig NS yourdomain.com +short
dig yourdomain.com A +short
curl -I http://www.yourdomain.com
```

**Output (example):**

```text
ns-1293.awsdns-33.org.
ns-412.awsdns-51.com.
ns-1820.awsdns-35.co.uk.
ns-662.awsdns-18.net.
13.234.17.92
3.110.45.201
HTTP/1.1 200 OK
```

(Two IPs: the ALB has one per AZ, and the Alias answer always matches its current addresses.)

5. **HTTPS:** request a free certificate in **ACM** for `yourdomain.com` and `*.yourdomain.com`,
   validate it with the **CNAME record ACM gives you** (one click: *Create records in Route 53*),
   then add it to the ALB's HTTPS listener.

## Common mistakes

- **CNAME at the apex.** Use an Alias A record.
- **Hosted zone created, NS not updated at the registrar:** nothing resolves to it.
- **Deleting and recreating a hosted zone:** the new zone gets **different NS servers**; update the registrar again.
- **Failover without a health check:** Route 53 can't tell the primary is down.
- **High TTLs during a migration** ([Session 13](13-vpc-flow-logs-dns.md)).

## Try it yourself

1. Which record do you need for `parottasalna.com` (the apex) → a CloudFront distribution?

   <details class="solution">
   <summary>Answer</summary>

   An **A record with Alias** pointing to the CloudFront distribution (plus AAAA Alias for IPv6).

   </details>

2. You want to send 10 % of users to a new version of the site. Which routing policy?

   <details class="solution">
   <summary>Answer</summary>

   **Weighted**: e.g. weight 90 for the current ALB and 10 for the new one.

   </details>

3. Users in Europe and India should reach the Region that's fastest for them. Which policy?

   <details class="solution">
   <summary>Answer</summary>

   **Latency-based** routing (geolocation picks by location, not by measured latency).

   </details>
