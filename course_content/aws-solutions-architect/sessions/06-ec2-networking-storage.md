# Session 6 · EC2 Networking, Storage & Access Management (Part 1)

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/CPhLFdJljsA"
  title="Session 6: EC2 networking, storage and access" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 **Session 6** of the [AWS Solutions Architect playlist](https://www.youtube.com/playlist?list=PLYmjGMwZ9N88) (Tamil) · [watch on YouTube](https://www.youtube.com/watch?v=CPhLFdJljsA)

## The big idea

Launching an EC2 instance is easy. Making it **production-grade** means answering three questions:
how is it **reached** (public vs private, Elastic IPs, Instance Connect), how does it **access
AWS** safely (instance roles instead of keys), and where does its **data live** so it survives
(EBS volumes and snapshots).

**Everyday example:** a rented office. Its **address** (IP) tells visitors where to come; a
**reception desk** (Instance Connect) checks who may enter; staff use an **access card from
building security** (role) instead of copying master keys; the **filing cabinet** (EBS) stays put
even if you change chairs (stop/start).

## 1. Public vs private instances

| | Public instance | Private instance |
|---|---|---|
| Subnet | route `0.0.0.0/0 → Internet Gateway` | no route to the IGW |
| IP addresses | private IP **and** a public IP | private IP only |
| Reachable from the internet | yes (if the security group allows) | no |
| Typical role | web server, bastion | app server, database |

:::{important}
A normal **public IPv4 address changes when you stop and start** the instance (a reboot keeps it).
The **private IP stays** for the instance's life.
:::

## 2. Elastic IPs

An **Elastic IP (EIP)** is a static public IPv4 address you own until you release it. You can move
it from one instance to another, e.g. to a standby server.

- AWS charges for **all public IPv4 addresses** (since February 2024), including Elastic IPs,
  attached or not. Release EIPs you don't use.
- Better design: don't depend on a fixed instance IP at all; put a load balancer or a DNS name in front.

## 3. Connecting: EC2 Instance Connect

- **EC2 Instance Connect:** the console pushes a one-time SSH key (valid 60 seconds) and opens a
  browser terminal. No key file to share. Port 22 must be open to the
  [Instance Connect IP range](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-connect-prerequisites.html)
  for your Region.
- **EC2 Instance Connect Endpoint:** reach **private** instances from the console without a bastion host.
- **Session Manager** (Systems Manager): a shell with **no inbound ports at all**, using the instance's IAM role.
- **Classic SSH:** `ssh -i mykey.pem ec2-user@<public-ip>` (Amazon Linux) or `ubuntu@…` (Ubuntu).

## 4. IAM instance roles: no keys on the server

```{raw} html
:file: ../diagrams/s06-role.html
```

Attach a role to the instance (**Actions → Security → Modify IAM role**). The AWS CLI and SDKs on the
instance automatically fetch **temporary credentials** from the instance metadata service and
refresh them before they expire.

```bash
aws sts get-caller-identity
# "Arn": "arn:aws:sts::111122223333:assumed-role/app-reads-s3/i-0abc123..."
aws s3 ls s3://company-reports/         # works with no 'aws configure'
```

:::{tip}
Use **IMDSv2** (token-based) for the metadata service: it blocks a class of SSRF attacks that
could steal those credentials. It's the default for new instances; keep it set to *required*.
:::

## 5. Amazon EBS: disks for EC2

```{raw} html
:file: ../diagrams/s06-ebs.html
```

An **EBS volume** is a network-attached disk. It lives in **one AZ** and attaches to instances in
that AZ. Data **persists** independently of the instance: stop/start keeps it; the root volume is
deleted on terminate by default (*Delete on termination*), extra volumes are kept.

| Volume type | What it's for |
|---|---|
| **gp3** (General Purpose SSD) | the default: 3,000 IOPS and 125 MB/s baseline, both adjustable |
| gp2 | older general purpose; IOPS grow with size |
| **io2 / io1** (Provisioned IOPS SSD) | databases needing high, guaranteed IOPS |
| **st1** (Throughput HDD) | big sequential reads: logs, data processing |
| **sc1** (Cold HDD) | cheapest, rarely read data |

Compare with **instance store**: fast disks physically on the host, but **data is lost on stop or
termination**. Only for caches and scratch data.

## 6. Hands-on: create, attach, mount, resize, snapshot

Create a 10 GiB gp3 volume **in the same AZ** as your instance and attach it as `/dev/sdf`, then
on the instance:

```bash
lsblk                                   # the new disk shows as nvme1n1 (or xvdf), no mount point
sudo mkfs -t xfs /dev/nvme1n1           # format ONLY a new, empty volume (erases data)
sudo mkdir /data && sudo mount /dev/nvme1n1 /data
df -h /data
```

**Output:**

```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/nvme1n1     10G  104M  9.9G   2% /data
```

Mount it automatically after a reboot (use the UUID; `nofail` lets the instance boot even if the
volume is missing):

```bash
sudo blkid /dev/nvme1n1                 # UUID="1b2c..."
echo 'UUID=1b2c...  /data  xfs  defaults,nofail  0  2' | sudo tee -a /etc/fstab
```

**Resize** (grow only; you can't shrink an EBS volume): *Modify volume* to 20 GiB in the console,
then grow the file system:

```bash
sudo xfs_growfs -d /data                # XFS
# for ext4: sudo resize2fs /dev/nvme1n1
# for a root volume with partitions, first: sudo growpart /dev/nvme0n1 1
```

**Snapshot:** *Actions → Create snapshot*. Snapshots are **incremental** (only changed blocks are
stored) and can be copied to another Region or used to create a volume in another AZ. Automate them
with **Data Lifecycle Manager** or **AWS Backup**.

## Common mistakes

- **Volume and instance in different AZs.** You can't attach across AZs; restore from a snapshot instead.
- **Running `mkfs` on a volume that already has data.** It wipes it.
- **Hard-coding a public IP** that changes on stop/start.
- **Access keys in `~/.aws/credentials` on an EC2 instance.** Use an instance role.
- **Forgotten Elastic IPs and snapshots** quietly adding to the bill.

## Try it yourself

1. Stop and start an instance with no Elastic IP. Which of its addresses changed?

   <details class="solution">
   <summary>Answer</summary>

   The **public** IPv4 address changed; the private IP stayed the same.

   </details>

2. You need the data on a volume in `ap-south-1a` on an instance in `ap-south-1b`. How?

   <details class="solution">
   <summary>Answer</summary>

   Snapshot the volume, create a new volume from the snapshot **in `ap-south-1b`**, and attach it there.

   </details>

3. Give an instance read-only access to one S3 bucket without any access keys.

   <details class="solution">
   <summary>Answer</summary>

   Create a role trusted by `ec2.amazonaws.com` with a policy allowing `s3:ListBucket` on the bucket
   and `s3:GetObject` on `bucket/*`, then attach it to the instance (an instance profile).

   </details>
