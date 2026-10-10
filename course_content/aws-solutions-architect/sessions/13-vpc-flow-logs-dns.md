# Session 13 · VPC Flow Logs & How DNS Works

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/Qch1QPtXTbg"
  title="Session 13: VPC Flow Logs and how DNS works" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 **Session 13** of the [AWS Solutions Architect playlist](https://www.youtube.com/playlist?list=PLYmjGMwZ9N88) (Tamil) · [watch on YouTube](https://www.youtube.com/watch?v=Qch1QPtXTbg)

## The big idea

Two pieces of network know-how every architect needs:

1. **VPC Flow Logs:** a record of **who talked to whom** in your VPC: source, destination, port,
   bytes, and whether the traffic was **ACCEPTed or REJECTed**. It's how you debug "why can't my app
   reach the database?" and spot suspicious traffic.
2. **DNS:** how a name like `learn.parottasalna.com` becomes an IP address, step by step. Every
   request starts here, and [Route 53](14-route-53.md) builds on it.

**Everyday example:** flow logs are the **visitor register** at a building gate: who came, when,
which floor, and whether security let them in. They don't record what people *said* inside
(packet contents), only the visit.

## Part 1 · VPC Flow Logs

```{raw} html
:file: ../diagrams/s13-flowlogs.html
```

### Where you can turn them on

| Level | Captures |
|---|---|
| **VPC** | every network interface in the VPC |
| **Subnet** | every interface in that subnet |
| **ENI** (network interface) | one instance / load balancer / endpoint |

**Filter:** `ACCEPT`, `REJECT` or `ALL`. **Destinations:** **CloudWatch Logs** (search and alarms;
needs an IAM role), **S3** (cheap storage, query with **Athena**) or **Kinesis Data Firehose**.
Records arrive in batches (aggregation interval 1 or 10 minutes): **not real-time**, and not a
packet capture.

### Reading a record (default format)

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

Someone on the internet tried SSH and was **rejected**: exactly what you want to see.

:::{note}
Flow logs **don't capture** some traffic: queries to the Amazon DNS server, instance metadata
(`169.254.169.254`), Amazon Time Sync, DHCP, and Windows license activation.
:::

### Hands-on: the class lab

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

### Debugging with flow logs

| You see | Likely cause |
|---|---|
| no records at all for the traffic | it never reached the ENI: a route table problem |
| inbound `REJECT` | security group or NACL blocked it |
| inbound `ACCEPT`, outbound reply `REJECT` | a **NACL** blocking the reply's ephemeral port (NACLs are stateless) |
| `ACCEPT` both ways but the app still fails | the network is fine: look at the application |

## Part 2 · How DNS works

```{raw} html
:file: ../diagrams/s13-dns.html
```

1. The browser checks its own cache, then the operating system's (and `/etc/hosts`).
2. It asks a **recursive resolver** (your ISP, `8.8.8.8`, or inside a VPC the **Amazon-provided
   resolver** at the VPC base address +2, e.g. `10.0.0.2`, also reachable at `169.254.169.253`).
3. The resolver asks a **root server**: "who handles `.com`?"
4. Then a **TLD server** for `.com`: "who handles `parottasalna.com`?"
5. Then the domain's **authoritative name server** (e.g. Route 53), which returns the record: `A 13.234.5.6`.
6. The resolver returns the answer and **caches it for the record's TTL** (time to live, in seconds).

Try it yourself:

```bash
dig +trace learn.parottasalna.com          # every step, from the root down
dig learn.parottasalna.com A +short         # just the answer
nslookup -type=NS parottasalna.com          # who is authoritative?
```

| Record | Holds | Example |
|---|---|---|
| **A** / **AAAA** | IPv4 / IPv6 address | `learn → 13.234.5.6` |
| **CNAME** | another name (alias) | `www → learn.parottasalna.com` |
| **NS** | the domain's name servers | `ns-123.awsdns-15.com` |
| **MX** | mail servers | `10 mail.example.com` |
| **TXT** | text: verification, SPF | `"v=spf1 include:_spf.google.com ~all"` |

:::{tip}
**Lower the TTL before a migration.** With a TTL of 86400 (one day), resolvers may keep the old IP
for a day after you change it. Drop it to 60 a day ahead, switch, then raise it again.
:::

## Common mistakes

- **Expecting flow logs to show packet contents or URLs.** They don't; use load balancer access logs or WAF logs.
- **Forgetting the IAM role** for CloudWatch Logs delivery: the flow log shows an error status.
- **Expecting instant logs.** Wait for the aggregation interval plus delivery time.
- **DNS changes "not working"** because the old answer is still cached for its TTL.

## Try it yourself

1. A flow log shows `ACCEPT` for inbound traffic to port 443, but `REJECT` for the outbound reply.
   What's wrong?

   <details class="solution">
   <summary>Answer</summary>

   A **network ACL** is blocking the outbound ephemeral ports (1024–65535). Security groups are
   stateful and would allow the reply automatically; NACLs are not.

   </details>

2. Which flow log destination would you choose to keep a year of logs cheaply and query them now and then?

   <details class="solution">
   <summary>Answer</summary>

   **Amazon S3**, queried with **Athena** (optionally with lifecycle rules to cheaper storage classes).

   </details>

3. Run `dig +trace` for any domain and name the servers at each step.

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
