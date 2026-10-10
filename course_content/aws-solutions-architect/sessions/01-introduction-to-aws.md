# Session 1 · Introduction to AWS: Cloud, Global Infrastructure & IAM

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/5bvkQEp_Tgg"
  title="Session 1: Introduction to AWS" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 **Session 1** of the [AWS Solutions Architect playlist](https://www.youtube.com/playlist?list=PLYmjGMwZ9N88) (Tamil) · [watch on YouTube](https://www.youtube.com/watch?v=5bvkQEp_Tgg)

## The big idea

**Cloud computing** means renting computers, storage, databases and networks over the internet,
paying only for what you use, instead of buying and running your own hardware. **AWS (Amazon Web
Services)** is the largest cloud provider, with 200+ services.

**Everyday example:** electricity. You don't build a power plant to switch on a fan; you plug in
and pay for the units you use. The cloud does the same for computing: plug in, use, pay per
hour or per GB, and switch off when done.

## 1. Why the cloud?

| Before the cloud (on-premises) | With the cloud |
|---|---|
| Buy servers weeks or months ahead | Launch a server in about a minute |
| Guess capacity: too much is wasted, too little crashes | Scale up and down with demand |
| Big up-front cost (capex) | Pay as you go (opex) |
| You run power, cooling, hardware repairs | AWS runs the data centres |
| Hard to reach users in other countries | Deploy in Regions around the world |

Three ways of using the cloud:

- **IaaS** (Infrastructure as a Service): you rent virtual machines and networks and manage the OS.
  *Example: EC2.*
- **PaaS** (Platform as a Service): you give your code; the platform runs it. *Example: Elastic Beanstalk, App Runner.*
- **SaaS** (Software as a Service): a finished product you just use. *Example: Gmail.*

## 2. AWS global infrastructure

```{raw} html
:file: ../diagrams/s01-global.html
```

| Term | What it is | Example |
|---|---|---|
| **Region** | A geographic area with its own complete set of AWS services, isolated from other Regions | `ap-south-1` Mumbai, `ap-south-2` Hyderabad, `us-east-1` N. Virginia |
| **Availability Zone (AZ)** | One or more data centres with separate power, cooling and network, a few km apart, connected by fast private links. Each Region has at least 3. | `ap-south-1a`, `ap-south-1b`, `ap-south-1c` |
| **Edge location** | A smaller site close to users, used by CloudFront (caching) and Route 53 (DNS) | many cities across India and the world |

**How to choose a Region:**

1. **Compliance:** must the data stay in a country? (for example, Indian data in an Indian Region)
2. **Latency:** close to your users.
3. **Service availability:** new services reach some Regions first.
4. **Price:** prices differ a little between Regions.

:::{important}
**High availability in one sentence:** run your app in **at least two AZs**. If one data centre
has a power failure, the other AZ keeps serving. You'll see this pattern in almost every
architecture in this course.
:::

## 3. The shared responsibility model

```{raw} html
:file: ../diagrams/s01-shared.html
```

- **AWS is responsible for security *of* the cloud:** buildings, hardware, the global network, the
  virtualisation layer.
- **You are responsible for security *in* the cloud:** your data, who can log in (IAM), patching
  the OS on your EC2 instances, firewall rules (security groups), and encryption settings.

The line moves with the service: on **EC2** you patch the OS; on **Lambda** or **S3**, AWS
manages the OS and you only manage your code, data and permissions.

## 4. IAM in one minute

**IAM (Identity and Access Management)** decides *who* can do *what* in your account. It is
global: not tied to a Region.

| Piece | Meaning |
|---|---|
| **Root user** | The email that created the account. Can do everything. Lock it with MFA and don't use it daily. |
| **User** | A person or app with long-term credentials |
| **Group** | A set of users who share permissions (e.g. `developers`) |
| **Role** | A set of permissions that someone or something *assumes* temporarily (e.g. an EC2 instance) |
| **Policy** | A JSON document listing allowed or denied actions |

[Session 2](02-iam-deep-dive.md) goes deep into each.

## 5. Your first resource: "Hello World" on AWS

The quickest real resource is an S3 bucket with a file in it:

```bash
aws s3 mb s3://hello-parottasalna-$RANDOM --region ap-south-1   # make a bucket (name must be globally unique)
echo "Hello AWS" > hello.txt
aws s3 cp hello.txt s3://hello-parottasalna-12345/              # use the name printed above
aws s3 ls s3://hello-parottasalna-12345/
```

**Output:**

```text
make_bucket: hello-parottasalna-12345
upload: ./hello.txt to s3://hello-parottasalna-12345/hello.txt
2026-10-10 20:15:02         10 hello.txt
```

**Clean up:** `aws s3 rb s3://hello-parottasalna-12345 --force` (removes the files and the bucket).

## Common mistakes

- **Working as the root user.** Create an admin user or use IAM Identity Center ([Setup](../setup.md)).
- **"My instance disappeared!"** It's almost always the Region selector at the top right.
- **Assuming the Free Tier covers everything.** It doesn't; set a budget alert.
- **Running production in one AZ.** One data-centre problem takes the whole app down.

## Try it yourself

1. Find three Regions near India in the Region menu and note their codes.
2. For each item, say who is responsible, AWS or you: (a) replacing a failed disk in the data
   centre, (b) patching Ubuntu on your EC2 instance, (c) making an S3 bucket private,
   (d) physical security guards.

   <details class="solution">
   <summary>Answer</summary>

   (a) AWS, (b) you, (c) you, (d) AWS.

   </details>

3. Why does an architect place servers in two Availability Zones instead of two servers in one AZ?

   <details class="solution">
   <summary>Answer</summary>

   AZs fail independently (separate power, cooling and network). Two servers in the same AZ can
   both go down with that AZ; servers in two AZs survive the loss of one.

   </details>

## Class files

- {download}`Whiteboard: Introduction to AWS <../code/whiteboards/01-introduction-to-aws.excalidraw>`
  (open at [excalidraw.com](https://excalidraw.com))
