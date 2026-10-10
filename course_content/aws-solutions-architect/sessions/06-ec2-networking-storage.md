# Session 6 · EC2 Networking, Storage & Access Management (Part 1)

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/CPhLFdJljsA"
  title="Session 6: EC2 networking, storage and access" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 **Session 6** of the [AWS Solutions Architect playlist](https://www.youtube.com/playlist?list=PLYmjGMwZ9N88) (Tamil) · [watch on YouTube](https://www.youtube.com/watch?v=CPhLFdJljsA)

## What you'll learn

- **Public vs private** instances, and the IP addresses an instance can have
- **Elastic IPs**: when you need one and what they cost
- Ways to **connect**: SSH key pairs, EC2 Instance Connect, Session Manager
- **IAM instance roles** and the **instance metadata service** (IMDSv2)
- **EBS** in depth: volume types, attaching, formatting, mounting, resizing, snapshots
- **Instance store** vs EBS, and when to use each

## 1. EC2 instance addresses: public vs private

**🧑 In plain words.** Every flat in an apartment complex has an **internal flat number** (private
IP) used by neighbours and the security guard. Only flats facing the road may also have a **postal
address** (public IP) that outsiders can send letters to.

**❓ The problem it solves.** Some servers must be reachable from the internet (a web server); most
must not (databases, internal APIs). Addresses decide who can even try to connect.

**⚙️ How it works.**

| Address | What it is | Lifetime |
|---|---|---|
| **Private IPv4** | from the subnet's range, e.g. `10.0.1.25` | stays for the instance's whole life |
| **Public IPv4** (auto-assigned) | from Amazon's pool | **released on stop**, a new one on start (kept on reboot) |
| **Elastic IP** | a static public IPv4 you allocate | yours until you release it |
| **IPv6** | globally unique, from the VPC's IPv6 block | stays with the network interface |
| **Private DNS** | `ip-10-0-1-25.ap-south-1.compute.internal` | resolves inside the VPC |
| **Public DNS** | `ec2-13-234-5-6.ap-south-1.compute.amazonaws.com` | changes with the public IP |

The public IPv4 isn't configured inside the OS: `ip addr` only shows the private IP. The VPC's
Internet Gateway does a 1:1 NAT between the public and private address. An instance is
*reachable* only if: it has a public IP, its subnet routes to an Internet Gateway, and its
**security group** (and NACL) allow the traffic.

**💡 Example.** The web server in a public subnet has `10.0.1.25` + `13.234.5.6`; the database in a
private subnet only has `10.0.2.40`. The web server talks to the DB on `10.0.2.40:5432`, inside the VPC.

## 2. Elastic IPs

**🧑 In plain words.** A **permanent phone number** you can move from one phone to another, instead
of a SIM that gets a new number every time it restarts.

**❓ The problem it solves.** Partners allow-list your IP; DNS records point at it; a changing public
IP after a stop/start breaks all of that.

**⚙️ How it works.** Allocate an EIP in a Region, **associate** it with an instance or network
interface, and **re-associate** it in seconds (e.g. to a standby server). AWS charges for **every
public IPv4 address** (since February 2024, about $0.005 per hour), whether attached or idle, so
release EIPs you don't use. Default limit: 5 EIPs per Region (can be raised).

**Better design:** don't rely on one instance's IP. Put a **load balancer** ([Session 5](05-elastic-load-balancer.md))
or **DNS** in front, or use a **NAT Gateway's EIP** for stable *outbound* IPs ([Session 8](08-nat-gateway.md)).

**💡 Example.** A payment gateway allow-lists `13.234.5.6`. You attach that EIP to your app server;
when it fails, you move the EIP to the standby server and the partner sees no change.

## 3. Connecting to instances

**🧑 In plain words.** Three ways into the building: your **own key** (SSH key pair), a **one-time
visitor pass from reception** (Instance Connect), or **reception escorting you in through a staff
corridor** with no front door at all (Session Manager).

**❓ The problem it solves.** Admins need shells on servers, but long-lived keys get shared and
lost, and an open port 22 attracts attacks.

**⚙️ How it works.**

| Method | How | Needs | Good for |
|---|---|---|---|
| **SSH key pair** | `ssh -i key.pem ec2-user@ip` | port 22 open, the private key file | simple labs |
| **EC2 Instance Connect** | console/CLI pushes a **one-time public key valid 60 s** | port 22 open to the Instance Connect IP range, the agent (preinstalled on Amazon Linux/Ubuntu) | no key files to share |
| **EC2 Instance Connect Endpoint** | an endpoint in your VPC tunnels SSH/RDP | the endpoint, SG rules | **private** instances without a bastion |
| **Session Manager** (SSM) | shell over the SSM agent's outbound connection | instance role with `AmazonSSMManagedInstanceCore`, outbound to SSM | **no inbound ports at all**, full audit logs |

Default users: `ec2-user` (Amazon Linux), `ubuntu` (Ubuntu), `admin` (Debian).

**💡 Example.** A bank forbids port 22 entirely. Admins use **Session Manager**; every command is
logged to S3/CloudWatch for audit.

## 4. IAM instance roles and the metadata service

```{raw} html
:file: ../diagrams/s06-role.html
```

**🧑 In plain words.** Staff don't carry copies of the master key. Each morning, building security
gives them an **access card that expires tonight**, and renews it automatically.

**❓ The problem it solves.** Apps on EC2 need AWS permissions (read S3, write to SQS). Putting access
keys in config files means they leak, get copied into AMIs and Git, and never rotate.

**⚙️ How it works.**

- You attach a **role** to the instance through an **instance profile** (the console does both).
- On the instance, the **Instance Metadata Service (IMDS)** at `169.254.169.254` serves temporary
  credentials for that role, refreshed automatically before they expire.
- The AWS CLI and SDKs look there automatically (after env vars and config files).
- **IMDSv2** requires a session token obtained with a PUT request; this blocks SSRF attacks where a
  vulnerable app is tricked into fetching the metadata URL. Set *IMDSv2 required* (the default for new
  instances) and a hop limit of 1 (2 if containers need it).

```bash
TOKEN=$(curl -s -X PUT http://169.254.169.254/latest/api/token -H "X-aws-ec2-metadata-token-ttl-seconds: 300")
curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/iam/security-credentials/
curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/placement/availability-zone
```

**💡 Example.** `aws sts get-caller-identity` on the instance shows
`arn:aws:sts::111122223333:assumed-role/app-reads-s3/i-0abc123…`, with no `aws configure` ever run.

## 5. Amazon EBS (Elastic Block Store)

```{raw} html
:file: ../diagrams/s06-ebs.html
```

**🧑 In plain words.** A **detachable hard disk** that lives in the same building (AZ) as your
computer. Unplug it, and plug it into another computer in the same building; the files stay.

**❓ The problem it solves.** Instances come and go; data must survive stops, restarts, instance
replacements and size changes.

**⚙️ How it works.**

- A **network-attached block device** in **one AZ**, automatically replicated *within* that AZ.
- Attaches to instances **in the same AZ** (one at a time, except io1/io2 **Multi-Attach** for
  special clustered apps). Survives stop/start. The **root volume** is deleted on termination by
  default (*Delete on termination*); extra volumes are kept.
- Can be **encrypted** with KMS (data at rest, in transit to the instance, and snapshots).
- Billed per GB-month provisioned (+ IOPS/throughput above the baseline for gp3/io2).

| Type | Kind | Performance | Use |
|---|---|---|---|
| **gp3** | SSD | 3,000 IOPS + 125 MB/s baseline, raise independently (up to 16,000 IOPS / 1,000 MB/s) | the default: boot volumes, most apps |
| gp2 | SSD | 3 IOPS per GiB, burst to 3,000 | older default |
| **io2 Block Express / io1** | SSD | provisioned IOPS (up to 256,000 for io2 BE), very low latency | busy databases |
| **st1** | HDD | throughput-optimised | big sequential reads: logs, Kafka, ETL |
| **sc1** | HDD | cheapest | cold, rarely read data |

HDD types (st1/sc1) **can't be boot volumes**.

**💡 Example.** A PostgreSQL server: root volume gp3 20 GiB, data volume **io2** 500 GiB with 20,000
provisioned IOPS, daily snapshots.

## 6. Snapshots

**🧑 In plain words.** A **photocopy** of the disk stored in a safe vault (S3). The first copy is
complete; after that, only the **pages that changed** are copied.

**❓ The problem it solves.** Backups, moving data to another AZ or Region, and creating identical
disks for new servers.

**⚙️ How it works.** Snapshots are **incremental** and stored in S3 (managed by AWS; not visible in
your buckets). Deleting an old snapshot keeps the data newer ones still need. From a snapshot you
can create a volume **in any AZ**, **copy** it to another Region (optionally re-encrypting), share it
with other accounts, or create an **AMI**. Automate with **Data Lifecycle Manager** or **AWS Backup**;
**Recycle Bin** can protect against accidental deletion. A new volume from a snapshot loads blocks
lazily on first read (unless **Fast Snapshot Restore** is enabled).

**💡 Example.** Data in `ap-south-1a` is needed by an instance in `ap-south-1b`: snapshot → create
volume in 1b → attach. For disaster recovery, copy the nightly snapshot to `ap-south-2`.

## 7. Hands-on: create, attach, mount, resize, snapshot

Create a 10 GiB gp3 volume **in the same AZ** as your instance and attach it as `/dev/sdf`, then on the instance:

```bash
lsblk                                   # the new disk shows as nvme1n1 (or xvdf), no mount point
sudo file -s /dev/nvme1n1               # "data" = empty; anything else = it already has a file system!
sudo mkfs -t xfs /dev/nvme1n1           # format ONLY a new, empty volume (erases data)
sudo mkdir /data && sudo mount /dev/nvme1n1 /data
df -h /data
```

**Output:**

```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/nvme1n1     10G  104M  9.9G   2% /data
```

Mount it automatically after a reboot (use the UUID; `nofail` lets the instance boot even if the volume is missing):

```bash
sudo blkid /dev/nvme1n1                 # UUID="1b2c..."
echo 'UUID=1b2c...  /data  xfs  defaults,nofail  0  2' | sudo tee -a /etc/fstab
sudo umount /data && sudo mount -a && df -h /data   # test fstab before rebooting
```

**Resize** (grow only): *Modify volume* to 20 GiB, wait for *optimizing*, then grow the file system:

```bash
sudo xfs_growfs -d /data                # XFS
# for ext4: sudo resize2fs /dev/nvme1n1
# for a root volume with partitions, first: sudo growpart /dev/nvme0n1 1
```

## 8. Instance store

**🧑 In plain words.** A **scratch pad on the desk** itself: very fast to write on, but it goes in
the bin when you leave the desk.

**❓ The problem it solves.** Some workloads need extremely fast local disk for temporary data:
caches, buffers, scratch space for processing.

**⚙️ How it works.** Physical NVMe/SSD disks on the host, available on certain instance types
(e.g. `m6id`, `i4i`). Very high IOPS and no network hop. **Data is lost** when the instance stops,
hibernates or terminates, or the host fails (it survives a reboot). You can't snapshot it.

**💡 Example.** A video-processing worker downloads files from S3 to the instance store, transcodes
them, uploads results to S3, and doesn't care if the scratch data disappears.

## Common mistakes

- **Volume and instance in different AZs.** You can't attach across AZs; restore from a snapshot instead.
- **Running `mkfs` on a volume that already has data.** Check with `sudo file -s` first.
- **A typo in `/etc/fstab` without `nofail`:** the instance won't boot. Test with `mount -a`.
- **Hard-coding a public IP** that changes on stop/start.
- **Access keys in `~/.aws/credentials` on an EC2 instance.** Use an instance role.
- **Forgotten Elastic IPs, volumes and snapshots** quietly adding to the bill.

## Hands-on exercises

⚠️ Instances, volumes, snapshots and public IPv4 addresses cost money. Use `t3.micro`/`t2.micro`
(Free Tier where available) and clean up at the end.

**Exercise 1 · Watch the public IP change.** Launch an instance with a public IP, note both IPs,
**stop** and **start** it, and compare. Then **reboot** and compare again.

<details class="solution"><summary>Answer</summary>

Stop/start → **new public IP**, same private IP. Reboot → both unchanged.

</details>

**Exercise 2 · Pin it with an Elastic IP.** Allocate an EIP, associate it, stop/start again, and
confirm the address stays. Then disassociate and **release** it.

<details class="solution"><summary>CLI</summary>

```bash
ALLOC=$(aws ec2 allocate-address --query AllocationId --output text)
aws ec2 associate-address --instance-id i-0abc... --allocation-id $ALLOC
# ... test ...
aws ec2 release-address --allocation-id $ALLOC   # disassociate first if needed
```

</details>

**Exercise 3 · No SSH keys: Instance Connect.** Launch an Amazon Linux instance **without a key
pair** and connect with **EC2 Instance Connect** from the console.

<details class="solution"><summary>Notes</summary>

Security group must allow port 22 from the EC2 Instance Connect prefix list for your Region
(`com.amazonaws.ap-south-1.ec2-instance-connect`). The console connects as `ec2-user`.

</details>

**Exercise 4 · No open ports: Session Manager.** Attach a role with `AmazonSSMManagedInstanceCore`,
**remove all inbound rules** from the security group, and open a shell with Session Manager.

<details class="solution"><summary>Check</summary>

Systems Manager → Fleet Manager shows the instance as *Online* (may take a few minutes after
attaching the role). Session Manager → Start session works even though the SG has no inbound rules.

</details>

**Exercise 5 · Instance role.** Create a role `lab-ec2-s3-read` (trusted by EC2,
`AmazonS3ReadOnlyAccess`), attach it, and run `aws s3 ls` on the instance without configuring keys.

<details class="solution"><summary>Check</summary>

`aws sts get-caller-identity` shows `assumed-role/lab-ec2-s3-read/i-…`. `aws s3 ls` lists buckets;
`aws s3 mb s3://x-$RANDOM` fails with AccessDenied (read-only).

</details>

**Exercise 6 · Read the metadata (IMDSv2).** Using IMDSv2 commands from section 4, print the
instance ID, AZ, and the role's credential expiry. Then try IMDSv1 (`curl` without a token).

<details class="solution"><summary>Answer</summary>

```bash
curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-id
curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/iam/security-credentials/lab-ec2-s3-read | grep Expiration
curl -s -o /dev/null -w "%{http_code}\n" http://169.254.169.254/latest/meta-data/   # 401 when IMDSv2 is required
```

</details>

**Exercise 7 · Add a data disk.** Create, attach, format and mount a 10 GiB gp3 volume at `/data`
(section 7) with an `/etc/fstab` entry. Reboot and confirm it's mounted.

<details class="solution"><summary>Check</summary>

After reboot, `df -h /data` shows the volume. `lsblk` shows `/data` as its mount point.

</details>

**Exercise 8 · Prove the data persists.** Write a file to `/data`, **detach** the volume, attach it
to a **second instance in the same AZ**, mount it there, and read the file.

<details class="solution"><summary>Key steps</summary>

Unmount first (`sudo umount /data`), detach in the console, attach to instance B, then on B:
`sudo mkdir /data && sudo mount /dev/nvme1n1 /data && cat /data/file.txt`. **Don't** run `mkfs` again!

</details>

**Exercise 9 · Grow the volume.** Increase the volume from 10 to 15 GiB and extend the file system
without unmounting.

<details class="solution"><summary>Solution</summary>

Console → Modify volume → 15 → wait for state *optimizing* or *completed* →
`sudo xfs_growfs -d /data` → `df -h /data` shows ~15G. Try making it smaller: the console refuses.

</details>

**Exercise 10 · Snapshot and restore in another AZ.** Snapshot the data volume, create a new volume
from it in a **different AZ**, attach it to an instance there, and read your file.

<details class="solution"><summary>CLI</summary>

```bash
SNAP=$(aws ec2 create-snapshot --volume-id vol-0abc --description lab --query SnapshotId --output text)
aws ec2 wait snapshot-completed --snapshot-ids $SNAP
aws ec2 create-volume --snapshot-id $SNAP --availability-zone ap-south-1b --volume-type gp3
```

</details>

**Exercise 11 · Copy a snapshot to another Region.** Copy the snapshot to `ap-south-2` (Hyderabad)
with encryption on.

<details class="solution"><summary>CLI</summary>

```bash
aws ec2 copy-snapshot --region ap-south-2 --source-region ap-south-1 \
    --source-snapshot-id $SNAP --encrypted --description "DR copy"
```

</details>

**Exercise 12 · Automate backups.** Create a **Data Lifecycle Manager** policy that snapshots
volumes tagged `backup=daily` every day and keeps 7.

<details class="solution"><summary>Where</summary>

EC2 → Lifecycle Manager → Create policy → *EBS snapshot policy* → target tag `backup=daily` →
schedule every 24 h → retain 7. Tag your volume and check the next day.

</details>

**Exercise 13 · Clean up.** Terminate the instances, delete the volumes, snapshots (both Regions) and
the DLM policy, and release any Elastic IPs.

<details class="solution"><summary>Check</summary>

EC2 → Volumes (only *in-use* root volumes of running instances, ideally none), Snapshots (none),
Elastic IPs (none) in **every Region you used**.

</details>
