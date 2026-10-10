# Session 4 · Load Balancing Explained: HAProxy Demo (Local Setup)

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/RUuR__pxzbw"
  title="Session 4: Load balancing with HAProxy" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 **Session 4** of the [AWS Solutions Architect playlist](https://www.youtube.com/playlist?list=PLYmjGMwZ9N88) (Tamil) · [watch on YouTube](https://www.youtube.com/watch?v=RUuR__pxzbw)

## The big idea

One server can only handle so many users, and if it crashes, your site is down. A **load
balancer** sits in front of several identical servers, **spreads requests** across them and
**stops sending traffic to any server that is unhealthy**. Users only ever see the load balancer's
address. We build one on our laptop with **HAProxy** first, so AWS's Elastic Load Balancer
([Session 5](05-elastic-load-balancer.md)) feels familiar.

**Everyday example:** a bank with several counters and one token machine. You don't choose a
counter; the token system sends you to the next free one. If a counter closes for lunch, no
tokens go there.

```{raw} html
:file: ../diagrams/s04-haproxy.html
```

## 1. Why load balance?

- **Scale out:** add more servers instead of buying one huge server.
- **High availability:** one server failing doesn't take the site down.
- **Zero-downtime deploys:** take servers out one at a time while updating.
- **One entry point:** a single DNS name / IP, TLS certificates in one place.

## 2. Balancing algorithms

| Algorithm | How it picks a server | Good for |
|---|---|---|
| **Round robin** | 1, 2, 3, 1, 2, 3… | similar servers, similar requests |
| **Least connections** | the server with the fewest active connections | requests of very different lengths |
| **Source (IP hash)** | the same client IP always goes to the same server | simple "stickiness" |
| **Weighted** | bigger servers get more requests | mixed server sizes |

## 3. Health checks

The load balancer keeps asking each server "are you OK?", for example `GET /health` every 2
seconds. After a few failures in a row the server is marked **down** and gets no traffic; after a
few successes it comes back. Your app should return `200` on `/health` only when it can really
serve requests (for example, when it can reach its database).

## 4. Hands-on: HAProxy in front of three apps (class code)

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

## 5. From HAProxy to AWS

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

## Try it yourself

1. Change `balance roundrobin` to `balance source`, restart HAProxy (`docker compose restart haproxy`), and `curl` six times. What changes?

   <details class="solution">
   <summary>Answer</summary>

   Every request now goes to the **same** app, because your source IP hashes to one server.

   </details>

2. Using `weighted_round_robin.cfg` (weights 5, 3, 2), send 100 requests. Roughly how many reach each app?

   <details class="solution">
   <summary>Answer</summary>

   About 50 to app1, 30 to app2 and 20 to app3.

   </details>

3. Why did one request return `503` right after `docker stop app3`, and how do you avoid it?

   <details class="solution">
   <summary>Answer</summary>

   HAProxy only marks a server down after several failed health checks (here ~15 s). Requests sent
   to app3 in that window fail. Faster checks (`inter 2s fall 2`) and `retries` + `option redispatch`
   reduce or hide it.

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
