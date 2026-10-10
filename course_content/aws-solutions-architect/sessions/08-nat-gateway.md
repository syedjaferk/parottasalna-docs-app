# Session 8 · NAT Gateway

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/rpqVSdKU1XM"
  title="Session 8: NAT Gateway" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 **Session 8** of the [AWS Solutions Architect playlist](https://www.youtube.com/playlist?list=PLYmjGMwZ9N88) (Tamil) · [watch on YouTube](https://www.youtube.com/watch?v=rpqVSdKU1XM)

## The big idea

Private instances still need the internet **outbound**: OS updates, `pip install`, calling a
payment API. A **NAT Gateway** lets them go out **without ever being reachable from the internet**.
It sits in a public subnet and swaps the private source address for its own public Elastic IP;
replies come back through it, but new inbound connections can't start.

**Everyday example:** an office receptionist who makes outside calls for staff. Callers see only
the office number; when they reply, the receptionist passes it to the right person. But nobody
outside can dial an employee's desk directly.

```{raw} html
:file: ../diagrams/s08-nat.html
```

## 1. Internet Gateway vs NAT Gateway

| | Internet Gateway | NAT Gateway |
|---|---|---|
| Direction | in **and** out | **out only** (plus replies) |
| Used by | public subnets | private subnets |
| Instance needs a public IP? | yes | no |
| Lives in | the VPC (one per VPC) | **one AZ, in a public subnet** |
| Cost | free | **hourly charge + per GB processed** |

## 2. How the routing works

```text
Private subnet route table           Public subnet route table (where the NAT lives)
10.0.0.0/16   local                  10.0.0.0/16   local
0.0.0.0/0     nat-0def456            0.0.0.0/0     igw-0abc123
```

The private instance → NAT Gateway → Internet Gateway → internet, and back the same way.

## 3. Hands-on: internet access for the private instance

Continuing from [Session 7](07-public-private-subnets.md):

1. *VPC → NAT gateways → Create*: subnet = the **public** subnet, connectivity = **Public**,
   **Allocate Elastic IP**.
2. Wait for **Available**, then edit the **private** route table: `0.0.0.0/0 → nat-…`.
3. On the private instance (through the public one, or Session Manager):

```bash
curl -s https://checkip.amazonaws.com      # prints the NAT Gateway's Elastic IP, not a private IP
sudo dnf install -y docker                 # now works
```

**Output:**

```text
13.234.112.45
```

## 4. High availability and cost

- A NAT Gateway is redundant **inside its AZ** but **lives in one AZ**. If that AZ fails, private
  subnets in other AZs routed through it lose internet access.
- **Production pattern:** one NAT Gateway **per AZ**, and each private subnet routes to the NAT in
  its own AZ (this also avoids cross-AZ data charges).
- **Cost:** you pay per hour for each NAT Gateway plus per GB of data it processes. In labs, **delete
  it** when you finish, and then **release its Elastic IP**.
- Heavy traffic to S3 or DynamoDB through a NAT is a common surprise on the bill: a free **gateway
  endpoint** ([Session 11](11-vpc-endpoints.md)) keeps that traffic off the NAT.

:::{note}
A **NAT instance** (an EC2 instance doing NAT) is the old way: cheaper for tiny labs, but you must
manage it, disable *source/destination check*, and handle its failure yourself. AWS recommends NAT
Gateways.
:::

## 5. Build a NAT yourself (local Docker lab)

A NAT Gateway is "just" a machine that forwards packets and rewrites addresses. Using the Docker
networks from [Session 7](07-public-private-subnets.md), turn `public-server` into a **NAT instance**.
Recreate both containers with `--cap-add NET_ADMIN` (needed to change routes and firewall rules), then:

```bash
# 1. On public-server: install the tools and add the NAT rules
docker exec public-server bash -c 'apt-get update -qq && apt-get install -y -qq iproute2 iptables'
docker exec public-server bash -c '
  iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE                                   # rewrite the source IP
  iptables -A FORWARD -i eth1 -o eth0 -j ACCEPT                                          # private → internet
  iptables -A FORWARD -i eth0 -o eth1 -m state --state RELATED,ESTABLISHED -j ACCEPT    # only replies come back'

# 2. Point private-server's default route at public-server (its IP on private-net)
docker exec public-server ip -br -4 addr      # e.g. eth1 10.20.0.2/24
docker run --rm --net container:private-server --cap-add NET_ADMIN alpine:3.20 \
    ip route add default via 10.20.0.2
```

The private container has no internet yet, so it can't install `ip` itself. The small Alpine
container borrows its network (`--net container:private-server`) just to add the route.

```bash
docker exec private-server bash -c 'timeout 5 bash -c "</dev/tcp/1.1.1.1/80" && echo "internet OK"'
```

**Output:**

```text
internet OK
```

And from the public network, the private server is still **not reachable**: only connections it
starts get replies (`RELATED,ESTABLISHED`). That's the NAT Gateway's behaviour.

| iptables rule | What it does | AWS equivalent |
|---|---|---|
| `MASQUERADE` on `eth0` | replace the private source IP with public-server's IP | NAT Gateway's Elastic IP |
| `FORWARD eth1 → eth0 ACCEPT` | let private traffic out | private route `0.0.0.0/0 → nat-gw` |
| `FORWARD eth0 → eth1 RELATED,ESTABLISHED` | let only replies back in | NAT blocks new inbound connections |
| `ip_forward = 1` | allow the machine to route (Docker already enables it) | disable *source/dest check* on a NAT **instance** |

## Common mistakes

- **NAT Gateway placed in the private subnet.** It must be in a **public** subnet (one with a route to the IGW).
- **Forgetting the route** `0.0.0.0/0 → nat` in the private route table.
- **One NAT for all AZs in production** = a single point of failure.
- **Leaving it running after a lab** = a steady hourly bill.

## Try it yourself

1. A private EC2 instance can't reach the internet. The NAT Gateway exists and is *Available*.
   List three things to check.

   <details class="solution">
   <summary>Answer</summary>

   (1) The private subnet's route table has `0.0.0.0/0 → nat-…`. (2) The NAT is in a **public**
   subnet whose route table has `0.0.0.0/0 → igw`. (3) Security group outbound rules and the
   NACLs allow the traffic (and its replies).

   </details>

2. Can someone on the internet open an SSH session to a private instance through the NAT Gateway?

   <details class="solution">
   <summary>Answer</summary>

   No. A NAT Gateway only allows connections that start from inside; it never forwards new inbound connections.

   </details>

## Class files

- {download}`NAT with iptables (class commands) <../code/07-subnets-local/nat-with-iptables.txt>`
- {download}`Docker networks for the local simulation <../code/07-subnets-local/docker-networks.txt>`
