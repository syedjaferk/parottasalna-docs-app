# Session 10 · Git Workflows: How Teams Organise Their Work

**⏱ about 90 minutes · 🧰 you need: [Session 9](09-power-tools.md) done**

## The big idea

Git gives you the *tools*: branches, merges, remotes, pull requests. It does **not** tell you *how a team should use them*. A **workflow** is the team's agreed set of rules: *where does new work start? Where is it reviewed? What is allowed to touch `main`? How do releases get made?*

**Everyday example:** a kitchen. A tiny food stall needs no rules: one cook does everything. A restaurant has stations and an order of service. A hotel serving a 500-person wedding has a head chef, written recipes and checks before every plate leaves. All three use the same knives (Git commands). What differs is the **process**, and the right process depends on the **size and style** of the kitchen.

There is no single "correct" workflow. This session explains **six** common ones, using the same small scenario each time, so you can compare them.

| # | Workflow | One-line idea | Typical team |
|---|---|---|---|
| 1 | **Centralized** | everyone commits straight to `main` | solo / tiny, high trust |
| 2 | **Feature Branch** | every task gets its own branch, merged when done | most small and medium teams |
| 3 | **GitHub Flow** | feature branch + pull request + deploy often | web apps, continuous delivery |
| 4 | **Git Flow** | long-lived `develop`, plus release and hotfix branches | versioned products with scheduled releases |
| 5 | **Forking** | contributors work on **their own copies** and send PRs | open source |
| 6 | **Trunk-Based** | tiny commits to one trunk; branches live hours | mature teams with strong automation |

**The scenario for every example:** a small shop website. Asha adds a *cart page*, Ravi adds *search*, and a *payment bug* appears in production.

## Words you need first

| Word | Meaning |
|---|---|
| **main** (or *master*, *trunk*) | the primary branch: the "official" version of the project |
| **production** | the live app that real users use |
| **deploy** | publish code to production |
| **CI** (continuous integration) | a robot that runs tests on every push |
| **CD** (continuous delivery/deployment) | a robot that ships passing code automatically |
| **release** | a named, versioned snapshot, for example `v2.1.0` |
| **hotfix** | an urgent fix to production |
| **long-lived branch** | a branch that exists for weeks or forever (`main`, `develop`) |
| **short-lived branch** | a branch that exists for hours or days (a feature) |

---

## Workflow 1 · Centralized Workflow

**The idea:** the simplest possible. There is **one branch, `main`**, on a central repository. Everyone commits to it directly. It works just like older tools (Subversion), only with Git underneath.

**Everyday example:** a shared notebook on the kitchen table. Anyone writes in it; you read the latest pages before adding yours.

```{raw} html
:file: ../diagrams/g10-centralized.html
```

**How a day looks:**

```bash
git pull                       # get everyone's latest work
# ... edit files ...
git add .
git commit -m "Add contact form"
git pull                       # again, in case someone pushed meanwhile
git push                       # share it
```

If someone pushed first, `git push` is rejected. You `git pull` (resolve any conflict) and push again.

| ✅ Good | ❌ Bad |
|---|---|
| Nothing new to learn. | `main` can break at any time, since everyone writes to it. |
| Perfect for a solo project or a school assignment. | No review step; mistakes go straight to everyone. |
| No branch management. | Many people editing at once means many conflicts. |

**Use it when:** you work alone, or on a 2 to 3 person project where everyone trusts everyone.
**Avoid it when:** more than a few people commit, or `main` is deployed to real users.

---

## Workflow 2 · Feature Branch Workflow

**The idea:** `main` stays **stable**. Every task (feature, bug fix) gets **its own branch**. You work there freely, and when the work is complete and checked, you merge it into `main`.

**Everyday example:** each cook prepares a dish on their own counter. Only a finished, tasted dish goes onto the shared serving table.

```{raw} html
:file: ../diagrams/g10-feature.html
```

**Rules:**

1. `main` is always in a working state.
2. Never commit directly to `main`.
3. Branch names say what the work is: `feature/cart-page`, `bugfix/wrong-total`.
4. Merge only after a review (a pull request) or at least a self-check.

**Commands, step by step:**

```bash
# 1. start from the latest main
git switch main
git pull

# 2. one branch per task
git switch -c feature/cart-page

# 3. work, in small commits
git add cart.html
git commit -m "Add cart page"
git add cart.css
git commit -m "Style the cart"

# 4. publish the branch
git push -u origin feature/cart-page

# 5. open a pull request on GitHub, get a review, click Merge
#    (or, without GitHub, merge locally:)
git switch main
git pull
git merge --no-ff feature/cart-page
git push

# 6. clean up
git branch -d feature/cart-page
git push origin --delete feature/cart-page
```

Meanwhile Ravi does the same for `feature/search` on his own branch. The two never disturb each other until merge time.

| ✅ Good | ❌ Bad |
|---|---|
| `main` stays clean and releasable. | Long-lived branches drift away from `main` and merge painfully. |
| Easy code review via pull requests. | You still need discipline in naming and cleaning up. |
| Work in parallel with little interference. | No rules for releases and hotfixes (see Git Flow). |

**Use it when:** a small to medium team wants a safe, simple default. This is the **foundation** that workflows 3 to 5 build on.

---

## Workflow 3 · GitHub Flow

**The idea:** Feature Branch plus two strong rules: **(1) anything in `main` is deployable**, and **(2) every change goes through a pull request**, then is deployed quickly. It is a continuous loop with no `develop` branch and no release branches.

**Everyday example:** a food-delivery kitchen. Each order (change) is prepared, checked by the manager (review + tests), and goes out the door immediately. Nothing waits for a "menu launch day".

```{raw} html
:file: ../diagrams/g10-githubflow.html
```

**The six steps:**

| # | Step | Detail |
|---|---|---|
| 1 | **Branch** off `main` | with a descriptive name |
| 2 | **Commit** | small steps, pushed often |
| 3 | **Open a pull request** | opens the conversation early (a *draft PR* is fine) |
| 4 | **Review + automated tests** | CI must pass; at least one approval |
| 5 | **Merge** into `main` | usually *Squash and merge* |
| 6 | **Deploy** | automatically, or by a button |

**Commands:**

```bash
git switch main && git pull
git switch -c fix/payment-rounding
# ... fix, commit ...
git push -u origin fix/payment-rounding
# open PR → CI runs → teammate approves → Squash and merge → auto-deploy
git switch main && git pull
git branch -d fix/payment-rounding
```

**Protect `main`** (Settings → Branches): require a PR, one approval, and passing checks. Then the rule "main is always deployable" is enforced by the machine.

**A bug in production?** There is no special "hotfix" process. It is just another branch: `fix/...` → PR → merge → deploy, only faster. If a deploy goes wrong, revert the PR (`git revert`) and ship again.

| ✅ Good | ❌ Bad |
|---|---|
| Very simple: one long-lived branch. | Assumes you can deploy continuously. |
| Fast feedback and releases. | Not suited to maintaining several released versions at once. |
| Works well with CI/CD. | Needs reliable automated tests to be safe. |

**Use it when:** you ship a web app or service and release whenever something is ready. It is the **most common choice for modern web teams**.

---

## Workflow 4 · Git Flow

**The idea:** a **structured** workflow with **five kinds of branches**, designed for software that ships in **numbered versions** (v1.0, v1.1, v2.0), like desktop apps, mobile apps or libraries. It was published by Vincent Driessen in 2010.

**Everyday example:** a publisher of printed books. Authors write new chapters in a *draft* (develop). When enough is ready, the editor prepares an *edition* (release branch), proofreads it and fixes only typos. The finished edition becomes the official printed copy (main). If a serious error is found after printing, a quick *errata correction* (hotfix) is made.

```{raw} html
:file: ../diagrams/g10-gitflow.html
```

| Branch | Lives | Purpose | Branches from | Merges into |
|---|---|---|---|---|
| **`main`** | forever | only **released** code; every commit is a release, tagged `v1.0` | none | none |
| **`develop`** | forever | integration of finished features, "next release in progress" | `main` | none |
| **`feature/*`** | days to weeks | one feature | `develop` | `develop` |
| **`release/*`** | days | stabilise the next version: bug fixes only, no new features | `develop` | `main` **and** `develop` |
| **`hotfix/*`** | hours | urgent fix to production | `main` | `main` **and** `develop` |

**Commands** (plain Git; no extra tool needed):

```bash
# --- set up once ---
git switch -c develop main
git push -u origin develop

# --- a feature ---
git switch develop
git switch -c feature/cart-page
# ... commits ...
git switch develop
git merge --no-ff feature/cart-page
git branch -d feature/cart-page

# --- prepare a release ---
git switch -c release/1.1.0 develop
# ... only bug fixes, version bump ...
git switch main
git merge --no-ff release/1.1.0
git tag -a v1.1.0 -m "Release 1.1.0"
git switch develop
git merge --no-ff release/1.1.0         # carry the release fixes back
git branch -d release/1.1.0

# --- an urgent production fix ---
git switch -c hotfix/1.1.1 main
# ... fix ...
git switch main
git merge --no-ff hotfix/1.1.1
git tag -a v1.1.1 -m "Hotfix 1.1.1"
git switch develop
git merge --no-ff hotfix/1.1.1
git branch -d hotfix/1.1.1
```

:::{note}
There is also a helper tool called `git-flow` (`git flow feature start cart-page`) that wraps these steps. It is optional. Understanding the plain commands above matters more.
:::

| ✅ Good | ❌ Bad |
|---|---|
| Clear roles for every branch. | **Heavy**: many branches and merges. |
| Supports several released versions and scheduled releases. | Slow feedback; features sit in `develop` waiting for a release. |
| `main` always shows what is in production. | Merge conflicts grow with long-lived branches. |
| | Poor fit for continuous deployment; even its author now says to prefer simpler flows for web apps. |

**Use it when:** you ship **versioned releases** and must maintain older versions (mobile apps, installable software, libraries, regulated products).
**Avoid it when:** you deploy a web app several times a day. Use GitHub Flow or trunk-based instead.

---

## Workflow 5 · Forking Workflow

**The idea:** nobody except the maintainers can push to the **official repository**. Instead, every contributor makes **their own server-side copy (a fork)**, works there, and sends a **pull request** to the official repo. This is how open source works.

**Everyday example:** a famous recipe book. You are not allowed to write in the original. You photocopy it, improve a recipe in your copy, and mail the improved page to the author, who decides whether to include it.

```{raw} html
:file: ../diagrams/g08-fork-pr.html
```

**Why it exists:** a popular project may have thousands of contributors. You cannot give thousands of strangers write access. With forks, **trust is in the pull request**, not in permissions.

**Commands:** (you practised these in Session 8)

```bash
git clone git@github.com:YOU/project.git        # your fork
git remote add upstream git@github.com:OWNER/project.git
git switch -c fix/typo
# ... commit ...
git push -u origin fix/typo                      # to YOUR fork
# open a PR: YOU/project:fix/typo → OWNER/project:main

# stay in sync with the original
git fetch upstream
git switch main
git merge upstream/main
git push origin main
```

| ✅ Good | ❌ Bad |
|---|---|
| Safe for projects with strangers. | Extra setup: forks, two remotes, syncing. |
| Maintainers keep full control. | Forks can fall behind and need regular syncing. |
| Contributors need no permission. | Slower for a team that already trusts each other. |

**Use it when:** open-source projects, or companies that accept contributions from outside teams.
**Avoid it when:** a small team that all have write access (use Feature Branch or GitHub Flow instead).

---

## Workflow 6 · Trunk-Based Development

**The idea:** the opposite of long-lived branches. Everyone integrates their work into **one shared branch, the trunk (`main`)**, **at least once a day**, in very small steps. If a branch exists at all, it lives for hours. Unfinished features are hidden behind **feature flags** (an `if` in the code that switches a feature on or off), so incomplete work can ship safely without users seeing it.

**Everyday example:** a team writing one shared document live, in small edits. Nobody keeps a private draft for a month and then dumps it on everyone.

```{raw} html
:file: ../diagrams/g10-trunk.html
```

**What makes it work:**

* very fast, reliable **automated tests** (CI) on every commit,
* **small commits** (usually under a day of work),
* **feature flags** to hide unfinished work,
* quick **code review** (or pair programming),
* the trunk is **always releasable**.

**Commands (a typical day):**

```bash
git switch main && git pull --rebase       # start from the newest trunk
git switch -c small-change                 # short-lived branch (optional)
# ... a few hours of work ...
git add -p && git commit -m "Add cart button behind flag cart_v2"
git pull --rebase                          # replay my commit on the newest trunk
git push                                   # to a short PR, or straight to main if the team allows
```

Because everyone integrates constantly, there are **very few merge conflicts**, and each is tiny. This is the style Google and many large companies use.

| ✅ Good | ❌ Bad |
|---|---|
| Fewer, smaller conflicts. | Needs mature CI, tests and discipline. |
| Always integrated and fast to release. | Feature flags add complexity. |
| Encourages small, safe changes. | Hard for beginners or teams without tests. |

**Use it when:** strong test automation and a culture of small changes (and often continuous deployment).
**Avoid it when:** your tests are weak, or contributors are untrusted or rarely online.

---

## Putting them side by side

| | Centralized | Feature Branch | GitHub Flow | Git Flow | Forking | Trunk-Based |
|---|---|---|---|---|---|---|
| Long-lived branches | 1 | 1 | 1 | 2 (`main`, `develop`) | 1 per repo | 1 |
| Branch lifetime | none | days | days | days to weeks | days | hours |
| Pull requests | no | optional | **yes** | optional | **yes (across forks)** | optional / short |
| Release style | any | any | continuous | **versioned** | any | continuous |
| Complexity | ⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ (needs automation) |
| Typical users | solo, tiny | small teams | web teams | app/library vendors | open source | big-tech, mature CI |

## How to choose

```{raw} html
:file: ../diagrams/g10-choose.html
```

**Questions to ask your team:**

1. *How do we ship?* A numbered version on a schedule points to Git Flow. Continuously points to GitHub Flow or trunk-based.
2. *Who contributes?* Strangers points to forking.
3. *How good are our automated tests?* Weak tests rule out trunk-based and make GitHub Flow risky.
4. *How big is the team?* Tiny can stay centralized; growth needs branches and reviews.
5. *Do we support old versions?* If yes, you need release branches (Git Flow or a simplified form).

:::{important}
**These are starting points, not laws.** Real teams mix them: *GitHub Flow with a protected `main`, squash merges and weekly release tags* is a very common hybrid. The best workflow is the **simplest one that your team follows consistently**. Write it down in `CONTRIBUTING.md` so newcomers know it.
:::

## Rules that apply to every workflow

* Pull the latest changes **before** you start and **before** you push.
* Keep commits small and messages meaningful.
* Never rewrite shared history (`push --force` on shared branches).
* Review changes before they reach the main line.
* Delete branches after merging.
* Tag releases (`v1.2.0`).

## Common mistakes

| Mistake | Fix |
|---|---|
| Picking Git Flow for a small web app "because it is famous" | Start with GitHub Flow. Add complexity only when needed. |
| A "feature branch" that lives for two months | Break the work into smaller pieces; merge pieces behind a flag. |
| Everybody has a different idea of the workflow | Write it in `CONTRIBUTING.md`; enforce with branch protection. |
| Using `develop` and `main` but forgetting to merge hotfixes back into `develop` | The bug returns in the next release. Merge hotfixes into **both**. |
| No tests but trying trunk-based | Add automated tests first. |

## Tryouts

**Tryout 1 · Match.** For each team, name the best-fitting workflow and give one reason:
(a) a student writing a project alone; (b) a startup deploying a website ten times a day with CI; (c) a company shipping a mobile app version every six weeks and supporting two old versions; (d) a community project with hundreds of volunteers.

<details class="solution">
<summary>Answer</summary>

(a) **Centralized**: no one to coordinate with. (b) **GitHub Flow** (or trunk-based if tests are excellent): continuous deployment and PRs. (c) **Git Flow**: scheduled versioned releases and hotfixes for old versions. (d) **Forking**: strangers cannot have write access, so contributions arrive as PRs from forks.

</details>

**Tryout 2 · Explain.** In Git Flow, why must a `hotfix/*` branch be merged into **both** `main` and `develop`?

<details class="solution">
<summary>Answer</summary>

Merging into `main` fixes production now. `develop` holds the *next* release. If you skip it, the next release (built from `develop`) will **reintroduce the bug**.

</details>

**Tryout 3 · Write.** Write a 6-line `CONTRIBUTING.md` for your own project describing its workflow: the branch rules, how to name branches, how to open a PR and who merges.

<details class="solution">
<summary>Answer</summary>

One example:

```text
# Contributing
1. `main` is always deployable. Never push to it directly.
2. Branch from main: feature/<short-name> or bugfix/<short-name>.
3. Keep PRs small and open them early (draft is fine).
4. A PR needs 1 approval and passing tests before merging.
5. Merge with "Squash and merge", then delete the branch.
6. Releases are tagged vMAJOR.MINOR.PATCH by the maintainer.
```

</details>

## Recap

* ✅ A **workflow** is the team's agreement on *how to use* Git, not a Git feature.
* ✅ **Centralized**: everyone on `main`. **Feature Branch**: one branch per task. **GitHub Flow**: feature branch + PR + deploy often.
* ✅ **Git Flow**: `main`, `develop`, `feature`, `release`, `hotfix`, for versioned releases.
* ✅ **Forking**: contributors work on their own copies and send PRs (open source).
* ✅ **Trunk-based**: tiny, frequent commits to one trunk, with feature flags and strong CI.
* ✅ Choose by **how you release, who contributes, how good your tests are and how big the team is**. Keep it simple and write it down.

**Next:** [Session 11 · Workflows Hands-On](11-workflows-hands-on.md).
