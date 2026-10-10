
## 1. Block a specific list of malicious IPs (IP Set)

**Purpose:** Instantly block known bad actors (e.g., IPs flagged from your logs or a threat feed).

1. Go to **WAF & Shield → IP sets → Create IP set**.
2. Name: `blocked-ips`, IP version: IPv4, Region: same as your Web ACL.
3. Add addresses in CIDR notation, e.g. `203.0.113.5/32`, `198.51.100.0/24`.
4. Save the IP set.
5. Go back to your Web ACL → Add my own rules → Rule type: **IP set** → select `blocked-ips`.
6. Match type: "originates from an address in" the IP set.
7. Action: **Block**.
8. Set priority high (e.g., 1) so it's evaluated first.
9. Save.

---

## 2. Allow-list an admin panel by IP

**Purpose:** Only your office/VPN IP can reach `/admin`; everyone else gets blocked.

1. Create an IP set named `office-vpn-ips` with your trusted CIDR ranges.
2. Add rule → Statement: build with **AND logic**:
   - Condition A: URI path **starts with** `/admin`
   - Condition B: source IP is **NOT IN** `office-vpn-ips`
3. Use the rule builder's "Logical rule statements" → `AND` → add a `NOT` around the IP set match.
4. Action: **Block**.
5. Priority: place above your general allow rules.
6. Save.

---

## 3. Rate-based rule on `/login` (brute-force protection)

**Purpose:** Stop credential-stuffing / brute-force attempts on a login endpoint.

1. Add rule → Rule type: **Rate-based rule**.
2. Name: `login-brute-force-guard`.
3. Rate limit: `100` requests per 5-minute window (tune based on real traffic).
4. Scope-down statement: URI path **starts with** `/login`.
5. Aggregate key: **IP address** (default).
6. Action: **Block**.
7. Save and set an appropriate priority.

---

## 4. Rate-based rule keyed by API key header (not raw IP)

**Purpose:** Rate-limit per API consumer instead of per IP — avoids punishing shared-IP users (offices, mobile carriers).

1. Add rule → Rule type: **Rate-based rule**.
2. Name: `api-key-rate-limit`.
3. Rate limit: e.g., `1000` requests per 5 minutes.
4. Aggregate key: choose **Custom keys** → select **Header** → header name: `x-api-key`.
5. Scope-down statement (optional): URI path **starts with** `/api/`.
6. Action: **Block** (or **Count** first to baseline).
7. Save.

---

## 5. Geo-block specific countries

**Purpose:** Block traffic from countries where you don't operate or don't expect legitimate users.

1. Add rule → Statement: **Originates from a country in**.
2. Select the country codes to block (e.g., `CN`, `RU`, `KP` — adjust to your actual policy/compliance needs).
3. Action: **Block**.
4. Priority: place near the top since it's a cheap, early filter.
5. Save.

---

## 6. Block a bad User-Agent (scanner/bot signature)

**Purpose:** Block known scanning tools like `sqlmap`, `nikto`, `nmap`.

1. Add rule → Statement: **Header**.
2. Header field name: `User-Agent`.
3. Match type: **Contains string**.
4. Value: `sqlmap` (create a separate rule or use OR logic for `nikto`, `nmap`, etc.).
5. Text transformation: **Lowercase** (so case variations still match).
6. Action: **Block**.
7. Save.

---

## 7. Block oversized request bodies (size constraint)

**Purpose:** Reject abnormally large payloads that shouldn't occur in normal use — protects against some DoS and buffer-abuse patterns.

1. Add rule → Statement: **Size constraint statement**.
2. Part of request to inspect: **Body**.
3. Comparison operator: **Greater than**.
4. Size: e.g., `8192` bytes (tune to your app's realistic max payload).
5. Action: **Block**.
6. Save.

---

## 8. Custom SQL injection pattern on a specific query parameter

**Purpose:** Add extra protection beyond the managed SQLi rule group, targeted at one known-sensitive parameter (e.g., `search`, `id`, `sort`).

1. Add rule → Statement: **SQL injection match statement**.
2. Part of request to inspect: **Single query parameter** → name: `search`.
3. Text transformation: **URL decode**, then **Lowercase** (stack both — order matters, URL-decode first).
4. Action: **Block** (or start in **Count**, per best practice).
5. Save.

---

## 9. Custom XSS check on the POST body

**Purpose:** Catch script-injection attempts submitted through forms (comments, profile fields, etc.).

1. Add rule → Statement: **Cross-site scripting (XSS) match statement**.
2. Part of request to inspect: **Body**.
3. Text transformation: **HTML entity decode**, then **Lowercase**.
4. Action: **Block** (Count first if this is a new rule going live).
5. Save.

---

## 10. CAPTCHA challenge on checkout instead of a hard block

**Purpose:** Slow down bots/scrapers on a sensitive path (checkout, coupon-apply) without blocking real users outright.

1. Add rule → Statement: **URI path** → match type: **Starts with** → value: `/checkout`.
2. (Optional) Combine with a rate-based condition using AND logic if you only want to challenge above a certain request rate.
3. Action: **CAPTCHA**.
4. Set the **Immunity time** (how long a solved CAPTCHA is trusted) — e.g., 300 seconds.
5. Save.

---

### General checklist to apply to every rule above
- Set new rules to **Count** first, review Sampled Requests / logs for a few days, then switch to **Block**.
- Order rules by **priority** — cheap/broad filters (geo, IP set) near the top; expensive/specific inspections (regex, SQLi/XSS) after.
- Watch your **Web ACL Capacity Units (WCU)** — stacking many custom + managed rules can hit the cap.
- Enable **logging to S3/CloudWatch** before you need it for an incident, not after.
