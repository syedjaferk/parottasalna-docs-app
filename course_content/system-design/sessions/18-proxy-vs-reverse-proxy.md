# Chapter 18 · Proxy vs reverse proxy

## The big idea

A **proxy** is a middleman that forwards requests on behalf of someone else. The two kinds differ in
**whom they represent**:

- A **forward proxy** represents the **clients**.
- A **reverse proxy** represents the **servers**.

**Everyday example:** a company receptionist who places calls for staff is a *forward proxy*: the
outside world sees the company, not the employee. A receptionist who answers the company's main number
and routes callers to the right person is a *reverse proxy*: callers do not know which employee they
reach.

```{raw} html
:file: ../diagrams/proxy-types.html
```

## Forward proxy

Sits **in front of clients**. The client is **configured** to send traffic through it.

What it is used for:

- **Filtering and policy:** a company blocks social media or logs web usage.
- **Caching:** many employees download the same update; the proxy fetches it once.
- **Anonymity and privacy:** the website sees the proxy's IP, not yours (VPNs work similarly).
- **Bypassing geo-restrictions.**

Examples: Squid, corporate gateways, VPN and "anonymiser" services.

## Reverse proxy

Sits **in front of servers**. Clients do not know it exists; they think they are talking to the website.

What it does for your servers:

| Job | Detail |
|---|---|
| **Load balancing** | Spreads requests across many servers |
| **TLS termination** | Handles HTTPS, so app servers speak plain HTTP internally |
| **Caching** | Serves repeated responses directly |
| **Compression** | gzip or brotli once, at the edge |
| **Security** | Hides server IPs, blocks bad requests, rate limits, web application firewall |
| **Routing** | `/api` to one pool, `/images` to another |
| **Connection handling** | Buffers slow clients so app servers are not tied up |

Examples: **Nginx, HAProxy, Envoy, Traefik, Cloudflare, AWS ALB**.

A **load balancer** is a reverse proxy with *more than one* server behind it. An **API gateway** is a
reverse proxy with API-specific features (authentication, quotas).

## A minimal reverse proxy

```nginx
upstream app_servers {
    server 10.0.1.11:8000;
    server 10.0.1.12:8000;
}

server {
    listen 443 ssl;
    server_name shop.example.com;

    location /static/ { root /var/www; expires 7d; }          # serve files itself, cached
    location /        { proxy_pass http://app_servers; }      # everything else to the app
}
```

## The idea in 20 lines of Python

```python
# a reverse proxy: clients talk to the proxy, never to the backends
backends = {"app1": 0, "app2": 0}      # name -> requests handled
cache = {}

def backend_handle(name, path):
    backends[name] += 1
    return f"page for {path} from {name}"

def reverse_proxy(path):
    if path.startswith("/static/"):
        if path in cache:                                      # answered by the proxy itself
            return cache[path] + "  [proxy cache hit]"
        cache[path] = backend_handle(min(backends, key=backends.get), path)
        return cache[path]
    name = min(backends, key=backends.get)                      # least-loaded backend
    return backend_handle(name, path)

for p in ["/home", "/static/logo.png", "/static/logo.png", "/cart", "/home"]:
    print(f"{p:<18} -> {reverse_proxy(p)}")
print("backend load:", backends)
```

**Output:**

```text
/home              -> page for /home from app1
/static/logo.png   -> page for /static/logo.png from app2
/static/logo.png   -> page for /static/logo.png from app2  [proxy cache hit]
/cart              -> page for /cart from app1
/home              -> page for /home from app2
backend load: {'app1': 2, 'app2': 2}
```

The second request for `/static/logo.png` was answered by the proxy and never reached a backend: the backend load
shows only 3 requests for 5 calls.

## Forward vs reverse at a glance

| | Forward proxy | Reverse proxy |
|---|---|---|
| In front of | Clients | Servers |
| Client aware? | Yes, configured | No, transparent |
| Hides | The client's identity | The servers' identity and layout |
| Main use | Filtering, anonymity, caching for users | Load balancing, TLS, caching, security |
| Examples | Squid, VPN | Nginx, Cloudflare, ALB |

## Risks

- The reverse proxy is a **SPOF**: run at least two.
- It can become a **bottleneck**: scale it horizontally.
- It adds a hop of **latency**.
- A misconfigured cache can leak one user's page to another (cache the public, never the private, or vary by user).

## Common mistakes

:::{warning}
- Mixing the two up: one protects **clients**, the other protects **servers**.
- Caching authenticated responses in a shared reverse-proxy cache.
- One proxy instance for the whole site.
- Forgetting `X-Forwarded-For`: your app sees the proxy's IP unless the proxy passes the real client IP in a header.
:::

## Try it yourself

1. A school blocks gaming sites for students. Forward or reverse proxy?
2. Where would you terminate TLS in a design with a CDN, a load balancer and app servers, and why?
3. Why must the reverse proxy forward the client's IP in a header?

<details class="solution"><summary>Answers</summary>

1. **Forward proxy**: it sits in front of the clients and applies a policy.
2. At the **CDN or load balancer**, so certificates are managed in one place and app servers avoid the CPU cost. Re-encrypt internally if the internal network is not trusted.
3. Without it every request appears to come from the proxy, which breaks logging, per-IP rate limits and geolocation.

</details>

:::{admonition} Next
:class: important
Now the protocol the browser speaks: [HTTP and HTTPS](19-http-and-https.md).
:::
