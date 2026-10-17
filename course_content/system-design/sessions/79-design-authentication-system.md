# Chapter 79 · Design an authentication system

## Concepts to review first

This design is built from earlier chapters. Skim them if any term feels new:

- [HTTP and HTTPS](19-http-and-https.md)
- [Rate limiting](28-rate-limiting.md)
- [API gateway](23-api-gateway.md)
- [Stateful vs stateless architecture](65-stateful-vs-stateless-architecture.md)
- [Checksums (hashes and HMACs)](16-checksums.md)
- [Data replication](33-replication.md)

## The problem

Let users sign up, log in, stay logged in, reset a forgotten password and log out, and let **other services trust
who is calling** without asking the auth service every time. **Authentication** answers *who are you?*;
**authorization** answers *what may you do?*. This chapter is authentication.

```{raw} html
:file: ../diagrams/authentication.html
```

## Step 1: clarify requirements

**Functional:** sign up and log in with email and password; stay logged in on a device; log out (and "log out of all
devices"); password reset by email; optional multi-factor authentication (MFA) and "log in with Google".

**Non-functional (in priority order):** **security first**, then **availability** (if login is down, the whole product
is down), then **latency of token checks** (every API call pays it), and the ability to survive a **login spike at
9 am**.

**Out of scope:** fine-grained permissions, enterprise single sign-on (SAML), building the UI.

## Step 2: estimate the load

```python
users = 10_000_000
logins_per_user_per_day = 2
share_in_peak_window, peak_window_hours = 0.80, 2
hash_cpu_ms = 100                                  # a password check is slow ON PURPOSE

logins_per_day = users * logins_per_user_per_day
peak_logins_per_s = logins_per_day * share_in_peak_window / (peak_window_hours * 3600)
cores = peak_logins_per_s * hash_cpu_ms / 1000

api_calls_per_user_per_day = 200
token_checks_per_s = users * api_calls_per_user_per_day / 86_400

print(f"peak logins     : {peak_logins_per_s:,.0f} per second")
print(f"CPU for hashing : about {cores:,.0f} cores busy at peak")
print(f"token checks    : about {token_checks_per_s:,.0f} per second (must be nearly free)")
```

**Output:**

```text
peak logins     : 2,222 per second
CPU for hashing : about 222 cores busy at peak
token checks    : about 23,148 per second (must be nearly free)
```

Two very different profiles: **login is rare and expensive** (hundreds of cores at peak), while **token verification is
constant and must be almost free**. The design should keep them apart: scale the auth service for logins and verify
tokens **locally at the gateway** without calling it.

## Step 3: storing passwords safely

Never store a password. Store a **slow, salted hash**. The salt is random per user (so identical passwords look
different and precomputed tables fail), and slowness makes guessing expensive.

```python
import hashlib
import hmac
import os

ITERATIONS = 200_000            # tune so one hash takes roughly 100 ms on your hardware

def hash_password(password, salt=None):
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
    return salt.hex(), digest.hex()

def verify_password(password, salt_hex, digest_hex):
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), ITERATIONS)
    return hmac.compare_digest(digest.hex(), digest_hex)          # constant-time comparison

salt_a, hash_a = hash_password("correct horse battery staple")
salt_b, hash_b = hash_password("correct horse battery staple")      # the same password for a second user

print("same password, different salts -> different stored hashes:", hash_a != hash_b)
print("stored hash length (hex chars)                           :", len(hash_a))
print("right password verifies                                  :", verify_password("correct horse battery staple", salt_a, hash_a))
print("wrong password verifies                                  :", verify_password("Correct horse battery staple", salt_a, hash_a))
```

**Output:**

```text
same password, different salts -> different stored hashes: True
stored hash length (hex chars)                           : 64
right password verifies                                  : True
wrong password verifies                                  : False
```

In production use **Argon2id** (or bcrypt or scrypt), store the algorithm parameters with the hash so you can raise the
cost later, and never log or email a password.

## Step 4: sessions or tokens?

| | Server-side session | Signed access token (JWT) |
|---|---|---|
| State | Session id in a cookie; data in Redis | Self-contained, signed |
| Revoke | Delete the session: instant | Hard before expiry, so keep expiry short |
| Verification | A store lookup per request | **Local**: check a signature, no lookup |
| Scales | Needs a highly available shared store | **Any service** can verify with a key |

The strongest practical design combines them: a **short-lived access token (about 15 minutes)** that services verify
locally, plus a **long-lived refresh token** stored **hashed on the server** so it can be revoked and rotated.

```python
import base64
import hashlib
import hmac
import json

KEY = b"server-signing-key"

def b64(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def unb64(text):
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))

def make_token(user, now, lifetime=900):
    header = b64(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = b64(json.dumps({"sub": user, "iat": now, "exp": now + lifetime}).encode())
    signature = b64(hmac.new(KEY, f"{header}.{payload}".encode(), hashlib.sha256).digest())
    return f"{header}.{payload}.{signature}"

def verify_token(token, now):
    header, payload, signature = token.split(".")
    expected = b64(hmac.new(KEY, f"{header}.{payload}".encode(), hashlib.sha256).digest())
    if not hmac.compare_digest(expected, signature):
        return "rejected: bad signature"
    claims = json.loads(unb64(payload))
    if now >= claims["exp"]:
        return "rejected: expired"
    return f"accepted: user {claims['sub']}"

now = 1_700_000_000
token = make_token("asha", now)
print("token parts       :", [len(p) for p in token.split(".")], "characters")
print("fresh token       :", verify_token(token, now + 60))
print("after 16 minutes  :", verify_token(token, now + 960))

h, p, s = token.split(".")
forged_payload = b64(json.dumps({"sub": "admin", "iat": now, "exp": now + 900}).encode())
print("forged admin token:", verify_token(f"{h}.{forged_payload}.{s}", now + 60))
```

**Output:**

```text
token parts       : [40, 71, 43] characters
fresh token       : accepted: user asha
after 16 minutes  : rejected: expired
forged admin token: rejected: bad signature
```

The gateway verified the token with **no database call**. A tampered payload broke the signature. And the short
lifetime limits the damage of a stolen token to minutes.

## Step 5: the login and refresh flow

```text
POST /v1/login    {"email": "...", "password": "..."}
  1. rate limit by account and by IP            (stop brute force; the cheapest check goes first)
  2. look up the user; verify the salted hash   (same error for "no such user" and "wrong password")
  3. if MFA is on: require the one-time code
  4. issue an access token (15 min) and a refresh token (days), record the session (device, IP, time)
  5. write an audit event
  -> 200 {"access_token": "...", "refresh_token": "...", "expires_in": 900}

POST /v1/refresh  {"refresh_token": "..."}   -> a new pair; the old refresh token is now invalid (rotation)
POST /v1/logout   {"refresh_token": "..."}   -> revoke this session (or all sessions)
```

**Refresh-token rotation with theft detection:** every refresh issues a *new* refresh token and invalidates the
old one. If an **already-used** token is presented again, someone stole it, so revoke the whole token family.

```python
import secrets

issued = {}        # token -> {"user": ..., "family": ..., "used": False}
revoked_families = set()

def new_refresh(user, family=None):
    token = secrets.token_hex(8)
    issued[token] = {"user": user, "family": family or token, "used": False}
    return token

def refresh(token):
    record = issued.get(token)
    if record is None or record["family"] in revoked_families:
        return None, "rejected: unknown or revoked"
    if record["used"]:
        revoked_families.add(record["family"])                  # reuse of an old token: assume theft
        return None, "REJECTED and the whole session family is revoked (token reuse detected)"
    record["used"] = True
    return new_refresh(record["user"], record["family"]), "ok: new refresh token issued"

t1 = new_refresh("asha")
t2, msg = refresh(t1);           print("first refresh        :", msg)
t3, msg = refresh(t2);           print("second refresh       :", msg)
_, msg = refresh(t1);            print("attacker replays t1  :", msg)
_, msg = refresh(t3);            print("legitimate user's t3 :", msg)
```

**Output:**

```text
first refresh        : ok: new refresh token issued
second refresh       : ok: new refresh token issued
attacker replays t1  : REJECTED and the whole session family is revoked (token reuse detected)
legitimate user's t3 : rejected: unknown or revoked
```

After the replay both the thief and the real user are logged out: annoying, but the safe outcome.

## Step 6: brute force and abuse

```python
class LoginGuard:
    def __init__(self, max_failures=5, window=300):
        self.max_failures, self.window, self.failures = max_failures, window, {}

    def allowed(self, key, now):
        recent = [t for t in self.failures.get(key, []) if now - t < self.window]
        self.failures[key] = recent
        return len(recent) < self.max_failures

    def record_failure(self, key, now):
        self.failures.setdefault(key, []).append(now)

guard = LoginGuard()
for attempt in range(8):
    if not guard.allowed("asha@example.com", now=attempt):
        print(f"attempt {attempt + 1}: LOCKED, try again later (HTTP 429)")
        continue
    guard.record_failure("asha@example.com", now=attempt)
    print(f"attempt {attempt + 1}: wrong password")
print("six minutes later, allowed again:", guard.allowed("asha@example.com", now=400))
```

**Output:**

```text
attempt 1: wrong password
attempt 2: wrong password
attempt 3: wrong password
attempt 4: wrong password
attempt 5: wrong password
attempt 6: LOCKED, try again later (HTTP 429)
attempt 7: LOCKED, try again later (HTTP 429)
attempt 8: LOCKED, try again later (HTTP 429)
six minutes later, allowed again: True
```

Real systems combine per-account and per-IP limits with **progressive delays** (not a hard lock a stranger can
trigger to lock the real owner out), a **breached-password check**, CAPTCHAs after repeated failures and **MFA**.

## Step 7: OAuth and "log in with Google" in brief

Your app redirects the user to Google; the user approves; Google redirects back with a one-time **code**; your server
exchanges the code for tokens and reads the verified identity. Use the **authorization code flow with PKCE** (never the
deprecated implicit flow). You never see the user's Google password. Verify the ID token's signature, issuer,
audience and expiry, then map Google's stable user id to your own user record.

## Step 8: scale, resilience and the threat list

- **Scale:** stateless auth servers behind a load balancer; sessions and rate-limit counters in a **replicated Redis**;
  the user database replicated and, if needed, sharded by user id; autoscale on CPU because hashing is CPU-bound.
- **Resilience:** token verification is local, so an **auth outage only blocks new logins**. Existing access tokens
  keep working until they expire.
- **Threats and defences:** credential stuffing (rate limits, breached-password checks, MFA); stolen tokens (short
  lifetimes, `HttpOnly; Secure; SameSite` cookies, rotation); phishing (MFA, passkeys); account enumeration (identical
  error messages); XSS and CSRF (content security policy, SameSite, CSRF tokens).

| Choice | You gain | You pay |
|---|---|---|
| Short access tokens | Limited damage when stolen | More refresh traffic |
| Stateless verification | Trivial scaling, no lookups | Revocation is delayed |
| Slow password hashing | Resists offline cracking | CPU cost at login peaks |
| MFA | Blocks stolen passwords | User friction |

## Common mistakes

:::{warning}
- Storing passwords with fast hashes (MD5, SHA-256) or without a salt.
- Long-lived access tokens with no way to revoke them.
- Different error messages for "unknown user" and "wrong password".
- Putting tokens where JavaScript can read them (use `HttpOnly` cookies where possible).
- Rolling your own cryptography instead of using vetted libraries.
:::

## Try it yourself

1. Why is a unique salt per user important even when the hash is already slow?
2. A refresh token is stolen. How does rotation limit the damage?
3. Why does token verification not need the auth service?

<details class="solution"><summary>Answers</summary>

1. Without salts, identical passwords give identical hashes, and an attacker can crack many accounts at once with a precomputed table. A unique salt forces a separate attack per user.
2. Each refresh invalidates the old token, so a stolen token works at most once, and reuse of an old token reveals the theft and revokes the whole family.
3. The token is signed. Any service holding the verification key can check the signature and expiry locally.

</details>

:::{admonition} Try it in the playground
:class: important
Build it in [Design an Authentication System](/system-design/authentication/).
:::

:::{admonition} Next
:class: important
Next case study: [Design UPI payments](80-design-upi-payments.md).
:::
