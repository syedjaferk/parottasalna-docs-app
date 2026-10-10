import pulumi
import pulumi_aws as aws


# Config

region   = "ap-south-1"
ami_id   = "ami-01a00762f46d584a1"   # Amazon Linux 2023 — Mumbai


# Key Pair  (uses existing server-pem key)

with open("server-pem.pub") as f:
    public_key_data = f.read().strip()

key_pair = aws.ec2.KeyPair(
    "server-pem-keypair",
    key_name   = "server-pem",
    public_key = public_key_data,
    tags       = {"Name": "server-pem"},
)


# VPC

vpc = aws.ec2.Vpc(
    "main-vpc",
    cidr_block           = "10.0.0.0/16",
    enable_dns_hostnames = True,
    enable_dns_support   = True,
    tags                 = {"Name": "vpc-endpoint-demo-vpc"},
)


# Subnets

public_subnet = aws.ec2.Subnet(
    "public-subnet",
    vpc_id                  = vpc.id,
    cidr_block              = "10.0.1.0/24",
    availability_zone       = f"{region}a",
    map_public_ip_on_launch = True,
    tags                    = {"Name": "vpc-endpoint-demo-public-subnet"},
)

private_subnet = aws.ec2.Subnet(
    "private-subnet",
    vpc_id            = vpc.id,
    cidr_block        = "10.0.2.0/24",
    availability_zone = f"{region}b",
    tags              = {"Name": "vpc-endpoint-demo-private-subnet"},
)


# Internet Gateway  (for public subnet only)

igw = aws.ec2.InternetGateway(
    "igw",
    vpc_id = vpc.id,
    tags   = {"Name": "vpc-endpoint-demo-igw"},
)


# Route Tables

# Public — routes internet traffic via IGW
public_rt = aws.ec2.RouteTable(
    "public-rt",
    vpc_id = vpc.id,
    routes = [
        aws.ec2.RouteTableRouteArgs(
            cidr_block = "0.0.0.0/0",
            gateway_id = igw.id,
        )
    ],
    tags = {"Name": "vpc-endpoint-demo-public-rt"},
)

aws.ec2.RouteTableAssociation(
    "public-rt-assoc",
    subnet_id      = public_subnet.id,
    route_table_id = public_rt.id,
)

# Private — NO internet route (no NAT GW by design)
# S3 traffic will be routed via the VPC Gateway Endpoint below.
private_rt = aws.ec2.RouteTable(
    "private-rt",
    vpc_id = vpc.id,
    tags   = {"Name": "vpc-endpoint-demo-private-rt"},
)

aws.ec2.RouteTableAssociation(
    "private-rt-assoc",
    subnet_id      = private_subnet.id,
    route_table_id = private_rt.id,
)


# Security Groups

public_sg = aws.ec2.SecurityGroup(
    "public-sg",
    vpc_id      = vpc.id,
    description = "Allow SSH from internet to bastion EC2",
    ingress = [
        aws.ec2.SecurityGroupIngressArgs(
            description = "SSH from anywhere",
            from_port   = 22,
            to_port     = 22,
            protocol    = "tcp",
            cidr_blocks = ["0.0.0.0/0"],
        ),
    ],
    egress = [
        aws.ec2.SecurityGroupEgressArgs(
            description = "All outbound",
            from_port   = 0,
            to_port     = 0,
            protocol    = "-1",
            cidr_blocks = ["0.0.0.0/0"],
        ),
    ],
    tags = {"Name": "vpc-endpoint-demo-public-sg"},
)

private_sg = aws.ec2.SecurityGroup(
    "private-sg",
    vpc_id      = vpc.id,
    description = "Allow SSH only from public (bastion) EC2",
    ingress = [
        aws.ec2.SecurityGroupIngressArgs(
            description     = "SSH from bastion SG only",
            from_port       = 22,
            to_port         = 22,
            protocol        = "tcp",
            security_groups = [public_sg.id],
        ),
    ],
    egress = [
        aws.ec2.SecurityGroupEgressArgs(
            description = "All outbound (S3 via VPC endpoint)",
            from_port   = 0,
            to_port     = 0,
            protocol    = "-1",
            cidr_blocks = ["0.0.0.0/0"],
        ),
    ],
    tags = {"Name": "vpc-endpoint-demo-private-sg"},
)


# IAM Role for Private EC2  (S3 Read Only)

assume_role_policy = aws.iam.get_policy_document(
    statements = [
        aws.iam.GetPolicyDocumentStatementArgs(
            actions    = ["sts:AssumeRole"],
            principals = [
                aws.iam.GetPolicyDocumentStatementPrincipalArgs(
                    type        = "Service",
                    identifiers = ["ec2.amazonaws.com"],
                )
            ],
        )
    ]
)

private_ec2_role = aws.iam.Role(
    "private-ec2-role",
    assume_role_policy = assume_role_policy.json,
    tags               = {"Name": "vpc-endpoint-demo-private-ec2-role"},
)

aws.iam.RolePolicyAttachment(
    "s3-readonly-attach",
    role       = private_ec2_role.name,
    policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess",
)

private_ec2_instance_profile = aws.iam.InstanceProfile(
    "private-ec2-instance-profile",
    role = private_ec2_role.name,
    tags = {"Name": "vpc-endpoint-demo-private-ec2-profile"},
)


# EC2 Instances

bastion_ec2 = aws.ec2.Instance(
    "bastion-ec2",
    ami                    = ami_id,
    instance_type          = "t3.micro",
    subnet_id              = public_subnet.id,
    vpc_security_group_ids = [public_sg.id],
    key_name               = key_pair.key_name,
    user_data              = """#!/bin/bash
# Bastion has internet access — download AWS CLI zip so we can
# copy it over to the private EC2 (which has NO internet).
apt-get update -y
apt-get install -y unzip curl
curl -sL "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "/home/ubuntu/awscliv2.zip"
chown ubuntu:ubuntu /home/ubuntu/awscliv2.zip
echo 'AWS CLI zip ready at /home/ubuntu/awscliv2.zip' >> /home/ubuntu/setup.log
""",
    tags = {"Name": "vpc-endpoint-demo-bastion"},
)

private_ec2 = aws.ec2.Instance(
    "private-ec2",
    ami                    = ami_id,
    instance_type          = "t3.micro",
    subnet_id              = private_subnet.id,
    vpc_security_group_ids = [private_sg.id],
    key_name               = key_pair.key_name,
    iam_instance_profile   = private_ec2_instance_profile.name,
    user_data              = """#!/bin/bash
# Private EC2 has NO internet — only install unzip from local apt cache
# (available during first-boot before network is needed).
apt-get update -y
apt-get install -y unzip
# AWS CLI will be copied from the bastion via SCP during the demo.
""",
    tags = {"Name": "vpc-endpoint-demo-private"},
)


# S3 Demo Bucket + Test Object

demo_bucket = aws.s3.BucketV2(
    "demo-bucket",
    bucket_prefix = "vpc-endpoint-demo-",
    force_destroy = True,
    tags          = {"Name": "vpc-endpoint-demo-bucket"},
)

# Block all public access (access only via VPC endpoint)
aws.s3.BucketPublicAccessBlock(
    "demo-bucket-public-access-block",
    bucket                  = demo_bucket.id,
    block_public_acls       = True,
    block_public_policy     = True,
    ignore_public_acls      = True,
    restrict_public_buckets = True,
)

# Upload a test file so we can download it during the demo
aws.s3.BucketObject(
    "hello-txt",
    bucket  = demo_bucket.id,
    key     = "hello.txt",
    content = "Hello from VPC Endpoint! Traffic never left AWS.\n",
    content_type = "text/plain",
)


# VPC Gateway Endpoint for S3
# This is the CORE of the demo.
# Routes S3 traffic from the private subnet through AWS backbone,
# without needing a NAT Gateway or internet access.

vpc_endpoint_s3 = aws.ec2.VpcEndpoint(
    "s3-vpc-endpoint",
    vpc_id            = vpc.id,
    service_name      = f"com.amazonaws.{region}.s3",
    vpc_endpoint_type = "Gateway",
    route_table_ids   = [private_rt.id],
    tags              = {"Name": "vpc-endpoint-demo-s3-endpoint"},
)


# Outputs

pulumi.export("vpc_id",                  vpc.id)
pulumi.export("public_subnet_id",        public_subnet.id)
pulumi.export("private_subnet_id",       private_subnet.id)
pulumi.export("bastion_public_ip",       bastion_ec2.public_ip)
pulumi.export("private_ec2_private_ip",  private_ec2.private_ip)
pulumi.export("s3_bucket_name",          demo_bucket.bucket)
pulumi.export("vpc_endpoint_id",         vpc_endpoint_s3.id)

pulumi.export("step1_ssh_to_bastion",
    bastion_ec2.public_ip.apply(
        lambda ip: f"ssh -A -i server-pem -o IdentitiesOnly=yes ubuntu@{ip}"
    )
)
pulumi.export("step2_ssh_to_private_ec2",
    private_ec2.private_ip.apply(
        lambda ip: f"ssh -o IdentitiesOnly=yes ubuntu@{ip}   # run this INSIDE the bastion"
    )
)
pulumi.export("step3_list_s3_bucket",
    demo_bucket.bucket.apply(
        lambda b: f"aws s3 ls s3://{b}/   # run on private EC2"
    )
)
pulumi.export("step4_download_file",
    demo_bucket.bucket.apply(
        lambda b: f"aws s3 cp s3://{b}/hello.txt .   # run on private EC2"
    )
)
