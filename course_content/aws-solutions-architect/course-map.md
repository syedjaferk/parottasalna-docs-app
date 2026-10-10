# Course map

The bootcamp follows **12 modules** for the AWS Solutions Architect Associate exam (**SAA-C03**).
The recorded sessions so far cover these topics; new chapters are added as each session is
published on the [YouTube playlist](https://www.youtube.com/playlist?list=PLYmjGMwZ9N88).

## Sessions so far

| Session | Chapter | Module |
|---|---|---|
| 1 | [Introduction to AWS: cloud, global infrastructure, shared responsibility](sessions/01-introduction-to-aws.md) | 1 · Cloud foundations & IAM |
| 2 | [IAM deep dive: users, groups, roles and policies](sessions/02-iam-deep-dive.md) | 1 · Cloud foundations & IAM |
| 3 | *Recording not in the playlist yet* | |
| 4 | [Load balancing explained with HAProxy](sessions/04-load-balancing-haproxy.md) | 3 · Compute & scaling |
| 5 | [Elastic Load Balancer: ALB, NLB, GWLB](sessions/05-elastic-load-balancer.md) | 3 · Compute & scaling |
| 6 | [EC2 networking, storage (EBS) and access](sessions/06-ec2-networking-storage.md) | 3 · Compute & 2 · Storage |
| 7 | [Public and private subnets with EC2 and Docker](sessions/07-public-private-subnets.md) | 4 · Networking |
| 8 | [NAT Gateway](sessions/08-nat-gateway.md) | 4 · Networking |
| 9 | [VPC peering](sessions/09-vpc-peering.md) | 4 · Networking |
| 10 | [Transit Gateway](sessions/10-transit-gateway.md) | 4 · Networking |
| 11 | [VPC endpoints and PrivateLink](sessions/11-vpc-endpoints.md) | 4 · Networking |
| 12 | [AWS WAF](sessions/12-aws-waf.md) | 10 · Security |
| 13 | [VPC Flow Logs and how DNS works](sessions/13-vpc-flow-logs-dns.md) | 4 · Networking & DNS |
| 14 | [Amazon Route 53](sessions/14-route-53.md) | 4 · Networking & DNS |
| 15 | [Amazon S3 (part 1)](sessions/15-amazon-s3.md) | 2 · Storage |
| 16 | [Amazon API Gateway](sessions/16-api-gateway.md) | 7 · Serverless & integration |

## The 12 modules

| # | Module | Main topics |
|---|---|---|
| 1 | Cloud foundations & IAM | Regions, AZs, edge; shared responsibility; IAM; Organizations & OUs; CLI; billing |
| 2 | Storage | S3 (versioning, replication, lifecycle, security, Object Lock); EBS vs EFS vs instance store; FSx; Storage Gateway; DataSync; Snowball |
| 3 | Compute, scaling & containers | EC2 types and lifecycle; Spot; Auto Scaling; ALB/NLB; ECS, Fargate, ECR, EKS; App Runner |
| 4 | Networking & DNS | VPC, subnets, route tables, IGW, NAT; security groups vs NACLs; peering, endpoints, PrivateLink; VPN & Direct Connect; Route 53 |
| 5 | Databases & caching | RDS Multi-AZ & read replicas; Aurora; DynamoDB (Streams, Global Tables, DAX); ElastiCache; DocumentDB, Neptune, Timestream |
| 6 | Analytics & big data | Athena; Redshift; OpenSearch; EMR; Glue & Lake Formation; Kinesis; MSK |
| 7 | Serverless & integration | Lambda; API Gateway; SQS, SNS, Amazon MQ; EventBridge; Step Functions; CloudFront Functions & Lambda@Edge |
| 8 | Edge & AI/ML | CloudFront; Global Accelerator; Rekognition, Textract, Comprehend, Lex, Polly; SageMaker |
| 9 | Disaster recovery | backup & restore, pilot light, warm standby, multi-site; RPO and RTO |
| 10 | Monitoring & security | CloudWatch; CloudTrail; AWS Config; KMS; Parameter Store & Secrets Manager; GuardDuty, Inspector, Macie; WAF |
| 11 | Migration & DevOps | DMS & SCT; Application Migration Service; AWS Backup; CloudFormation & Systems Manager; Batch |
| 12 | Best practices & exam | Well-Architected (6 pillars); caching & HA patterns; mock exams |

:::{note}
**About the exam:** SAA-C03 has 65 questions (multiple choice and multiple response) in 130
minutes, scored from 100 to 1000; **720** is the pass mark. Most questions are short scenarios:
"a company needs X, with the least cost / operational overhead / highest availability: which
solution?" The **Scenarios** quiz in every chapter practises exactly that style.
:::
