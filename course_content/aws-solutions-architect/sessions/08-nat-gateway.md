# Session 8 · NAT Gateway

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/rpqVSdKU1XM"
  title="Session 8: NAT Gateway" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 **Session 8** of the [AWS Solutions Architect playlist](https://www.youtube.com/playlist?list=PLYmjGMwZ9N88) (Tamil) · [watch on YouTube](https://www.youtube.com/watch?v=rpqVSdKU1XM)

## What you'll learn

- What **NAT** (Network Address Translation) is and why private subnets need it
- **Internet Gateway vs NAT Gateway**
- How the **routing** fits together, packet by packet
- **High availability** (one NAT per AZ) and **cost** (and how to cut it)
- **NAT Gateway vs NAT instance**, and **private NAT gateways**
- Building a NAT yourself with iptables, locally

```{raw} html
:file: ../diagrams/s08-nat.html
```

## 1. NAT: Network Address Translation

**🧑 In plain words.** An office **receptionist who makes outside calls for staff**. Callers outside
only ever see the office's main number; when they call back, the receptionist passes the call to the
right person. But nobody outside can dial an employee's desk directly.

**❓ The problem it solves.** Private servers (app servers, databases) still need to go **out** to the
internet: OS updates, `pip install`, Docker image pulls, calling a payment or SMS API. But they must
**never be reachable from** the internet.

**⚙️ How it works.** The NAT device sits between the private network and the internet. For each
outgoing connection it:

1. replaces the private **source IP** (e.g. `10.0.2.15`) with its own **public IP**, and the source
   port with one it picks,
2. records the mapping in a **connection table**,
3. when a reply arrives on that port, looks up the table and forwards it back to `10.0.2.15`.

A packet arriving from the internet with **no matching entry** (a new inbound connection) has nowhere
to go and is dropped. That's why NAT allows "out and replies back" but not "in".

**💡 Example.** Ten private app servers all show the **same source IP** (the NAT's Elastic IP) to the
outside world: `curl https://checkip.amazonaws.com` prints the NAT's address on every one of them.

## 2. Internet Gateway vs NAT Gateway

**🧑 In plain words.** The **IGW** is the building's **main gate** (people go in and out). The **NAT
Gateway** is the **receptionist's phone line** (staff can call out; outsiders can't call in).

**❓ The problem it solves.** Knowing which one a subnet needs, and why private subnets don't simply
use the IGW.

**⚙️ How it works.**

| | Internet Gateway | NAT Gateway |
|---|---|---|
| Direction | in **and** out | **out only** (plus replies) |
| Used by | public subnets | private subnets |
| Instance needs a public IP? | yes | no |
| Address translation | 1:1 (public ↔ private per instance) | many-to-one (many private → one EIP) |
| Lives in | the VPC (one per VPC) | **one AZ, in a public subnet** |
| Scaling | automatic | automatic, up to 100 Gbps |
| Cost | free | **hourly + per GB processed** |

**💡 Example.** The web servers (public subnet) use the IGW directly; the app servers and the database
(private subnets) use the NAT Gateway for updates, which itself uses the IGW.

## 3. How the routing works

**🧑 In plain words.** Two signboards in a row: the private block's sign says "outside → reception",
and reception's sign says "outside → main gate".

**❓ The problem it solves.** Traffic must take the right path both ways.

**⚙️ How it works.**

```text
Private subnet route table           Public subnet route table (where the NAT lives)
10.0.0.0/16   local                  10.0.0.0/16   local
0.0.0.0/0     nat-0def456            0.0.0.0/0     igw-0abc123
```

A packet from `10.0.2.15` to `142.250.x.x`: private route table → **NAT Gateway** (source becomes
`10.0.1.100`, the NAT's private IP) → public route table → **IGW** (source becomes the NAT's **Elastic
IP**) → internet. The reply retraces the path; the NAT maps it back to `10.0.2.15`.

**💡 Example.** If the NAT Gateway is wrongly placed in the **private** subnet, its own route to the
internet is missing (no IGW route there), so nothing works.

## 4. High availability and cost

**🧑 In plain words.** If the only receptionist sits in building A and building A loses power,
staff in buildings B and C can't call out either.

**❓ The problem it solves.** Designing so one AZ failure doesn't cut every private server off the
internet, without overspending.

**⚙️ How it works.**

- A NAT Gateway is **redundant inside its AZ**, but it **lives in one AZ**.
- **Production pattern:** one NAT Gateway **per AZ**; each private subnet's route table points to the
  NAT **in its own AZ**. This also avoids **cross-AZ data charges**.
- **Cost:** per hour per NAT Gateway, plus **per GB processed** (on top of normal data transfer).
- Save money: use **gateway endpoints** for S3 and DynamoDB (free, [Session 11](11-vpc-endpoints.md)),
  interface endpoints for heavy AWS-service traffic, and in dev/labs use **one** NAT or none, and delete it after.
- After deleting a NAT Gateway, **release its Elastic IP** (it's still billed).

**💡 Example.** A data pipeline pulls 10 TB/month from S3 through the NAT: you pay NAT processing on
all of it. Adding a free **S3 gateway endpoint** removes that charge entirely.

## 5. NAT Gateway vs NAT instance, and private NAT

**🧑 In plain words.** A **NAT Gateway** is a professional receptionist service the building runs for
you. A **NAT instance** is you asking one of your own staff to also handle the phones: cheaper, but
when they're sick, nobody covers.

**❓ The problem it solves.** Choosing between managed convenience and do-it-yourself cost/control.

**⚙️ How it works.**

| | NAT Gateway | NAT instance (EC2) |
|---|---|---|
| Managed by | AWS | **you** (patching, scaling, failover) |
| Availability | redundant in its AZ | single instance unless you build failover |
| Bandwidth | up to 100 Gbps | depends on instance size |
| Security groups | not supported | yes |
| Setup | a few clicks | disable **source/destination check**, iptables (see section 7) |
| Bastion on the same box | no | possible (not recommended) |

**Private NAT gateway:** connectivity type *Private*, no Elastic IP. Used to connect private subnets
to **other VPCs or on-premises** networks (via Transit Gateway or VPN) when IP ranges overlap, by
translating to the NAT's private IP. It can't reach the internet.

**💡 Example.** A student lab uses a `t4g.nano` NAT instance to save cost; a production system always
uses NAT Gateways, one per AZ.

## 6. Hands-on: internet access for the private instance

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

## 7. Build a NAT yourself (local Docker lab)

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

## Hands-on exercises

⚠️ NAT Gateways cost money **every hour** and per GB. Do the AWS exercises in one sitting, delete
the NAT Gateway and **release its Elastic IP** at the end. The local Docker exercises are free.

**Exercise 1 · Before NAT.** On a private instance (from [Session 7](07-public-private-subnets.md)),
confirm there's no internet: `curl --max-time 5 https://checkip.amazonaws.com`.

<details class="solution"><summary>Expected</summary>

Timeout. The private route table only has the `local` route.

</details>

**Exercise 2 · Create the NAT Gateway.** Create a **public** NAT Gateway in the **public** subnet with
a new Elastic IP, and wait until it's *Available*.

<details class="solution"><summary>CLI</summary>

```bash
EIP=$(aws ec2 allocate-address --query AllocationId --output text)
NAT=$(aws ec2 create-nat-gateway --subnet-id $PUB --allocation-id $EIP --query NatGateway.NatGatewayId --output text)
aws ec2 wait nat-gateway-available --nat-gateway-ids $NAT
```

</details>

**Exercise 3 · Route the private subnet.** Add `0.0.0.0/0 → nat-…` to the private route table and
repeat Exercise 1.

<details class="solution"><summary>Expected</summary>

`curl https://checkip.amazonaws.com` now prints the **NAT Gateway's Elastic IP**, not the instance's
(it has no public IP).

</details>

**Exercise 4 · Install software through NAT.** On the private instance install Docker and run
`docker pull nginx:alpine`.

<details class="solution"><summary>Check</summary>

`sudo dnf install -y docker && sudo systemctl start docker && sudo docker pull nginx:alpine` succeeds.

</details>

**Exercise 5 · Inbound is still blocked.** From your laptop, try to reach the private instance via the
NAT's Elastic IP (`curl --max-time 5 http://<nat-eip>`, `ssh ec2-user@<nat-eip>`). What happens and why?

<details class="solution"><summary>Answer</summary>

Nothing answers: a NAT Gateway never forwards new inbound connections, there's no port mapping to configure.

</details>

**Exercise 6 · Misplace it on purpose.** Create a second NAT Gateway in the **private** subnet and point
the private route table at it. Does internet access work? Then delete it.

<details class="solution"><summary>Answer</summary>

No: the private subnet has no route to the IGW, so the NAT itself can't reach the internet. A public
NAT Gateway must be in a public subnet.

</details>

**Exercise 7 · Check the NAT's metrics.** In CloudWatch, find `BytesOutToDestination`,
`ActiveConnectionCount` and `ErrorPortAllocation` for your NAT Gateway after Exercise 4.

<details class="solution"><summary>Where</summary>

CloudWatch → Metrics → **NATGateway** → per-NAT metrics. `ErrorPortAllocation` > 0 means too many
simultaneous connections to the same destination; fix by spreading traffic or adding NAT Gateways.

</details>

**Exercise 8 · Design for two AZs.** Draw (or build) a VPC with public and private subnets in AZ a
and b. Where do the NAT Gateways go, and what does each private route table point to?

<details class="solution"><summary>Model answer</summary>

`nat-a` in `public-a`, `nat-b` in `public-b`. `private-a` route table: `0.0.0.0/0 → nat-a`;
`private-b` route table: `0.0.0.0/0 → nat-b`. Losing AZ a doesn't affect AZ b's internet access.

</details>

**Exercise 9 · Estimate the bill.** With the Pricing Calculator, compare one NAT Gateway vs three
(one per AZ) for a month, with 100 GB processed. Is HA worth it for dev? For prod?

<details class="solution"><summary>What to conclude</summary>

Three NATs cost about three times the hourly part. Usually **one NAT in dev** (accepting the risk) and
**one per AZ in prod**.

</details>

**Exercise 10 · Build a NAT locally.** Do section 7's Docker lab: give `public-server` the iptables
NAT rules, set `private-server`'s default route, and confirm `internet OK`.

<details class="solution"><summary>Check</summary>

`docker exec private-server bash -c 'timeout 5 bash -c "</dev/tcp/1.1.1.1/80" && echo "internet OK"'`
prints `internet OK`. Remove the `MASQUERADE` rule (`iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE`)
and it fails again.

</details>

**Exercise 11 · Watch the translation.** In the local lab, run `apt-get install -y conntrack` on
`public-server` and, while the private server makes a request, list `conntrack -L`. Find the original
and translated addresses.

<details class="solution"><summary>What you'll see</summary>

An entry like `src=10.20.0.3 dst=1.1.1.1 ... src=1.1.1.1 dst=10.10.0.2`: the private source on the
way out, and the NAT's own address that replies come back to. That table is exactly what a NAT Gateway keeps.

</details>

**Exercise 12 · NAT instance in AWS (optional).** Launch a small Amazon Linux instance in the public
subnet, **disable source/destination check**, enable IP forwarding and MASQUERADE, and route the
private subnet to the **instance** instead of the NAT Gateway.

<details class="solution"><summary>Key steps</summary>

`aws ec2 modify-instance-attribute --instance-id i-… --no-source-dest-check`; on the instance:
`sudo sysctl -w net.ipv4.ip_forward=1` and `sudo iptables -t nat -A POSTROUTING -o ens5 -j MASQUERADE`
(interface name may differ); private route `0.0.0.0/0 → i-…` (target type *Instance*). Its SG must
allow traffic from the private subnet.

</details>

**Exercise 13 · Clean up.** Delete the NAT Gateway(s), **release the Elastic IPs**, remove the
`0.0.0.0/0 → nat` route, and terminate test instances.

<details class="solution"><summary>Check</summary>

VPC → NAT gateways: *Deleted*. EC2 → Elastic IPs: none left. Billing stops for both.

</details>

## Class files

- {download}`NAT with iptables (class commands) <../code/07-subnets-local/nat-with-iptables.txt>`
- {download}`Docker networks for the local simulation <../code/07-subnets-local/docker-networks.txt>`
