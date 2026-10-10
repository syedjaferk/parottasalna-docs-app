# Session 11 · VPC Endpoints & PrivateLink

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/pJYjR3xzEBs"
  title="Session 11: VPC endpoints" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 **Session 11** of the [AWS Solutions Architect playlist](https://www.youtube.com/playlist?list=PLYmjGMwZ9N88) (Tamil) · [watch on YouTube](https://www.youtube.com/watch?v=pJYjR3xzEBs)

## What you'll learn

- Why reaching AWS services from private subnets is a problem (cost and security)
- **Gateway endpoints** (S3, DynamoDB): how a route-table entry does the job
- **Interface endpoints** and **AWS PrivateLink**: private IPs and private DNS
- **Endpoint policies**, and bucket policies that insist on an endpoint
- Publishing **your own service** with PrivateLink
- The class lab, built as code with **Pulumi**

```{raw} html
:file: ../diagrams/s11-endpoints.html
```

## 1. The problem: AWS services live "outside" your VPC

**🧑 In plain words.** Your office is inside a gated complex. The bank branch is in the same city,
but its entrance faces the public road: to reach it, staff must walk out of the gate and in through
the public door.

**❓ The problem it solves.** Services like S3, SQS, Secrets Manager and ECR are reached through
**public endpoints** (`s3.ap-south-1.amazonaws.com`). A private subnet can only reach them via a
**NAT Gateway**, which means:

- **Cost:** every GB through the NAT is charged (big for data pipelines and backups).
- **Exposure:** the subnet needs a path to the internet at all, which strict environments forbid.
- **Control:** it's harder to say "only *our* buckets, only from *this* VPC".

**⚙️ How it works.** A **VPC endpoint** creates a **private path** from the VPC to the service that
never leaves the AWS network and needs **no IGW, NAT, VPN or public IP**. There are two kinds:
gateway and interface.

**💡 Example.** A bank's analytics servers have **no internet route at all**, yet read and write S3
all day through a gateway endpoint.

## 2. Gateway endpoints

**🧑 In plain words.** A **staff-only internal door** from your complex straight into the bank, marked
on your blocks' signboards.

**❓ The problem it solves.** Free, private, high-throughput access to the two most heavily used data services.

**⚙️ How it works.**

- Only for **Amazon S3** and **DynamoDB**.
- You pick **route tables**; AWS adds a route whose destination is the service's **prefix list**
  (e.g. `pl-78a54011` = S3's IP ranges in the Region) and whose target is the endpoint (`vpce-…`).
- Traffic matching the prefix list goes privately to the service; DNS names don't change.
- **Free.** Same **Region** only. Can't be reached from on-premises, peered VPCs or over a TGW
  (it's a routing trick inside your VPC).

**💡 Example.** After creating the S3 gateway endpoint, the private route table shows
`pl-78a54011 (com.amazonaws.ap-south-1.s3) → vpce-0a1b…`, and `aws s3 ls` works with no NAT.

## 3. Interface endpoints (AWS PrivateLink)

**🧑 In plain words.** The bank opens a **small counter inside your office building**, with its own
desk number (private IP). Staff go to that counter; it connects privately to the bank's main branch.

**❓ The problem it solves.** Private access to the **hundreds of other services** (SQS, SNS, SSM,
Secrets Manager, KMS, ECR, CloudWatch, STS…), and access from on-premises or other VPCs.

**⚙️ How it works.**

- The endpoint places an **ENI with a private IP** in each subnet (AZ) you choose.
- **Private DNS** (on by default for AWS services): the normal name, e.g.
  `secretsmanager.ap-south-1.amazonaws.com`, now resolves to the **private IPs** inside your VPC,
  so applications need no changes.
- Protected by **security groups** (allow 443 from your app servers) and endpoint policies.
- Reachable from **peered VPCs, Transit Gateway and on-premises** (VPN/Direct Connect).
- **Cost:** per endpoint **per AZ per hour**, plus per GB.

| | Gateway endpoint | Interface endpoint |
|---|---|---|
| Services | S3, DynamoDB | most AWS services, your own and partners' services |
| Mechanism | route-table entry | ENI + private IP + private DNS |
| Security | endpoint policy | endpoint policy **+ security groups** |
| From on-prem / other VPCs | ❌ | ✅ |
| Cost | **free** | hourly per AZ + per GB |

S3 supports **both**: use the free gateway endpoint inside the VPC; use an S3 interface endpoint
when on-premises networks must reach S3 privately.

**💡 Example.** Private ECS tasks with no NAT pull images from ECR using interface endpoints
`ecr.api` and `ecr.dkr`, plus an **S3 gateway endpoint** (ECR stores image layers in S3), and read
secrets via a Secrets Manager endpoint.

## 4. Endpoint policies and bucket policies

**🧑 In plain words.** The internal door has its own **guard with a list**: "staff may only go to
*our* company's lockers". And the lockers can say "only open for people coming through *our* internal door".

**❓ The problem it solves.** Data exfiltration (someone copying data to *their own* bucket from your
network) and making sure sensitive data is only reachable from inside your network.

**⚙️ How it works.** An **endpoint policy** (resource-based, default: allow all) limits what can pass
through the endpoint, for example only your company's buckets:

```json
{
  "Statement": [{
    "Effect": "Allow",
    "Principal": "*",
    "Action": ["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
    "Resource": ["arn:aws:s3:::company-data", "arn:aws:s3:::company-data/*"]
  }]
}
```

And the bucket can insist on the endpoint, so the data is unreachable from anywhere else:

```json
{
  "Statement": [{
    "Effect": "Deny",
    "Principal": "*",
    "Action": "s3:*",
    "Resource": ["arn:aws:s3:::company-data", "arn:aws:s3:::company-data/*"],
    "Condition": { "StringNotEquals": { "aws:SourceVpce": "vpce-0a1b2c3d" } }
  }]
}
```

(`aws:SourceVpc` works the same way with a VPC ID.) An endpoint policy **never grants** permissions
on its own; the caller still needs IAM permissions.

:::{warning}
A bucket policy like this also blocks **you** in the console (you're not coming through the
endpoint). Add an exception for an admin role before applying it.
:::

**💡 Example.** An insider on a private server tries `aws s3 cp secrets.csv s3://my-personal-bucket/`:
the endpoint policy only allows `company-data`, so it's denied.

## 5. PrivateLink for your own services

**🧑 In plain words.** You're the bank now: you open a **counter inside each customer's building**
without connecting the buildings' corridors together.

**❓ The problem it solves.** Exposing **one service** (an API, a SaaS product) to other VPCs or
customer accounts privately, without peering whole networks, and even when their **CIDRs overlap** with yours.

**⚙️ How it works.** Put your service behind a **Network Load Balancer** (or GWLB), create an
**endpoint service**, and allow specific accounts (with optional manual acceptance). Consumers create
an **interface endpoint** to it in their VPC. Traffic is one-way: consumers can reach your service;
you can't reach into their VPC. This is how many SaaS vendors offer "private connectivity".

**💡 Example.** A payments company exposes its API to 200 merchant VPCs through PrivateLink. Many
merchants use `10.0.0.0/16` like the payments VPC; with peering that would be impossible, with PrivateLink it doesn't matter.

## 6. Hands-on: S3 from a subnet with no internet

1. Use the private instance from [Session 8](08-nat-gateway.md) and **remove the NAT route**, so it
   has no internet at all. Attach an instance role that can read your bucket.
2. `aws s3 ls s3://company-data` now hangs and times out.
3. *VPC → Endpoints → Create*: service `com.amazonaws.ap-south-1.s3`, type **Gateway**, select the
   **private route table**.
4. Try again:

```bash
aws s3 ls s3://company-data --region ap-south-1
```

**Output:**

```text
2026-10-10 21:02:11       2048 report.csv
```

The private route table now shows a new route: `pl-78a54011 (com.amazonaws.ap-south-1.s3) → vpce-…`.

### The class lab as code (Pulumi)

The class built this lab with **Pulumi** (infrastructure as code in Python): a VPC with a public
**bastion** and a private EC2 instance, an S3 bucket with `hello.txt`, and an S3 **gateway endpoint**
on the private route table.

```bash
ssh-keygen -t ed25519 -f server-pem -N ""     # the program uploads server-pem.pub as the key pair
pip install -r requirements.txt
pulumi stack init endpoint-demo
pulumi config set aws:region ap-south-1
pulumi up                                     # creates everything and prints the next steps

# then, as the outputs say:
ssh -A -i server-pem ubuntu@<bastion_public_ip>   # 1. into the bastion (agent forwarding)
ssh ubuntu@<private_ec2_private_ip>                # 2. from the bastion into the private EC2
aws s3 ls s3://<bucket>/                           # 3. works through the gateway endpoint
pulumi destroy                                     # clean up
```

:::{note}
The lab opens SSH to the bastion from `0.0.0.0/0` for simplicity. For anything real, allow only
your own IP, or use Session Manager instead of SSH.
:::

## Common mistakes

- **Gateway endpoint created but not associated with the right route table.**
- **Interface endpoint without private DNS**, so the app still resolves the public name and goes via NAT.
- **Interface endpoint security group** not allowing 443 from your instances.
- **Region mismatch:** gateway endpoints only reach the service in the **same Region**.

## Hands-on exercises

Gateway endpoints are **free**. ⚠️ Interface endpoints are charged per AZ per hour; EC2 instances
cost money. Delete them at the end (or `pulumi destroy` for the class lab).

**Exercise 1 · No internet, no S3.** On a private instance with **no NAT route** and a read-only S3
instance role, run `aws s3 ls --region ap-south-1`. What happens?

<details class="solution"><summary>Expected</summary>

It hangs and times out (`Connect timeout on endpoint URL`): there's no path to S3's public endpoint.

</details>

**Exercise 2 · Add a gateway endpoint.** Create an S3 gateway endpoint for the private route table and
retry Exercise 1. Then look at the route table.

<details class="solution"><summary>CLI</summary>

```bash
aws ec2 create-vpc-endpoint --vpc-id $VPC --vpc-endpoint-type Gateway \
    --service-name com.amazonaws.ap-south-1.s3 --route-table-ids $PRIV_RT
aws ec2 describe-route-tables --route-table-ids $PRIV_RT --query 'RouteTables[].Routes'
```

`aws s3 ls` now works; a route with `DestinationPrefixListId: pl-…` → `GatewayId: vpce-…` appears.

</details>

**Exercise 3 · What's in the prefix list?** Look up the S3 prefix list's CIDR ranges.

<details class="solution"><summary>CLI</summary>

```bash
aws ec2 describe-prefix-lists --filters Name=prefix-list-name,Values=com.amazonaws.ap-south-1.s3
aws ec2 get-managed-prefix-list-entries --prefix-list-id pl-78a54011
```

These are S3's public IP ranges in the Region; traffic to them now uses the endpoint.

</details>

**Exercise 4 · Same Region only.** From the private instance, list a bucket in **another Region**
(e.g. `us-east-1`). Does the gateway endpoint help?

<details class="solution"><summary>Answer</summary>

No, it times out: gateway endpoints only cover the **same Region's** S3. Cross-Region access needs
a NAT/internet path or an interface endpoint design.

</details>

**Exercise 5 · Restrict with an endpoint policy.** Change the endpoint policy so only your lab bucket
is allowed. Test listing the lab bucket and another bucket.

<details class="solution"><summary>Check</summary>

Lab bucket works; any other bucket returns **AccessDenied** even though the instance role allows `s3:*` read.

</details>

**Exercise 6 · Bucket accepts only the endpoint.** Add the `aws:SourceVpce` deny statement (with an
exception for your admin role) to the lab bucket. Try from the private instance and from your laptop.

<details class="solution"><summary>Check</summary>

Private instance (through the endpoint): works. Laptop: **AccessDenied** (unless you're the excepted
admin role). The data is only reachable from inside the VPC.

</details>

**Exercise 7 · Interface endpoint for Secrets Manager.** Store a test secret, create an **interface**
endpoint for `secretsmanager` in the private subnet (SG: 443 from the instance), and read the secret
from the private instance with no NAT.

<details class="solution"><summary>Check</summary>

`aws secretsmanager get-secret-value --secret-id lab/test --region ap-south-1` works.
`dig +short secretsmanager.ap-south-1.amazonaws.com` on the instance returns a **10.x** private IP.

</details>

**Exercise 8 · Private DNS off.** Disable *private DNS* on that endpoint and retry. Then use the
endpoint-specific DNS name with `--endpoint-url`.

<details class="solution"><summary>Answer</summary>

With private DNS off, the normal name resolves to public IPs again → timeout. It works with
`--endpoint-url https://vpce-0abc...secretsmanager.ap-south-1.vpce.amazonaws.com`. Turn private DNS back on.

</details>

**Exercise 9 · Security group on the endpoint.** Remove the 443 rule from the interface endpoint's
security group. What error do you get?

<details class="solution"><summary>Answer</summary>

The call **times out** (connection refused at the network level), not AccessDenied: interface
endpoints are network interfaces, so security groups apply.

</details>

**Exercise 10 · The class lab with Pulumi.** Deploy the class Pulumi program (bastion + private EC2 +
bucket + gateway endpoint), follow its output steps to read `hello.txt` from the private instance, then destroy it.

<details class="solution"><summary>Commands</summary>

```bash
ssh-keygen -t ed25519 -f server-pem -N ""
pip install -r requirements.txt && pulumi stack init endpoint-demo && pulumi config set aws:region ap-south-1
pulumi up
ssh -A -i server-pem ubuntu@$(pulumi stack output bastion_public_ip)
ssh ubuntu@<private_ec2_private_ip>
aws s3 cp s3://<bucket>/hello.txt . && cat hello.txt
pulumi destroy
```

</details>

**Exercise 11 · Cost check.** Compare the monthly cost of pulling 2 TB/month from S3 through (a) a
NAT Gateway, (b) a gateway endpoint, (c) an interface endpoint in 2 AZs.

<details class="solution"><summary>What to conclude</summary>

(b) is free; (a) pays NAT per-GB processing on 2 TB; (c) pays hourly per AZ plus per GB. For
in-VPC S3 access, the gateway endpoint is the clear winner.

</details>

**Exercise 12 · ECR without NAT (design).** List every endpoint a private ECS/EC2 workload needs to
pull from ECR, write logs to CloudWatch, read SSM parameters and use Session Manager, all with no NAT.

<details class="solution"><summary>Answer</summary>

Interface: `ecr.api`, `ecr.dkr`, `logs`, `ssm`, `ssmmessages`, `ec2messages` (for Session Manager),
and `kms`/`secretsmanager` if used. Gateway: **`s3`** (ECR layers).

</details>

**Exercise 13 · Clean up.** Delete interface endpoints (hourly charge), the gateway endpoint, test
secrets and instances.

<details class="solution"><summary>Check</summary>

VPC → Endpoints: none left. Secrets Manager → secret scheduled for deletion.

</details>

## Class files

<details class="source">
<summary>__main__.py (Pulumi: VPC, bastion, private EC2, S3 bucket, gateway endpoint)</summary>

```{literalinclude} ../code/11-vpc-endpoint-pulumi/__main__.py
:language: python
```

</details>

- Downloads: {download}`__main__.py <../code/11-vpc-endpoint-pulumi/__main__.py>` ·
  {download}`Pulumi.yaml <../code/11-vpc-endpoint-pulumi/Pulumi.yaml>` ·
  {download}`requirements.txt <../code/11-vpc-endpoint-pulumi/requirements.txt>`
