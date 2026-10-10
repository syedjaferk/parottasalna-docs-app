# Session 2 · IAM Deep Dive: Users, Groups, Roles & Policies

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/9pqRCGaUhAg"
  title="Session 2: IAM deep dive" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 **Session 2** of the [AWS Solutions Architect playlist](https://www.youtube.com/playlist?list=PLYmjGMwZ9N88) (Tamil) · [watch on YouTube](https://www.youtube.com/watch?v=9pqRCGaUhAg)

## What you'll learn

- Authentication vs authorisation, and how IAM handles both for **every** AWS API call
- **Users**, **groups**, **roles** and **policies**, with the problem each one solves
- Reading and writing **JSON policies**: Effect, Action, Resource, Condition, Principal
- How AWS **evaluates** a request (implicit deny, explicit allow, explicit deny)
- **Roles and STS**: temporary credentials, trust policies, cross-account access
- **MFA**, least privilege, and the tools that keep IAM clean

```{raw} html
:file: ../diagrams/s02-iam.html
```

## 1. Authentication and authorisation

**🧑 In plain words.** At an office gate, the guard first checks your **ID card** (who are you?),
then checks the **list of rooms** you're allowed into (what can you do?).

**❓ The problem it solves.** In a shared account, many people and programs act at once. Without a
clear "who" and "what", one mistake or one stolen password can delete everything.

**⚙️ How it works.** Every request to AWS (console click, CLI command, SDK call) is **signed**
(SigV4) with credentials. IAM first **authenticates** the signer: a user's password or access key,
a role's temporary credentials, or a federated login. Then it **authorises**: it collects every
policy that applies (identity policies, resource policies, permissions boundaries, Organizations
SCPs, session policies) and evaluates them. IAM is **global** and **free**.

**💡 Example.** `aws s3 rm s3://reports/q3.csv` → IAM checks the access key is valid
(authentication), then whether any policy allows `s3:DeleteObject` on
`arn:aws:s3:::reports/q3.csv` with no deny anywhere (authorisation).

## 2. The root user

**🧑 In plain words.** The building **owner's master key**: opens every door, including the one to
sell the building.

**❓ The problem it solves.** Someone must own the account and be able to recover it. But such a
powerful login must almost never be used.

**⚙️ How it works.** The root user is the email that created the account. It **can't be limited** by
IAM policies (only by Organizations SCPs for member accounts). A few tasks need root: changing the
account's email or support plan, closing the account, restoring IAM admin access. Protect it:
**MFA**, a strong unique password, **no access keys**, and use it only for those tasks.

**💡 Example.** A developer uses root keys in a script that gets pushed to GitHub. Within minutes,
bots find the key and launch crypto-mining instances in every Region: the classic surprise bill.

## 3. IAM users

**🧑 In plain words.** A personal **ID card** for one person (or one program) with their own login.

**❓ The problem it solves.** Each person gets their own identity, so actions are traceable
(CloudTrail shows *who* did what) and access can be removed for one person without affecting others.

**⚙️ How it works.**

- Credentials: a **console password** (with MFA) and/or up to **two access keys**
  (`AKIA…` ID + secret) for the CLI/SDK. Two keys allow rotation without downtime.
- Users have no permissions until policies are attached (directly or via groups).
- Today AWS recommends **IAM Identity Center** (SSO) for people, and **roles** for applications;
  IAM users with long-term keys are for special cases (e.g. a tool that can't use roles).

```bash
aws iam create-user --user-name priya
aws iam create-login-profile --user-name priya --password 'Str0ng#Temp' --password-reset-required
aws iam list-users --query 'Users[].UserName'
```

**💡 Example.** `priya` (developer) and `jenkins-ci` (a program) are separate users, so revoking
Jenkins' keys doesn't log Priya out.

## 4. IAM groups

**🧑 In plain words.** A **department**. Everyone in "Developers" gets the developers' badge rights.

**❓ The problem it solves.** Managing 50 people's permissions one by one is slow and error-prone;
someone always ends up with too much or too little.

**⚙️ How it works.** A group is a collection of users with attached policies. A user can be in up to
10 groups and gets the **union** of their permissions. Groups **can't be nested**, and a group is
**not an identity**: it can't sign in or be named as a Principal in a policy.

```bash
aws iam create-group --group-name developers
aws iam attach-group-policy --group-name developers \
    --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess
aws iam add-user-to-group --user-name priya --group-name developers
```

**💡 Example.** A new joiner is added to `developers`; on their last day they're removed. No
policy is edited either time.

## 5. Policies (JSON)

**🧑 In plain words.** The **rule book**: "people with this badge may open these doors, under these
conditions".

**❓ The problem it solves.** Permissions need to be precise, written down, reviewable and reusable.

**⚙️ How it works.** A policy is a JSON document with one or more **statements**:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadReports",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:ListBucket"],
      "Resource": ["arn:aws:s3:::company-reports", "arn:aws:s3:::company-reports/*"],
      "Condition": { "Bool": { "aws:MultiFactorAuthPresent": "true" } }
    }
  ]
}
```

| Element | Meaning | Notes |
|---|---|---|
| `Version` | policy language version | always `2012-10-17` |
| `Effect` | `Allow` or `Deny` | |
| `Action` | API calls, `service:Action` | wildcards: `s3:Get*`, `ec2:*` |
| `Resource` | which resources, by **ARN** | `*` = all; S3 bucket vs objects differ |
| `Condition` | extra checks | source IP, MFA, tags, time, Region, VPC endpoint… |
| `Principal` | *who* (resource-based policies only) | an account, user, role or service |

**ARN format:** `arn:partition:service:region:account-id:resource`, e.g.
`arn:aws:iam::111122223333:user/priya`, `arn:aws:s3:::bucket/key` (S3 ARNs have no Region or account).

**Policy types:**

| Type | Attached to | Use |
|---|---|---|
| **AWS managed** | users/groups/roles | quick start (`ReadOnlyAccess`); often broader than needed |
| **Customer managed** | users/groups/roles | **your own reusable, versioned policies (preferred)** |
| **Inline** | one identity | strict 1:1 cases; deleted with the identity |
| **Resource-based** | a resource (S3 bucket, SQS queue, KMS key…) | has `Principal`; enables cross-account access |
| **Permissions boundary** | a user/role | the *maximum* permissions it can ever get |
| **SCP** (Organizations) | an account or OU | guardrails for whole accounts |

**💡 Example.** A policy that lets a user manage only EC2 instances tagged with their team:

```json
{
  "Effect": "Allow",
  "Action": ["ec2:StartInstances", "ec2:StopInstances"],
  "Resource": "arn:aws:ec2:ap-south-1:111122223333:instance/*",
  "Condition": { "StringEquals": { "aws:ResourceTag/team": "${aws:PrincipalTag/team}" } }
}
```

## 6. How AWS evaluates a request

```{raw} html
:file: ../diagrams/s02-evaluation.html
```

**🧑 In plain words.** Every door is locked by default. A note saying "allowed" opens it, but a
single note saying "never" anywhere wins over all the "allowed" notes.

**❓ The problem it solves.** With many policies from many places, there must be one predictable
rule for the final answer.

**⚙️ How it works (single account):**

1. Start with **implicit deny**.
2. If **any** applicable policy has an **explicit Deny** that matches → **DENY** (final).
3. Else, if an SCP or permissions boundary applies, the action must be allowed there too.
4. Else, if any identity or resource policy **explicitly Allows** it → **ALLOW**.
5. Otherwise → **implicit deny**.

For **cross-account** access, *both* sides must allow: the caller's identity policy **and** the
resource policy (or a role trust policy) in the other account.

**💡 Example.** Priya's group allows `s3:*`. A permissions boundary on her user allows only
`s3:Get*`, and a bucket policy denies `s3:DeleteObject` to everyone. Result: she can read objects;
she can't delete (explicit deny) and can't upload (`PutObject` is outside the boundary).

## 7. Roles and STS

**🧑 In plain words.** A **visitor pass** that's handed out when needed and expires at the end of the
day. Nobody carries a permanent key.

**❓ The problem it solves.** Applications, AWS services and outside accounts need access, but
long-term keys stored in code or servers leak, and are hard to rotate.

**⚙️ How it works.**

- A role has a **trust policy** (*who* may assume it) and **permissions policies** (*what* it can do).
- Assuming a role calls **STS `AssumeRole`**, which returns **temporary credentials**: access key ID,
  secret, **session token**, and an **expiration** (15 minutes to 12 hours; 1 hour by default).
- Common role types: **service roles** (EC2 instance profile, Lambda execution role), **cross-account
  roles**, **federation** (IAM Identity Center, SAML, OIDC like GitHub Actions), and
  **service-linked roles** that AWS services create for themselves.

Trust policy letting EC2 assume a role:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Service": "ec2.amazonaws.com" },
    "Action": "sts:AssumeRole"
  }]
}
```

Trust policy letting another account (an auditor) assume a role, only with MFA:

```json
{
  "Effect": "Allow",
  "Principal": { "AWS": "arn:aws:iam::444455556666:root" },
  "Action": "sts:AssumeRole",
  "Condition": { "Bool": { "aws:MultiFactorAuthPresent": "true" } }
}
```

```bash
aws sts assume-role --role-arn arn:aws:iam::111122223333:role/AuditReadOnly \
    --role-session-name audit-oct
```

**💡 Example.** An EC2 app reads S3 using an **instance role** ([Session 6](06-ec2-networking-storage.md)):
no keys on disk, credentials rotate automatically, and CloudTrail shows
`assumed-role/app-reads-s3/i-0abc…` for every call.

## 8. MFA and best practices

**🧑 In plain words.** A password is *something you know*; MFA adds *something you have* (your
phone, a security key). A stolen password alone is no longer enough.

**❓ The problem it solves.** Passwords get phished, reused and leaked. MFA blocks most account takeovers.

**⚙️ How it works.** MFA devices: authenticator apps (TOTP), **passkeys / FIDO2 security keys**, or
hardware TOTP tokens. Up to 8 MFA devices per user. Policies can **require** MFA with the
`aws:MultiFactorAuthPresent` condition, for example for destructive actions.

**Best-practice checklist:**

| Practice | Tool |
|---|---|
| MFA on root and every human | IAM → Security credentials |
| People sign in via SSO, not IAM users | **IAM Identity Center** |
| Apps use roles, never stored keys | instance profiles, Lambda roles, OIDC for CI |
| Least privilege | start small; **IAM Access Analyzer** policy generation and unused-access findings |
| Remove unused users and keys | **credential report**, "last accessed" info |
| Guardrails for whole accounts | **Organizations SCPs** |
| Audit everything | **CloudTrail** |

**💡 Example.** The credential report shows `jenkins-ci` has an access key not used for 200 days.
Deactivate it, wait a week for complaints, then delete it.

## Common mistakes

- **Access keys in code, `.env` files committed to Git, or on EC2.** Use roles.
- **`AdministratorAccess` "just to make it work".** It works for attackers too.
- **Bucket vs object ARNs:** `ListBucket` needs `arn:aws:s3:::bucket`; `GetObject` needs `arn:aws:s3:::bucket/*`.
- **Expecting an Allow to override a Deny.** It never does.
- **Forgetting both sides in cross-account access:** the role must trust the account, *and* the
  caller needs permission to call `sts:AssumeRole`.

## Hands-on exercises

All IAM exercises are **free**. Use a lab account, and delete what you create at the end.

**Exercise 1 · A read-only group.** Create a group `readers` with `ReadOnlyAccess`, a user `test-reader`
in it with console access, and sign in as that user in a private window.

<details class="solution"><summary>What success looks like</summary>

`test-reader` can open every service and *see* resources, but clicking **Create bucket** or
**Launch instance** fails with an *AccessDenied / not authorized* error.

</details>

**Exercise 2 · See the implicit deny.** As `test-reader`, run `aws s3 mb s3://anything-$RANDOM` (after
creating an access key for the user and running `aws configure --profile reader`).

<details class="solution"><summary>Expected result</summary>

```text
make_bucket failed: s3://anything-123 An error occurred (AccessDenied) when calling the CreateBucket operation: Access Denied
```

No policy allows `s3:CreateBucket`, so the implicit deny applies. Delete the access key afterwards.

</details>

**Exercise 3 · Write a bucket-scoped policy.** Create a customer managed policy that allows listing
and reading only the bucket `exam-results-<yourname>`, attach it to `test-reader`, and test that
another bucket is still denied.

<details class="solution"><summary>Policy</summary>

```json
{
  "Version": "2012-10-17",
  "Statement": [
    { "Effect": "Allow", "Action": "s3:ListBucket", "Resource": "arn:aws:s3:::exam-results-jafer" },
    { "Effect": "Allow", "Action": "s3:GetObject",  "Resource": "arn:aws:s3:::exam-results-jafer/*" }
  ]
}
```

(`ReadOnlyAccess` still lets them read everything; detach it from the group first to see the narrow policy alone.)

</details>

**Exercise 4 · Deny always wins.** Give `test-reader` an inline policy with `"Effect": "Deny",
"Action": "s3:GetObject", "Resource": "*"` while `ReadOnlyAccess` is still attached. Can they download
an object?

<details class="solution"><summary>Answer</summary>

No: the explicit **Deny** overrides the Allow from `ReadOnlyAccess`.

</details>

**Exercise 5 · Policy simulator.** Use the **IAM Policy Simulator** to test whether `test-reader` can
call `s3:PutObject` and `ec2:DescribeInstances`, without touching real resources.

<details class="solution"><summary>Where</summary>

IAM → Users → test-reader → **Simulate** (or <https://policysim.aws.amazon.com>). Select S3
`PutObject` and EC2 `DescribeInstances` → Run simulation. Expect *denied* and *allowed*, and it shows
which statement decided.

</details>

**Exercise 6 · Require MFA for deletes.** Write a policy that allows `s3:DeleteObject` on your bucket
only when MFA was used.

<details class="solution"><summary>Policy</summary>

```json
{
  "Effect": "Allow",
  "Action": "s3:DeleteObject",
  "Resource": "arn:aws:s3:::exam-results-jafer/*",
  "Condition": { "Bool": { "aws:MultiFactorAuthPresent": "true" } }
}
```

CLI calls with plain access keys have no MFA, so they're denied; console sessions with MFA work.

</details>

**Exercise 7 · Create and assume a role.** Create a role `lab-s3-reader` that **your own account** can
assume, with `AmazonS3ReadOnlyAccess`. Assume it from the CLI and check who you are.

<details class="solution"><summary>Solution</summary>

Console: IAM → Roles → Create role → **AWS account → This account** → attach `AmazonS3ReadOnlyAccess`.

```bash
aws sts assume-role --role-arn arn:aws:iam::<acct>:role/lab-s3-reader --role-session-name lab
# export the three values it returns, then:
export AWS_ACCESS_KEY_ID=... AWS_SECRET_ACCESS_KEY=... AWS_SESSION_TOKEN=...
aws sts get-caller-identity     # Arn: ...:assumed-role/lab-s3-reader/lab
```

</details>

**Exercise 8 · Role expiry.** Assume the role with `--duration-seconds 900`. Note the `Expiration`
time. Try a command after it passes.

<details class="solution"><summary>Expected result</summary>

After 15 minutes: `ExpiredToken: The security token included in the request is expired`. That's
the point of temporary credentials: a leaked token stops working on its own.

</details>

**Exercise 9 · Credential report.** Generate and download the credential report. Which users have
no MFA? Which access keys are older than 90 days?

<details class="solution"><summary>Solution</summary>

```bash
aws iam generate-credential-report
aws iam get-credential-report --query Content --output text | base64 -d > report.csv
column -s, -t < report.csv | less -S
```

Look at `mfa_active`, `access_key_1_last_rotated` and `access_key_1_last_used_date`.

</details>

**Exercise 10 · Access Analyzer.** Create an **IAM Access Analyzer** for your account and check
whether any resource (bucket, role, KMS key) is shared with an external principal.

<details class="solution"><summary>Where</summary>

IAM → Access analyzer → **Create analyzer** (zone of trust: current account). Findings list any
resource accessible from outside the account, e.g. a role trusting another account. Archive the
ones you intended.

</details>

**Exercise 11 · Tag-based access (ABAC).** Tag `test-reader` with `team=blue`. Write a policy allowing
`ec2:StopInstances` only on instances tagged `team=blue`, and test with two tagged instances (blue and red).

<details class="solution"><summary>Key condition</summary>

`"Condition": {"StringEquals": {"aws:ResourceTag/team": "${aws:PrincipalTag/team}"}}`. Stopping the
blue instance works; the red one is denied. Terminate both instances afterwards. ⚠️ (they cost while running)

</details>

**Exercise 12 · Clean up.** Delete `test-reader` (its access keys, login profile, group memberships
and policies first), the `readers` group and the `lab-s3-reader` role.

<details class="solution"><summary>Order</summary>

A user can't be deleted while it has keys, a login profile, MFA devices, attached/inline policies or
group memberships. The console's **Delete** does it all for you; with the CLI remove each first.

</details>
