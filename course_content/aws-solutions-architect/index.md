# AWS Solutions Architect (SAA-C03)

Welcome! This course takes you from "what is the cloud?" to designing secure, highly available
systems on AWS, the way a Solutions Architect thinks. It follows the live bootcamp and its
**[YouTube playlist](https://www.youtube.com/playlist?list=PLYmjGMwZ9N88)** (Tamil):
**one chapter per session**, with the recording at the top.

## How each chapter works

Every concept is explained four ways:

- **🧑 In plain words:** an everyday comparison anyone can follow
- **❓ The problem it solves:** why the thing exists at all
- **⚙️ How it works:** the technical details, limits and numbers an architect needs
- **💡 Example:** a concrete scenario, command or configuration

Then come the class demos (with the real code from the sessions), the **common mistakes**, and **at
least 10 hands-on exercises** with step-by-step solutions you can reveal. Exercises that create paid
resources are marked ⚠️ and end with a clean-up step. At the end of each chapter you'll find a
**quiz** (including exam-style scenario questions for SAA-C03) and **flashcards** for revision.

:::{tip}
New to AWS? Start with **[Setup](setup.md)**. It shows how to create your account *safely*: MFA
on the root user and a **budget alert**, so a forgotten resource never surprises you with a bill.
The **[Course map](course-map.md)** shows how the sessions fit the 12 modules of the bootcamp.
:::

:::{important}
**Clean up after every lab.** Some resources cost money every hour they exist, even when idle:
NAT Gateways, load balancers, interface endpoints, Elastic IPs that aren't attached and Transit
Gateway attachments. Each chapter ends with a clean-up note.
:::

```{toctree}
:maxdepth: 1
:caption: Getting started

setup
course-map
```

```{toctree}
:maxdepth: 1
:caption: Cloud foundations & IAM

sessions/01-introduction-to-aws
sessions/02-iam-deep-dive
```

```{toctree}
:maxdepth: 1
:caption: Compute & load balancing

sessions/04-load-balancing-haproxy
sessions/05-elastic-load-balancer
sessions/06-ec2-networking-storage
```

```{toctree}
:maxdepth: 1
:caption: VPC networking

sessions/07-public-private-subnets
sessions/08-nat-gateway
sessions/09-vpc-peering
sessions/10-transit-gateway
sessions/11-vpc-endpoints
```

```{toctree}
:maxdepth: 1
:caption: Security, visibility & DNS

sessions/12-aws-waf
sessions/13-vpc-flow-logs-dns
sessions/14-route-53
```

```{toctree}
:maxdepth: 1
:caption: Storage & serverless

sessions/15-amazon-s3
sessions/16-api-gateway
```
