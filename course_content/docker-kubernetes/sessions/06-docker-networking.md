# Chapter 6 · Docker Networking: Bridge, Host, None & Overlay

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/NEaL_5WVcaI"
  title="Episode 6: Docker networking explained" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 **Episode 6** of the [Kube Engineering playlist](https://www.youtube.com/playlist?list=PLMtFsmo8jrN8) (Tamil) · [watch on YouTube](https://www.youtube.com/watch?v=NEaL_5WVcaI)

## The big idea

Every container gets its **own network namespace**: its own network card, IP address and ports.
**Docker networks** decide how those private networks connect: to each other, to your laptop and to
the internet. Pick the right network type and "my app can't reach the database" problems go away.

**Everyday example:** an apartment block. Each flat (container) has its own intercom number (IP).
The flats in one block are joined by the building's corridor (a **bridge** network). Visitors from
outside only reach a flat if the security desk forwards them (**port publishing**). A *custom*
block also has a **directory at the entrance**, so you can find a flat by name, not number (DNS).

## The network types at a glance

```{raw} html
:file: ../diagrams/net-modes.html
```

```bash
docker network ls
```

**Output (on a fresh install):**

```text
NETWORK ID     NAME      DRIVER    SCOPE
…              bridge    bridge    local
…              host      host      local
…              none      null      local
```

| Driver | What it gives a container | Use it for |
|---|---|---|
| **bridge** (default) | its own IP on a private subnet behind the host | almost everything on one machine |
| **host** | the host's network directly; no isolation | maximum network speed, or apps needing many ports (Linux only) |
| **none** | only loopback; no network at all | batch jobs that must not talk to anything |
| **macvlan** | its own MAC and IP **on your real LAN**, like a physical device | old apps that expect to be on the LAN |
| **overlay** | one network spanning **many hosts** | Docker Swarm; the idea behind Kubernetes pod networks |

## 1. The default bridge network

```{raw} html
:file: ../diagrams/net-bridge.html
```

Docker creates a virtual switch called **docker0** on the host (`172.17.0.1`, the gateway from
[Chapter 5](05-ip-addressing-subnets.md)). Each container is plugged into it with a **veth pair**,
a virtual cable with one end in the container (`eth0`) and one end on the bridge.

```bash
docker run -d --name net-a alpine sleep 300
docker run -d --name net-b alpine sleep 300
docker exec net-a ip -4 addr show eth0 | grep inet
```

**Output:**

```text
inet 172.17.0.2/16 brd 172.17.255.255 scope global eth0
```

Can they talk? By **IP**, yes. By **name**, no:

```bash
docker exec net-a ping -c1 172.17.0.3     # 1 packets transmitted, 1 packets received
docker exec net-a ping -c1 net-b          # ping: bad address 'net-b'
docker rm -f net-a net-b
```

:::{important}
**The default bridge has no DNS for container names.** Container IPs change every time they
restart, so hard-coding them is fragile. The fix is a **user-defined** network.
:::

## 2. User-defined bridge networks (with DNS)

```bash
docker network create mynet
docker network inspect mynet --format '{{(index .IPAM.Config 0).Subnet}}'   # 172.21.0.0/16 (yours may differ)
docker run -d --name net-c --network mynet alpine sleep 300
docker run -d --name net-d --network mynet alpine sleep 300
docker exec net-c ping -c1 net-d
```

**Output:**

```text
PING net-d (172.21.0.3): 56 data bytes
1 packets transmitted, 1 packets received, 0% packet loss
```

The name worked. Docker runs a small **DNS server at `127.0.0.11`** inside every user-defined
network:

```bash
docker exec net-c cat /etc/resolv.conf     # nameserver 127.0.0.11
docker rm -f net-c net-d
```

Other things you get with user-defined networks:

- **Isolation:** containers on `mynet` can't reach containers on another network.
- **Connect and disconnect live:** `docker network connect mynet web` gives `web` a second
  network card (and a second IP) without restarting it.

## 3. Host and none

```bash
docker run --rm --network host alpine hostname      # prints YOUR laptop's hostname
docker run --rm --network none alpine ip -4 addr    # only: inet 127.0.0.1/8 scope host lo
docker run --rm --network none alpine ping -c1 8.8.8.8
# ping: sendto: Network unreachable
```

- **host:** no separate network namespace. nginx in a host-network container listens directly on
  the host's port 80, so `-p` isn't needed (and is ignored). But two containers can't both use
  port 80. On Docker Desktop (macOS/Windows) "host" means the hidden Linux VM, not your laptop.
- **none:** only loopback. Good for jobs that process files and must never call out.

## 4. Publishing ports with `-p` (and how NAT does it)

Containers on a bridge have **private** IPs; your browser can't reach `172.17.0.2` from outside
the host. `-p HOST_PORT:CONTAINER_PORT` publishes a port:

```bash
docker run -d --name web -p 8099:80 nginx:alpine
docker port web
```

**Output:**

```text
80/tcp -> 0.0.0.0:8099
80/tcp -> [::]:8099
```

Under the hood Docker adds a **NAT rule** (with iptables) on the host: *"traffic arriving on port
8099 → send it to 172.17.0.2:80"*. That's the same NAT idea your home router uses. See the rules
with `sudo iptables -t nat -L DOCKER -n`.

- `-p 8099:80` listens on **all** host addresses. `-p 127.0.0.1:8099:80` listens only on
  localhost, which is safer for databases on a server.
- Only one program can use a host port. Try a port that's already taken and you get
  `failed to bind host port … address already in use`.

## 5. Wiring a multi-container app

Manually, with a user-defined network so the containers find each other **by name**:

```bash
docker network create appnet
docker run -d --name cache --network appnet redis:7-alpine
docker run --rm --network appnet redis:7-alpine redis-cli -h cache ping     # PONG
```

The app connects to the host name `cache`. No IP addresses anywhere.

**With Docker Compose**, this happens automatically. Compose creates a network for the project and
every service is reachable by its **service name**:

```yaml
# compose.yaml
services:
  web:
    image: nginx:alpine
    ports:
      - "8080:80"
  cache:
    image: redis:7-alpine      # web reaches it at host "cache", port 6379
```

```bash
docker compose up -d
docker compose exec web ping -c1 cache
docker compose down
```

That's why "it just works" in Compose: it's a user-defined bridge network with DNS. Compose gets
its own sessions later in the course.

## 6. Macvlan and overlay (advanced)

- **macvlan:** the container appears on your **real LAN** with its own MAC and IP (say
  `192.168.1.50`), like another physical device plugged into the router. Useful for legacy apps or
  network tools. Your network must allow several MAC addresses per port; many Wi-Fi networks
  don't.
- **overlay:** one virtual network spread over **several hosts**. Containers on different
  machines talk as if they were on one switch; traffic between hosts is wrapped (VXLAN) and sent
  across the real network. Docker Swarm uses it, and Kubernetes pod networking (CNI plugins like
  Flannel and Calico) builds on the same idea.

## Common mistakes

- **Using the default bridge and container names.** Names only resolve on user-defined networks
  (and in Compose).
- **App listens on `127.0.0.1` inside the container.** `-p` forwards to the container's `eth0`,
  so the app must listen on `0.0.0.0`.
- **`localhost` from inside a container** means the container itself, not your laptop. To reach
  the host, use the gateway IP (`172.17.0.1` on Linux) or `host.docker.internal` on Docker Desktop.
- **Publishing databases on `0.0.0.0` on a cloud server.** Anyone on the internet can try to
  connect. Use `127.0.0.1:5432:5432`, or don't publish at all and use a Docker network.

## Try it yourself

1. Start two containers on the default bridge and two on your own network. Show that names work
   only on your own network.
2. Start nginx on a user-defined network with **no** `-p`. Can another container on that network
   `wget -qO- http://<name>`? Can your laptop's browser reach it?

   <details class="solution">
   <summary>Answer</summary>

   The other container can, by name, because they share the network. Your laptop can't, because
   no port was published.

   </details>

3. Run `docker run --rm --network host nginx:alpine` and open <http://localhost> (Linux). Why
   wasn't `-p` needed?

   <details class="solution">
   <summary>Answer</summary>

   With `--network host` the container uses the host's network namespace, so nginx listens on the
   host's port 80 directly. Nothing needs forwarding.

   </details>

4. Connect a running container to a second network with `docker network connect`, then list its
   IPs with:
   `docker inspect -f '{{range $k,$v := .NetworkSettings.Networks}}{{$k}}={{$v.IPAddress}} {{end}}' <name>`

   <details class="solution">
   <summary>What you should see</summary>

   One IP per network, e.g. `bridge=172.17.0.2 mynet=172.21.0.2`.

   </details>
