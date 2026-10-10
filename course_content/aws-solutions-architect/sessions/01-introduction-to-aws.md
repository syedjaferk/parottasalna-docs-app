# Session 1 · Introduction to AWS: Cloud, Global Infrastructure & IAM

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/5bvkQEp_Tgg"
  title="Session 1: Introduction to AWS" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 **Session 1** of the [AWS Solutions Architect playlist](https://www.youtube.com/playlist?list=PLYmjGMwZ9N88) (Tamil) · [watch on YouTube](https://www.youtube.com/watch?v=5bvkQEp_Tgg)

## What you'll learn

- What cloud computing really is, and the problems it solves compared with running your own servers
- The service models (IaaS, PaaS, SaaS) and deployment models (public, private, hybrid)
- AWS global infrastructure: **Regions**, **Availability Zones** and **edge locations**, and how to choose a Region
- The **shared responsibility model**: what AWS secures and what *you* must secure
- A first look at **IAM** (users, groups, roles, policies)
- How to navigate the console and the CLI, and create your first resource

Each concept below is explained four ways: **🧑 in plain words**, **❓ the problem it solves**,
**⚙️ how it works technically**, and **💡 an example**.

## 1. Cloud computing

**🧑 In plain words.** Instead of buying computers and keeping them in your office, you rent them
from a company that runs huge data centres, over the internet, by the hour. Like electricity: you
don't build a power plant to switch on a fan; you plug in and pay for the units you use.

**❓ The problem it solves.** Running your own servers ("on-premises") means:

- **Buying ahead:** you order servers weeks or months before you need them, and guess how many.
- **Wasted or missing capacity:** guess too high and money sits idle; guess too low and the site
  crashes on a busy day (exam results, a sale, a viral video).
- **Big up-front cost:** lakhs spent before a single user arrives.
- **Running a building:** power backup, cooling, security guards, hardware repairs, spare parts.
- **Slow experiments:** trying an idea means a purchase order, not a click.

**⚙️ How it works.** A cloud provider runs millions of servers in data centres and uses
**virtualisation** to slice each physical machine into many virtual ones. Everything is exposed
through **APIs**: the web console, the CLI and SDKs are all just clients calling those APIs. You
are billed by measured use: per second/hour of compute, per GB stored, per GB transferred out, per
request. The six classic benefits (straight from AWS, and common in exam questions):

| Benefit | Meaning |
|---|---|
| Trade fixed expense (capex) for variable expense (opex) | pay as you use, not up front |
| Benefit from massive economies of scale | AWS buys at huge volume; prices drop over time |
| Stop guessing capacity | scale up and down with real demand |
| Increase speed and agility | new resources in minutes |
| Stop spending money running data centres | focus on your product, not cooling and racks |
| Go global in minutes | deploy in Regions around the world |

**💡 Example.** A college results website gets 500 visitors a day, and 5 lakh visitors in the hour
results are published. On-premises, you'd buy servers for the peak and leave them idle 364 days a
year. In AWS, you run two small servers normally and let **Auto Scaling** add 30 more for that one
hour, paying for 30 servers × 1 hour.

## 2. Service models: IaaS, PaaS, SaaS

**🧑 In plain words.** Think of getting a meal. **IaaS** is renting a kitchen: you cook. **PaaS**
is a meal kit: ingredients are ready, you just assemble. **SaaS** is ordering food: you just eat.

**❓ The problem it solves.** Different teams want to manage different amounts. A team with
special OS needs wants control; a small team wants to just ship code; a business user just wants
working software.

**⚙️ How it works.**

| Model | You manage | Provider manages | AWS examples |
|---|---|---|---|
| **IaaS** | OS, runtime, app, data | hardware, network, virtualisation | **EC2**, EBS, VPC |
| **PaaS** | app code and data | OS, runtime, scaling, patching | **Elastic Beanstalk**, App Runner, RDS (managed DB) |
| **SaaS** | just use it (and your data/settings) | everything | Amazon Connect, Amazon QuickSight (and Gmail, Zoom outside AWS) |
| **Serverless / FaaS** | function code | servers, scaling, OS | **Lambda**, Fargate |

**Deployment models:** **public cloud** (AWS, shared infrastructure), **private cloud** (your own
data centre run cloud-style), **hybrid** (both, connected by VPN or Direct Connect, very common in
banks and large companies).

**💡 Example.** Hosting a Django app: on **EC2** (IaaS) you install Python, Nginx and patches
yourself; on **App Runner** (PaaS) you hand over a container image and it runs; using **Lambda**
you only write functions.

## 3. Regions

**🧑 In plain words.** A Region is a **city-sized area** where AWS has a cluster of data centres,
like a bank having separate head offices in Mumbai, Singapore and Frankfurt.

**❓ The problem it solves.** Users are far apart (latency), countries have data-residency laws, and
one geographic disaster must never take everything down.

**⚙️ How it works.**

- Each Region is **fully independent**: its own power, network and copies of the services. Data
  **doesn't leave a Region** unless you copy it out.
- Region codes: `ap-south-1` (Mumbai), `ap-south-2` (Hyderabad), `ap-southeast-1` (Singapore),
  `us-east-1` (N. Virginia), `eu-west-1` (Ireland)…
- Most services are **regional** (EC2, VPC, S3 buckets, RDS). A few are **global**: **IAM**,
  **Route 53**, **CloudFront**, **WAF for CloudFront**. Global services' console shows "Global".
- **How to choose a Region**, in order:
  1. **Compliance / data residency:** does the data have to stay in India?
  2. **Latency:** closest to most users.
  3. **Service availability:** new services reach some Regions first (often `us-east-1`).
  4. **Price:** costs differ a little by Region.

**💡 Example.** An Indian fintech must keep customer data in India (regulators require it), and
most users are in South India, so it picks `ap-south-1` (Mumbai) with a disaster-recovery copy in
`ap-south-2` (Hyderabad), keeping both inside India.

## 4. Availability Zones (AZs)

```{raw} html
:file: ../diagrams/s01-global.html
```

**🧑 In plain words.** Inside each city (Region), AWS has **several separate buildings far enough
apart** that a fire, flood or power cut in one doesn't affect the others, but close enough to talk
almost instantly.

**❓ The problem it solves.** Single data centres fail: power, cooling, network cables, floods. If
your app lives in one building, it goes down with it.

**⚙️ How it works.**

- An AZ is **one or more discrete data centres** with redundant power, networking and cooling.
- Every Region has **at least 3 AZs** (Mumbai has 3: `ap-south-1a`, `-1b`, `-1c`).
- AZs in a Region are connected with high-bandwidth, **low-latency** (single-digit millisecond)
  private fibre, so you can replicate data synchronously between them.
- Many services are **AZ-scoped**: an EC2 instance, an EBS volume and a subnet each live in exactly
  one AZ. Others are **Region-scoped and multi-AZ by design**: S3, DynamoDB, a load balancer.
- AZ names like `ap-south-1a` are **mapped differently per account**; the stable identifier is the
  **AZ ID** (e.g. `aps1-az1`).

**💡 Example.** A web app runs two EC2 instances, one in `ap-south-1a` and one in `ap-south-1b`,
behind a load balancer, and its database uses **RDS Multi-AZ** (a standby copy in another AZ). If
1a loses power, the load balancer sends everyone to 1b and the database fails over to its standby,
with users seeing at most a brief blip.

## 5. Edge locations

**🧑 In plain words.** Small **branch offices** in many more cities, close to users, that keep copies
of popular content so it doesn't travel from the main office every time.

**❓ The problem it solves.** Even fast networks have physics: a user in Chennai downloading images
from a server in Virginia waits ~250 ms per round trip. Copies nearby cut that to ~10–20 ms.

**⚙️ How it works.** There are hundreds of edge locations (points of presence) worldwide,
including several Indian cities. They run **CloudFront** (content delivery/caching), **Route 53**
(DNS answers) and **AWS WAF/Shield at the edge**; **Lambda@Edge** and **CloudFront Functions** run
code there. You don't launch servers in edge locations; services use them for you.

**💡 Example.** Course videos stored in S3 in Mumbai are served through **CloudFront**: a student in
Coimbatore gets them from a nearby edge cache, and the S3 bucket only serves the first request.

## 6. The shared responsibility model

```{raw} html
:file: ../diagrams/s01-shared.html
```

**🧑 In plain words.** A rented flat. The **owner** is responsible for the building: foundation,
lifts, outer walls, the main gate. **You** are responsible for locking your own door, who you give
keys to, and what you keep inside.

**❓ The problem it solves.** It makes clear **who must do what**, so nobody assumes "the cloud is
secure, so my data is safe" while leaving a bucket public.

**⚙️ How it works.**

- **AWS: security *of* the cloud:** physical data centres, hardware, the global network, the
  virtualisation layer (hypervisor), and the managed parts of services.
- **You: security *in* the cloud:** your data and its encryption choices, **IAM** (who has access),
  **OS patches on EC2**, **security groups and NACLs**, application code, backups.
- The line **moves with the service type**:

| Service | AWS manages | You manage |
|---|---|---|
| EC2 (IaaS) | hardware, hypervisor | **guest OS patches**, firewall rules, app, data, IAM |
| RDS (managed DB) | OS and DB engine patching, backups infrastructure | DB users, network access, encryption settings, data |
| Lambda / S3 (serverless) | servers, OS, runtime patching | code, IAM permissions, data, bucket policies |

**💡 Example.** A company's data leaks because an S3 bucket was made public. That's the
**customer's** responsibility (configuration), not AWS's, even though S3 itself is secure. AWS's
part was making sure nobody could walk into the data centre and take the disks.

## 7. IAM in one minute

**🧑 In plain words.** The building's **security office**: it issues ID cards (users), department
badges (groups), temporary visitor passes (roles), and the rule book saying which doors each badge
opens (policies).

**❓ The problem it solves.** Without IAM, everyone would share the root (owner) login, and one leak
or mistake could delete everything.

**⚙️ How it works.** IAM is **global** and free. Every API call is **authenticated** (who are you?)
and **authorised** (are you allowed?). The **root user** (the email that created the account) can do
everything; protect it with **MFA**, never create access keys for it, and use separate identities
for daily work. [Session 2](02-iam-deep-dive.md) goes deep.

**💡 Example.** A team lead creates a `developers` group with read-only access, adds three users to
it, and keeps the root login in a safe with MFA.

## 8. Console, CLI and your first resource

**🧑 In plain words.** The **console** is the shop's front counter (point and click); the **CLI** is
phoning in an order with exact instructions (repeatable, scriptable).

**❓ The problem it solves.** Clicking is great for learning; repeating 50 clicks every time is slow
and error-prone. The CLI and SDKs automate.

**⚙️ How it works.** The console, CLI (`aws ...`) and SDKs (boto3 for Python, etc.) all call the
same APIs and are all controlled by IAM. The CLI reads credentials from `aws configure` /
`aws configure sso`, environment variables, or an instance role.

**💡 Example: "Hello World" on AWS.**

```bash
aws sts get-caller-identity                                     # who am I?
aws s3 mb s3://hello-parottasalna-$RANDOM --region ap-south-1   # make a bucket (name must be globally unique)
echo "Hello AWS" > hello.txt
aws s3 cp hello.txt s3://hello-parottasalna-12345/              # use the name printed above
aws s3 ls s3://hello-parottasalna-12345/
```

**Output:**

```text
{
    "UserId": "AIDA...",
    "Account": "111122223333",
    "Arn": "arn:aws:iam::111122223333:user/admin-jafer"
}
make_bucket: hello-parottasalna-12345
upload: ./hello.txt to s3://hello-parottasalna-12345/hello.txt
2026-10-10 20:15:02         10 hello.txt
```

**Clean up:** `aws s3 rb s3://hello-parottasalna-12345 --force`.

## Common mistakes

- **Working as the root user** day to day. Create an admin user or use IAM Identity Center ([Setup](../setup.md)).
- **"My instance disappeared!"** It's almost always the **Region selector** at the top right.
- **Assuming the Free Tier covers everything.** It doesn't; set a **budget alert**.
- **Running production in one AZ.** One data-centre problem takes the whole app down.
- **Thinking AWS secures your configuration.** Public buckets and open security groups are *your* side.

## Hands-on exercises

Do these in your own account. Everything here is free or a few rupees; the ⚠️ marks anything that
costs money if left running.

**Exercise 1 · Secure the account.** Enable MFA on the root user, then create an everyday admin
identity (IAM Identity Center user or an IAM user with `AdministratorAccess` and MFA).

<details class="solution"><summary>What success looks like</summary>

IAM → Dashboard shows **"Root user has MFA"** ✅. You can sign out of root and sign in with the new
admin identity, and `aws sts get-caller-identity` no longer shows `:root`.

</details>

**Exercise 2 · Budget alert.** Create a **zero-spend budget** (or a $5 monthly budget) that emails you.

<details class="solution"><summary>Steps</summary>

Billing and Cost Management → Budgets → Create budget → Use a template → **Zero spend budget** →
your email → Create. It appears in the Budgets list with status OK.

</details>

**Exercise 3 · Explore Regions.** From the CLI, list all Regions enabled for your account and count them.

<details class="solution"><summary>Solution</summary>

```bash
aws ec2 describe-regions --query 'Regions[].RegionName' --output table
aws ec2 describe-regions --query 'length(Regions)'
```

</details>

**Exercise 4 · AZ names vs AZ IDs.** List the AZs in `ap-south-1` with their **zone IDs**. Compare
with a friend's account: are `ap-south-1a` and the zone ID the same for both of you?

<details class="solution"><summary>Solution</summary>

```bash
aws ec2 describe-availability-zones --region ap-south-1 \
    --query 'AvailabilityZones[].[ZoneName,ZoneId]' --output table
```

The names (`ap-south-1a`) may map to different physical AZs in different accounts; the **zone IDs**
(`aps1-az1`…) are the same everywhere. Use zone IDs when coordinating across accounts.

</details>

**Exercise 5 · Global vs regional services.** Open IAM, Route 53, EC2 and S3 in the console. Which
show "Global" in the Region selector? Which are tied to a Region?

<details class="solution"><summary>Answer</summary>

**Global:** IAM, Route 53 (and CloudFront). **Regional:** EC2. **S3** shows "Global" in the console
list, but every **bucket** lives in one Region you choose.

</details>

**Exercise 6 · Latency to Regions.** Measure your round-trip time to three Regions' endpoints and pick the best for you.

<details class="solution"><summary>Solution</summary>

```bash
for r in ap-south-1 ap-southeast-1 us-east-1; do
  printf "%s " $r; curl -s -o /dev/null -w "%{time_connect}s\n" https://ec2.$r.amazonaws.com
done
```

From India, `ap-south-1` is typically ~10–40 ms and `us-east-1` ~200+ ms.

</details>

**Exercise 7 · Hello World with the CLI.** Create a bucket, upload a file, list it, download it
again as `copy.txt`, then delete the bucket.

<details class="solution"><summary>Solution</summary>

```bash
B=hello-$RANDOM-$RANDOM
aws s3 mb s3://$B --region ap-south-1
echo "Hello AWS" > hello.txt && aws s3 cp hello.txt s3://$B/
aws s3 ls s3://$B/
aws s3 cp s3://$B/hello.txt copy.txt && cat copy.txt
aws s3 rb s3://$B --force
```

</details>

**Exercise 8 · Shared responsibility sorting.** For each, write AWS or YOU: (a) patching the Linux
kernel on EC2, (b) patching the hypervisor, (c) encrypting an RDS database, (d) replacing a failed
power supply, (e) rotating an IAM user's access keys, (f) patching the OS under a Lambda function,
(g) closing port 22 to the internet.

<details class="solution"><summary>Answer</summary>

(a) YOU, (b) AWS, (c) YOU (you choose encryption; AWS provides it), (d) AWS, (e) YOU, (f) AWS, (g) YOU.

</details>

**Exercise 9 · Find the cost of a mistake.** Using the [AWS Pricing Calculator](https://calculator.aws/),
estimate the monthly cost of one `t3.micro` EC2 instance running 24×7 in Mumbai, and of the same
instance left running by accident for a year.

<details class="solution"><summary>What to notice</summary>

A small instance is cheap per hour but adds up 24×7 (730 hours/month). The habit to build: check
**Billing → Bills** and **Cost Explorer** weekly, and stop/terminate lab resources.

</details>

**Exercise 10 · Free Tier tracking.** Turn on **Free Tier usage alerts** and find the page that shows
how much of each free allowance you've used this month.

<details class="solution"><summary>Steps</summary>

Billing → Billing preferences → **Receive AWS Free Tier alerts** ✅. Usage: Billing → **Free Tier**
shows each service's usage vs the monthly limit.

</details>

**Exercise 11 · Explore with the CloudShell.** Open **CloudShell** (the terminal icon in the console)
and run `aws sts get-caller-identity` and `aws s3 ls`. Why didn't you need `aws configure`?

<details class="solution"><summary>Answer</summary>

CloudShell runs in your console session and automatically uses **your signed-in identity's**
credentials. It's handy when you can't install the CLI locally.

</details>

**Exercise 12 · Design question.** A hospital in Chennai wants an appointment app that keeps patient
data in India and survives a data-centre failure. Sketch: which Region, how many AZs, and why.

<details class="solution"><summary>Model answer</summary>

`ap-south-1` (Mumbai; or Hyderabad `ap-south-2`) for data residency and latency. Application
servers in **at least two AZs** behind a load balancer, and a **Multi-AZ** database, so losing one
data centre doesn't stop the app. Optionally a backup copy in the other Indian Region for disaster
recovery.

</details>

## Class files

- {download}`Whiteboard: Introduction to AWS <../code/whiteboards/01-introduction-to-aws.excalidraw>`
  (open at [excalidraw.com](https://excalidraw.com))
