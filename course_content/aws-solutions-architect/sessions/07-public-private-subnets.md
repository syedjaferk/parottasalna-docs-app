# Session 7 · Public & Private Subnets with EC2 and Docker

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/GS5Eyvl01nY"
  title="Session 7: Public and private subnets with EC2 and Docker" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 **Session 7** of the [AWS Solutions Architect playlist](https://www.youtube.com/playlist?list=PLYmjGMwZ9N88) (Tamil) · [watch on YouTube](https://www.youtube.com/watch?v=GS5Eyvl01nY)

## What you'll learn

- What a **VPC** is and how to plan its **CIDR** range
- **Subnets** and AZs, and why AWS reserves 5 addresses in each
- **Route tables**: the single setting that makes a subnet public or private
- The **Internet Gateway**
- **Security groups** vs **network ACLs**, stateful vs stateless, and the three-tier pattern
- Running Docker apps on EC2 in public and private subnets, and simulating it all locally

```{raw} html
:file: ../diagrams/s07-vpc.html
```

## 1. The VPC (Virtual Private Cloud)

**🧑 In plain words.** A **gated apartment complex** that belongs only to you inside the huge AWS
city. You decide the street layout, which blocks face the main road, and who the guards let in.

**❓ The problem it solves.** Without isolation, your servers would sit on one big shared network
with everyone else's. A VPC gives you a private network with your own IP ranges, routing and firewalls.

**⚙️ How it works.**

- A VPC lives in **one Region** and spans **all its AZs**.
- You give it an IPv4 **CIDR block** between `/16` (65,536 addresses) and `/28` (16), from the
  private ranges: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`. You can add secondary CIDRs and an IPv6 block later.
- Every account has a **default VPC** in each Region (`172.31.0.0/16`, public subnets in every AZ)
  for quick starts. For real work, create your own.
- Inside every VPC: a **main route table**, a **default security group**, a **default NACL**, and the
  **VPC DNS resolver** at base +2 (e.g. `10.0.0.2`).

**CIDR in one line:** the number after the `/` says how many bits are fixed for the network; the rest
are for hosts. A `/n` block has 2^(32 − n) addresses: `/16` = 65,536, `/24` = 256, `/28` = 16.
Bigger number = smaller network. **Plan ranges so VPCs you may connect later don't overlap**
([Session 9](09-vpc-peering.md)).

**💡 Example.** A company plans `10.0.0.0/16` for prod, `10.1.0.0/16` for staging, `10.2.0.0/16` for
dev and leaves `10.100.0.0/16` for the office network, so any of them can be connected later.

## 2. Subnets

**🧑 In plain words.** The **blocks** inside the complex. Each block is in one specific building
(AZ), and you decide which blocks face the main road.

**❓ The problem it solves.** Different groups of servers need different exposure and placement:
public web servers, private apps, isolated databases, spread across AZs for availability.

**⚙️ How it works.**

- A subnet is a slice of the VPC CIDR **in exactly one AZ** (e.g. `10.0.1.0/24` in `ap-south-1a`).
- AWS **reserves 5 addresses** in each subnet. In `10.0.1.0/24`: `.0` network, `.1` VPC router,
  `.2` DNS, `.3` reserved for future use, `.255` broadcast. So a `/24` has **251** usable IPs.
- Each subnet is associated with **one route table** and **one NACL**.
- Settings: *auto-assign public IPv4* (on for public subnets), IPv6 assignment.
- **Typical layout:** for each AZ, a public subnet (load balancers, NAT), a private app subnet and a
  private data subnet.

| Subnet | AZ a | AZ b |
|---|---|---|
| public | `10.0.1.0/24` | `10.0.2.0/24` |
| private app | `10.0.11.0/24` | `10.0.12.0/24` |
| private data | `10.0.21.0/24` | `10.0.22.0/24` |

**💡 Example.** A Kubernetes cluster needs many IPs (one per pod), so its private subnets are `/20`
(4,091 usable) instead of `/24`.

## 3. Route tables: what makes a subnet public

**🧑 In plain words.** The **signboards** at each block's exit: "Main road → this way". A block with
no signboard to the main road is effectively inner, whatever its name.

**❓ The problem it solves.** Traffic needs rules for where to go: to other subnets, to the internet,
to a NAT, to a peered VPC, to a VPN.

**⚙️ How it works.** A route table is a list of **destination → target** entries. The most specific
matching route wins (longest prefix match). Every route table has an unremovable **local** route for
the VPC CIDR, so all subnets can reach each other.

```text
Public subnet route table            Private subnet route table
10.0.0.0/16   local                  10.0.0.0/16   local
0.0.0.0/0     igw-0abc123            (nothing else, or 0.0.0.0/0 → nat-… in Session 8)
```

A subnet is **public** if its route table sends `0.0.0.0/0` to an **Internet Gateway**. That's the
only difference; the subnet's name means nothing. Targets you'll meet later: `nat-…` (NAT Gateway),
`pcx-…` (peering), `tgw-…` (Transit Gateway), `vpce-…` (gateway endpoint), `vgw-…` (VPN).

**💡 Example.** A team names a subnet "public-1" but associates it with the main route table (local
only). Instances there have public IPs but are unreachable. The fix is the route, not the name.

## 4. The Internet Gateway (IGW)

**🧑 In plain words.** The complex's **main gate** to the public road.

**❓ The problem it solves.** Something has to connect the private VPC network to the internet, and
translate between public and private addresses.

**⚙️ How it works.** One IGW per VPC; **horizontally scaled, redundant and free**. It performs a
**1:1 NAT** between an instance's public IPv4 and its private IPv4 (for IPv6 there's no translation).
Without an IGW (and a route to it), nothing in the VPC reaches the internet directly.

**💡 Example.** `curl ifconfig.me` from a public instance prints its **public** IP, even though
`ip addr` on the instance only shows `10.0.1.25`: the IGW translated the address on the way out.

## 5. Security groups

**🧑 In plain words.** A **personal bodyguard** for each server: a list of who is allowed to come
in. Once a guest is in, they're allowed to leave again without a second check.

**❓ The problem it solves.** Each server should accept only the traffic it needs (e.g. port 443 from
the load balancer), whatever subnet it's in.

**⚙️ How it works.**

- Attached to **network interfaces** (instances, load balancers, RDS, Lambda in a VPC…).
- **Allow rules only**; everything not allowed is denied.
- **Stateful:** if inbound traffic is allowed, the reply is automatically allowed out (and vice versa).
- Sources can be CIDR ranges, **prefix lists**, or **other security groups** (the key trick).
- Default: no inbound rules, all outbound allowed. Changes apply immediately.

**Three-tier pattern** (reference security groups, not IPs):

| Security group | Inbound rule |
|---|---|
| `alb-sg` | 443 from `0.0.0.0/0` |
| `app-sg` | 8000 from **`alb-sg`** |
| `db-sg` | 5432 from **`app-sg`** |

**💡 Example.** Auto Scaling adds 10 app servers with new IPs; the database rule "5432 from
`app-sg`" covers them all with no change.

## 6. Network ACLs (NACLs)

**🧑 In plain words.** The **checkpoint at each block's entrance**, with a numbered rule book that
checks everyone going in **and** out, and doesn't remember who it let in.

**❓ The problem it solves.** A coarse, subnet-wide layer of defence, including the ability to
**deny** specific IPs, which security groups can't do.

**⚙️ How it works.**

| | Security group | Network ACL |
|---|---|---|
| Applies to | network interfaces | **subnets** |
| Rules | allow only | **allow and deny** |
| State | **stateful** | **stateless**: replies need their own rule |
| Evaluation | all rules together | **in number order**, first match wins |
| Default | deny in, allow out | default NACL allows all; a **new custom NACL denies all** |

Because NACLs are stateless, allow **ephemeral ports 1024–65535** for replies (outbound for
inbound requests, inbound for requests your servers make).

**💡 Example.** An attacker at `203.0.113.50` hammers your web subnet. Add NACL rule 50:
`DENY all traffic from 203.0.113.50/32` (before the allow rules at 100+).

## 7. Hands-on: Docker on EC2 in both subnets

1. **Create the VPC** (*VPC → Create VPC → VPC only*): `10.0.0.0/16`.
2. **Subnets:** `10.0.1.0/24` (public, AZ a) and `10.0.2.0/24` (private, AZ a).
3. **Internet Gateway:** create → *Attach to VPC*.
4. **Route tables:** a `public-rt` with `0.0.0.0/0 → igw`, associated with the public subnet. The
   private subnet keeps the main route table (local only).
5. **Public EC2** (auto-assign public IP on) with user data that runs a container:

   ```bash
   #!/bin/bash
   dnf install -y docker
   systemctl enable --now docker
   docker run -d --restart unless-stopped -p 80:80 --name web nginx:alpine
   ```

6. **Private EC2** in `10.0.2.0/24`, no public IP, security group allowing SSH/HTTP **only from the
   public instance's security group**.

Test from your laptop and from the public instance:

```bash
curl http://<public-instance-ip>             # nginx welcome page ✓
ssh ec2-user@<public-instance-ip>
curl --max-time 5 http://10.0.2.25           # reach the private instance from inside the VPC ✓
```

The private instance can't install Docker yet (`dnf install` times out): it has **no route to the
internet**. Fixing that safely is exactly what the **NAT Gateway** in [Session 8](08-nat-gateway.md) does.

:::{tip}
*VPC → Create VPC → **VPC and more*** builds all of this (public and private subnets in 2 AZs,
IGW, route tables, optional NAT) in one wizard and shows a preview diagram. Build it by hand once to
understand it, then use the wizard.
:::

## 8. Simulate it on your laptop with Docker

In class we copied the same idea with two Docker networks: a normal one (public) and an
`--internal` one (private, no way out), with a "public server" plugged into both:

```bash
docker network create --subnet=10.10.0.0/24 public-net
docker network create --internal --subnet=10.20.0.0/24 private-net

docker run -dit --name public-server --hostname public-server --network public-net ubuntu:24.04
docker network connect private-net public-server            # second network card in the private network
docker run -dit --name private-server --hostname private-server --network private-net ubuntu:24.04
```

| AWS | Docker simulation |
|---|---|
| VPC with two subnets | two Docker networks |
| public subnet (route to the IGW) | `public-net`: can reach the internet |
| private subnet (local route only) | `private-net` with `--internal`: no way out |
| bastion host in the public subnet | `public-server`, connected to both networks |

Check it:

```bash
docker exec private-server bash -c 'timeout 5 bash -c "</dev/tcp/1.1.1.1/80" && echo "internet OK" || echo "no internet"'
```

**Output:**

```text
bash: connect: Network is unreachable
no internet
```

Just like the private subnet: the private server can talk to `public-server`, but not to the
internet. [Session 8](08-nat-gateway.md) turns `public-server` into a NAT to fix that.

## Common mistakes

- **Instance in a "public" subnet but no public IP:** auto-assign was off.
- **Route table not associated:** the subnet silently uses the main route table.
- **Opening `0.0.0.0/0` on database ports.** Reference security groups instead.
- **Forgetting the NACL is stateless:** allowing inbound 443 but blocking the outbound
  ephemeral ports (1024–65535) the replies use.

## Hands-on exercises

VPCs, subnets, route tables, Internet Gateways, security groups and NACLs are **free**. ⚠️ EC2
instances and public IPv4 addresses cost money; terminate them at the end.

**Exercise 1 · Build a VPC by hand.** Create `lab-vpc` (`10.0.0.0/16`) with `public-a`
(`10.0.1.0/24`, AZ a) and `private-a` (`10.0.2.0/24`, AZ a).

<details class="solution"><summary>CLI</summary>

```bash
VPC=$(aws ec2 create-vpc --cidr-block 10.0.0.0/16 --query Vpc.VpcId --output text)
aws ec2 create-tags --resources $VPC --tags Key=Name,Value=lab-vpc
PUB=$(aws ec2 create-subnet --vpc-id $VPC --cidr-block 10.0.1.0/24 --availability-zone ap-south-1a --query Subnet.SubnetId --output text)
PRIV=$(aws ec2 create-subnet --vpc-id $VPC --cidr-block 10.0.2.0/24 --availability-zone ap-south-1a --query Subnet.SubnetId --output text)
```

</details>

**Exercise 2 · Make one subnet public.** Create and attach an Internet Gateway, a route table with
`0.0.0.0/0 → igw`, associate it with `public-a`, and turn on auto-assign public IPv4.

<details class="solution"><summary>CLI</summary>

```bash
IGW=$(aws ec2 create-internet-gateway --query InternetGateway.InternetGatewayId --output text)
aws ec2 attach-internet-gateway --internet-gateway-id $IGW --vpc-id $VPC
RT=$(aws ec2 create-route-table --vpc-id $VPC --query RouteTable.RouteTableId --output text)
aws ec2 create-route --route-table-id $RT --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW
aws ec2 associate-route-table --route-table-id $RT --subnet-id $PUB
aws ec2 modify-subnet-attribute --subnet-id $PUB --map-public-ip-on-launch
```

</details>

**Exercise 3 · Count usable IPs.** Check `AvailableIpAddressCount` of `public-a`. Why isn't it 256?

<details class="solution"><summary>Answer</summary>

`aws ec2 describe-subnets --subnet-ids $PUB --query 'Subnets[].AvailableIpAddressCount'` → **251**:
AWS reserves 5 addresses (.0, .1, .2, .3 and .255).

</details>

**Exercise 4 · Docker web server in the public subnet.** Launch an instance in `public-a` with the
nginx Docker user data (section 7) and open its public IP in a browser.

<details class="solution"><summary>Check</summary>

Security group allows 80 from your IP. The nginx welcome page loads. `docker ps` on the instance
shows the `web` container.

</details>

**Exercise 5 · A private instance.** Launch an instance in `private-a` with **no public IP**. From the
public instance, reach it on its private IP.

<details class="solution"><summary>Check</summary>

Private instance SG allows SSH/ICMP **from the public instance's security group**. From the public
instance: `ping 10.0.2.x` works; from your laptop the private instance is unreachable (no public IP, no route).

</details>

**Exercise 6 · Prove the private subnet has no internet.** On the private instance, try
`curl --max-time 5 https://aws.amazon.com`.

<details class="solution"><summary>Expected</summary>

It times out: the private route table has only the `local` route. [Session 8](08-nat-gateway.md) fixes this with a NAT Gateway.

</details>

**Exercise 7 · Break and fix "public".** Remove the `0.0.0.0/0 → igw` route from the public route
table and reload the web page. Then add it back.

<details class="solution"><summary>Answer</summary>

The page stops loading even though the instance still has a public IP: without the route, the subnet
is no longer public. Adding the route back restores it immediately.

</details>

**Exercise 8 · Security group chaining.** Create `web-sg` (80 from anywhere) and `app-sg`
(8080 from `web-sg` only). Run a container on the private instance on 8080 and reach it from the
public instance only.

<details class="solution"><summary>Check</summary>

`docker run -d -p 8080:80 nginx:alpine` on the private instance (pull needs internet; use an image
baked into the AMI or do this after Session 8's NAT). From the public instance `curl 10.0.2.x:8080`
works; a third instance without `web-sg` is refused.

</details>

**Exercise 9 · Stateless NACL trap.** Create a custom NACL for `public-a` that allows only inbound
80 and outbound 80. Does the web page load? Fix it.

<details class="solution"><summary>Answer</summary>

It doesn't: replies go back to the browser's **ephemeral port** (1024–65535), which the outbound
rules don't allow. Add outbound `1024-65535 ALLOW 0.0.0.0/0` (and inbound ephemeral ports for
requests the instance makes itself).

</details>

**Exercise 10 · Block one IP with a NACL.** Find your public IP (`curl ifconfig.me`) and add a NACL
rule number **50** denying it. Does the page still load for you? Remove the rule.

<details class="solution"><summary>Answer</summary>

No, because rule 50 (deny) is evaluated before the allow rules (100+). This is something a security
group can't do.

</details>

**Exercise 11 · Simulate locally.** Do section 8's Docker simulation: create `public-net` and an
`--internal` `private-net`, connect `public-server` to both, and show the private server has no
internet but can reach the public server.

<details class="solution"><summary>Check</summary>

`docker exec private-server bash -c 'timeout 5 bash -c "</dev/tcp/1.1.1.1/80"'` fails with
*Network is unreachable*; `docker exec public-server ip -br addr` (after installing iproute2) shows two
network cards, one in each network.

</details>

**Exercise 12 · Use the wizard.** Create a second VPC with *VPC → Create VPC → **VPC and more***:
2 AZs, 2 public + 2 private subnets, **no NAT**. Compare its route tables with yours.

<details class="solution"><summary>What to notice</summary>

The wizard creates the same pieces: one public route table (`0.0.0.0/0 → igw`) shared by both
public subnets, and one route table per private subnet (local only). The preview diagram shows the layout.

</details>

**Exercise 13 · Clean up.** Terminate the instances, then delete the VPCs (deleting a VPC removes its
subnets, route tables, IGW attachment and security groups).

<details class="solution"><summary>Order</summary>

Instances must be terminated first. Then *VPC → Your VPCs → Delete VPC* lists and deletes the
dependent resources.

</details>

## Class files

- {download}`Docker networks for the local simulation <../code/07-subnets-local/docker-networks.txt>`
- {download}`Whiteboard: AWS public & private subnets <../code/whiteboards/07-public-private-subnets.drawio>`
  (open at [app.diagrams.net](https://app.diagrams.net))
