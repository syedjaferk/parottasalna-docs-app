# Session 7 · Public & Private Subnets with EC2 and Docker

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/GS5Eyvl01nY"
  title="Session 7: Public and private subnets with EC2 and Docker" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 **Session 7** of the [AWS Solutions Architect playlist](https://www.youtube.com/playlist?list=PLYmjGMwZ9N88) (Tamil) · [watch on YouTube](https://www.youtube.com/watch?v=GS5Eyvl01nY)

## The big idea

A **VPC** (Virtual Private Cloud) is your own private network inside AWS. You split it into
**subnets**: **public** ones for things the internet must reach (load balancers, a web server), and
**private** ones for things it must never reach (app servers, databases). What makes a subnet
public is just **one route**: `0.0.0.0/0 → Internet Gateway`.

**Everyday example:** a gated apartment complex. The **gate** is the Internet Gateway. Flats facing
the main road (public subnet) have a door to the street; inner flats (private subnet) can only be
reached from inside the complex.

```{raw} html
:file: ../diagrams/s07-vpc.html
```

## 1. The building blocks

| Piece | What it does |
|---|---|
| **VPC** | a private IP range, e.g. `10.0.0.0/16` (65,536 addresses), in one Region |
| **Subnet** | a slice of the VPC in **one AZ**, e.g. `10.0.1.0/24`. AWS reserves 5 addresses in each subnet (first four and last), so a /24 gives 251 usable IPs |
| **Route table** | rules for where traffic goes; every subnet is associated with exactly one |
| **Internet Gateway (IGW)** | the VPC's door to the internet; one per VPC, highly available, free |
| **Security group** | a **stateful** firewall on each instance/ENI: allow rules only; replies are allowed automatically |
| **Network ACL** | a **stateless** firewall on the subnet: allow and deny rules, numbered; replies must be allowed explicitly |

:::{note}
**CIDR in one line:** the number after the `/` says how many bits are fixed for the network; the rest
are for hosts. A `/n` block has 2^(32 − n) addresses: `/16` = 65,536, `/24` = 256, `/28` = 16.
Bigger number = smaller network. Use private ranges (`10.x`, `172.16–31.x`, `192.168.x`) and plan
them so VPCs you may connect later **don't overlap** ([Session 9](09-vpc-peering.md)).
:::

## 2. Public vs private: it's the route table

```text
Public subnet route table            Private subnet route table
10.0.0.0/16   local                  10.0.0.0/16   local
0.0.0.0/0     igw-0abc123            (nothing else)
```

An instance in the public subnet also needs a **public IP** (turn on *auto-assign public IPv4* on
the subnet, or attach an Elastic IP) to actually be reachable.

## 3. Security groups: chaining tiers

A clean three-tier pattern references **security groups instead of IP ranges**:

| Security group | Inbound rule |
|---|---|
| `alb-sg` | 443 from `0.0.0.0/0` |
| `app-sg` | 8000 from **`alb-sg`** |
| `db-sg` | 5432 from **`app-sg`** |

Only the load balancer can reach the app, and only the app can reach the database, no matter how
many instances come and go.

## 4. Hands-on: Docker on EC2 in both subnets

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

## 5. Simulate it on your laptop with Docker

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

## Try it yourself

1. Remove the `0.0.0.0/0 → igw` route from the public route table. What happens to the web page?

   <details class="solution">
   <summary>Answer</summary>

   It stops loading: the subnet is now private, because nothing routes internet traffic to the IGW,
   even though the instance still has a public IP.

   </details>

2. How many usable IP addresses does a `/28` subnet have in AWS?

   <details class="solution">
   <summary>Answer</summary>

   16 − 5 reserved = **11**.

   </details>

3. Security group or NACL: which one would you use to block a single attacking IP address?

   <details class="solution">
   <summary>Answer</summary>

   A **NACL**: security groups only have allow rules, so they can't deny one IP.

   </details>

## Class files

- {download}`Docker networks for the local simulation <../code/07-subnets-local/docker-networks.txt>`
- {download}`Whiteboard: AWS public & private subnets <../code/whiteboards/07-public-private-subnets.drawio>`
  (open at [app.diagrams.net](https://app.diagrams.net))
