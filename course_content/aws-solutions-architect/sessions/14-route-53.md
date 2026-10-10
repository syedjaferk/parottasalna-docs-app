# Session 14 · Amazon Route 53

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/EXbcDwvIdu0"
  title="Session 14: Amazon Route 53" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 **Session 14** of the [AWS Solutions Architect playlist](https://www.youtube.com/playlist?list=PLYmjGMwZ9N88) (Tamil) · [watch on YouTube](https://www.youtube.com/watch?v=EXbcDwvIdu0)

## What you'll learn

- What **Route 53** does: domain registration, DNS hosting, health checks and traffic routing
- **Registrar vs DNS hosting**, and delegating a domain bought elsewhere
- **Public and private hosted zones**
- Record types, the **Alias** record and the **zone apex** rule
- All **routing policies** with when to use each
- **Health checks** and DNS failover
- Pointing a real domain at an ALB with HTTPS

```{raw} html
:file: ../diagrams/s14-route53.html
```

## 1. Route 53 in one picture

**🧑 In plain words.** A **phone directory with smart operators**. Ask for "Parottasalna" and the
operator gives you the nearest branch's number, or the backup branch's number if the main one isn't
answering. (The name: DNS runs on port **53**.)

**❓ The problem it solves.** Running your own DNS servers means keeping them up worldwide, fast and
secure; plain DNS also can't react to failures or send users to the closest Region.

**⚙️ How it works.** Route 53 is a **global**, highly available (100 % availability SLA) DNS service
with four jobs:

1. **Domain registration** (it's a registrar for many TLDs),
2. **DNS hosting** in hosted zones (authoritative name servers worldwide, anycast),
3. **Health checks** of your endpoints,
4. **Traffic routing** policies that answer differently by weight, latency, location or health.

Pricing: per hosted zone per month, per million queries (Alias queries to AWS resources are free),
per health check.

**💡 Example.** `parottasalna.com` is registered in Route 53; its hosted zone points the apex at
CloudFront, `api` at an ALB with a failover record, and `mail` MX records at Google Workspace.

## 2. Registrar vs DNS hosting

**🧑 In plain words.** The **land registry** says who owns the plot and which **post office** handles
its mail. The **post office** actually knows the house numbers on the plot.

**❓ The problem it solves.** People often buy a domain in one place and want DNS in another, and
mix up the two jobs.

**⚙️ How it works.**

- **Registrar** (Route 53, GoDaddy, Namecheap…): you buy/renew the domain; the registrar tells the
  **TLD registry** (e.g. `.com`) which **name servers** are authoritative (the domain's **NS** delegation).
- **DNS hosting** (a Route 53 **hosted zone**): those name servers answer queries with your records.
- **Delegating** a domain bought elsewhere: create a public hosted zone in Route 53, copy its **4 NS
  records** (they're on different TLDs, e.g. `.com`, `.net`, `.org`, `.co.uk`, for resilience) into the
  registrar's *custom name servers*. Propagation follows the old NS records' TTL (up to 48 h, often minutes).
- Recreating a hosted zone gives **new NS servers**: update the registrar again.

**💡 Example (class demo).** A domain bought at GoDaddy is delegated to Route 53; after updating the
NS at GoDaddy, `dig NS yourdomain.com` returns the four `awsdns` servers.

## 3. Hosted zones: public and private

**🧑 In plain words.** A **public directory** anyone can read, and an **internal directory** only
staff inside the building can read.

**❓ The problem it solves.** Public names for customers, and internal names for services
(`db.internal.corp`) that must never be visible from the internet.

**⚙️ How it works.**

| | Public hosted zone | Private hosted zone |
|---|---|---|
| Answers | the whole internet | only **VPCs associated** with it (any Region/account via authorisation) |
| Needs | delegation from the registrar | the VPC's `enableDnsSupport` and `enableDnsHostnames` |
| Example | `parottasalna.com` | `internal.corp`: `db.internal.corp` → `10.0.2.40` |
| Cost | about $0.50 per zone per month + queries | same |

**Split-horizon DNS:** a public and a private zone with the **same name**, so `api.example.com`
resolves to a private IP inside the VPC and a public one outside.

**💡 Example.** Apps use `postgres.internal.corp` instead of an RDS endpoint; when the database moves,
one record changes, not every app's config.

## 4. Record types, Alias and the zone apex

**🧑 In plain words.** Most entries are phone numbers (A) or "see this other contact" (CNAME). Route
53 adds a smart entry (**Alias**) that **follows an AWS resource's number** even when it changes.

**❓ The problem it solves.** AWS resources like load balancers and CloudFront change IP addresses,
and DNS rules forbid a CNAME at the **zone apex** (the bare `example.com`).

**⚙️ How it works.**

| Record | Points to | Notes |
|---|---|---|
| **A / AAAA** | IPv4 / IPv6 | |
| **CNAME** | another name | **not allowed at the apex**, and nothing else may share its name |
| **Alias** (Route 53) | ALB/NLB, CloudFront, S3 website, API Gateway, Global Accelerator, VPC endpoint, another record in the zone | **works at the apex**, tracks the resource's IPs, **free queries** to AWS targets, TTL taken from the target |
| **MX** | mail servers | priority + host |
| **TXT** | text | verification, SPF/DKIM/DMARC |
| **NS / SOA** | the zone's own servers | created automatically |
| **CAA** | which CAs may issue certificates | e.g. `0 issue "amazon.com"` |

Alias is a **Route 53 feature**, not a DNS record type: it answers as an A/AAAA (or other) record.

**💡 Example.** `parottasalna.com` → **A Alias** to CloudFront (CNAME impossible at apex);
`www.parottasalna.com` → CNAME (or Alias) to `parottasalna.com`.

## 5. Routing policies

**🧑 In plain words.** The operator's **strategy**: always the same number, share callers between
branches, the nearest branch, the backup if the main is closed, by caller's country…

**❓ The problem it solves.** Plain DNS returns the same answer to everyone; real systems need canary
releases, multi-Region speed, disaster recovery and country rules.

**⚙️ How it works.**

| Policy | Answers with… | Use |
|---|---|---|
| **Simple** | one record (may hold several values, returned in random order) | a single resource |
| **Weighted** | records in proportion to weights (e.g. 90 / 10; weight 0 = off) | canary releases, A/B tests, gradual migration |
| **Latency-based** | the Region with the lowest **measured** latency for the user | multi-Region apps |
| **Failover** | **primary** while its health check passes, else **secondary** | active–passive disaster recovery |
| **Geolocation** | by the user's continent / country / (US) state, with a **default** | legal/content rules per country |
| **Geoproximity** | by distance, adjustable with a **bias** (Traffic Flow) | shift traffic between Regions gradually |
| **Multivalue answer** | up to 8 **healthy** records at random | simple client-side load spreading |
| **IP-based** | by the client's IP range (CIDR collections) | ISP- or network-specific routing |

Several policies can be combined in a tree with **Traffic Flow** policies.

**💡 Example.** Weighted records send 95 % of `app.example.com` to the old ALB and 5 % to the new one;
each day the weights move until the new ALB has 100 %, with instant rollback by changing a number.

## 6. Health checks and DNS failover

**🧑 In plain words.** The operator **calls each branch every few seconds** from many cities; if a
branch stops answering, its number is no longer given out.

**❓ The problem it solves.** DNS must stop sending users to a dead site.

**⚙️ How it works.** Health checks run from **many AWS locations** against an endpoint (HTTP, HTTPS
or TCP; optionally searching the response for a string), with an interval (30 s, or 10 s "fast") and
a failure threshold. Types: **endpoint**, **calculated** (combine other checks), and **CloudWatch
alarm** based (useful for private resources). Records with health checks are skipped when unhealthy
(failover, weighted, latency, multivalue, geo…). Alias records can **evaluate target health** instead.

**💡 Example.** Primary ALB in Mumbai, secondary S3 "we'll be back soon" page. When the Mumbai health
check fails 3 times, Route 53 answers with the S3 site until Mumbai recovers.

## 7. Hands-on: point a real domain at AWS

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

## Hands-on exercises

A hosted zone costs a little per month (deleted within 12 hours it's not charged); queries and
health checks cost a little; ⚠️ ALBs and instances cost per hour. A cheap domain (a few hundred
rupees a year) makes these exercises real; without one, you can still do most of them with
`dig @<name-server>`.

**Exercise 1 · Create a hosted zone.** Create a public hosted zone for your domain (or a test name
like `lab-<yourname>.com`). Note its four NS servers.

<details class="solution"><summary>CLI</summary>

```bash
aws route53 create-hosted-zone --name yourdomain.com --caller-reference $(date +%s)
aws route53 get-hosted-zone --id <zone-id> --query 'DelegationSet.NameServers'
```

</details>

**Exercise 2 · Query the zone directly.** Before delegating, add an A record `test → 1.2.3.4` and query
one of the zone's name servers directly.

<details class="solution"><summary>Solution</summary>

```bash
dig @ns-1293.awsdns-33.org test.yourdomain.com A +short    # 1.2.3.4
dig test.yourdomain.com A +short                            # nothing yet (not delegated)
```

</details>

**Exercise 3 · Delegate the domain.** At your registrar, set the four NS values; then check delegation.

<details class="solution"><summary>Check</summary>

`dig NS yourdomain.com +short` returns the four `awsdns` servers; `dig test.yourdomain.com +short`
now returns `1.2.3.4` from anywhere.

</details>

**Exercise 4 · CNAME at the apex.** Try to create a CNAME for the bare domain. What happens?

<details class="solution"><summary>Answer</summary>

Route 53 rejects it: a CNAME can't exist at the zone apex (it would clash with the NS and SOA
records). Use an **Alias** record instead.

</details>

**Exercise 5 · Alias to an ALB.** Point `yourdomain.com` at an ALB with an **A record, Alias = yes**,
and `www` with a CNAME to the apex. Test both.

<details class="solution"><summary>Check</summary>

`dig yourdomain.com +short` returns the ALB's current IPs (one per AZ); `curl -I http://www.yourdomain.com`
returns 200 from your instances.

</details>

**Exercise 6 · Free HTTPS with ACM.** Request an ACM certificate for `yourdomain.com` and
`*.yourdomain.com`, validate by DNS (*Create records in Route 53*), and add it to an HTTPS listener.

<details class="solution"><summary>Check</summary>

The certificate status becomes **Issued** within minutes; `curl -I https://yourdomain.com` works with a
valid certificate.

</details>

**Exercise 7 · Weighted canary.** Create two weighted records for `app.yourdomain.com` (weights 80 and
20) pointing at two different IPs/endpoints. Query 50 times with a low TTL and count.

<details class="solution"><summary>Solution</summary>

```bash
for i in $(seq 50); do dig @<ns> app.yourdomain.com +short; done | sort | uniq -c
```

Roughly 40 / 10. Querying the authoritative server directly avoids resolver caching.

</details>

**Exercise 8 · Health check.** Create an HTTP health check on your ALB's `/health` path. Stop the
instances (or break the path) and watch the status.

<details class="solution"><summary>Check</summary>

Route 53 → Health checks: status goes **Unhealthy** after the failure threshold; the *Health checkers*
tab shows results from many locations.

</details>

**Exercise 9 · Failover.** Create a **failover** pair for `site.yourdomain.com`: primary = ALB (with
the health check), secondary = an **S3 static website** with a maintenance page. Break the primary.

<details class="solution"><summary>What you'll see</summary>

While the primary is healthy, `dig` returns the ALB; after it's marked unhealthy, `dig` returns the
S3 website endpoint and the browser shows the maintenance page. Fix the primary and it switches back.

</details>

**Exercise 10 · Geolocation with a default.** Create geolocation records: **India** → endpoint A,
**Default** → endpoint B. Test with an EDNS client subnet hint.

<details class="solution"><summary>Solution</summary>

```bash
dig @<ns> geo.yourdomain.com +subnet=49.204.0.0/24 +short    # an Indian range → A
dig @<ns> geo.yourdomain.com +subnet=8.8.8.0/24 +short       # US range → B (default)
```

Without a **Default** record, users from unmatched countries get no answer.

</details>

**Exercise 11 · Private hosted zone.** Create a private zone `internal.lab` associated with a lab VPC,
add `db.internal.lab → 10.0.2.40`, and resolve it from an instance and from your laptop.

<details class="solution"><summary>Check</summary>

From the instance: `dig +short db.internal.lab` → `10.0.2.40`. From your laptop: no answer. (The VPC
needs DNS support and DNS hostnames enabled.)

</details>

**Exercise 12 · MX and TXT records.** Add a TXT record `"hello-from-route53"` and an MX record
`10 mail.yourdomain.com`, then check them.

<details class="solution"><summary>Check</summary>

`dig TXT yourdomain.com +short` and `dig MX yourdomain.com +short` return your values (after their TTL
if you changed them).

</details>

**Exercise 13 · Clean up.** Delete health checks, test records, ALB/instances, and (if you don't keep
the domain on Route 53) the hosted zone: delete all records except NS/SOA first.

<details class="solution"><summary>Note</summary>

If the domain stays delegated to this zone, deleting the zone breaks the domain's DNS. Keep the zone
if you'll use the domain.

</details>
