# Session 11 · VPC Endpoints & PrivateLink

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/pJYjR3xzEBs"
  title="Session 11: VPC endpoints" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 **Session 11** of the [AWS Solutions Architect playlist](https://www.youtube.com/playlist?list=PLYmjGMwZ9N88) (Tamil) · [watch on YouTube](https://www.youtube.com/watch?v=pJYjR3xzEBs)

## The big idea

AWS services like S3, SQS or Secrets Manager have **public** endpoints. Without help, a private
instance reaches them through a NAT Gateway and the internet path, which costs NAT data charges and
leaves the AWS network edge. A **VPC endpoint** gives your VPC a **private path** straight to the
service, inside the AWS network: more secure, often cheaper, and it works with **no internet access at all**.

**Everyday example:** a staff-only internal door from your office straight into the bank branch
in the same building, instead of walking out onto the road and in through the public entrance.

```{raw} html
:file: ../diagrams/s11-endpoints.html
```

## 1. Two kinds of endpoints

| | **Gateway endpoint** | **Interface endpoint** (PrivateLink) |
|---|---|---|
| Services | **only S3 and DynamoDB** | most AWS services (SQS, SNS, SSM, Secrets Manager, ECR, KMS, CloudWatch…), your own and partners' services |
| How it works | a **route** in your route tables (prefix list `pl-…` → `vpce-…`) | an **ENI with a private IP** in your subnets |
| DNS | normal service name | private DNS makes the normal name resolve to the private IP |
| Security | endpoint policy | endpoint policy **+ security groups** |
| Reach from on-premises / peered VPC | ❌ | ✅ |
| Cost | **free** | per hour per AZ + per GB |

:::{note}
S3 supports **both** kinds. Use the free gateway endpoint inside the VPC; use an S3 interface
endpoint when on-premises networks (over VPN/Direct Connect) must reach S3 privately.
:::

## 2. Endpoint policies and bucket policies

An **endpoint policy** limits what can pass through the endpoint, for example only your company's buckets:

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

:::{warning}
A bucket policy like this also blocks **you** in the console (you're not coming through the
endpoint). Add an exception for an admin role before applying it.
:::

## 3. Hands-on: S3 from a subnet with no internet

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

## 4. PrivateLink beyond AWS services

With **PrivateLink** you can publish **your own service** (behind a Network Load Balancer) as an
*endpoint service*. Other VPCs or customer accounts create an interface endpoint to it. They reach
only that one service, not your whole network, and **overlapping CIDRs don't matter**. SaaS
vendors use this to offer private connectivity.

## Common mistakes

- **Gateway endpoint created but not associated with the right route table.**
- **Interface endpoint without private DNS**, so the app still resolves the public name and goes via NAT.
- **Interface endpoint security group** not allowing 443 from your instances.
- **Region mismatch:** gateway endpoints only reach the service in the **same Region**.

## Try it yourself

1. Your private EC2 instances pull Docker images from ECR and read secrets from Secrets Manager,
   with no NAT Gateway. Which endpoints do you need?

   <details class="solution">
   <summary>Answer</summary>

   Interface endpoints for **ECR API** (`ecr.api`), **ECR Docker** (`ecr.dkr`) and **Secrets
   Manager**, plus a **gateway endpoint for S3**, because ECR stores image layers in S3.

   </details>

2. Why might a team replace NAT Gateway traffic to S3 with a gateway endpoint, even if security weren't a concern?

   <details class="solution">
   <summary>Answer</summary>

   Cost: gateway endpoints are free, while every GB through a NAT Gateway is charged.

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
