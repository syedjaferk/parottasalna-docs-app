# Session 5 · Elastic Load Balancer (ELB): Distributing Traffic in AWS

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/F3GMXWbm7Ww"
  title="Session 5: Elastic Load Balancer" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 **Session 5** of the [AWS Solutions Architect playlist](https://www.youtube.com/playlist?list=PLYmjGMwZ9N88) (Tamil) · [watch on YouTube](https://www.youtube.com/watch?v=F3GMXWbm7Ww)

## What you'll learn

- What **Elastic Load Balancing** adds over running HAProxy yourself
- The three types: **ALB**, **NLB**, **GWLB**, and how to choose
- **Listeners**, **rules**, **target groups**, **targets** and **health checks**
- **Path- and host-based routing**, redirects and fixed responses
- **Cross-zone load balancing**, **connection draining** and **stickiness**
- **Security groups** and **TLS termination** with ACM
- Building an ALB in front of EC2 in two Availability Zones

## 1. Elastic Load Balancing (managed load balancers)

**🧑 In plain words.** In [Session 4](04-load-balancing-haproxy.md) we hired and managed our own
token-machine operator (HAProxy). ELB is a **token service run by the building**: always staffed,
in every wing, and it adds counters automatically on busy days.

**❓ The problem it solves.** A self-run HAProxy is itself a single server: it can fail, needs
patching, must be scaled, and must run in several AZs. You'd need a load balancer for your load balancer.

**⚙️ How it works.** You create a load balancer and choose **subnets in at least two AZs**. AWS
places load balancer **nodes** in each, behind a **DNS name**
(`my-alb-123456.ap-south-1.elb.amazonaws.com`) that resolves to the nodes' IPs. AWS scales the
nodes with traffic, replaces failed ones, and patches them. It integrates with **Auto Scaling**
(new instances register automatically), **ACM** (certificates), **WAF**, **CloudWatch** metrics
and **access logs** to S3. You pay per hour plus **LCUs/NLCUs** (capacity units based on new
connections, active connections, bytes and rule evaluations).

**💡 Example.** A store's Auto Scaling group grows from 2 to 12 instances during a sale. Each new
instance registers with the target group, passes its health check, and starts getting traffic, with
no config changes.

## 2. The three types

```{raw} html
:file: ../diagrams/s05-types.html
```

**🧑 In plain words.** A hospital **receptionist** (ALB) reads why you came and sends you to the
right department. A **highway toll booth** (NLB) doesn't care why you travel; it just moves cars fast.
An **airport security scanner** (GWLB) sends every bag through inspection machines and back.

**❓ The problem it solves.** HTTP websites, raw high-speed TCP/UDP, and traffic inspection are very
different jobs; one design can't be best at all three.

**⚙️ How it works.**

| | **ALB** Application | **NLB** Network | **GWLB** Gateway |
|---|---|---|---|
| OSI layer | 7: HTTP/1.1, HTTP/2, gRPC, WebSockets | 4: TCP, UDP, TLS | 3: IP packets |
| Routes by | path, host, headers, method, query, source IP | listener port/protocol | everything → appliances |
| Targets | EC2, IP, **Lambda**, (ECS tasks) | EC2, IP, **ALB** | appliance EC2 / IP |
| Addresses | DNS name; IPs change | **one static IP per AZ**, or your **Elastic IPs** | used via GWLB endpoints |
| Client IP | `X-Forwarded-For` header | **preserved** for instance targets (or Proxy Protocol v2) | preserved |
| Extras | redirects, fixed responses, Cognito/OIDC login, **WAF** | PrivateLink endpoint services, very high scale | GENEVE (port 6081), transparent bump-in-the-wire |
| Typical use | websites, REST APIs, microservices | games, IoT, financial feeds, non-HTTP, fixed IPs | firewalls, IDS/IPS from vendors |

(The **Classic Load Balancer** is legacy; don't use it for new designs.)

**💡 Example.** A food-delivery company uses an **ALB** for its web and mobile APIs, an **NLB** for
the driver app's real-time TCP stream (partners allow-list its Elastic IPs), and a **GWLB** to send
all traffic through a Palo Alto firewall fleet.

## 3. Listeners, rules, target groups and targets

```{raw} html
:file: ../diagrams/s05-alb.html
```

**🧑 In plain words.** The **listener** is the front door number (443). **Rules** are the signboards
("Accounts → 2nd floor"). A **target group** is a department, and **targets** are the people working there.

**❓ The problem it solves.** One entry point must serve many services, each with its own servers,
ports and health checks.

**⚙️ How it works.**

- **Listener:** protocol + port (`HTTP:80`, `HTTPS:443`). Has a **default action** and, on ALB, ordered **rules**.
- **Rules** (ALB): `IF` conditions (path, host, HTTP header, method, query string, source IP)
  `THEN` actions: **forward** (optionally weighted between target groups), **redirect**,
  **fixed-response**, **authenticate**. Evaluated in **priority order**, lowest number first.
- **Target group:** protocol/port to targets, **health check** settings, **deregistration delay**,
  **stickiness**, algorithm (round robin or least outstanding requests).
- **Target types:** `instance` (by instance ID), `ip` (any IP in the VPC or on-premises), `lambda`, `alb`.

```text
Listener HTTPS:443
  rule 10: host = api.example.com  AND path = /v1/*  → forward tg-api
  rule 20: path = /images/*                          → forward tg-images
  rule 30: path = /old-page                          → redirect 301 to /new-page
  default                                            → forward tg-web
Listener HTTP:80
  default                                            → redirect to HTTPS:443 (301)
```

**💡 Example.** A **weighted forward** sends 90 % of `/` to `tg-web-v1` and 10 % to `tg-web-v2`:
a canary release without DNS changes.

## 4. Health checks in AWS

**🧑 In plain words.** The same manager walking past each counter, but configured per department.

**❓ The problem it solves.** Traffic must only reach targets that can actually serve it.

**⚙️ How it works.** Per target group: protocol, **path** (`/health`), port, **interval** (5–300 s,
default 30), **timeout**, **healthy threshold** (default 5 on ALB), **unhealthy threshold**
(default 2), and **success codes** (`200` or ranges like `200-299`). Target states: `initial`,
`healthy`, `unhealthy`, `draining`, `unused`. If **all** targets are unhealthy, the ALB "fails open"
and sends traffic to all of them.

**💡 Example.** Health check path `/` returns a `302` redirect to `/login` → targets show
**unhealthy** (`Health checks failed with these codes: [302]`). Fix: use a dedicated `/health` path
or allow `200,302`.

## 5. Cross-zone load balancing

**🧑 In plain words.** If each wing's receptionist only sends visitors to counters in their own
wing, a wing with 2 counters gets as many visitors as a wing with 8. Cross-zone lets every
receptionist use **all counters in the building**.

**❓ The problem it solves.** Uneven target counts per AZ cause uneven load.

**⚙️ How it works.** Clients spread across the load balancer's AZ nodes roughly evenly (via DNS).
**Without** cross-zone, each node only uses targets in its own AZ. AZ a has 2 instances and AZ b
has 8: each instance in a gets 25 % of all traffic, each in b gets 6.25 %. **With** cross-zone, all
10 instances get 10 %.

| Type | Default | Inter-AZ data charge |
|---|---|---|
| ALB | **on** (can be turned off per target group) | none |
| NLB / GWLB | **off** | charged when on |

**💡 Example.** After an AZ outage, Auto Scaling replaces instances unevenly (2 in a, 4 in b).
Cross-zone keeps every instance equally busy until the groups rebalance.

## 6. Connection draining and stickiness

**🧑 In plain words.** **Draining:** a counter closing for lunch finishes serving the people already
in front of it, but takes no new tokens. **Stickiness:** a returning customer goes back to the same
counter that has their file open.

**❓ The problem it solves.** Removing a server mid-request would break users' uploads or checkouts;
some old apps keep session state in memory.

**⚙️ How it works.**

- **Deregistration delay** (connection draining), default **300 s**: a deregistering target gets no
  new requests, but in-flight ones may finish. Lower it (e.g. 30 s) for short requests so deploys are faster.
- **Stickiness** (ALB target group): a **duration-based** cookie (`AWSALB`) or an **application cookie**
  you choose. Prefer stateless apps; use stickiness only when needed.

**💡 Example.** A rolling deployment deregisters instance 1; for 30 s it finishes current requests,
then it's replaced. Users never see an error.

## 7. Security groups and TLS

**🧑 In plain words.** The front gate (load balancer) is open to the public; the office doors
(instances) only open for people the front gate sends in. And the conversation is in a locked
envelope (TLS) until it reaches the front gate.

**❓ The problem it solves.** Users shouldn't be able to bypass the load balancer, and traffic must
be encrypted without installing certificates on every server.

**⚙️ How it works.**

- **ALB security group** (`alb-sg`): inbound 80/443 from `0.0.0.0/0` (or a narrower range).
- **Instance security group**: inbound app port **from `alb-sg` only**, never from the internet.
- **TLS termination:** request a free certificate in **ACM** (validated by DNS), attach it to the
  HTTPS listener with a **security policy** (allowed TLS versions/ciphers). Several certificates can
  share one listener (**SNI**). Re-encrypt to targets with an HTTPS target group if required.
- NLBs got security group support too (for new NLBs); with TLS listeners they also terminate TLS.

**💡 Example.** An audit requires TLS 1.2+ only: choose a listener security policy like
`ELBSecurityPolicy-TLS13-1-2-2021-06` and add an HTTP→HTTPS redirect on port 80.

## 8. Hands-on: an ALB in front of two EC2 instances

1. Launch two EC2 instances in **different AZs** (public subnets for this lab) with this user data:

   ```bash
   #!/bin/bash
   dnf install -y nginx
   echo "<h1>Hello from $(hostname -f)</h1>" > /usr/share/nginx/html/index.html
   systemctl enable --now nginx
   ```

2. **Target group** → type *Instances*, HTTP:80, health check path `/` → register both instances.
3. **Load balancer** → *Application Load Balancer*, internet-facing, **two public subnets** in two
   AZs, security group `alb-sg` (80 from anywhere) → listener HTTP:80 → forward to the target group.
4. Change the instances' security group: inbound 80 **from `alb-sg`** only.
5. Wait until both targets are **healthy**, then refresh the ALB's DNS name: the host name alternates.

```bash
for i in 1 2 3 4; do curl -s http://my-alb-123456.ap-south-1.elb.amazonaws.com; done
```

**Output (example):**

```text
<h1>Hello from ip-10-0-1-25.ap-south-1.compute.internal</h1>
<h1>Hello from ip-10-0-2-48.ap-south-1.compute.internal</h1>
<h1>Hello from ip-10-0-1-25.ap-south-1.compute.internal</h1>
<h1>Hello from ip-10-0-2-48.ap-south-1.compute.internal</h1>
```

⚠️ **Clean up:** delete the load balancer, then the target group, then terminate the instances.
Load balancers are billed per hour even with no traffic.

## Common mistakes

- **Targets stay "unhealthy":** the instance security group doesn't allow `alb-sg`, or the health
  check path returns 404/302.
- **Using the ALB's IP address:** ALB IPs change. Use its DNS name or a Route 53 Alias ([Session 14](14-route-53.md)).
- **Choosing NLB for path-based routing:** NLB doesn't read HTTP.
- **Leaving deregistration delay at 300 s** for an API whose requests take 100 ms: deploys crawl.
- **Opening instance ports to `0.0.0.0/0`**, so users can bypass the ALB (and WAF).

## Hands-on exercises

⚠️ ALBs, NLBs and EC2 instances cost money per hour. Do the exercises in one sitting and clean up at the end.

**Exercise 1 · Your first ALB.** Build the ALB from section 8 and confirm the host name alternates.

<details class="solution"><summary>Check</summary>

Target group → **Targets** tab shows both `healthy`; repeated `curl` to the DNS name alternates
between the two instances' host names.

</details>

**Exercise 2 · Lock down the instances.** Make the instances accept HTTP **only** from the ALB, then
prove you can't reach an instance's public IP directly.

<details class="solution"><summary>Solution</summary>

Instance SG inbound: HTTP 80, source **`alb-sg`** (remove `0.0.0.0/0`). `curl --max-time 5 http://<instance-public-ip>`
now times out, while the ALB DNS name still works.

</details>

**Exercise 3 · Break a health check.** Set the health check path to `/health`. What happens to the
targets and to the site? Then fix it.

<details class="solution"><summary>Answer</summary>

nginx returns 404 for `/health`, so targets turn **unhealthy**. With all targets unhealthy the ALB
fails open, so the site may still load, but the target group shows the failure reason. Fix:
create `/usr/share/nginx/html/health` on each instance, or set the path back to `/`.

</details>

**Exercise 4 · Path-based routing.** Create a second target group `tg-api` with one new instance whose
page says "API". Add a listener rule: path `/api/*` → `tg-api`.

<details class="solution"><summary>Check</summary>

`curl <alb>/api/test` returns "API" (create `/usr/share/nginx/html/api/test` on that instance);
`curl <alb>/` still alternates between the web instances.

</details>

**Exercise 5 · Host-based routing.** Add a rule: host header `admin.example.com` → fixed response
`403 Admins only`. Test without owning the domain.

<details class="solution"><summary>Solution</summary>

```bash
curl -s -H "Host: admin.example.com" http://<alb-dns>/
```

Returns `Admins only` with status 403; other hosts still reach the web targets.

</details>

**Exercise 6 · Redirect HTTP to HTTPS.** If you have a domain, request an ACM certificate (DNS
validation), add an HTTPS:443 listener with it, and change the HTTP:80 listener to a **301 redirect** to HTTPS.

<details class="solution"><summary>Check</summary>

`curl -sI http://yourdomain` shows `HTTP/1.1 301` with `Location: https://yourdomain:443/`.
The ALB security group must allow 443. (No domain? Do the redirect part with a fixed response instead.)

</details>

**Exercise 7 · Weighted canary.** Create `tg-v2` with an instance showing "v2". Change the default
action to forward **90 % to tg-web, 10 % to tg-v2**. Send 100 requests and count.

<details class="solution"><summary>Solution</summary>

```bash
for i in $(seq 100); do curl -s http://<alb-dns>/; done | grep -c v2
```

Roughly 10 (it's probabilistic).

</details>

**Exercise 8 · Stickiness.** Enable stickiness (load balancer–generated cookie, 1 minute) on `tg-web`.
Test with curl and a cookie jar.

<details class="solution"><summary>Solution</summary>

```bash
curl -s -c jar http://<alb-dns>/ ; for i in 1 2 3; do curl -s -b jar http://<alb-dns>/; done
```

With the `AWSALB` cookie, all responses come from the same instance; without `-b jar` they alternate.

</details>

**Exercise 9 · Draining in action.** Set the deregistration delay to 30 s. Deregister one instance
while running `while true; do curl -s <alb-dns>; sleep 0.5; done`. What do you see?

<details class="solution"><summary>Answer</summary>

The target shows **draining** for ~30 s; new requests go only to the other instance, and no errors
appear. After 30 s it shows **unused**.

</details>

**Exercise 10 · Access logs.** Enable ALB **access logs** to an S3 bucket (the bucket policy must allow
the ELB log delivery service). Generate traffic, wait ~5 minutes, and read a log line.

<details class="solution"><summary>What you'll see</summary>

Gzipped files under `AWSLogs/<account>/elasticloadbalancing/ap-south-1/…`. Each line has the time,
client IP:port, target IP:port, processing times, status codes, bytes, and the request line, e.g.
`"GET http://my-alb…:80/ HTTP/1.1"`.

</details>

**Exercise 11 · CloudWatch metrics.** Find `RequestCount`, `TargetResponseTime`,
`HTTPCode_Target_5XX_Count` and `HealthyHostCount` for your ALB. Create an alarm when
`HealthyHostCount < 2` for 2 minutes.

<details class="solution"><summary>Where</summary>

CloudWatch → Metrics → **ApplicationELB** → Per AppELB (or per target group) metrics. Alarms →
Create alarm → `HealthyHostCount` (target group dimension) → *Lower than 2* → 2 datapoints of 1 minute.

</details>

**Exercise 12 · Try an NLB.** Create an internet-facing **NLB** with a TCP:80 listener to the same
instances. Compare: does `dig <nlb-dns>` return stable IPs? Does the instance see the real client IP?

<details class="solution"><summary>Answer</summary>

`dig` returns **one fixed IP per AZ** that doesn't change (you could also attach Elastic IPs at
creation). For instance targets, nginx's access log shows **your real public IP**, not the load
balancer's. ⚠️ Delete the NLB afterwards.

</details>

**Exercise 13 · Clean up and verify.** Delete the load balancers, target groups and instances, then
confirm nothing billable is left.

<details class="solution"><summary>Check</summary>

EC2 → Load balancers (empty), Target groups (empty), Instances (terminated). Tomorrow, check
Billing → Bills for the ELB line items stopping.

</details>
