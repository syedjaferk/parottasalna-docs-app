# AWS Solutions Architect (SAA-C03)

Welcome! This course takes you from "what is the cloud?" to designing secure, highly available
systems on AWS, the way a Solutions Architect thinks. It follows the live bootcamp and its
**[YouTube playlist](https://www.youtube.com/playlist?list=PLYmjGMwZ9N88)** (Tamil):
**one chapter per session**, with the recording at the top.

Every chapter explains the idea in simple words, with an everyday example and a diagram, then shows
the console steps or CLI commands, the mistakes people usually make, and exercises with answers.
At the end of each chapter you'll find a **quiz** (including exam-style scenario questions for
SAA-C03) and a set of **flashcards** for revision.

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
