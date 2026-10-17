# Chapter 13 · The OSI model

## The big idea

Sending data between two computers is a huge job: radio waves, cables, addresses, lost packets,
encryption, web pages. The **OSI model** splits it into **seven layers**. Each layer does one job and
only talks to the layer directly above and below it.

**Everyday example:** sending a gift abroad. You wrap it (application), a courier company puts it in a
labelled box (transport), the postal service sorts it by country and city (network), a truck driver
carries it down the road (data link), and the road itself is the physical layer. The driver does not
care what is inside the box. You do not care which road the truck takes.

```{raw} html
:file: ../diagrams/osi-layers.html
```

## The seven layers

| # | Layer | Job | Examples | Data unit |
|---|---|---|---|---|
| 7 | **Application** | What the program wants to say | HTTP, DNS, SMTP, FTP | message |
| 6 | **Presentation** | Format, compress, encrypt | TLS, JSON, gzip, JPEG | |
| 5 | **Session** | Open, keep and close conversations | sessions, RPC, NetBIOS | |
| 4 | **Transport** | Delivery between **programs** (ports), reliable or not | **TCP, UDP**, QUIC | segment / datagram |
| 3 | **Network** | Addressing and routing between **machines** | **IP**, ICMP, routers | packet |
| 2 | **Data link** | Delivery on one local network | Ethernet, Wi-Fi, MAC address, switches | frame |
| 1 | **Physical** | Bits as signals | cable, fibre, radio | bits |

A memory trick, bottom to top: **P**lease **D**o **N**ot **T**hrow **S**ausage **P**izza **A**way.

In real life the model is condensed into four layers (the **TCP/IP model**): Application (OSI 5-7),
Transport (4), Internet (3), Link (1-2).

## Encapsulation: how a request travels down the stack

As data moves **down** the layers on the sender, each layer **wraps** it with its own header (like
putting a letter in an envelope, inside a box, inside a crate). On the receiver the layers **unwrap**
in reverse.

```python
http_message = "GET /index.html HTTP/1.1"                       # layer 7

tcp_segment = f"[TCP src=51000 dst=80 seq=1]{http_message}"      # layer 4: ports
ip_packet = f"[IP src=10.0.0.5 dst=203.0.113.7]{tcp_segment}"     # layer 3: machine addresses
frame = f"[ETH src=aa:aa dst=bb:bb]{ip_packet}[CRC]"              # layer 2: local delivery

print("L7 :", http_message)
print("L4 :", tcp_segment)
print("L3 :", ip_packet)
print("L2 :", frame)

# receiver unwraps in reverse
payload = frame.split("]", 1)[1].rsplit("[CRC]", 1)[0]            # strip Ethernet
payload = payload.split("]", 1)[1]                                 # strip IP
payload = payload.split("]", 1)[1]                                 # strip TCP
print("received:", payload)
```

**Output:**

```text
L7 : GET /index.html HTTP/1.1
L4 : [TCP src=51000 dst=80 seq=1]GET /index.html HTTP/1.1
L3 : [IP src=10.0.0.5 dst=203.0.113.7][TCP src=51000 dst=80 seq=1]GET /index.html HTTP/1.1
L2 : [ETH src=aa:aa dst=bb:bb][IP src=10.0.0.5 dst=203.0.113.7][TCP src=51000 dst=80 seq=1]GET /index.html HTTP/1.1[CRC]
received: GET /index.html HTTP/1.1
```

Each header holds exactly what that layer needs: ports for TCP, machine addresses for IP, local
hardware addresses for Ethernet.

## Which layer does what to my system?

| If you are talking about... | It lives at |
|---|---|
| HTTP, REST, GraphQL, gRPC | L7 |
| TLS encryption | L6 (practically between 4 and 7) |
| TCP vs UDP, ports | L4 |
| IP addresses, routing, subnets, VPCs | L3 |
| MAC addresses, switches, VLANs | L2 |
| Cables, fibre, signal strength | L1 |

**Load balancers:** "**Layer 4**" balancers forward by IP and port without reading the request (fast).
"**Layer 7**" balancers read the HTTP request and can route by URL, header or cookie (flexible).

**Firewalls:** a network firewall filters at L3/L4 (IP, port). A web application firewall (WAF) filters at L7
(SQL injection patterns in the request).

## Debugging with the layers

When "the site is down", walk up from the bottom:

1. **L1/L2:** is the cable or Wi-Fi connected?
2. **L3:** can I `ping` the server's IP? (If not: routing or firewall.)
3. **L4:** can I connect to port 443? (`nc -vz host 443`; if not: service down or port blocked.)
4. **L7:** does `curl -I https://host` return `200`? (If not: application error.)

This approach finds the broken layer in minutes.

## Common mistakes

:::{warning}
- Memorising layer names without being able to say what **load balancer layer 4 vs 7** means.
- Thinking OSI is how the internet is literally built. It is a **teaching model**; the real internet follows TCP/IP.
- Putting application logic at the network layer, or assuming IP guarantees delivery (it does not).
:::

## Try it yourself

1. At which layer do each of these live: TCP, HTTP, IP address, Ethernet MAC address, TLS?
2. A request reaches the server's port 443 but returns HTTP 502. Which layer is healthy and which is not?
3. Why can a Layer 7 load balancer route `/api` and `/images` differently but a Layer 4 balancer cannot?

<details class="solution"><summary>Answers</summary>

1. TCP: 4. HTTP: 7. IP: 3. MAC: 2. TLS: 6 (sits between transport and application).
2. L1-L4 are healthy (the connection was made). The problem is at **L7**: the application or an upstream behind the proxy.
3. A Layer 4 balancer only sees IPs and ports, never the URL. Layer 7 reads the HTTP request line.

</details>

:::{admonition} Next
:class: important
Layer 3 gives every machine an address: [IP addresses](14-ip-addresses.md).
:::
