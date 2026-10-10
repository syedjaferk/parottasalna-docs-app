# Session 2 · IAM Deep Dive: Users, Groups, Roles & Policies

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/9pqRCGaUhAg"
  title="Session 2: IAM deep dive" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 **Session 2** of the [AWS Solutions Architect playlist](https://www.youtube.com/playlist?list=PLYmjGMwZ9N88) (Tamil) · [watch on YouTube](https://www.youtube.com/watch?v=9pqRCGaUhAg)

## The big idea

IAM answers two questions for **every** request to AWS: **who are you?** (authentication) and
**are you allowed to do this?** (authorisation). Get IAM right and every other service is safer;
get it wrong and one leaked key can empty your account.

**Everyday example:** an office building. Your **ID card** proves who you are (user). Your
**department** (group) decides which floors you can enter. A **visitor badge** (role) gives a
guest temporary access that expires at the end of the day. The **rule book** at reception
(policy) lists exactly which doors each badge opens.

```{raw} html
:file: ../diagrams/s02-iam.html
```

## 1. Users and groups

- An **IAM user** has long-term credentials: a console password and/or **access keys**
  (`AKIA…` key ID + secret) for the CLI and SDKs.
- A **group** is a collection of users. Attach policies to the group, not to each user. Groups
  can't be nested, and a group is not an identity: you can't log in as a group.

```bash
aws iam create-group --group-name developers
aws iam attach-group-policy --group-name developers \
    --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess
aws iam create-user --user-name priya
aws iam add-user-to-group --user-name priya --group-name developers
```

## 2. Policies: the JSON that grants permissions

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

| Field | Meaning |
|---|---|
| `Effect` | `Allow` or `Deny` |
| `Action` | which API calls, `service:Action`, wildcards allowed (`s3:Get*`) |
| `Resource` | which things, by **ARN** (Amazon Resource Name) |
| `Condition` | optional extra rules: MFA present, source IP, time, tags… |

Policy kinds:

- **AWS managed:** written by AWS (`ReadOnlyAccess`, `AmazonS3ReadOnlyAccess`). Easy, but often broad.
- **Customer managed:** written by you, reusable across users, groups and roles. **Preferred.**
- **Inline:** embedded in one identity; deleted with it. Use rarely.
- **Resource-based:** attached to a resource instead of a person, e.g. an **S3 bucket policy**.
  It has a `Principal` field saying who is allowed.

## 3. How AWS evaluates a request

```{raw} html
:file: ../diagrams/s02-evaluation.html
```

1. Everything is **denied by default** (implicit deny).
2. An **explicit Allow** in any applicable policy grants access…
3. …unless there's an **explicit Deny** anywhere. **Deny always wins.**

## 4. Roles: temporary access without passwords

A **role** has permissions but no long-term credentials. Something **assumes** it and gets
**temporary credentials** from **STS** (Security Token Service) that expire automatically.

Each role has two policies:

- **Trust policy:** *who* may assume the role (e.g. the EC2 service, or another AWS account).
- **Permissions policy:** *what* the role can do once assumed.

Typical uses:

| Use | Example |
|---|---|
| AWS service acting for you | EC2 instance reading S3 ([Session 6](06-ec2-networking-storage.md)), Lambda writing to DynamoDB |
| **Cross-account access** | Your auditor's account assumes a read-only role in yours |
| Federation / SSO | Company login (Google, Okta, IAM Identity Center) assumes a role |

```bash
aws sts assume-role --role-arn arn:aws:iam::111122223333:role/AuditReadOnly \
    --role-session-name audit-oct
# returns AccessKeyId, SecretAccessKey, SessionToken, Expiration
```

## 5. MFA and best practices

- **MFA on root and every human user.** Authenticator app, passkey or hardware key.
- **Least privilege:** start with nothing, add only the actions needed. Use **IAM Access
  Analyzer** to find unused permissions.
- **Prefer roles over access keys.** Apps on EC2, Lambda or ECS should use roles, never stored keys.
- **Rotate and remove** unused access keys; the **credential report** lists them.
- **Use groups**, not per-user policies.
- **Don't use root** except for the few tasks that need it (closing the account, some billing settings).

## Common mistakes

- **Putting access keys in code or on EC2.** Use an instance role.
- **Attaching `AdministratorAccess` "just to make it work".** It works, and so does any attacker who gets those keys.
- **Forgetting the bucket ARN vs objects ARN:** `ListBucket` needs `arn:aws:s3:::bucket`, `GetObject` needs `arn:aws:s3:::bucket/*`.
- **Expecting a Deny to be overridden by an Allow.** It never is.

## Try it yourself

1. Create a group `readers` with `ReadOnlyAccess`, a user in it, and sign in as that user. Try to
   create an S3 bucket. What happens?

   <details class="solution">
   <summary>Answer</summary>

   An **AccessDenied** error: the user has no Allow for `s3:CreateBucket`, so the implicit deny applies.

   </details>

2. A user's group policy allows `s3:*`, and a separate policy on the same user has an explicit
   `Deny` for `s3:DeleteObject`. Can the user delete objects?

   <details class="solution">
   <summary>Answer</summary>

   No. An explicit Deny always wins over any Allow.

   </details>

3. Write a policy that lets a user read objects in `exam-results` but not list the bucket.

   <details class="solution">
   <summary>Answer</summary>

   ```json
   {"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Action": "s3:GetObject",
     "Resource": "arn:aws:s3:::exam-results/*"}]}
   ```

   </details>
