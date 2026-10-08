# Chapter 5 · IP Addressing & Subnetting, Simply

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/c667FdXRlmI"
  title="Episode 5: IP addressing and subnetting" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 **Episode 5** of the [Kube Engineering playlist](https://www.youtube.com/playlist?list=PLMtFsmo8jrN8) (Tamil) · [watch on YouTube](https://www.youtube.com/watch?v=c667FdXRlmI)

## The big idea

Every device on a network needs an **address** so data can reach it: that's the **IP address**.
Addresses are grouped into **subnets** (smaller networks), like houses grouped into streets.
Docker gives each container an IP address in its own subnet, and Kubernetes does the same for
every pod, so this chapter is the base for all the networking that follows. No heavy maths, just
what you need.

**Everyday example:** a postal address. `192.168.1.10` is like *"Street 192.168.1, house 10"*.
The **subnet** is the street; everyone on the same street can deliver to each other directly. To
reach another street, you go through the **gateway**, like the main road at the end of the street.

## 1. What an IPv4 address looks like

```{raw} html
:file: ../diagrams/net-ip-address.html
```

- An IPv4 address is **4 numbers separated by dots**, each from **0 to 255**: `192.168.1.10`.
- Each number is called an **octet**, because it is **8 bits**. 4 × 8 = **32 bits** in total.
- Why 255? 8 bits can count from `00000000` (0) to `11111111` (255).

See your own addresses:

```bash
ip addr            # every network card and its address (look for "inet")
hostname -I        # just your IP addresses
ip route           # your gateway: the line starting with "default via"
curl ifconfig.me   # your PUBLIC address, as the internet sees it
```

## 2. Public vs private addresses

```{raw} html
:file: ../diagrams/net-public-private.html
```

There aren't enough IPv4 addresses for every device in the world (only about 4.3 billion exist).
So some ranges are reserved as **private**: used inside homes, offices and Docker, and never seen
directly on the internet.

| Range | CIDR | Where you see it |
|---|---|---|
| `10.0.0.0` – `10.255.255.255` | `10.0.0.0/8` | offices, cloud VPCs, Kubernetes pods |
| `172.16.0.0` – `172.31.255.255` | `172.16.0.0/12` | **Docker** (`172.17.0.0/16` is the default bridge) |
| `192.168.0.0` – `192.168.255.255` | `192.168.0.0/16` | home Wi-Fi routers |
| `127.0.0.0` – `127.255.255.255` | `127.0.0.0/8` | **loopback**: `127.0.0.1` = "this machine itself" (`localhost`) |

Everything else (like `8.8.8.8`, Google's DNS) is a **public** address, reachable from anywhere.
Your router uses **NAT** (Network Address Translation) to let many private devices share one public
address. Docker does the same for containers, as you'll see in [Chapter 6](06-docker-networking.md).

## 3. Subnets, masks and CIDR

A **subnet** is a block of addresses that belong together. The **subnet mask** (or the
**CIDR** number after the `/`) says how many bits, from the left, are the **network** part. The
rest are the **host** part: one value per device.

| CIDR | Subnet mask | Network bits | Addresses in the block | Example |
|---|---|---|---|---|
| `/8` | `255.0.0.0` | 8 | 16,777,216 | `10.0.0.0/8` |
| `/16` | `255.255.0.0` | 16 | 65,536 | `172.17.0.0/16` (Docker) |
| `/24` | `255.255.255.0` | 24 | 256 | `192.168.1.0/24` (home) |
| `/26` | `255.255.255.192` | 26 | 64 | a small cloud subnet |
| `/32` | `255.255.255.255` | 32 | 1 | exactly one machine |

**The one formula you need:** a `/n` block has **2^(32 − n)** addresses. **Bigger number after the
slash = smaller network.**

In each subnet, two addresses are reserved:

- the **first** is the **network address** itself (`192.168.1.0`),
- the **last** is the **broadcast address**, meaning "everyone on this subnet" (`192.168.1.255`).

So `192.168.1.0/24` has 256 addresses but **254 usable** ones: `192.168.1.1` to `192.168.1.254`.
Usually `.1` is the **gateway** (your router).

**Same subnet or not?** `192.168.1.10/24` and `192.168.1.200/24` share the first 24 bits
(`192.168.1`), so they talk **directly**. `192.168.2.5` is on a different subnet, so traffic goes
**through the gateway**.

## 4. How this connects to Docker

```bash
docker network inspect bridge --format '{{(index .IPAM.Config 0).Subnet}} gw {{(index .IPAM.Config 0).Gateway}}'
docker run --rm alpine ip route
```

**Output:**

```text
172.17.0.0/16 gw 172.17.0.1
default via 172.17.0.1 dev eth0
172.17.0.0/16 dev eth0 scope link  src 172.17.0.4
```

Read it with what you just learned:

- Docker's default network is the **private** subnet `172.17.0.0/16`: 65,536 addresses.
- `172.17.0.1` is the **gateway**: the host's side of the network. Containers send everything
  outside the subnet to it.
- This container got `172.17.0.4`. Other containers get `.2`, `.3`… on the same subnet, so they
  can reach each other directly.

## Common mistakes

- **Thinking `127.0.0.1` inside a container is your laptop.** It's the **container itself**:
  every container has its own loopback.
- **Mixing up "bigger network" and "bigger number".** `/16` is a *much bigger* network than `/24`.
- **Overlapping subnets.** If your office VPN uses `172.17.x.x`, it clashes with Docker's default
  bridge and some sites stop working. Docker's subnet can be changed in `/etc/docker/daemon.json`.

## Try it yourself

1. Find your laptop's private IP, its subnet (the `/` number), its gateway and your public IP.
2. How many addresses are in `10.0.5.0/24`? What are the first and last **usable** ones?

   <details class="solution">
   <summary>Answer</summary>

   256 addresses. Usable: `10.0.5.1` to `10.0.5.254` (`.0` is the network, `.255` is broadcast).

   </details>

3. Which of these are private? `172.20.1.5`, `172.32.0.1`, `192.168.0.7`, `8.8.4.4`, `10.99.0.1`

   <details class="solution">
   <summary>Answer</summary>

   `172.20.1.5` (inside 172.16–172.31), `192.168.0.7` and `10.99.0.1`. `172.32.0.1` is just
   outside the 172.16.0.0/12 range, and `8.8.4.4` is Google's public DNS.

   </details>

4. A `/26` subnet: how many addresses, and how many usable for devices?

   <details class="solution">
   <summary>Answer</summary>

   2^(32 − 26) = 2^6 = **64** addresses, **62** usable.

   </details>

5. Write `255.255.255.0` in binary. How many `1` bits does it have, and what CIDR is that?

   <details class="solution">
   <summary>Answer</summary>

   `11111111.11111111.11111111.00000000`: 24 ones, so **/24**.

   </details>
