# Session 5 · Elastic Load Balancer (ELB): Distributing Traffic in AWS

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/F3GMXWbm7Ww"
  title="Session 5: Elastic Load Balancer" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 **Session 5** of the [AWS Solutions Architect playlist](https://www.youtube.com/playlist?list=PLYmjGMwZ9N88) (Tamil) · [watch on YouTube](https://www.youtube.com/watch?v=F3GMXWbm7Ww)

## The big idea

**Elastic Load Balancing** is AWS's managed load balancer: everything HAProxy did in
[Session 4](04-load-balancing-haproxy.md), but AWS runs it across several Availability Zones,
scales it automatically and patches it for you. You choose the **type**, add **listeners**, and
point them at **target groups**.

**Everyday example:** a hospital reception. The receptionist (ALB) reads why you came: "child
fever" goes to paediatrics, "X-ray" goes to radiology. A highway toll booth (NLB) doesn't care
why you're travelling; it just moves cars through as fast as possible.

```{raw} html
:file: ../diagrams/s05-types.html
```

## 1. The three types

| | **ALB** Application | **NLB** Network | **GWLB** Gateway |
|---|---|---|---|
| OSI layer | 7 (HTTP/HTTPS, gRPC, WebSockets) | 4 (TCP, UDP, TLS) | 3 (IP packets) |
| Routes by | path, host name, headers, query, method | port and protocol | sends everything to appliances |
| Targets | EC2, IP, **Lambda** | EC2, IP, ALB | appliance EC2 / IP |
| Special | redirects, fixed responses, user auth (Cognito/OIDC), **WAF** | **static IP per AZ** (or Elastic IP), extreme performance, keeps client IP | GENEVE on port 6081 |
| Typical use | websites, APIs, microservices | games, IoT, non-HTTP, need fixed IPs | third-party firewalls, IDS/IPS |

(The old **Classic Load Balancer** still exists but shouldn't be used for new work.)

## 2. Listeners, rules and target groups

```{raw} html
:file: ../diagrams/s05-alb.html
```

- **Listener:** a protocol and port the load balancer accepts, e.g. `HTTP:80`, `HTTPS:443`.
- **Rules** (ALB): conditions → actions, checked in priority order.
  - **Path-based:** `/api/*` → `api` target group, `/images/*` → `images`.
  - **Host-based:** `api.example.com` → `api`, `www.example.com` → `web`.
  - Actions: forward, **redirect** (e.g. HTTP → HTTPS), fixed response, authenticate.
- **Target group:** a set of targets + a **health check** (path, interval, healthy/unhealthy thresholds).

## 3. Cross-zone load balancing

Without cross-zone, each load balancer node only sends traffic to targets **in its own AZ**. If AZ
a has 2 instances and AZ b has 8, the 2 in AZ a each get 25 % of all traffic while the 8 in AZ b get
6.25 % each. With **cross-zone on**, all 10 instances get 10 % each.

| Type | Cross-zone default | Data transfer between AZs |
|---|---|---|
| ALB | **on** (can be turned off per target group) | no extra charge |
| NLB / GWLB | **off** | charged when turned on |

## 4. Security and TLS

- The ALB has its own **security group**: allow 80/443 from the internet.
- The instances' security group should allow traffic **only from the ALB's security group**, not
  from `0.0.0.0/0`. Users can't bypass the load balancer.
- **TLS termination:** put the certificate (free from **ACM**, AWS Certificate Manager) on the
  HTTPS listener. The ALB decrypts, inspects and forwards to targets over HTTP or HTTPS.
- Add an **HTTP:80 listener that redirects to HTTPS:443**.

## 5. Hands-on: an ALB in front of two EC2 instances

1. Launch two EC2 instances in **different AZs** with this user data:

   ```bash
   #!/bin/bash
   dnf install -y nginx
   echo "<h1>Hello from $(hostname -f)</h1>" > /usr/share/nginx/html/index.html
   systemctl enable --now nginx
   ```

2. **Target group** → type *Instances*, protocol HTTP:80, health check path `/` → register both instances.
3. **Load balancer** → *Application Load Balancer*, internet-facing, pick **two public subnets** in
   two AZs, security group `alb-sg` (80 from anywhere) → listener HTTP:80 → forward to the target group.
4. Change the instances' security group: inbound 80 **from `alb-sg`** only.
5. Wait until both targets are **healthy**, then open the ALB's DNS name and refresh: the host name alternates.

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

**Clean up:** delete the load balancer, then the target group, then terminate the instances.
Load balancers are billed per hour even with no traffic.

## Common mistakes

- **Targets stay "unhealthy":** the instance security group doesn't allow the ALB, or the health
  check path returns 404/302.
- **Only one AZ selected:** an ALB needs at least two subnets in different AZs anyway; use them for
  your targets too.
- **Using the ALB's IP address:** ALB IPs change. Always use its DNS name (or a Route 53 alias, [Session 14](14-route-53.md)).
- **Picking NLB for path-based routing:** NLB doesn't look inside HTTP.

## Try it yourself

1. Which load balancer would you choose for: (a) a REST API with `/users` and `/orders` services,
   (b) a multiplayer game on UDP, (c) traffic inspection by a third-party firewall appliance,
   (d) a partner who must allow-list two fixed IP addresses?

   <details class="solution">
   <summary>Answer</summary>

   (a) ALB, (b) NLB, (c) GWLB, (d) NLB (static or Elastic IPs per AZ).

   </details>

2. Add a listener rule so `/health-check-page` returns a fixed `200 OK` text without reaching the instances.

   <details class="solution">
   <summary>Answer</summary>

   Listener → Rules → Add rule → condition *Path is* `/health-check-page` → action **Return fixed
   response**, 200, text/plain, body `OK`.

   </details>
