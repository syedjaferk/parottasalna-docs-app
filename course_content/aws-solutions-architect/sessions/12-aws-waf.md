# Session 12 · AWS WAF (Web Application Firewall)

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/k-CDuJjZV6o"
  title="Session 12: AWS WAF" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 **Session 12** of the [AWS Solutions Architect playlist](https://www.youtube.com/playlist?list=PLYmjGMwZ9N88) (Tamil) · [watch on YouTube](https://www.youtube.com/watch?v=k-CDuJjZV6o)

## The big idea

Security groups and NACLs look at **IP addresses and ports**. They can't tell a normal search from
`' OR 1=1 --` in a login form. **AWS WAF** reads **HTTP requests** (paths, headers, query strings,
bodies) and blocks attacks such as **SQL injection**, **cross-site scripting (XSS)** and floods of
requests from bots, *before* they reach your application.

**Everyday example:** airport security. The gate pass (security group) lets passengers into the
terminal; the baggage scanner (WAF) looks inside each bag for dangerous items.

```{raw} html
:file: ../diagrams/s12-waf.html
```

## 1. Where WAF runs

You attach a **Web ACL** to a front-door resource:

- **Amazon CloudFront** (global, protects at the edge)
- **Application Load Balancer**
- **API Gateway** (REST APIs)
- AWS AppSync, Amazon Cognito user pools, App Runner, Verified Access

WAF **can't** be attached to a Network Load Balancer or directly to EC2: it needs a layer-7 front door.

## 2. Web ACLs, rules and actions

| Piece | Meaning |
|---|---|
| **Web ACL** | the list of rules attached to a resource, plus a **default action** (Allow or Block) |
| **Rule** | a condition + an action, evaluated in **priority order**; the first terminating match wins |
| **Rule group** | a reusable bundle of rules (your own or managed) |
| **Actions** | **Allow**, **Block** (403), **Count** (just log: test before blocking), **CAPTCHA**, **Challenge** |
| **WCUs** | each rule costs capacity units; a Web ACL has a capacity limit (1,500 by default) |

Things a rule can match: IP sets, countries (geo match), headers, query strings, URI paths, body,
regex patterns, size limits, SQLi and XSS patterns, labels added by earlier rules.

## 3. Managed rules vs custom rules

**AWS Managed Rules** are maintained by AWS's threat team. Good starting set:

| Managed rule group | Protects against |
|---|---|
| `AWSManagedRulesCommonRuleSet` | common OWASP issues, including XSS |
| `AWSManagedRulesSQLiRuleSet` | SQL injection |
| `AWSManagedRulesKnownBadInputsRuleSet` | known exploit patterns (e.g. Log4j) |
| `AWSManagedRulesAmazonIpReputationList` | IPs known for bots and attacks |
| Bot Control, Account Takeover Prevention | paid add-ons for bots and credential stuffing |

**Custom rules** handle your own needs: block an IP range, allow only India (geo match), require a
header, limit `/login`.

## 4. Rate-based rules

A **rate-based rule** counts requests per client IP (or per header, cookie, etc.) over a time window
and blocks clients above the limit, e.g. "more than **300 requests in 5 minutes** to `/login`". It
slows brute-force attacks and noisy bots. For large DDoS attacks, WAF works alongside **AWS Shield**
(Standard is automatic and free; Advanced is a paid service).

## 5. Hands-on: protect an ALB

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

## 6. Ten rules to try (class recipes)

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

## Try it yourself

1. Students from outside India are spamming your sign-up form. Which WAF features help?

   <details class="solution">
   <summary>Answer</summary>

   A **geo-match** rule (allow or CAPTCHA only for traffic from India), plus a **rate-based rule**
   on `/signup`, optionally the Bot Control managed rule group.

   </details>

2. A Web ACL rule blocks real customers by mistake. How should you have rolled it out?

   <details class="solution">
   <summary>Answer</summary>

   In **Count** mode first, checking sampled requests and logs before changing the action to Block.

   </details>

## Class files

- {download}`WAF try-outs: 10 rules step by step <../code/12-waf/waf-tryouts.txt>`
