# Session 12 · AWS WAF (Web Application Firewall)

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/k-CDuJjZV6o"
  title="Session 12: AWS WAF" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 **Session 12** of the [AWS Solutions Architect playlist](https://www.youtube.com/playlist?list=PLYmjGMwZ9N88) (Tamil) · [watch on YouTube](https://www.youtube.com/watch?v=k-CDuJjZV6o)

## What you'll learn

- Why network firewalls (security groups, NACLs) can't stop web attacks
- Common web attacks: **SQL injection**, **XSS**, brute force, bots and floods
- How **AWS WAF** works: **Web ACLs**, **rules**, **rule groups**, **actions**, **priorities**, **WCUs**
- **AWS managed rules** vs your own **custom rules**, and **text transformations**
- **Rate-based rules**, **CAPTCHA/Challenge**, logging, and where **AWS Shield** fits
- Protecting an ALB, and ten practical rules from class

```{raw} html
:file: ../diagrams/s12-waf.html
```

## 1. Why a web application firewall?

**🧑 In plain words.** Airport security has two layers. The **gate pass check** (security group)
decides who may enter the terminal. The **baggage scanner** (WAF) looks **inside each bag**. A
dangerous item in a valid passenger's bag gets past the first layer, but not the second.

**❓ The problem it solves.** Security groups and NACLs only see **IP addresses and ports**. An attack
like `' OR 1=1 --` in a login form arrives on port 443 from a normal IP, exactly like real users, so
network firewalls let it straight through.

**⚙️ How it works.** A **WAF** inspects the **HTTP request itself**: method, URI path, query string,
headers, cookies, body, source IP and country. It compares them with rules and **allows, blocks,
counts, or challenges** the request **before** it reaches your application.

**💡 Example.** `GET /search?q=1' UNION SELECT password FROM users--` reaches port 443 like any search.
WAF's SQL-injection rule spots the pattern and returns **403** before the app (and its database) sees it.

## 2. Common web attacks (OWASP-style)

**🧑 In plain words.** Tricks to make the app do something it shouldn't: run your text as a
database command, run your script in other users' browsers, or overwhelm it.

**❓ The problem it solves.** Knowing the attack tells you which rule stops it.

**⚙️ How it works.**

| Attack | What the attacker sends | Damage | WAF defence |
|---|---|---|---|
| **SQL injection** | `' OR '1'='1` in a parameter | read/modify the database | SQLi match / SQL database managed rules |
| **Cross-site scripting (XSS)** | `<script>…</script>` in a comment | runs code in other users' browsers | XSS match / Core rule set |
| **Brute force / credential stuffing** | thousands of logins per minute | account takeover | rate-based rules, ATP, CAPTCHA |
| **Bad bots / scrapers** | automated crawling | data theft, cost | Bot Control, CAPTCHA, user-agent rules |
| **Known exploits** | e.g. Log4Shell `${jndi:…}` | remote code execution | Known bad inputs managed rules |
| **Floods (layer 7 DDoS)** | huge request volume | outage | rate-based rules + Shield |

**💡 Example.** The Log4Shell vulnerability (2021): teams that had the **Known bad inputs** managed rule
group got protection the day AWS updated it, before they could patch their Java apps.

## 3. Where WAF runs

**🧑 In plain words.** The scanner can only be installed at a **front door that opens bags**:
reception desks, not raw cargo docks.

**❓ The problem it solves.** Knowing where you can attach it shapes the architecture.

**⚙️ How it works.** You attach a **Web ACL** to a layer-7 front door:

- **Amazon CloudFront** (global: create the Web ACL in **Global / us-east-1**; blocks at the edge, closest to attackers)
- **Application Load Balancer** (regional: create it **in the ALB's Region**)
- **API Gateway REST APIs**, **AWS AppSync**, **Amazon Cognito user pools**, **App Runner**, **Verified Access**

WAF **can't** attach to a **Network Load Balancer** or directly to EC2. One Web ACL can protect many
resources, but each resource has at most one Web ACL.

**💡 Example.** An app behind an NLB needs WAF: put **CloudFront** in front (WAF there), or switch to an ALB.

## 4. Web ACLs, rules, actions and capacity

**🧑 In plain words.** The scanner follows a **numbered checklist**. The first item that says "stop"
or "let through" decides; if nothing matches, the **default rule** applies.

**❓ The problem it solves.** Predictable, ordered decisions for millions of requests.

**⚙️ How it works.**

| Piece | Meaning |
|---|---|
| **Web ACL** | an ordered list of rules + a **default action** (Allow or Block) |
| **Rule** | a **statement** (match conditions, can combine with AND/OR/NOT) + an **action** |
| **Priority** | lower number = evaluated first; the first **terminating** action (Allow/Block) ends evaluation |
| **Rule group** | a reusable bundle of rules: AWS managed, Marketplace, or your own |
| **Actions** | **Allow** · **Block** (403, or a custom response) · **Count** (log only, keep evaluating) · **CAPTCHA** · **Challenge** (silent browser check) |
| **Labels** | rules can add labels that later rules match on |
| **WCU** | Web ACL capacity units: each rule costs some (regex and body inspection cost more); default limit **1,500** per Web ACL |

Statements you can use: IP sets, geo match (country), string/regex match on any request part,
**size constraint**, **SQLi match**, **XSS match**, rate-based, label match, managed rule groups.

**Text transformations** run **before** matching: URL decode, HTML entity decode, lowercase,
compress whitespace, Base64 decode… so `%27%20OR%201%3D1` and `' OR 1=1` look the same to the rule.
Order matters: **decode first, then lowercase**.

**💡 Example.** Priority 1 blocks IPs in `blocked-ips` (cheap and broad), priority 10 runs the managed
SQLi rules (more expensive), and the default action is Allow.

## 5. Managed rules vs custom rules

**🧑 In plain words.** **Managed rules** are the airport's **official list of banned items**, kept
up to date by security experts. **Custom rules** are **your airline's own extra rules** ("no pets on this flight").

**❓ The problem it solves.** Few teams can track every new attack pattern, but every app also has its
own specific needs.

**⚙️ How it works.**

| Managed rule group | Protects against |
|---|---|
| `AWSManagedRulesCommonRuleSet` (Core) | common OWASP issues, including XSS, bad sizes |
| `AWSManagedRulesSQLiRuleSet` | SQL injection |
| `AWSManagedRulesKnownBadInputsRuleSet` | known exploit patterns (e.g. Log4j) |
| `AWSManagedRulesAmazonIpReputationList` | IPs known for bots and attacks |
| `AWSManagedRulesAnonymousIpList` | VPNs, Tor, hosting providers |
| Bot Control, Account Takeover Prevention (ATP), Account Creation Fraud Prevention | paid add-ons for bots and credential attacks |

You can **override** individual rules in a managed group to Count (to fix false positives) and use
**scope-down statements** to apply a group only to some paths. **Custom rules** cover your own
needs: block an IP range, allow only India, require a header, protect `/admin`.

**💡 Example.** The Core rule set blocks large uploads with `SizeRestrictions_BODY`. For `/upload`
only, the team overrides that rule to Count, and adds its own size rule allowing up to 10 MB there.

## 6. Rate-based rules, CAPTCHA and Shield

**🧑 In plain words.** A guard who notices one person **trying the door 500 times in five minutes**
and stops letting them in for a while, or asks them to **prove they're human**.

**❓ The problem it solves.** Brute-force logins, scraping and application-layer floods use valid-looking requests.

**⚙️ How it works.**

- A **rate-based rule** counts requests per **aggregation key** (by default the source IP; or a
  header, cookie, query arg, country, forwarded IP, or a combination) over an **evaluation window**
  (1, 2, 5 or 10 minutes) and applies the action to keys above the **limit**, until they drop below it.
- A **scope-down statement** limits counting to, say, `/login`.
- **CAPTCHA** shows a puzzle; **Challenge** runs a silent browser check; both set a token with an
  **immunity time** so real users aren't asked again and again.
- **AWS Shield Standard** (free, automatic) protects against network/transport-layer DDoS; **Shield
  Advanced** (paid) adds 24×7 response team help, cost protection and advanced detection, and works with WAF.

**💡 Example.** Rule: more than 100 requests in 5 minutes to `/login` from one IP → Block. A
password-spraying bot is blocked after its 100th attempt; real users never get near the limit.

## 7. Logging and monitoring

**🧑 In plain words.** The scanner keeps a **logbook** of every bag it stopped, and why.

**❓ The problem it solves.** Tuning rules, investigating incidents and proving compliance.

**⚙️ How it works.** **Sampled requests** (last few hours, in the console) and **CloudWatch metrics**
per rule (allowed/blocked/counted) are always available. **Full logs** go to **CloudWatch Logs**,
**S3** or **Kinesis Data Firehose** (log group/bucket names must start with `aws-waf-logs-`), with the
matching rule, labels and request details; sensitive fields can be **redacted**.

**💡 Example.** Logs Insights query `filter action = "BLOCK" | stats count(*) by terminatingRuleId`
shows which rules block the most.

## 8. Hands-on: protect an ALB

1. *WAF & Shield → Web ACLs → Create*: Region = your ALB's Region, **associate** the ALB.
2. Add managed rule groups: **Core rule set** and **SQL database**.
3. Add a **rate-based rule**: limit 100 per 5 minutes, action Block (lab value).
4. Default action **Allow**. Turn on sampled requests and CloudWatch metrics.

Test it:

```bash
curl -s -o /dev/null -w "%{http_code}\n" "http://my-alb/search?q=docker"          # 200
curl -s -o /dev/null -w "%{http_code}\n" "http://my-alb/search?q=1'%20OR%20'1'='1"  # 403
```

**Output:**

```text
200
403
```

The blocked request appears under **Sampled requests** with the rule that matched.

:::{tip}
Roll out new rules in **Count** mode first, watch the logs for a few days for false positives
(legitimate users who'd be blocked), then switch to Block.
:::

## 9. Ten rules to try (class recipes)

The class worked through ten practical rules. The full step-by-step guide is in the class files below.

| # | Rule | Statement | Action |
|---|---|---|---|
| 1 | Block known bad IPs | IP set `blocked-ips` | Block (priority 1) |
| 2 | Lock `/admin` to the office | path starts with `/admin` **AND NOT** IP in `office-vpn-ips` | Block |
| 3 | Brute-force guard on `/login` | rate-based, 100 / 5 min, scope-down to `/login` | Block |
| 4 | Per-API-key limit | rate-based, custom key = header `x-api-key` | Block (Count first) |
| 5 | Geo-block | originates from selected countries | Block |
| 6 | Scanner user agents | header `User-Agent` contains `sqlmap` (lowercase transform) | Block |
| 7 | Huge request bodies | size constraint: body > 8 KB | Block |
| 8 | SQLi on one parameter | SQLi match on query param `search` (URL-decode → lowercase) | Block |
| 9 | XSS in form posts | XSS match on body (HTML-entity decode → lowercase) | Block |
| 10 | Bots on checkout | path starts with `/checkout` | **CAPTCHA** |

**Text transformations** (URL decode, lowercase, HTML entity decode…) run before matching, so
`%27%20OR%201%3D1` and `' OR 1=1` look the same to the rule. Order matters: decode first, then lowercase.

## Common mistakes

- **Trying to attach WAF to an NLB or EC2.** Put an ALB, CloudFront or API Gateway in front.
- **Web ACL in the wrong Region:** for CloudFront it must be created in **Global (us-east-1)**; for an ALB, in the ALB's Region.
- **Going straight to Block** with new rules and locking out real users.
- **Thinking WAF replaces fixing the code.** Still use parameterised queries and output escaping.

## Hands-on exercises

⚠️ AWS WAF charges per Web ACL, per rule and per million requests, and the ALB costs per hour. Do
these in one sitting with a test ALB ([Session 5](05-elastic-load-balancer.md)), then delete
everything. Start rules in **Count** where noted.

**Exercise 1 · Create and attach a Web ACL.** Create a Web ACL in the ALB's Region, associate it with
your ALB, default action **Allow**, with CloudWatch metrics and sampled requests on.

<details class="solution"><summary>Check</summary>

WAF & Shield → Web ACLs shows your ACL with the ALB under *Associated AWS resources*. The site works as before.

</details>

**Exercise 2 · Managed SQLi protection.** Add `AWSManagedRulesSQLiRuleSet` and test a normal and an
injected search.

<details class="solution"><summary>Test</summary>

```bash
curl -s -o /dev/null -w "%{http_code}\n" "http://<alb>/search?q=docker"          # 200
curl -s -o /dev/null -w "%{http_code}\n" "http://<alb>/search?q=1'%20OR%20'1'='1"  # 403
```

</details>

**Exercise 3 · Block bad IPs (recipe 1).** Create an IP set `blocked-ips` with your own public IP
`/32`, add a rule at priority 1 to Block it, test, then remove your IP.

<details class="solution"><summary>Check</summary>

Your requests get **403**; a friend's (or a phone on mobile data) still get 200. Sampled requests
show the IP-set rule as the terminating rule.

</details>

**Exercise 4 · Lock /admin to the office (recipe 2).** Block requests whose path starts with `/admin`
**and** whose source IP is **not** in `office-vpn-ips`.

<details class="solution"><summary>Rule logic</summary>

`AND( URI path starts with "/admin", NOT( IP in office-vpn-ips ) )` → Block. Test `/admin` from an
IP inside and outside the set: 200 vs 403. Other paths are unaffected.

</details>

**Exercise 5 · Brute-force guard (recipe 3).** Rate-based rule: limit 100 per 5 minutes, scope-down
URI starts with `/login`, Block. Fire 150 requests.

<details class="solution"><summary>Test</summary>

```bash
for i in $(seq 150); do curl -s -o /dev/null -w "%{http_code}\n" http://<alb>/login; done | sort | uniq -c
```

After the limit is detected (it can take up to a minute or so), responses switch to **403**. Other
paths keep working. The block lifts once your rate falls below the limit.

</details>

**Exercise 6 · Per-API-key limits (recipe 4).** Rate-based rule keyed on the `x-api-key` header
(custom aggregation key), action **Count** first. Send requests with two different keys.

<details class="solution"><summary>What to notice</summary>

Counting is **per key value**, not per IP: one noisy client doesn't affect another on the same office IP.
Check the rule's metrics, then switch to Block.

</details>

**Exercise 7 · Geo rule (recipe 5).** Add a rule that **Counts** requests from countries other than
India (`NOT geo match IN`). Look at sampled requests after testing from a VPN or another Region's instance.

<details class="solution"><summary>Check</summary>

Requests from outside India appear in sampled requests with the geo rule matched (action Count).
Change to Block only if your business really serves India only.

</details>

**Exercise 8 · Block scanners (recipe 6).** Block requests whose `User-Agent` contains `sqlmap`
(transformation: lowercase).

<details class="solution"><summary>Test</summary>

```bash
curl -s -o /dev/null -w "%{http_code}\n" -A "sqlmap/1.7" http://<alb>/     # 403
curl -s -o /dev/null -w "%{http_code}\n" -A "SQLMap" http://<alb>/         # 403 (lowercase transform)
```

</details>

**Exercise 9 · Size limit (recipe 7).** Block POST bodies larger than 8 KB. Test with a 4 KB and a 16 KB body.

<details class="solution"><summary>Test</summary>

```bash
head -c 4096  /dev/zero | curl -s -o /dev/null -w "%{http_code}\n" --data-binary @- http://<alb>/
head -c 16384 /dev/zero | curl -s -o /dev/null -w "%{http_code}\n" --data-binary @- http://<alb>/   # 403
```

</details>

**Exercise 10 · Decoding matters (recipe 8).** Create an SQLi match on query parameter `search`
**without** text transformations, and test with a URL-encoded attack. Then add *URL decode* + *lowercase*.

<details class="solution"><summary>What to notice</summary>

Encoded payloads like `%27%20OR%201%3D1` can slip past without **URL decode**. With the
transformations (decode first, then lowercase), they're caught.

</details>

**Exercise 11 · XSS on bodies (recipe 9).** Add an XSS match on the request body (HTML entity decode
→ lowercase) and POST a comment containing `<script>alert(1)</script>`.

<details class="solution"><summary>Test</summary>

```bash
curl -s -o /dev/null -w "%{http_code}\n" -d 'comment=<script>alert(1)</script>' http://<alb>/comments   # 403
```

</details>

**Exercise 12 · CAPTCHA on checkout (recipe 10).** Path starts with `/checkout` → **CAPTCHA**, immunity
300 s. Open it in a browser, then with curl.

<details class="solution"><summary>What to notice</summary>

The browser shows a puzzle once, then works for 5 minutes. curl gets an HTTP **405** with the CAPTCHA
page instead of your content: bots without a browser can't pass.

</details>

**Exercise 13 · Logging.** Send WAF logs to a CloudWatch log group named `aws-waf-logs-lab`, generate
some blocked requests, and find the top blocking rules with Logs Insights.

<details class="solution"><summary>Query</summary>

```text
fields @timestamp, action, terminatingRuleId, httpRequest.clientIp, httpRequest.uri
| filter action = "BLOCK"
| stats count(*) as hits by terminatingRuleId
| sort hits desc
```

</details>

**Exercise 14 · Clean up.** Disassociate and delete the Web ACL, IP sets and log group; delete the ALB
and instances.

<details class="solution"><summary>Check</summary>

WAF & Shield → Web ACLs (the right Region): none. EC2 → Load balancers: none.

</details>

## Class files

- {download}`WAF try-outs: 10 rules step by step <../code/12-waf/waf-tryouts.txt>`
