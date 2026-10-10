# Session 4 · Load Balancing Explained: HAProxy Demo (Local Setup)

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/RUuR__pxzbw"
  title="Session 4: Load balancing with HAProxy" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 **Session 4** of the [AWS Solutions Architect playlist](https://www.youtube.com/playlist?list=PLYmjGMwZ9N88) (Tamil) · [watch on YouTube](https://www.youtube.com/watch?v=RUuR__pxzbw)

## What you'll learn

- Why a single server isn't enough, and what a **load balancer** fixes
- **Scaling up vs scaling out**
- Balancing **algorithms** (round robin, least connections, source hash, weighted) and when each wins
- **Health checks**: how a load balancer notices a dead server, and the gap before it does
- **Layer 4 vs layer 7** load balancing
- **Sticky sessions** and why stateless apps are easier
- Running it all locally with **HAProxy**, then mapping each idea to AWS ([Session 5](05-elastic-load-balancer.md))

```{raw} html
:file: ../diagrams/s04-haproxy.html
```

## 1. The load balancer

**🧑 In plain words.** A bank with several counters and one **token machine**. You don't choose a
counter; the token system sends you to the next free one. If a counter closes for lunch, no tokens
go there. Customers only see the token machine, never the back office.

**❓ The problem it solves.**

- **One server has a limit:** CPU, memory and connections run out as users grow.
- **One server is a single point of failure:** it crashes, reboots for patches, or its disk fills,
  and the whole site is down.
- **Deployments cause downtime** if there's only one copy to update.
- **Clients would need to know every server's address**, and update it whenever servers change.

**⚙️ How it works.** The load balancer owns a public address (an IP or DNS name). For each incoming
connection or request it:

1. picks a **healthy** backend using an **algorithm**,
2. opens (or reuses) a connection to that backend and **forwards** the request,
3. relays the response back to the client.

It keeps a **health state** for every backend, can **terminate TLS** (decrypt HTTPS once, centrally),
add headers like `X-Forwarded-For` (the client's real IP), and expose **metrics** (requests,
errors, latency per backend).

**💡 Example.** `learn.example.com` points at the load balancer. Behind it run three copies of the
app. On deploy day you remove one copy, update it, put it back, and repeat: users never see an outage.

## 2. Scaling up vs scaling out

**🧑 In plain words.** A restaurant that's too busy can buy a **bigger stove** (scale up) or hire
**more cooks with more stoves** (scale out). Only the second keeps cooking when one stove breaks.

**❓ The problem it solves.** Deciding how to grow without hitting a ceiling or a single point of failure.

**⚙️ How it works.**

| | Scale up (vertical) | Scale out (horizontal) |
|---|---|---|
| How | bigger machine (more CPU/RAM) | more machines behind a load balancer |
| Limit | the biggest instance size | practically unlimited |
| Downtime to grow | usually a restart | none: add machines live |
| Failure | one machine = one point of failure | survives losing machines |
| Needs | nothing special | a load balancer + a **stateless** app |

**💡 Example.** A Python API maxes out a 2-CPU server at 400 requests/second. Instead of moving to a
64-CPU machine, you run five 2-CPU copies behind HAProxy for ~2,000 req/s, and add a sixth on sale days.

## 3. Balancing algorithms

**🧑 In plain words.** Different ways the token machine decides: **take turns**, **send to the
least busy counter**, **regular customers always go to the same counter**, or **send more people to
the counter with two clerks**.

**❓ The problem it solves.** Requests and servers differ. A bad choice overloads one server while
others sit idle.

**⚙️ How it works.**

| Algorithm | HAProxy | How it picks | Best for | Watch out |
|---|---|---|---|---|
| **Round robin** | `balance roundrobin` | 1, 2, 3, 1, 2, 3… | similar servers, short similar requests | a few slow requests can pile up on one server |
| **Weighted round robin** | `weight 5` per server | in proportion to weights | servers of different sizes, canary releases | weights must be kept in sync with sizes |
| **Least connections** | `balance leastconn` | fewest open connections right now | long or uneven requests, WebSockets, DB proxies | needs live connection counts |
| **Source / IP hash** | `balance source` | hash of client IP → same server | simple stickiness without cookies | uneven if many users share one IP (offices, mobile NAT) |
| **URI hash** | `balance uri` | hash of the path → same server | caches (same file always on same cache) | hot paths overload one server |

**💡 Example.** A video transcoding API where some calls take 2 seconds and others 2 minutes: with round
robin, one unlucky server gets three 2-minute jobs while another is idle. **Least connections** sends the
next job to the server that's actually free.

## 4. Health checks

**🧑 In plain words.** The manager **walks past each counter every few seconds** asking "are you OK?".
A clerk who doesn't answer three times is marked closed; after answering twice they're open again.

**❓ The problem it solves.** Servers fail silently: the process crashes, the database connection
breaks, a disk fills. Without checks, the load balancer keeps sending users to a dead server.

**⚙️ How it works.**

- **Active checks:** the balancer calls each backend on a schedule. HAProxy: `option httpchk GET /health`,
  `check inter 5s fall 3 rise 2` = check every 5 s, **down after 3 failures**, **up after 2 successes**.
- **Passive checks:** watching real traffic for errors and timeouts.
- **Detection time** ≈ `inter × fall` (5 s × 3 = ~15 s). During that window some requests can fail,
  which is why `retries` + `option redispatch` exist (retry on another server).
- A good `/health` endpoint checks **what the app needs to serve** (e.g. it can reach its database),
  but stays **cheap and fast**, and doesn't fail because of an optional dependency.

**💡 Example.** In the class demo, `docker stop app3` caused one `503` immediately, then after ~15 s app3
was marked DOWN and every request went to app1 and app2 without errors (see the hands-on below).

## 5. Layer 4 vs layer 7

**🧑 In plain words.** A **layer 4** balancer is a postman who only reads the **address on the
envelope**. A **layer 7** balancer **opens the letter** and reads what it says before deciding where it goes.

**❓ The problem it solves.** Sometimes you just need fast forwarding of any TCP/UDP traffic;
sometimes you need decisions based on URLs, hosts or headers.

**⚙️ How it works.**

| | Layer 4 (TCP/UDP) | Layer 7 (HTTP) |
|---|---|---|
| Sees | IPs and ports | method, path, host, headers, cookies |
| Can route by | port only | `/api/*`, `api.example.com`, headers |
| Speed | extremely fast, minimal processing | more work per request |
| TLS | usually passed through | usually terminated (decrypted) here |
| HAProxy | `mode tcp` | `mode http` |
| AWS | **Network Load Balancer** | **Application Load Balancer** |

**💡 Example.** A PostgreSQL proxy or a game server on UDP → layer 4. A website where `/api` goes to
Python services and `/images` to an image service → layer 7.

## 6. Sticky sessions and stateless apps

**🧑 In plain words.** If your **shopping cart is kept at one counter**, every visit must go back to
that counter. If the cart is kept in a **shared locker** anyone can open, any counter can serve you.

**❓ The problem it solves.** Apps that keep login sessions or carts in a server's memory break under
round robin: the next request lands on another server and the user looks "logged out".

**⚙️ How it works.**

- **Stickiness (session affinity):** the balancer pins a client to one server, by cookie
  (`cookie SERVERID insert` in HAProxy; *stickiness* on an AWS target group) or by source IP.
- **Downsides:** uneven load, and users still lose their session when "their" server dies.
- **Better:** make the app **stateless**: keep sessions in **Redis/ElastiCache**, a database, or a
  signed cookie/JWT, so any server can serve any request.

**💡 Example.** A Django app moved sessions from local memory to Redis: stickiness could be turned
off, load evened out, and deploys stopped logging people out.

## 7. Hands-on: HAProxy in front of three apps (class code)

The class demo runs three identical **FastAPI** apps and HAProxy with **Docker Compose**. Each app
says which server answered and has a `/health` endpoint:

```python
@app.get("/")
def home():
    return {"server": "app1", "hostname": socket.gethostname()}

@app.get("/health")
def health():
    return {"status": "UP"}
```

`haproxy/round_robin.cfg` (the other files only change the `balance` line and weights):

```text
frontend web
    bind *:80
    default_backend apps

backend apps
    balance roundrobin
    option httpchk GET /health
    server app1 app1:8000 check inter 5s
    server app2 app2:8000 check inter 5s
    server app3 app3:8000 check inter 5s

listen stats
    bind *:8404
    stats enable
    stats uri /
    stats refresh 5s
```

Point `docker-compose.yml` at the config you want to try, then start everything:

```bash
docker compose up -d --build
for i in 1 2 3 4 5 6; do curl -s localhost:8081/; echo; done
```

**Output** (round robin, all three healthy):

```text
{"server":"app1","hostname":"ea701aa96aa1"}
{"server":"app2","hostname":"cbf322f6707f"}
{"server":"app3","hostname":"946570368c95"}
{"server":"app1","hostname":"ea701aa96aa1"}
{"server":"app2","hostname":"cbf322f6707f"}
{"server":"app3","hostname":"946570368c95"}
```

Open <http://localhost:8404> for the live stats page. Now kill one server and watch:

```bash
docker stop app3
for i in 1 2 3; do curl -s -o /dev/null -w "%{http_code} " localhost:8081/; done   # straight away
# 200 200 503
sleep 20
for i in 1 2 3 4; do curl -s localhost:8081/; echo; done                           # 20 s later
# {"server":"app1",...}  {"server":"app2",...}  {"server":"app1",...}  {"server":"app2",...}
```

Notice the **`503` right after app3 died**: HAProxy hadn't noticed yet. With `check inter 5s` and
the default `fall 3`, detection takes about 15 seconds. After that, app3 is skipped and nobody sees
errors. Two ways to shrink that window: check more often (`inter 2s fall 2`), and let HAProxy
**retry another server** when a connection fails:

```text
defaults
    retries 2
    option redispatch
```

### Trying the other algorithms

| Config file | `backend` setting | What you'll see |
|---|---|---|
| `round_robin.cfg` | `balance roundrobin` | 1, 2, 3, 1, 2, 3… |
| `weighted_round_robin.cfg` | `weight 5 / 3 / 2` | out of 10 requests ≈ 5 app1, 3 app2, 2 app3 |
| `least_conn.cfg` | `balance leastconn` | the server with fewest open connections wins: shows up under load |
| `weighted_least_conn.cfg` | `leastconn` + weights | least connections, but bigger servers take more |

Use `request_sender.py` (one request every 0.5 s) to watch the pattern, or a load tool like
[`hey`](https://github.com/rakyll/hey) to see `leastconn` in action:

```bash
hey -n 100 -c 10 http://localhost:8081/        # 100 requests, 10 at a time
hey -z 1m -c 100 http://localhost:8081/        # 100 concurrent users for one minute
```

### Bonus: rate limiting at the load balancer

HAProxy can also refuse clients that send too many requests (AWS does this with **WAF rate-based
rules**, [Session 12](12-aws-waf.md)). In the `frontend`:

```text
stick-table type ip size 1m expire 1m store http_req_rate(60s)
http-request track-sc0 src
acl abuse sc_http_req_rate(0) gt 100
http-request return status 429 content-type application/json \
    string '{"error":"Too Many Requests"}' if abuse
```

**Clean up:** `docker compose down`.

## 8. From HAProxy to AWS

| HAProxy | AWS Elastic Load Balancer |
|---|---|
| `frontend` + `bind *:8080` | **Listener** (protocol + port, e.g. HTTPS:443) |
| `backend apps` | **Target group** |
| `server app1 …` | **Target** (EC2 instance, IP address or Lambda) |
| `option httpchk`, `inter/fall/rise` | **Health check** settings on the target group |
| `balance roundrobin` | ALB uses round robin by default (least outstanding requests optional) |
| You run and patch HAProxy yourself | AWS runs, scales and patches the load balancer, across AZs |

AWS's three load balancers (**ALB**, **NLB**, **GWLB**) are the topic of [Session 5](05-elastic-load-balancer.md).

## Common mistakes

- **No health check endpoint**, so a broken server keeps receiving traffic.
- **Storing sessions in server memory.** With round robin the next request hits another server
  and the user is "logged out". Keep sessions in a shared store (Redis, a database) or use
  stickiness carefully.
- **One load balancer, one AZ.** On AWS, always enable at least two AZs.

## Hands-on exercises

All of these run **locally and free** with the class Docker Compose setup (see *Class files*).
Change which config is mounted in `docker-compose.yml`, then `docker compose up -d` or
`docker compose restart haproxy`.

**Exercise 1 · Watch round robin.** Start the stack with `round_robin.cfg` and send 9 requests.
Count how many each app answers.

<details class="solution"><summary>Solution</summary>

```bash
for i in $(seq 9); do curl -s localhost:8081/ | python3 -c "import sys,json;print(json.load(sys.stdin)['server'])"; done | sort | uniq -c
```

Expected: `3 app1`, `3 app2`, `3 app3`.

</details>

**Exercise 2 · Weighted round robin.** Switch to `weighted_round_robin.cfg` (weights 5/3/2) and send
100 requests. Does the split match the weights?

<details class="solution"><summary>Solution</summary>

Same loop with `seq 100`. Expect about **50 / 30 / 20**. Weights are relative shares, not percentages.

</details>

**Exercise 3 · Stats page.** Open <http://localhost:8404> while running Exercise 2. Find each server's
status, sessions and number of requests.

<details class="solution"><summary>What to look at</summary>

The **backend apps** table: Status (UP/DOWN, green/red), **Cur** and **Max** sessions, **Total**
requests per server, **LastChk** (last health check result).

</details>

**Exercise 4 · Failover timing.** With `round_robin.cfg` (`check inter 5s`), stop app2 and measure how
long until HAProxy stops sending it requests.

<details class="solution"><summary>Solution</summary>

```bash
docker stop app2
for i in $(seq 30); do printf "%s " "$(curl -s -o /dev/null -w '%{http_code}' localhost:8081/)"; sleep 1; done; echo
```

You'll see a few `503`s in the first ~15 s (5 s × 3 failed checks), then only `200`s. Start app2 again
and it rejoins after 2 successful checks (~10 s).

</details>

**Exercise 5 · Hide the failure window.** Add `retries 2` and `option redispatch` to the `defaults`
section and repeat Exercise 4. What changes?

<details class="solution"><summary>Answer</summary>

The `503`s disappear (or nearly): when a connection to the dead server fails, HAProxy retries on
another healthy server before the health check has even marked it down.

</details>

**Exercise 6 · Faster detection.** Change `check inter 5s` to `check inter 1s fall 2 rise 2`. How long
does detection take now, and what's the downside?

<details class="solution"><summary>Answer</summary>

About **2 seconds** (1 s × 2). Downside: more health-check traffic, and a server that's briefly slow
(e.g. a GC pause) can be marked down too eagerly ("flapping").

</details>

**Exercise 7 · Least connections under load.** Add a slow endpoint to app1 (`import time` and
`@app.get("/slow")` that sleeps 3 s), rebuild, switch to `least_conn.cfg`, and load-test `/slow` with
[`hey`](https://github.com/rakyll/hey). Compare the per-server request counts with round robin.

<details class="solution"><summary>What to expect</summary>

```bash
hey -n 60 -c 15 http://localhost:8081/slow
```

With **leastconn**, the servers stuck on slow requests get fewer new ones, so the load stays even
and the slowest requests finish sooner. With round robin, requests queue up behind the slow ones.

</details>

**Exercise 8 · Sticky by IP.** Set `balance source` and send 10 requests from your laptop. Then send
10 from inside a container (`docker run --rm --network <project>_default curlimages/curl ...`). What
do you notice?

<details class="solution"><summary>Answer</summary>

Each **client IP** always lands on the same server: all 10 from your laptop hit one app; the container
(a different IP) may hit another. That's stickiness without cookies.

</details>

**Exercise 9 · Cookie stickiness.** Make HAProxy insert a cookie so a browser sticks to one server:
add `cookie SERVERID insert indirect nocache` to the backend and `cookie s1` / `cookie s2` / `cookie s3`
to each `server` line. Test with curl's cookie jar.

<details class="solution"><summary>Solution</summary>

```bash
curl -s -c jar.txt localhost:8081/ ; for i in 1 2 3 4; do curl -s -b jar.txt localhost:8081/; echo; done
```

Every request with the cookie goes to the same app. Without `-b jar.txt` it round-robins again.

</details>

**Exercise 10 · Rate limiting.** Add the stick-table rate-limit snippet from the class files to the
`frontend` (limit 100 requests/minute per IP) and fire 150 requests quickly. What status codes come back?

<details class="solution"><summary>Solution</summary>

```bash
for i in $(seq 150); do curl -s -o /dev/null -w "%{http_code}\n" localhost:8081/; done | sort | uniq -c
```

About 100 × `200`, then `429` with `{"error":"Too Many Requests"}` for the rest of the minute.

</details>

**Exercise 11 · Real client IP.** Add `option forwardfor` to the backend and make app1 return the
`X-Forwarded-For` header. Why does the app need this header behind a load balancer?

<details class="solution"><summary>Answer</summary>

Without it, every request seems to come from HAProxy's IP. `X-Forwarded-For` carries the original
client IP for logging, rate limiting and geo rules. AWS ALBs add the same header.

</details>

**Exercise 12 · Layer 4 mode.** Change `mode http` to `mode tcp` in `defaults` (and remove
`option httpchk`, which is HTTP-only). Does load balancing still work? What can't you do any more?

<details class="solution"><summary>Answer</summary>

Yes: connections are still spread across the apps. But HAProxy no longer understands HTTP, so you
lose path/host routing, HTTP health checks, cookie stickiness, `X-Forwarded-For` and HTTP rate-limit
responses. That's the ALB (layer 7) vs NLB (layer 4) trade-off in [Session 5](05-elastic-load-balancer.md).

</details>

## Class files

<details class="source">
<summary>docker-compose.yml</summary>

```{literalinclude} ../code/04-haproxy-local/docker-compose.yml
:language: yaml
```

</details>

<details class="source">
<summary>app1/main.py</summary>

```{literalinclude} ../code/04-haproxy-local/app1/main.py
:language: python
```

</details>

<details class="source">
<summary>haproxy/round_robin.cfg</summary>

```{literalinclude} ../code/04-haproxy-local/haproxy/round_robin.cfg
:language: text
```

</details>

<details class="source">
<summary>haproxy/weighted_round_robin.cfg</summary>

```{literalinclude} ../code/04-haproxy-local/haproxy/weighted_round_robin.cfg
:language: text
```

</details>

<details class="source">
<summary>haproxy/least_conn.cfg</summary>

```{literalinclude} ../code/04-haproxy-local/haproxy/least_conn.cfg
:language: text
```

</details>

<details class="source">
<summary>request_sender.py</summary>

```{literalinclude} ../code/04-haproxy-local/request_sender.py
:language: python
```

</details>

- Downloads: {download}`docker-compose.yml <../code/04-haproxy-local/docker-compose.yml>` ·
  {download}`app1/main.py <../code/04-haproxy-local/app1/main.py>` ·
  {download}`app1/Dockerfile <../code/04-haproxy-local/app1/Dockerfile>` ·
  {download}`round_robin.cfg <../code/04-haproxy-local/haproxy/round_robin.cfg>` ·
  {download}`weighted_round_robin.cfg <../code/04-haproxy-local/haproxy/weighted_round_robin.cfg>` ·
  {download}`least_conn.cfg <../code/04-haproxy-local/haproxy/least_conn.cfg>` ·
  {download}`weighted_least_conn.cfg <../code/04-haproxy-local/haproxy/weighted_least_conn.cfg>` ·
  {download}`load test & rate limit snippets <../code/04-haproxy-local/load-test-and-rate-limit.txt>`
- The app2 and app3 folders are the same as app1 with `"server": "app2"` / `"app3"`.
