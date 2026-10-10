# Session 15 · Amazon S3 (Part 1): Buckets, Objects, Storage Classes & CLI

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/Y8bqgBAlC6Y"
  title="Session 15: Amazon S3 part 1" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 **Session 15** of the [AWS Solutions Architect playlist](https://www.youtube.com/playlist?list=PLYmjGMwZ9N88) (Tamil) · [watch on YouTube](https://www.youtube.com/watch?v=Y8bqgBAlC6Y)

## The big idea

**Amazon S3 (Simple Storage Service)** stores **files ("objects")** of any kind and size, with
practically unlimited space, accessed over HTTPS. It's where almost every AWS project keeps
images, backups, logs, static websites and data lakes. You pay for what you store (per GB per month)
and for requests. The right **storage class** can cut the bill a lot.

**Everyday example:** a huge valet locker room. You hand over a parcel and a label (the key);
the staff store it safely, with copies in other buildings; you get it back with the label. You
never pick a shelf or worry about space. Rarely-collected parcels can go to the cheaper warehouse
outside town (Glacier), but fetching them back takes longer.

## 1. Object vs block vs file storage

| | Object (S3) | Block (EBS) | File (EFS, FSx) |
|---|---|---|---|
| Unit | whole objects, read/written over HTTP | raw disk blocks | files in folders |
| Accessed by | any app, via API/URL | one EC2 instance (mounted disk) | many instances at once (NFS/SMB) |
| Edit a part of it? | no: replace the whole object | yes | yes |
| Typical use | media, backups, logs, static sites, data lakes | OS disk, databases | shared folders, CMS uploads |

## 2. Buckets, objects and keys

```{raw} html
:file: ../diagrams/s15-bucket.html
```

- **Bucket:** a container for objects, created in **one Region**. General purpose bucket names are
  **globally unique** (3–63 lowercase letters, numbers, dots, hyphens).
- **Object:** the data + **metadata** (content type, custom `x-amz-meta-*` tags) + an optional
  **version ID**. Max size **5 TB**; a single upload (PUT) can be up to 5 GB, so use
  **multipart upload** for big files (recommended above ~100 MB; the CLI does it automatically).
- **Key:** the object's full name, e.g. `2026/oct/notes.pdf`. **There are no real folders**: the
  console just splits keys on `/` (prefixes).
- **Bucket types:** *general purpose* (the normal kind) and *directory buckets* (for the
  single-AZ, ultra-low-latency **S3 Express One Zone** class).

## 3. Durability and availability

- **Durability 99.999999999 % (11 nines):** S3 keeps copies across at least 3 AZs (except One Zone
  classes). Store 10 million objects and you might lose one every 10,000 years.
- **Availability** (can I read it right now?) differs by class: Standard is designed for **99.99 %**.

## 4. Security settings you'll see on every bucket

| Setting | Default for new buckets | Meaning |
|---|---|---|
| **Block Public Access** | **on** (all four options) | stops any policy or ACL from making data public. Turn off only for a deliberate public website |
| **Object Ownership** | **ACLs disabled** (bucket owner enforced) | access is controlled by policies, not old-style ACLs |
| **Default encryption** | **SSE-S3** (on for every new object) | encrypted at rest automatically; SSE-KMS for key control and audit |
| **Versioning** | off | when on, overwrites and deletes keep the old versions (protects against mistakes) |
| **Tags** | none | for cost allocation and access conditions |

## 5. Storage classes

```{raw} html
:file: ../diagrams/s15-classes.html
```

| Class | For | Min storage | Retrieval |
|---|---|---|---|
| **S3 Standard** | frequently used data | – | milliseconds, no retrieval fee |
| **Intelligent-Tiering** | unknown or changing access patterns: moves objects between tiers automatically | – | milliseconds (archive tiers optional); small monitoring fee per object |
| **Standard-IA** (Infrequent Access) | used about monthly, needs fast access | 30 days, min 128 KB billed | ms, **per-GB retrieval fee** |
| **One Zone-IA** | re-creatable infrequent data; **one AZ only** | 30 days, 128 KB | ms, retrieval fee |
| **Glacier Instant Retrieval** | archives read about once a quarter, needed instantly | 90 days, 128 KB | ms, retrieval fee |
| **Glacier Flexible Retrieval** | archives read a few times a year | 90 days | expedited 1–5 min · standard 3–5 h · bulk 5–12 h |
| **Glacier Deep Archive** | compliance archives kept for years | **180 days** | standard within 12 h · bulk within 48 h |

(Plus **S3 Express One Zone** for single-digit-millisecond access in directory buckets, and the
legacy Reduced Redundancy class, which you shouldn't use.)

:::{tip}
**Lifecycle rules** move or delete objects automatically, for example: logs → Standard-IA after 30
days → Glacier Flexible after 90 days → delete after 365 days. Use the
[AWS Pricing Calculator](https://calculator.aws/) to compare the cost before and after.
:::

## 6. Hands-on: the S3 CLI

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

## Try it yourself

1. Pick a storage class: (a) thumbnails used every day, (b) monthly reports opened a few times in
   the first month, (c) 7-year-old tax records kept for audit, (d) re-creatable image previews read monthly.

   <details class="solution">
   <summary>Answer</summary>

   (a) Standard, (b) Standard-IA (or Intelligent-Tiering if unsure), (c) Glacier Deep Archive,
   (d) One Zone-IA.

   </details>

2. Share a private file with a colleague for one hour without making the bucket public.

   <details class="solution">
   <summary>Answer</summary>

   `aws s3 presign s3://bucket/key --expires-in 3600`: a pre-signed URL that stops working after an hour.

   </details>

3. Why does the console show "folders" if S3 has none?

   <details class="solution">
   <summary>Answer</summary>

   It groups object keys by the `/` in them (prefixes) to make browsing easier; the bucket itself is a flat list of keys.

   </details>

## Class files

- {download}`Whiteboard: S3 part 1 <../code/whiteboards/15-s3-part-1.excalidraw>` ·
  {download}`Whiteboard: all S3 diagrams <../code/whiteboards/15-s3-all-diagrams.excalidraw>`
  (open at [excalidraw.com](https://excalidraw.com))
