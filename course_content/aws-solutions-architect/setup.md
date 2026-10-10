# Setup: a safe AWS account

Do these steps once, before the first lab. They take about 20 minutes and protect you from the two
classic beginner problems: **a hacked account** and **a surprise bill**.

## Step 1 · Create the account

1. Go to <https://aws.amazon.com> → **Create an AWS account**.
2. Use an email you'll keep for years. This becomes the **root user**, the all-powerful owner.
3. Add a card. AWS charges only for what you use beyond the Free Tier, and a small verification
   charge may appear and be refunded.
4. Choose the **Basic support** plan (free).

:::{note}
**Free Tier** = limited free usage for new accounts (for example some EC2 hours and some S3
storage). It does **not** make everything free: NAT Gateways, load balancers beyond the free
allowance, interface endpoints and many other services charge from the first hour. Always check
the pricing page and clean up after labs.
:::

## Step 2 · Lock down the root user

The root user can do *everything*, including closing the account. Use it as little as possible.

1. Sign in as root → top-right menu → **Security credentials**.
2. **Assign MFA device** → use an authenticator app (Google Authenticator, Authy, Microsoft
   Authenticator) or a passkey/security key.
3. **Never create access keys for the root user.**

## Step 3 · Create your everyday admin login

Don't work as root. Create a separate identity for daily work:

- **Recommended:** **IAM Identity Center** → enable it → create a user for yourself → give it the
  `AdministratorAccess` permission set. You sign in through a portal URL with MFA.
- **Simpler for a personal lab account:** IAM → **Users** → create `admin-yourname` → attach the
  `AdministratorAccess` policy → enable console access and MFA.

[Session 2](sessions/02-iam-deep-dive.md) explains users, groups, roles and policies properly.

## Step 4 · Set a budget alert

**Billing and Cost Management → Budgets → Create budget → Use a template → Zero spend budget**
(or a monthly cost budget of, say, $5). Enter your email. AWS emails you as soon as anything
starts costing money.

:::{tip}
Also open **Billing → Billing preferences** and turn on **Free Tier usage alerts**.
:::

## Step 5 · Pick a Region

Top-right Region menu → **Asia Pacific (Mumbai) `ap-south-1`** is closest for most students in
India. Resources are created **per Region**: if you can't find something you created, check the
Region menu first.

## Step 6 · Install the AWS CLI

```bash
# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o awscliv2.zip
unzip awscliv2.zip && sudo ./aws/install
aws --version          # aws-cli/2.x.x ...
```

On macOS and Windows, use the installer from the
[AWS CLI install guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).

Connect it to your account:

```bash
aws configure sso      # if you use IAM Identity Center (recommended)
# or, with an IAM user's access key:
aws configure          # asks for key ID, secret, default region (ap-south-1), output (json)

aws sts get-caller-identity   # who am I? prints your account ID and user/role ARN
```

:::{warning}
**Never commit access keys to Git** or paste them in chats or screenshots. Bots scan GitHub for
AWS keys within minutes. If a key leaks, **deactivate it immediately** in IAM, then create a new one.
:::

## Step 7 · Clean-up habit

After every lab, delete what you created, in this order: instances → load balancers and target
groups → NAT Gateways → **release Elastic IPs** → endpoints → Transit Gateway attachments → VPCs.
Then check **Billing → Bills** the next day.
