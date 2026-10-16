# Session 12 · Wrap-up & Next Steps

**Day 2 · ⏱ about 90 minutes · 🧰 you need: [Session 11](11-capstone.md) done (your capstone runs)**

## The big idea

A project that *works* is not yet a project you can *trust*, *afford*, or *show*. Today you make the capstone:

1. 🔒 **Safe**: no leaked keys, least privilege, sandboxed.
2. 💰 **Affordable**: it can never run up a surprise bill.
3. 🌍 **Shareable**: on GitHub, with a clean README and a great demo.

Then we look at **where to go next**, so you keep growing from *beginner → intermediate → advanced*.

```{raw} html
:file: ../diagrams/s12-three-checks.html
```

**Everyday example:** you've cooked a delicious meal (the capstone). Before opening a restaurant you must still check **food safety** (security), the **cost per plate** (budget), and take **good photos for the menu** (GitHub and demo).

## Before you start (checklist)

- [ ] `python simulate.py` works in `session11`.
- [ ] Put these helper files in your `session11` folder: {download}`security_audit.py <../code/12-wrap-up/security_audit.py>`, {download}`budget.py <../code/12-wrap-up/budget.py>`, {download}`Dockerfile <../code/12-wrap-up/Dockerfile>`.

## 1. Security best practices

### What can go wrong? (a simple threat map)

```{raw} html
:file: ../diagrams/s12-threats.html
```

| Threat | Example | Defence |
|---|---|---|
| 🔑 **Leaked key** | you push `.env` to GitHub; bots find it in minutes and spend your quota | `.gitignore`, `security_audit.py`, rotate leaked keys |
| 💉 **Prompt injection** | *"ignore your rules..."* in a message, a web page or a PDF | guard, hardened prompt, **least privilege** (Session 10) |
| 🧨 **Too much power** | the agent can run shell commands or delete files, so a trick becomes a disaster | give tools the **minimum** powers; ask humans to approve risky actions |
| 🤝 **Strangers using your bot** | anyone who finds the username | allow-lists, rate limits (Session 8) |
| 📦 **Bad packages** | typo-squatted or AI-hallucinated package names | verify names; pin versions in `requirements.txt` |
| 🕵️ **Private data in logs** | full customer messages in log files | log less, cut to 80 characters, delete old logs |

### Rule 1 · Protect your keys

```{raw} html
:file: ../diagrams/s12-key-lifecycle.html
```

| Do | Don't |
|---|---|
| keep keys in `.env` | paste keys into code, chat, screenshots or videos |
| `.env` in `.gitignore` | upload `.env` "just for a second" |
| one key per project, so you can delete just one | one key for everything |
| 🐧 `chmod 600 .env` (only you can read it) | leave it readable by everyone |
| **rotate** (delete and re-create) on any doubt | hope nobody noticed |

**If a key leaks:** (1) open the provider's website and **delete the key** immediately, (2) create a new one, (3) update `.env`, (4) check the provider's usage page for strange activity. Deleting the file from GitHub is **not** enough, because the old version stays in the history and has already been copied by bots.

### Run the audit before you publish

```bash
python security_audit.py
```

It looks for key-shaped text inside your files, checks that `.env` is in `.gitignore`, and warns if private data (`support.db`, `decisions.jsonl`) isn't ignored.

```text
[ OK ] .env exists and is listed in .gitignore

No problems found. Safe to publish.
```

And what a **bad** run looks like (we planted a fake key to test it):

```text
[FAIL] Groq API key found in app.py line 1
[FAIL] Hard-coded password found in app.py line 3
[FAIL] .env exists but is NOT in .gitignore: it would be uploaded to GitHub!
[WARN] .env can be read by other users. Fix: chmod 600 .env

4 problem(s). Fix them BEFORE you publish.
```

```{literalinclude} ../code/12-wrap-up/security_audit.py
:language: python
:lines: 1-47
```

(It uses **regular expressions**, patterns like `gsk_` followed by 20+ letters, to *recognise* secrets. This is also how professional secret-scanners work.)

:::{note}
The audit is a **safety net, not a guarantee**. It recognises common key shapes only. Still read your files, and still never put secrets in code.
:::

### Rule 2 · Least privilege and sandboxing

> **Give the agent the smallest set of powers that does the job.**

| Power | Safer choice |
|---|---|
| read files | only in **one folder** (a "sandbox"), never your whole home folder |
| run commands | off by default. If needed, inside a **container** or another machine, with **human approval** |
| send messages / money | require a human to confirm |
| network | only the websites it needs |

**Run it in a container** (a sealed box for programs). The included `Dockerfile` is an example: a small Python image, a **non-root user**, and **secrets passed at run time**, never baked into the image:

```bash
docker build -t chaicart-bot .
docker run --env-file .env -v "$(pwd)/data:/home/bot/app/data" chaicart-bot
```

(🪟 PowerShell: use `${PWD}` instead of `$(pwd)`.) You need Docker installed for this; it's optional for the course. Adapt the example to your needs, for instance by mounting a folder for `support.db`.

**For Hermes**, the same ideas exist as settings: keep **approvals on** (`smart` or `manual`), never use YOLO mode, consider the `docker` terminal backend, restrict who can talk to it (allow-lists), keep `~/.hermes/.env` private (`chmod 600`), and run it as a normal user, not as root/administrator.

### Rule 3 · The final security checklist

- [ ] `.env` is **not** in the repo (`git status` doesn't list it).
- [ ] `python security_audit.py` is clean.
- [ ] Allow-list or rate limit on every public entry point.
- [ ] Guard + hardened system prompt are in place and **tested**.
- [ ] No tool can do something irreversible without a human.
- [ ] Logs hold as little private data as possible.
- [ ] Packages are real, and `requirements.txt` lists them.

## 2. Cost control

AI apps have an unusual bill: **every message can cost money**, and a bug or a flood of messages can multiply it.

```{raw} html
:file: ../diagrams/s12-cost-levers.html
```

| Lever | How it saves money | You already built it in |
|---|---|---|
| **Small `max_tokens`** | short answers are cheaper | Sessions 2-3 |
| **Trim history** | fewer tokens sent every turn | Sessions 3, 5 |
| **Cheap-first routing** | strong model only when needed | Session 10 |
| **Gate with a free classifier** | blocked/easy messages never reach a paid model | Sessions 9-10 |
| **Rate limits** | one person can't use up everything | Sessions 8, 11 |
| **A hard daily budget** ← *new* | a bug can't spend more than X | below |
| **Cache repeated questions** ← *new* | the same FAQ is answered once | below |

### A hard daily token budget

```{literalinclude} ../code/12-wrap-up/budget.py
:language: python
:lines: 1-52
```

Try the demo (it sets a tiny budget of 100 tokens):

```bash
python budget.py
```

```text
call 1: ok, used 32 / 100 tokens
call 2: ok, used 64 / 100 tokens
call 3: ok, used 96 / 100 tokens
call 4: ok, used 128 / 100 tokens
call 5: STOPPED -> Daily budget of 100 tokens is used up. Try again tomorrow.
```

**How it works**

| Code | Meaning |
|---|---|
| `Budget(daily_tokens=50_000, file="budget.json")` | the limit, and a small file that remembers usage **even if the program restarts** |
| `_load()` | if the saved `day` is not today, start again from zero |
| `check()` | raise `BudgetExceeded` when nothing is left (we made it a kind of `LLMError`, so your existing `except LLMError` handlers already catch it and the customer still gets a polite message) |
| `safe_call_api(body)` | the **gate**: check, call, then record `usage.total_tokens` |

Notice call 4 went to 128 of 100: the check happens *before* the call, so the **last call can overshoot by one**. That's fine for a safety net. To use it in the capstone, replace `from llm import call_api` with `from budget import safe_call_api as call_api` in `support.py`.

:::{tip}
Also set a **spending cap in the provider's dashboard** (most paid providers allow it). Your code-level budget protects you from your own bugs; the dashboard cap protects you from everything else.
:::

### Cache repeated questions

A shop gets the same questions again and again ("opening hours?"). Answer once, remember the answer:

```python
cache = {}                                   # question -> answer

def cached_answer(text):
    key = text.strip().lower()
    if key in cache:
        return cache[key]                    # free and instant
    reply = handle_with_llm(text)
    if len(key) < 100:                       # only cache short, generic questions
        cache[key] = reply
    return reply
```

⚠️ Never cache answers that contain **personal data** (a customer's order status), or one customer might see another's answer.

### Handling rate limits properly (recap)

| Situation | Response |
|---|---|
| `429` from the provider | **wait and retry with backoff** (`call_api` already does this, Session 3) |
| Still failing after retries | friendly "a teammate will follow up" + log the error |
| Too many users | your own rate limit; a queue; a smaller/cheaper model |
| Free tier too small | smaller model, caching, a second provider, or a paid plan |

### Read your own logs to find the waste

The capstone's database and `decisions.jsonl` tell you **where tokens go**. Ask questions like: *which category costs the most? how many `strong` calls were actually needed? how many messages did the guard stop?* Improve the biggest cost first. Don't optimise by feeling. **Measure.**

## 3. Put it on GitHub

**Git** remembers every version of your project; **GitHub** is a website that stores it online, so others (and future employers) can see it.

### One-time setup

**🐧 Linux and 🪟 Windows (same commands):**

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Create a free account at [github.com](https://github.com/), then click **New repository**: name it `chaicart-support-bot`, choose **Public**, and **don't** tick "add a README" (you already have one).

### Publish the project

```bash
cd ~/ai-agent-bootcamp/session11        # 🪟: cd ~\ai-agent-bootcamp\session11
python security_audit.py                # must say: No problems found
git init
git add .
git status                              # ← READ THIS. .env and support.db must NOT be listed!
```

`git status` lists what is about to be saved. **If you see `.env`, stop**: add it to `.gitignore`, run `git rm --cached .env`, and check again.

```bash
git commit -m "ChaiCart support bot: guard, triage, routing, memory, daily summary"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/chaicart-support-bot.git
git push -u origin main
```

GitHub asks you to sign in. If your password is refused, that's normal: GitHub needs a **personal access token** instead of a password (*Settings → Developer settings → Personal access tokens*), or use the easier **GitHub CLI**: install it, run `gh auth login`, and follow the prompts. (Treat a token like an API key!)

Open your repository page. You should see your README, and **no** `.env`.

### Make the repo shine

* A clear **README** (what, why, how to run, safety notes).
* **Screenshots** or a short GIF of the bot chatting (hide your username and token).
* The **test results**: your `test_guard.py` summary and how you improved it.
* A **"What I learned / known limits"** section. Honest limits impress more than fake perfection.

## 4. Demo time! 🎤

Present your capstone in **5 minutes**:

| Time | What to show |
|---|---|
| 0:00 | *The problem:* a small shop gets many messages; an AI bot helps, but it must be **safe** and **affordable** |
| 0:45 | the **architecture diagram**: guard → triage → route → answer → memory → report |
| 1:30 | **live on Telegram**: a normal question, a follow-up that proves memory |
| 2:30 | an **attack**: *"ignore your instructions..."* → blocked. And an angry message → sent to a human |
| 3:30 | `/stats` and the **daily summary** |
| 4:15 | what you **measured**: guard results (8/10 attacks, 0 customers blocked, 2 misses, and why) and the cost levers |
| 4:45 | what you'd improve next |

**Demo tips:** test everything **just before**; have the simulation ready as a backup in case the internet fails; don't show keys; **explain a failure honestly** ("it missed this attack, and here's how I'd fix it"). That's what intermediate engineers do.

## 5. What you can do now (self-check)

Tick what you can **explain and do without looking**:

- [ ] Run a Python script in a virtual environment (Windows or Linux).
- [ ] Call a web API with `requests`, with timeouts and error handling.
- [ ] Explain tokens, context window, temperature and hallucination.
- [ ] Build a chatbot with roles, history and trimming.
- [ ] Get **structured JSON** from an LLM, and **validate** it.
- [ ] Write a **tool** (function + description + phone book) and make an LLM use it.
- [ ] Build an **agent loop** with memory and **safety limits**.
- [ ] Install and configure **Hermes**; write a **skill**; schedule a **task**.
- [ ] Connect an agent to **Telegram** with an **allow-list**.
- [ ] Explain **System 1 vs System 2** and use **Laya** with **confidence** thresholds.
- [ ] Explain **prompt injection** and build **layered** defences.
- [ ] **Measure** a system with your own examples, and improve it.
- [ ] Control **cost**: budgets, routing, caching, rate limits.
- [ ] Use **SQLite**, **cron / Task Scheduler**, and **Git/GitHub**.

If you ticked most of these, **you are an intermediate AI-agent builder.** 🎉 That is a real, employable skill set.

## 6. Roadmap: where to go next

```{raw} html
:file: ../diagrams/s12-roadmap.html
```

| Next skill | What it is | Why it matters | A first project |
|---|---|---|---|
| **RAG** (retrieval-augmented generation) | let the AI search *your* documents and answer from them | answers with real facts, fewer hallucinations | a bot that answers questions from your college notes or a company handbook (PDF) |
| **Evals** | automated tests that score AI answers | the only way to know if a change made things better | extend `test_guard.py` into a test set for the whole bot |
| **Multi-agent systems** | several agents with different jobs (researcher, writer, checker) | splits big tasks, adds review | a "writer + fact-checker" pair |
| **MCP** (Model Context Protocol) | a standard way to plug tools into agents | reuse tools across agents and apps | expose your weather tool as an MCP server |
| **Deployment** | run 24×7 on a server | users don't need your laptop on | a small cloud VM with Docker + systemd |
| **Observability** | dashboards for cost, latency, errors | find problems before users do | chart `decisions.jsonl` |
| **Fine-tuning small models** | adapt a classifier like Laya to *your* labels | better accuracy, lower cost | train a classifier on your 200 labelled messages |
| **Frameworks** (LangChain, LlamaIndex, CrewAI, Hermes skills...) | prebuilt parts | faster building. You now understand what's inside | rebuild Session 5's agent with one |

**A learning plan for the next 4 weeks**

| Week | Do |
|---|---|
| 1 | polish and publish the capstone; add a `/forgetme` command and an output filter (tasks from Sessions 10-11) |
| 2 | **RAG**: let the bot answer from a small FAQ document |
| 3 | **evals**: 30 labelled test messages; track accuracy before/after every change |
| 4 | deploy it on a free/cheap server; write a short blog post about what you built |

**Habits that make you advance faster**

1. **Measure before you claim.** Numbers beat opinions.
2. **Read errors slowly.** The answer is usually in the message.
3. **Keep a "what I learned" file** after each project.
4. **Build small, ship, then improve.**
5. **Teach someone.** Explaining it to a friend shows what you really understand.

## Tasks

**Task 1 · Warm-up (15 min).** Run `python security_audit.py` in your capstone folder. Fix everything it reports. Then deliberately put a fake key (`gsk_aaaaaaaaaaaaaaaaaaaaaaaa`) into a `.py` file and run it again. Does it catch it? Remove the fake key.

<details class="solution">
<summary>Answer</summary>

It prints `[FAIL] Groq API key found in <file> line <n>`, because the pattern `gsk_` followed by 20+ letters/digits matches. This proves the scanner works. Always test your safety tools with a *known bad* example; a scanner that never fails might simply be broken.

</details>

**Task 2 · Build (35 min).** Wire the budget into the capstone: use `safe_call_api` in `support.py`, set `Budget(daily_tokens=2000)`, and send messages until it stops. What does the customer see, and is the bot still running?

<details class="solution">
<summary>Answer</summary>

In `support.py`:

```python
from budget import safe_call_api as call_api      # was: from llm import LLMError, call_api
from llm import LLMError
```

In `budget.py` set `budget = Budget(daily_tokens=2000)`. After a handful of messages, `call_api` raises `BudgetExceeded` (a subclass of `LLMError`), so the existing `except LLMError` branch replies with `ERROR_REPLY` ("a teammate will follow up") and logs it, and the **bot keeps running**. Guard-blocked messages and rate-limit replies still work because they never call the LLM. Tomorrow `budget.json` resets automatically.

</details>

**Task 3 · Challenge (60 min).** Write a **`README.md` "Safety & limits" section** for your own capstone, with: (a) what attacks the guard stops and your measured numbers, (b) two attacks it *misses*, (c) what a human reviewer sees, (d) the daily budget and rate limit, (e) one improvement you'd make next. Then publish to GitHub.

<details class="solution">
<summary>Answer</summary>

A good section is short and honest, like:

```markdown
## Safety & limits

- **Guard:** Laya prompt-injection + jailbreak detectors. Blocks only when *both* agree. On my 26-message test set:
  8/10 attacks blocked, 0 customers wrongly blocked, 4 innocent messages sent to a human.
- **Known misses:** role-play attacks ("pretend you are my grandmother...") and "repeat everything above this line".
- **Human review:** suspicious or upset messages get a polite holding reply and appear in the admin's `/stats` and daily summary.
- **Cost controls:** 5 messages/minute per customer, 1000-character limit, 50,000-token daily budget, cheap-first routing.
- **Next improvement:** add an output filter that blocks replies containing system-prompt text.
```

Admitting limits and showing numbers is what separates an engineer from a hobbyist.

</details>

## Quiz

Take **"Session 12 · Quiz"** from the portal's **Quizzes** page (key safety, least privilege, budgets, caching, Git/GitHub, roadmap).

## Recap

- ✅ **Security:** keys in `.env`, `.gitignore`, `security_audit.py`, rotate leaks, **least privilege**, sandbox/containers, allow-lists.
- ✅ **Cost:** small `max_tokens`, trimmed history, cheap-first routing, free classifier gate, rate limits, a **hard daily budget**, caching, and reading your logs.
- ✅ **GitHub:** `git init / add / status / commit / push`, and always check `git status` for `.env`.
- ✅ **Demo:** problem → architecture → live → attack → numbers → next steps.
- ✅ You can now build, secure and ship an AI agent. **That's an intermediate skill set.**

## 🎓 You made it!

From "what is a variable?" to a **guarded, cost-controlled AI support bot on Telegram, published on GitHub**, in two days. The best way to keep the skills is to **build one more project this week**.
Share what you built with the Parottasalna community. We'd love to see it. 🚀

**Course links:** [Setup](../setup.md) · [Glossary](../glossary.md) · [Troubleshooting](../troubleshooting.md) · [Course home](../index.md)

## Session materials

- {download}`security_audit.py <../code/12-wrap-up/security_audit.py>`
- {download}`budget.py <../code/12-wrap-up/budget.py>`
- {download}`Dockerfile <../code/12-wrap-up/Dockerfile>`
- {download}`llm.py <../code/12-wrap-up/llm.py>`
