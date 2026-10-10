# Session 13 · VPC Flow Logs & How DNS Works

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/Qch1QPtXTbg"
  title="Session 13: VPC Flow Logs and how DNS works" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 **Session 13** of the [AWS Solutions Architect playlist](https://www.youtube.com/playlist?list=PLYmjGMwZ9N88) (Tamil) · [watch on YouTube](https://www.youtube.com/watch?v=Qch1QPtXTbg)

## What you'll learn

- What **VPC Flow Logs** record (and what they don't), and the problem they solve
- Flow log **levels**, **filters**, **destinations** and the **record format**
- Debugging connectivity with flow logs, and querying them with **Logs Insights** / **Athena**
- **DNS** from scratch: why names exist, and how a name becomes an IP step by step
- **Record types**, **TTL** and caching
- How DNS works **inside a VPC** (the Amazon resolver, DNS settings, Route 53 Resolver)

## 1. VPC Flow Logs: the network's visitor register

```{raw} html
:file: ../diagrams/s13-flowlogs.html
```

**🧑 In plain words.** The **visitor register at a building gate**: who came, from where, to which
floor, when, and whether security let them in. It doesn't record what people *said* inside.

**❓ The problem it solves.**

- "Why can't my app reach the database?" Without flow logs you're guessing between routes, security
  groups, NACLs and the app itself.
- "Is someone scanning or attacking us?" You need evidence of who knocked on which port.
- Compliance and forensics: keeping a record of network connections.

**⚙️ How it works.** Flow logs capture **IP traffic metadata** (not packet contents) for network
interfaces, aggregate it into records over an **aggregation interval** (1 or 10 minutes), and deliver
the records to a destination. They're collected outside your instances, so they **don't affect
network performance**. Not real-time: allow several minutes for delivery.

**💡 Example.** A developer says "the API can't reach Postgres". The flow log on the DB's interface
shows `10.0.1.25 → 10.0.2.40:5432 REJECT`: the database security group is missing a rule. Found in two minutes.

## 2. Levels, filters, destinations and the record format

**🧑 In plain words.** You can keep a register for the **whole complex**, **one block**, or **one
door**; record **everyone**, only those **let in**, or only those **turned away**; and file it in a
**searchable logbook** or a **cheap archive**.

**❓ The problem it solves.** Matching cost and detail to the need.

**⚙️ How it works.**

| Choice | Options |
|---|---|
| **Level** | **VPC** (every ENI), **subnet** (every ENI in it), **ENI** (one interface: an instance, load balancer, endpoint, NAT Gateway…). Also Transit Gateway flow logs. |
| **Filter** | `ACCEPT`, `REJECT` or `ALL` |
| **Interval** | 1 minute or 10 minutes |
| **Destination** | **CloudWatch Logs** (search, metric filters, alarms; needs an IAM role), **S3** (cheap; query with **Athena**), **Kinesis Data Firehose** (stream to tools like OpenSearch or Splunk) |
| **Format** | default (version 2 fields) or **custom** fields: `vpc-id`, `subnet-id`, `instance-id`, `tcp-flags`, `pkt-srcaddr`/`pkt-dstaddr` (original IPs behind a NAT), `flow-direction`, `traffic-path`… |

**Reading a default record:**

```text
2 111122223333 eni-0a1b2c3d 203.0.113.50 10.0.1.25 51544 22 6 3 180 1760103000 1760103060 REJECT OK
```

| Field | Value | Meaning |
|---|---|---|
| version, account | `2 111122223333` | format version, AWS account |
| interface | `eni-0a1b2c3d` | the network card |
| srcaddr → dstaddr | `203.0.113.50 → 10.0.1.25` | who → whom |
| srcport → dstport | `51544 → 22` | port 22 = SSH |
| protocol | `6` | TCP (17 = UDP, 1 = ICMP) |
| packets, bytes | `3 180` | how much |
| start, end | Unix timestamps | the capture window |
| **action** | **`REJECT`** | blocked by a security group or NACL |
| log-status | `OK` | `NODATA` / `SKIPDATA` when nothing or some was lost |

**Not captured:** traffic to the Amazon DNS server, instance metadata (`169.254.169.254`), Amazon
Time Sync (`169.254.169.123`), DHCP, Windows license activation, and mirrored traffic.

**💡 Example.** For a cheap year-long archive: VPC-level, filter ALL, 10-minute interval, delivered to
S3 in Parquet with hourly partitions, queried with Athena when needed.

## 3. Debugging with flow logs

**🧑 In plain words.** Reading the register like a detective: "they reached the gate but were turned
away", "they got in but never came back out", "they never arrived at all".

**❓ The problem it solves.** Pinpointing **which layer** is breaking a connection.

**⚙️ How it works.**

| You see | Likely cause |
|---|---|
| no records at all for the traffic | it never reached the ENI: a **route table** problem (or wrong IP/DNS) |
| inbound `REJECT` | **security group or NACL** blocked it |
| inbound `ACCEPT`, outbound reply `REJECT` | a **NACL** blocking the reply's **ephemeral port** (NACLs are stateless) |
| `ACCEPT` both ways but the app still fails | the network is fine: look at the **application** (wrong port, app down, TLS) |
| lots of `REJECT` from many IPs on 22/3389 | internet scanners: normal noise, but proof the port was exposed |

**💡 Example.** CloudWatch **Logs Insights** query for the top rejected sources:

```text
fields @timestamp, srcAddr, dstAddr, dstPort, action
| filter action = "REJECT"
| stats count(*) as attempts by srcAddr, dstPort
| sort attempts desc
| limit 10
```

## 4. DNS: names instead of numbers

**🧑 In plain words.** Your phone's **contacts list**. You remember "Amma", not 98xxxxxxxx. DNS is the
internet's contacts list: `learn.parottasalna.com` → `13.234.5.6`.

**❓ The problem it solves.** Humans can't remember IPs, and IPs **change** (new servers, load
balancers, failover). Names stay the same while the addresses behind them move.

**⚙️ How it works.** DNS is a **distributed, hierarchical database**. No single server knows every
name; each level knows who is responsible for the next level down:

```text
.  (root)  →  com.  (TLD)  →  parottasalna.com.  (authoritative)  →  learn.parottasalna.com  A 13.234.5.6
```

It mostly uses **UDP port 53** (TCP for large answers and zone transfers). Answers are **cached**
everywhere (browser, OS, resolver) for the record's **TTL**, which is why DNS is fast at internet scale.

**💡 Example.** You move the site to a new server; you only update **one DNS record**, and users keep
typing the same name.

## 5. How a lookup works, step by step

```{raw} html
:file: ../diagrams/s13-dns.html
```

**🧑 In plain words.** You ask the **librarian** (resolver) for a book. The librarian asks the
**main catalogue** (root) which section, then the **section desk** (TLD) which shelf, then the
**shelf owner** (authoritative server), and remembers the answer for next time.

**❓ The problem it solves.** Finding the right answer among millions of domains without any central bottleneck.

**⚙️ How it works.**

1. The browser checks its own cache, then the operating system's (and `/etc/hosts`).
2. It asks a **recursive resolver**: your ISP, `8.8.8.8`, `1.1.1.1`, or inside a VPC the **Amazon
   resolver** at the VPC base +2 (e.g. `10.0.0.2`, also `169.254.169.253`).
3. The resolver asks a **root server**: "who handles `.com`?" → a referral to the `.com` servers.
4. It asks a **TLD server**: "who handles `parottasalna.com`?" → a referral to the domain's **NS records**.
5. It asks the domain's **authoritative name server** (e.g. Route 53), which returns the record:
   `learn.parottasalna.com. 300 IN A 13.234.5.6`.
6. The resolver returns the answer and **caches it for the TTL** (300 s here).

```bash
dig +trace learn.parottasalna.com          # every step, from the root down
dig learn.parottasalna.com A +short         # just the answer
dig NS parottasalna.com +short              # who is authoritative?
```

**💡 Example.** The first visitor of the day waits ~100 ms for the full lookup; everyone using the same
resolver after them gets the cached answer in ~1 ms until the TTL expires.

## 6. Record types and TTL

**🧑 In plain words.** Different **kinds of contact entries**: a phone number, a "see this other
contact", the address for letters (mail), a note.

**❓ The problem it solves.** One name can have several kinds of information.

**⚙️ How it works.**

| Record | Holds | Example |
|---|---|---|
| **A** / **AAAA** | IPv4 / IPv6 address | `learn → 13.234.5.6` |
| **CNAME** | another name (an alias) | `www → learn.parottasalna.com` |
| **NS** | the domain's name servers | `ns-123.awsdns-15.com` |
| **SOA** | start of authority: primary server, serial, negative-cache TTL | created automatically |
| **MX** | mail servers, with priority | `10 mail.example.com` |
| **TXT** | text: domain verification, SPF, DKIM | `"v=spf1 include:_spf.google.com ~all"` |
| **SRV / CAA / PTR** | services, allowed certificate authorities, reverse lookup | |

**TTL** (time to live, seconds) says how long others may cache the record. Low TTL (60) = changes
spread fast, more queries. High TTL (86400) = fewer queries, but changes take up to a day to be seen everywhere.

**💡 Example.** Before migrating the site, lower the TTL from 86400 to 60 a day ahead; switch the IP;
everyone sees the new IP within a minute; then raise the TTL again.

## 7. DNS inside a VPC

**🧑 In plain words.** The complex has its **own internal directory desk** that knows both the
outside world's numbers and the internal flat numbers.

**❓ The problem it solves.** Instances need to resolve internet names, AWS service names, internal
host names and private domains, without managing DNS servers.

**⚙️ How it works.**

- The **Route 53 Resolver** (the "Amazon-provided DNS") answers at **VPC base +2** and `169.254.169.253`.
- Two VPC settings: **`enableDnsSupport`** (the resolver works) and **`enableDnsHostnames`**
  (instances get DNS names like `ip-10-0-1-25.ap-south-1.compute.internal` and public DNS names).
- **Private hosted zones** ([Session 14](14-route-53.md)) give your own internal names (`db.internal.corp`).
- **Resolver endpoints** (inbound/outbound) and **forwarding rules** connect VPC DNS with on-premises
  DNS servers; **Route 53 Resolver DNS Firewall** can block lookups of malicious domains.
- Interface endpoints with **private DNS** rely on this resolver ([Session 11](11-vpc-endpoints.md)).

**💡 Example.** `dig db.internal.corp` on an EC2 instance returns `10.0.2.40` from a private hosted
zone, while the same name from your laptop returns nothing.

## 8. Hands-on: the class lab (flow logs)

The class lab (Pulumi program in the class files) builds a **web** instance in a public subnet
(port 80) that calls a **backend** API in a private subnet (port 5000, allowed only from the web
security group). The flow log is created by hand:

1. `pulumi up`, then open the web instance's URL: the page shows JSON from the private backend.
2. *VPC → your VPC → Flow logs → Create*: filter **All**, interval **1 minute**, destination
   **CloudWatch Logs**, log group `/vpc/flowlogs-demo`, IAM role with `logs:CreateLogStream` and
   `logs:PutLogEvents` (the console can create it).
3. Generate traffic: refresh the page a few times; also try `curl --max-time 5 http://<web-ip>:5000`
   from your laptop (blocked).
4. After a couple of minutes, open **CloudWatch → Logs Insights** on the log group:

```text
fields @timestamp, srcAddr, dstAddr, dstPort, action
| filter action = "REJECT"
| stats count(*) as attempts by srcAddr, dstPort
| sort attempts desc
| limit 10
```

You'll see your laptop's attempt on port 5000, and probably random internet scanners knocking on
port 22: every public IP gets scanned within minutes.

**Clean up:** delete the flow log, then `pulumi destroy`, then delete the log group.

## Common mistakes

- **Expecting flow logs to show packet contents or URLs.** They don't; use load balancer access logs or WAF logs.
- **Forgetting the IAM role** for CloudWatch Logs delivery: the flow log shows an error status.
- **Expecting instant logs.** Wait for the aggregation interval plus delivery time.
- **DNS changes "not working"** because the old answer is still cached for its TTL.

## Hands-on exercises

Flow logs are charged for data ingested into CloudWatch Logs or S3; ⚠️ EC2 instances (the class lab
creates two) cost money. Run `pulumi destroy` and delete the log group at the end. The DNS exercises are free.

**Exercise 1 · Deploy the class lab.** `pulumi up` the flow-logs program and open the web URL.

<details class="solution"><summary>Check</summary>

The page shows JSON fetched from the private backend (`10.0.2.x:5000`). `pulumi stack output` lists
`web_url`, `web_eni_id`, `backend_eni_id`.

</details>

**Exercise 2 · Create a VPC flow log to CloudWatch.** Filter *All*, interval *1 minute*, log group
`/vpc/flowlogs-demo`, and let the console create the IAM role.

<details class="solution"><summary>CLI alternative</summary>

```bash
aws ec2 create-flow-logs --resource-type VPC --resource-ids $VPC --traffic-type ALL \
    --log-destination-type cloud-watch-logs --log-group-name /vpc/flowlogs-demo \
    --deliver-logs-permission-arn arn:aws:iam::<acct>:role/flowlogs-role --max-aggregation-interval 60
```

</details>

**Exercise 3 · Find your own requests.** Refresh the web page a few times, wait 2–5 minutes, and find
records with your laptop's public IP and destination port 80.

<details class="solution"><summary>Logs Insights</summary>

```text
fields @timestamp, srcAddr, dstAddr, dstPort, action
| filter srcAddr = "<your-public-ip>" and dstPort = 80
| sort @timestamp desc
```

Note that `dstAddr` is the instance's **private** IP: the IGW translated the public IP.

</details>

**Exercise 4 · See a REJECT.** From your laptop, try `curl --max-time 5 http://<web-ip>:5000`. Find the REJECT record.

<details class="solution"><summary>Answer</summary>

A record `your-ip → 10.0.1.x:5000 ... REJECT`: port 5000 isn't open to the internet on the web SG.

</details>

**Exercise 5 · Web → backend traffic.** Find the web tier's calls to the backend on port 5000. Are they ACCEPT?

<details class="solution"><summary>Query</summary>

```text
fields srcAddr, dstAddr, dstPort, action | filter dstPort = 5000 and action = "ACCEPT"
```

`10.0.1.x → 10.0.2.x:5000 ACCEPT`: allowed by the backend SG rule that references the web SG.

</details>

**Exercise 6 · Internet noise.** Count rejected attempts on port 22 from the internet over the last hour.

<details class="solution"><summary>Query</summary>

```text
filter action = "REJECT" and dstPort = 22 | stats count(*) as attempts by srcAddr | sort attempts desc
```

Every public IP gets scanned within minutes of launch: a good reason to keep port 22 closed.

</details>

**Exercise 7 · Break it with a NACL.** Add a NACL rule on the backend subnet that denies **outbound**
ephemeral ports (1024–65535) to the web subnet. Reload the page and read the flow logs.

<details class="solution"><summary>What you'll see</summary>

The page shows *Backend unreachable*. Flow logs show the request to `:5000` **ACCEPT** inbound but the
reply **REJECT** outbound: the stateless NACL signature. Remove the rule.

</details>

**Exercise 8 · Flow logs to S3 + Athena (optional).** Create a second flow log to an S3 bucket,
create an Athena table (the console's *Generate Athena integration* helps), and count REJECTs per port.

<details class="solution"><summary>Query idea</summary>

```sql
SELECT dstport, count(*) AS rejects
FROM vpc_flow_logs WHERE action = 'REJECT'
GROUP BY dstport ORDER BY rejects DESC LIMIT 10;
```

</details>

**Exercise 9 · Trace a DNS lookup.** Run `dig +trace` for a domain you know. Write down the root, TLD
and authoritative servers it used.

<details class="solution"><summary>What to look for</summary>

Lines from `a.root-servers.net` (root), `*.gtld-servers.net` (`.com` TLD), then the domain's NS
(e.g. `ns-xxx.awsdns-xx.org` for Route 53).

</details>

**Exercise 10 · Watch the TTL count down.** Run `dig google.com A` twice, 10 seconds apart, against the
same resolver. What happens to the TTL number?

<details class="solution"><summary>Answer</summary>

It **decreases** between runs: the resolver is serving its cached answer and counting down until it must ask again.

</details>

**Exercise 11 · DNS inside the VPC.** On the web instance, run `cat /etc/resolv.conf` and
`dig +short $(hostname)`. Which resolver is used? What does the private name resolve to?

<details class="solution"><summary>Answer</summary>

`nameserver 10.0.0.2` (VPC base +2), and the private host name resolves to the instance's `10.0.1.x` address.

</details>

**Exercise 12 · Record types.** Use `dig` to find the MX, TXT and NS records of a domain you use (e.g. your college or company).

<details class="solution"><summary>Commands</summary>

```bash
dig MX example.com +short
dig TXT example.com +short
dig NS example.com +short
```

</details>

**Exercise 13 · Clean up.** Delete the flow logs, the log group and any S3 test bucket, then `pulumi destroy`.

<details class="solution"><summary>Check</summary>

VPC → Flow logs: none. CloudWatch → Log groups: `/vpc/flowlogs-demo` gone. `pulumi stack output` shows nothing.

</details>

## Class files

<details class="source">
<summary>__main__.py (Pulumi: web + private backend for the flow logs lab)</summary>

```{literalinclude} ../code/13-flow-logs-pulumi/__main__.py
:language: python
```

</details>

- Downloads: {download}`__main__.py <../code/13-flow-logs-pulumi/__main__.py>` ·
  {download}`Pulumi.yaml <../code/13-flow-logs-pulumi/Pulumi.yaml>` ·
  {download}`requirements.txt <../code/13-flow-logs-pulumi/requirements.txt>` ·
  {download}`commands <../code/13-flow-logs-pulumi/commands.txt>`
