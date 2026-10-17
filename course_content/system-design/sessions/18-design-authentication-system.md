# Chapter 18 · Design an authentication system

## The problem

Let users sign up, log in, stay logged in and log out safely, and let other services trust who the
caller is. **Authentication** answers *who are you?* **Authorization** answers *what may you do?*

```{raw} html
:file: ../diagrams/authentication.html
```

## Requirements

- Register, log in with email and password, log out, reset a forgotten password.
- Stay logged in on a device; log out of all devices.
- Optional: multi-factor authentication (MFA), social login (OAuth).
- Secure first. Then fast, then available. 10 million users, a login spike at 9am.

## Storing passwords

Never store the password, nor an unsalted hash. Store a **slow, salted hash** made by **bcrypt,
scrypt or Argon2**. The salt is random per user, so identical passwords hash differently and
precomputed tables ("rainbow tables") fail. The slowness makes guessing expensive.

## Sessions or tokens?

| | Server session | JWT access token |
|---|---|---|
| State | Session id in a cookie, data in Redis | Self-contained signed token |
| Revoke | Delete the session: instant | Hard until expiry, so keep it short |
| Scale | Needs a shared store | Any service can verify with a public key |

A good modern design: a **short-lived access token (about 15 minutes)** plus a **long-lived refresh
token** stored server-side (hashed) so it can be revoked. Send cookies as `HttpOnly; Secure; SameSite`.

## Login flow

1. Client sends credentials over **HTTPS** to the auth service.
2. Look up the user, verify the hash, apply **rate limiting and lockout** per account and per IP.
3. If MFA is enabled, require the second factor (TOTP code or push).
4. Issue the access token and refresh token; record the session (device, IP, time).
5. Each API request carries the access token; the **API gateway** verifies the signature and expiry.
6. When the access token expires, the client trades the refresh token for a new pair
   (**rotate** the refresh token; reuse of an old one signals theft).

## OAuth 2.0 and OpenID Connect in one minute

"Log in with Google": your app redirects to Google, the user approves, Google redirects back with a
one-time **code**, your server exchanges the code for tokens. Use the **authorization code with PKCE**
flow. You never see the user's Google password.

## Scaling

The auth service is **stateless**; sessions live in Redis; user data is sharded by user id. Verifying
a JWT needs no database call, so login is the only heavy path. Put a rate limiter in front.

## Threats to name

Credential stuffing (rate limit, breached-password check), session fixation, CSRF, XSS stealing
tokens (HttpOnly cookies), phishing (MFA, WebAuthn passkeys), account enumeration (same message for
"unknown user" and "wrong password").

## Common mistakes

- Rolling your own crypto.
- Long-lived access tokens with no revocation.
- Different error messages that reveal which emails exist.
- Logging passwords or tokens.

:::{admonition} Try it in the playground
:class: important
Build it in [Design an Authentication System](/system-design/authentication/).
:::
