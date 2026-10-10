# Session 15 · Amazon S3 (Part 1): Buckets, Objects, Storage Classes & CLI

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/Y8bqgBAlC6Y"
  title="Session 15: Amazon S3 part 1" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 **Session 15** of the [AWS Solutions Architect playlist](https://www.youtube.com/playlist?list=PLYmjGMwZ9N88) (Tamil) · [watch on YouTube](https://www.youtube.com/watch?v=Y8bqgBAlC6Y)

## What you'll learn

- **Object vs block vs file** storage, and where S3 fits
- **Buckets, objects, keys, prefixes, metadata**, and the two bucket types
- **Durability vs availability** (11 nines)
- **Access control**: Block Public Access, bucket policies, IAM, ACLs, pre-signed URLs
- **Encryption** options and **versioning**
- All **storage classes** with their trade-offs, and **lifecycle rules**
- How S3 is **priced**, and the S3 CLI

## 1. Object vs block vs file storage

**🧑 In plain words.** **Block** storage is a hard disk plugged into one computer. **File** storage is
a shared office drive many computers open at once. **Object** storage is a **valet locker room**:
hand over a parcel with a label, get it back later with the label; you never see shelves.

**❓ The problem it solves.** Disks attach to one server and fill up; shared drives are limited and
harder to scale. Apps need storage for **billions of files**, reachable from anywhere over HTTP,
that never runs out and almost never loses data.

**⚙️ How it works.**

| | Object (S3) | Block (EBS) | File (EFS, FSx) |
|---|---|---|---|
| Unit | whole objects via HTTP API | raw disk blocks | files and folders |
| Accessed by | any app, anywhere (with permission) | one EC2 instance (mounted) | many instances (NFS/SMB) |
| Edit part of it? | no: replace the whole object | yes | yes |
| Capacity | unlimited | you provision GiB | grows automatically (EFS) |
| Typical use | media, backups, logs, static sites, data lakes | OS disks, databases | shared folders, CMS uploads |

**💡 Example.** A course portal keeps uploaded PDFs and videos in **S3**, its database on **EBS**, and
nothing on the web servers' disks, so servers can be replaced freely.

## 2. Buckets, objects, keys and prefixes

```{raw} html
:file: ../diagrams/s15-bucket.html
```

**🧑 In plain words.** A **bucket** is your locker room; each **object** is a parcel; the **key** is the
full label written on it, like `2026/oct/notes.pdf`.

**❓ The problem it solves.** A simple, flat, unlimited namespace that's easy to address by URL.

**⚙️ How it works.**

- **Bucket:** created in **one Region** (data stays there unless you replicate it). General purpose
  bucket names are **globally unique**, 3–63 characters, lowercase letters, numbers, dots, hyphens;
  default limit 10,000 buckets per account.
- **Object:** data + **metadata** (system: `Content-Type`, `Last-Modified`, `ETag`; user:
  `x-amz-meta-*`) + optional **tags** (up to 10) + a **version ID** if versioning is on.
- **Size:** up to **5 TB** per object; a single PUT up to **5 GB**; use **multipart upload** for
  large files (recommended above ~100 MB; the CLI does it automatically, parts upload in parallel and can be retried).
- **Key:** the full name. There are **no real folders**; the console groups keys by `/` (**prefixes**).
- **URL styles:** `https://bucket.s3.ap-south-1.amazonaws.com/2026/oct/notes.pdf`.
- **Bucket types:** **general purpose** (all classes except Express One Zone) and **directory buckets**
  (single AZ, **S3 Express One Zone**, single-digit-millisecond latency for hot data).
- **Consistency:** S3 is **strongly consistent**: after a successful write, every read sees it.

**💡 Example.** Keys `logs/2026/10/10/app.log` and `logs/2026/10/11/app.log` let you list one day
with `--prefix logs/2026/10/10/` and give lifecycle rules a prefix to act on.

## 3. Durability and availability

**🧑 In plain words.** **Durability** = "will my parcel ever be lost?" **Availability** = "can I get
my parcel *right now*, or is the counter closed for a moment?"

**❓ The problem it solves.** Knowing what you're guaranteed when choosing classes and designing backups.

**⚙️ How it works.**

- **Durability 99.999999999 % (11 nines)** for all classes: objects are stored redundantly across
  **at least 3 AZs** (One Zone classes: within one AZ). Store 10 million objects and you might lose
  one every 10,000 years.
- **Availability** differs by class: Standard designed for **99.99 %**, Standard-IA 99.9 %, One Zone-IA 99.5 %.
- Durability protects against **hardware** loss, not against **you** deleting or overwriting:
  that's what **versioning**, **Object Lock** and **replication** are for.

**💡 Example.** S3 won't lose your backup to a failed disk, but a script with `aws s3 rm --recursive`
will. Versioning turns that delete into a recoverable "delete marker".

## 4. Access control and security defaults

**🧑 In plain words.** The locker room has a **master switch** that keeps it closed to the public,
a **rule board at the door** (bucket policy), **staff badges** (IAM), and **one-time collection
slips** you can hand to a friend (pre-signed URLs).

**❓ The problem it solves.** Public buckets are one of the most common causes of data leaks. Access
must be private by default and precise when shared.

**⚙️ How it works.**

| Mechanism | What it does | Default |
|---|---|---|
| **Block Public Access** (account and bucket level) | overrides any policy or ACL that would make data public | **on** (all four settings) |
| **Bucket policy** (resource-based JSON) | who may do what on this bucket: other accounts, conditions (IP, VPC endpoint, TLS) | none |
| **IAM policies** | what *your* users/roles may do in S3 | — |
| **Object Ownership / ACLs** | legacy per-object permissions | **ACLs disabled** (bucket owner enforced) |
| **Pre-signed URLs** | time-limited link signed with *your* credentials | — |
| **Access Points** | named entry points with their own policies, per team/app | — |

A request is allowed if IAM **or** the bucket policy allows it (same account) and nothing denies it;
Block Public Access trumps public grants.

**💡 Example.** Bucket policy that forces HTTPS:

```json
{
  "Statement": [{
    "Effect": "Deny", "Principal": "*", "Action": "s3:*",
    "Resource": ["arn:aws:s3:::ps-notes", "arn:aws:s3:::ps-notes/*"],
    "Condition": { "Bool": { "aws:SecureTransport": "false" } }
  }]
}
```

## 5. Encryption and versioning

**🧑 In plain words.** **Encryption** puts each parcel in a locked box; you choose who holds the key.
**Versioning** keeps **every old copy** of a parcel when you replace it.

**❓ The problem it solves.** Data at rest must be unreadable if disks are stolen; mistakes (overwrites,
deletes, ransomware) must be recoverable.

**⚙️ How it works.**

| Encryption | Keys managed by | Notes |
|---|---|---|
| **SSE-S3** | S3 (AES-256) | **on by default** for every new object |
| **SSE-KMS** | AWS KMS key (AWS managed or yours) | key policies, CloudTrail audit of key use; use **S3 Bucket Keys** to cut KMS costs |
| **DSSE-KMS** | KMS, two layers | for strict compliance |
| **SSE-C** | you send the key with each request | S3 doesn't store it |
| **Client-side** | you encrypt before upload | S3 never sees plaintext |

**Versioning** (bucket setting: off → enabled → can only be *suspended*): each PUT creates a new
**version ID**; a DELETE adds a **delete marker** (the object "disappears" but old versions remain).
Restore by deleting the marker or copying an old version. Old versions are **billed**, so add a
lifecycle rule for noncurrent versions. **MFA Delete** and **Object Lock** (WORM retention) add protection.

**💡 Example.** A developer overwrites `config.json` with a broken file. With versioning on, they list
versions and copy the previous version back in seconds.

## 6. Storage classes

```{raw} html
:file: ../diagrams/s15-classes.html
```

**🧑 In plain words.** Lockers near the door (fast, expensive), lockers at the back (cheaper, small
fetching fee), and a **warehouse outside town** (cheapest, but fetching takes hours).

**❓ The problem it solves.** Most data gets **colder** with age. Paying "hot" prices for data nobody
reads wastes money.

**⚙️ How it works.**

| Class | For | AZs | Min storage | Min size billed | Retrieval |
|---|---|---|---|---|---|
| **S3 Standard** | frequently used data | ≥ 3 | – | – | milliseconds, no fee |
| **Intelligent-Tiering** | unknown/changing patterns: moves objects between tiers automatically | ≥ 3 | – | (objects < 128 KB stay in frequent tier) | ms; small monitoring fee per object; optional archive tiers |
| **Standard-IA** | used about monthly, needs fast access | ≥ 3 | 30 days | 128 KB | ms, **per-GB retrieval fee** |
| **One Zone-IA** | re-creatable infrequent data | **1** | 30 days | 128 KB | ms, retrieval fee |
| **Glacier Instant Retrieval** | archives read ~once a quarter, needed instantly | ≥ 3 | 90 days | 128 KB | ms, retrieval fee |
| **Glacier Flexible Retrieval** | archives read a few times a year | ≥ 3 | 90 days | – | expedited 1–5 min · standard 3–5 h · bulk 5–12 h |
| **Glacier Deep Archive** | compliance archives kept for years | ≥ 3 | **180 days** | – | standard within 12 h · bulk within 48 h |
| **S3 Express One Zone** | hot data needing single-digit ms | **1** (directory bucket) | – | – | fastest |

Glacier Flexible and Deep Archive objects must be **restored** (a temporary copy) before reading.
**Lifecycle rules** move objects between classes or **expire** them by age, prefix or tag, and can
clean up old versions and incomplete multipart uploads.

**💡 Example.** Logs: Standard for 30 days → Standard-IA → Glacier Flexible after 90 days → delete
after 365 days. The storage bill for old logs drops by over 80 %.

## 7. How S3 is priced

**🧑 In plain words.** You pay **rent** for space, a **small fee per visit**, a **delivery charge** when
parcels leave town, and sometimes a **fetching fee** for back-room lockers.

**❓ The problem it solves.** Avoiding bill surprises (e.g. lots of small objects in IA, or big downloads to the internet).

**⚙️ How it works.**

- **Storage:** per GB-month, by class.
- **Requests:** per 1,000 PUT/COPY/POST/LIST (more expensive) and GET/SELECT (cheaper).
- **Data transfer out** to the internet (inbound is free; to CloudFront and same-Region services is free or cheap).
- **Retrievals** (IA and Glacier classes), **monitoring** (Intelligent-Tiering), **replication**, etc.
- Use the [AWS Pricing Calculator](https://calculator.aws/) and **S3 Storage Lens** to see where money goes.

**💡 Example.** 1 million tiny 4 KB thumbnails moved to Standard-IA cost *more*: each is billed as
128 KB, plus retrieval fees. Keep small, hot objects in Standard.

## 8. Hands-on: the S3 CLI

```bash
aws s3 mb s3://ps-demo-notes-2026 --region ap-south-1              # make bucket
aws s3 cp notes.pdf s3://ps-demo-notes-2026/2026/oct/              # upload
aws s3 ls s3://ps-demo-notes-2026 --recursive --human-readable     # list everything
aws s3 sync ./site s3://ps-demo-notes-2026/site/                   # copy only what changed
aws s3 cp big-backup.tar s3://ps-demo-notes-2026/ --storage-class STANDARD_IA
aws s3 presign s3://ps-demo-notes-2026/2026/oct/notes.pdf --expires-in 3600   # temporary share link
aws s3api head-object --bucket ps-demo-notes-2026 --key 2026/oct/notes.pdf    # metadata
```

**Output (ls):**

```text
2026-10-10 20:41:03    1.2 MiB 2026/oct/notes.pdf
2026-10-10 20:42:17  512.0 MiB big-backup.tar
```

`aws s3` is the friendly high-level CLI; `aws s3api` exposes every API call (versioning, lifecycle, tagging…):

```bash
aws s3api put-bucket-versioning --bucket ps-demo-notes-2026 --versioning-configuration Status=Enabled
aws s3api list-object-versions --bucket ps-demo-notes-2026 --prefix 2026/oct/notes.pdf
```

**Clean up:** `aws s3 rb s3://ps-demo-notes-2026 --force` (with versioning on, delete all versions
first, or empty the bucket from the console).

## Common mistakes

- **Turning off Block Public Access "to make an image show".** Use a pre-signed URL or CloudFront instead.
- **Moving small or short-lived objects to IA or Glacier.** The 128 KB minimum and 30/90/180-day
  minimum durations can make them cost *more*.
- **Expecting to rename or append to an object.** Copy to a new key, and rewrite the whole object.
- **Choosing One Zone-IA for the only copy of important data.**
- **Forgetting old versions** when versioning is on: they're billed too. Add a lifecycle rule for noncurrent versions.

## Hands-on exercises

S3 costs are tiny for these exercises (a few MB), but ⚠️ delete buckets at the end. Use a unique
bucket name, e.g. `ps-lab-<yourname>-<random>`, in `ap-south-1`.

**Exercise 1 · Bucket and objects.** Create a bucket, upload three files into `2026/oct/` and one at the
top level, and list recursively.

<details class="solution"><summary>Solution</summary>

```bash
B=ps-lab-jafer-$RANDOM; aws s3 mb s3://$B --region ap-south-1
for f in a b c; do echo $f > $f.txt; aws s3 cp $f.txt s3://$B/2026/oct/; done
echo home > index.html && aws s3 cp index.html s3://$B/
aws s3 ls s3://$B --recursive --human-readable
```

</details>

**Exercise 2 · Prefixes are not folders.** List only `2026/oct/` with `aws s3api list-objects-v2
--prefix`, then with `--delimiter /` at the top level. What does the delimiter change?

<details class="solution"><summary>Answer</summary>

`--prefix 2026/oct/` returns the three keys. With `--delimiter /` and no prefix, you get `index.html`
plus a **CommonPrefix** `2026/`: that's how the console draws "folders".

</details>

**Exercise 3 · Metadata.** Upload `notes.pdf` with `Content-Type: application/pdf` and a custom
metadata `course=aws`, then read it back with `head-object`.

<details class="solution"><summary>Solution</summary>

```bash
aws s3 cp notes.pdf s3://$B/notes.pdf --content-type application/pdf --metadata course=aws
aws s3api head-object --bucket $B --key notes.pdf
```

The output shows `ContentType` and `Metadata: {"course": "aws"}`.

</details>

**Exercise 4 · Block Public Access in action.** Try to add a bucket policy that allows public
`s3:GetObject`. What happens? (Don't turn Block Public Access off.)

<details class="solution"><summary>Answer</summary>

The `put-bucket-policy` call fails with **AccessDenied** because Block Public Access forbids public
policies. That's the safety net working.

</details>

**Exercise 5 · Share privately with a pre-signed URL.** Create a 5-minute pre-signed URL for
`notes.pdf`, open it in a private browser window, and try again after it expires.

<details class="solution"><summary>Solution</summary>

```bash
aws s3 presign s3://$B/notes.pdf --expires-in 300
```

Works for 5 minutes; afterwards: `AccessDenied: Request has expired`.

</details>

**Exercise 6 · Versioning saves the day.** Enable versioning, overwrite `a.txt` twice, delete it, then restore the first version.

<details class="solution"><summary>Solution</summary>

```bash
aws s3api put-bucket-versioning --bucket $B --versioning-configuration Status=Enabled
echo v2 > a.txt && aws s3 cp a.txt s3://$B/2026/oct/a.txt
echo v3 > a.txt && aws s3 cp a.txt s3://$B/2026/oct/a.txt
aws s3 rm s3://$B/2026/oct/a.txt                      # adds a delete marker
aws s3api list-object-versions --bucket $B --prefix 2026/oct/a.txt
aws s3api copy-object --bucket $B --key 2026/oct/a.txt \
    --copy-source "$B/2026/oct/a.txt?versionId=<oldest-version-id>"
```

(Versions uploaded before versioning was enabled have version ID `null`.)

</details>

**Exercise 7 · Encryption check.** Find out how a new object is encrypted, then upload one with SSE-KMS
using the AWS managed key.

<details class="solution"><summary>Solution</summary>

```bash
aws s3api head-object --bucket $B --key index.html --query ServerSideEncryption    # "AES256" (SSE-S3)
aws s3 cp index.html s3://$B/kms.html --sse aws:kms
aws s3api head-object --bucket $B --key kms.html --query ServerSideEncryption       # "aws:kms"
```

</details>

**Exercise 8 · Force HTTPS.** Apply the "deny if `aws:SecureTransport` is false" bucket policy from
section 4 and test with `--endpoint-url http://s3.ap-south-1.amazonaws.com`.

<details class="solution"><summary>Expected</summary>

HTTPS (the default) works; the plain-HTTP request returns **AccessDenied**.

</details>

**Exercise 9 · Storage classes.** Upload a 1 MB file directly to `STANDARD_IA` and another to
`GLACIER`, list their classes, and try to download the Glacier one.

<details class="solution"><summary>Solution</summary>

```bash
head -c 1048576 /dev/urandom > big.bin
aws s3 cp big.bin s3://$B/ia.bin --storage-class STANDARD_IA
aws s3 cp big.bin s3://$B/cold.bin --storage-class GLACIER
aws s3api list-objects-v2 --bucket $B --query 'Contents[].[Key,StorageClass]' --output table
aws s3 cp s3://$B/cold.bin .     # fails: InvalidObjectState, the object must be restored first
aws s3api restore-object --bucket $B --key cold.bin --restore-request '{"Days":1,"GlacierJobParameters":{"Tier":"Bulk"}}'
```

(Bulk restores are cheapest and finish within hours.)

</details>

**Exercise 10 · Lifecycle rule.** Add a rule for prefix `logs/`: transition to Standard-IA after 30
days, Glacier Flexible after 90, expire after 365, and delete noncurrent versions after 30 days.

<details class="solution"><summary>lifecycle.json</summary>

```json
{"Rules": [{
  "ID": "logs-tiering", "Status": "Enabled", "Filter": {"Prefix": "logs/"},
  "Transitions": [{"Days": 30, "StorageClass": "STANDARD_IA"}, {"Days": 90, "StorageClass": "GLACIER"}],
  "Expiration": {"Days": 365},
  "NoncurrentVersionExpiration": {"NoncurrentDays": 30}
}]}
```

`aws s3api put-bucket-lifecycle-configuration --bucket $B --lifecycle-configuration file://lifecycle.json`

</details>

**Exercise 11 · Sync a static site.** Make a folder with three HTML files, `aws s3 sync` it, change one
file, sync again, then sync with `--delete` after removing a file locally.

<details class="solution"><summary>What to notice</summary>

The second sync uploads **only the changed file**. With `--delete`, files removed locally are removed
from the bucket too (careful!).

</details>

**Exercise 12 · Estimate a bill.** In the Pricing Calculator, price 1 TB of logs for a year: (a) all in
Standard, (b) with the lifecycle rule from Exercise 10.

<details class="solution"><summary>What to conclude</summary>

The tiered version is far cheaper once most data is older than 90 days, minus small transition
request and retrieval costs.

</details>

**Exercise 13 · Clean up.** Delete every object **and every version**, then the bucket.

<details class="solution"><summary>Solution</summary>

With versioning, `aws s3 rb --force` leaves old versions behind. Easiest: console → bucket → **Empty**
(deletes all versions), then **Delete**.

</details>

## Class files

- {download}`Whiteboard: S3 part 1 <../code/whiteboards/15-s3-part-1.excalidraw>` ·
  {download}`Whiteboard: all S3 diagrams <../code/whiteboards/15-s3-all-diagrams.excalidraw>`
  (open at [excalidraw.com](https://excalidraw.com))
