# Session 8 · Collaborating: Pull Requests, Forks and Reviews

**⏱ about 75 minutes · 🧰 you need: [Session 7](07-remotes-and-github.md) done**

## The big idea

When many people work on one project, nobody should be able to change the main code unchecked. A **pull request** (PR) is a polite request: *"I finished this work on my branch. Please review it, and if it is good, merge it into `main`."*

**Everyday example:** a newspaper. Reporters do not print directly. They hand the article to an editor, who reads it, leaves comments ("check this number"), and approves it. The pull request is the hand-over, the comments are the review, and the approval plus merge is the publication.

Pull requests are **not a Git feature**. They are a feature of GitHub, GitLab and similar websites, built on top of branches. (GitLab calls them *merge requests*.)

## 1. The life of a pull request

```{raw} html
:file: ../diagrams/g08-pr-flow.html
```

| Step | What you do | Command / place |
|---|---|---|
| 1 Branch | start from an up-to-date `main` | `git switch main && git pull && git switch -c feature/x` |
| 2 Commit | small, clear commits | `git add` / `git commit` |
| 3 Push | publish the branch | `git push -u origin feature/x` |
| 4 Open PR | ask for review | GitHub → *Compare & pull request* |
| 5 Review | teammates comment, you fix and push again | same branch; the PR updates itself |
| 6 Merge | click *Merge*, then delete the branch | GitHub |

## 2. Try it: your first pull request

In your `hello-git` repo (from Session 7):

```bash
cd ~/git-lab/hello-git
git switch main
git pull
git switch -c feature/add-greeting
echo "def greet(name):" > greet.py
echo "    return f'Hello, {name}!'" >> greet.py
git add greet.py
git commit -m "Add greet function"
git push -u origin feature/add-greeting
```

Git prints a link such as `https://github.com/you/hello-git/pull/new/feature/add-greeting`. Open it (or visit the repo, where GitHub shows a yellow **Compare & pull request** button).

### Writing a good PR

| Field | What to write |
|---|---|
| **Title** | one line, like a commit message: *Add greet function* |
| **Description** | what changed, **why**, how to test it, and a link to the issue (`Closes #12` auto-closes issue 12 on merge) |
| **Reviewers** | pick one or two teammates |
| **Draft** | tick "Create draft" if it is not ready; reviewers will wait |

A useful template:

```text
## What
Adds a greet() helper.

## Why
The signup page needs a friendly message (Closes #12).

## How to test
python -c "import greet; print(greet.greet('Asha'))"
```

Keep PRs **small**. A PR with 50 changed lines gets a careful review; one with 2,000 gets "looks fine".

## 3. Reviewing a PR

On the **Files changed** tab, hover over a line and click **+** to comment. Reviewers finish with one of three verdicts:

| Verdict | Meaning |
|---|---|
| **Comment** | feedback only |
| **Approve** | good to merge |
| **Request changes** | must be fixed first |

If changes are requested, you do **not** open a new PR. Just commit and push to the same branch:

```bash
# fix what was asked
git add greet.py
git commit -m "Handle empty name in greet"
git push
```

The PR updates itself.

**How to review well (be kind and specific):** ask questions instead of giving orders ("What happens if `name` is empty?"); separate *must-fix* from *nice-to-have*; praise good work; check that tests exist.

## 4. Three ways to merge a PR

On the green button's drop-down, GitHub offers:

| Option | Result in `main` | Best for |
|---|---|---|
| **Create a merge commit** | all your commits + one merge commit | keeping full history |
| **Squash and merge** | all commits squashed into **one** | tidy history; messy "wip" commits disappear |
| **Rebase and merge** | your commits replayed one by one, no merge commit | a perfectly straight history |

Many teams pick **Squash and merge** as the default.

After merging, tidy up:

```bash
git switch main
git pull
git branch -d feature/add-greeting          # delete the local branch
git push origin --delete feature/add-greeting   # (GitHub has a "Delete branch" button too)
```

## 5. Protecting `main`

Team leads usually set **branch protection** (Repo → Settings → Branches): require a pull request, require at least one approval, require tests (CI) to pass, and block force-pushes. Then *nobody* can push straight to `main`, even by accident.

## 6. Forks: contributing to a project you do not own

In an open-source project you usually cannot push to the owner's repo. Instead you make **your own copy** on GitHub, a **fork**, work there, and ask the owner to take your changes.

**Everyday example:** you like a friend's recipe book. You photocopy the book (fork), improve a recipe in *your* copy, and then show your friend the improved page (pull request).

```{raw} html
:file: ../diagrams/g08-fork-pr.html
```

```bash
# 1. On GitHub click Fork (top right). You now own  you/project.
# 2. Clone YOUR fork
git clone git@github.com:YOU/project.git
cd project

# 3. Add the original as a second remote, usually named "upstream"
git remote add upstream git@github.com:OWNER/project.git
git remote -v

# 4. Work on a branch and push it to YOUR fork
git switch -c fix/typo-in-readme
# ... edit, add, commit ...
git push -u origin fix/typo-in-readme

# 5. On GitHub open a pull request from your fork's branch to OWNER's main
```

### Keeping your fork up to date

The owner's `main` keeps moving while you work. Bring those changes into your copy:

```bash
git switch main
git fetch upstream
git merge upstream/main          # or: git pull upstream main
git push origin main             # update your fork on GitHub
```

| Remote name | Points to |
|---|---|
| `origin` | **your fork** (you can push) |
| `upstream` | **the original project** (usually read-only for you) |

## 7. Issues and good collaboration habits

* **Issues** are GitHub's to-do items and bug reports. Reference them from commits and PRs: `Fixes #34`.
* **Labels / milestones / projects** organise work; **assignees** say who owns it.
* Pull `main` **before** you branch; keep your branch updated with `git merge main` (or rebase, Session 9).
* Write a short **CONTRIBUTING.md** and a **README.md** so newcomers know the rules.
* **Review within a day** if you can. Waiting PRs are the most expensive thing in a team.
* Never commit secrets. Use environment variables and `.gitignore`.

## Common mistakes

| Mistake | Fix |
|---|---|
| Working directly on `main` and then wanting a PR | Create a branch from where you are: `git switch -c feature/x`, then reset `main` (Session 12). |
| Opening a **new** PR for review fixes | Push to the same branch; the PR updates itself. |
| Giant PRs with unrelated changes | Split them: one purpose per PR. |
| Forgetting to sync a fork, so the PR has conflicts | `git fetch upstream` then `git merge upstream/main` first. |
| Merging your own PR without review in a team repo | Use branch protection to prevent it. |

## Hands-on exercises

**Tryout 1 · Open a PR.** Create a branch `feature/readme-badges`, change `README.md`, push, and open a pull request on GitHub (you can review and merge your own PR on your personal repo for practice).

<details class="solution">
<summary>Answer</summary>

```bash
git switch -c feature/readme-badges
echo "Built with Git and GitHub." >> README.md
git commit -am "Add a note to the readme"
git push -u origin feature/readme-badges
```

Open the *Compare & pull request* button, write a description, click **Create pull request**, then **Squash and merge**.

</details>

**Tryout 2 · Review round.** In your PR, add a comment on a line from the **Files changed** tab, then push a second commit that addresses it. Confirm the PR shows both commits and **no new PR** was needed.

<details class="solution">
<summary>Answer</summary>

Make the change, then `git commit -am "Address review comment"` and `git push`. Open the PR's **Commits** tab: both commits are listed.

</details>

**Tryout 3 · Fork.** Fork any small public repo (for example `octocat/Spoon-Knife`), clone **your fork**, add `upstream`, and list your remotes.

<details class="solution">
<summary>Answer</summary>

```bash
git clone git@github.com:YOU/Spoon-Knife.git
cd Spoon-Knife
git remote add upstream git@github.com:octocat/Spoon-Knife.git
git remote -v
```

You should see both `origin` (your fork) and `upstream` (the original), each with fetch and push lines.

</details>

## Recap

* ✅ A **pull request** asks for your branch to be reviewed and merged. It is a GitHub feature built on branches.
* ✅ Flow: branch → commit → push → open PR → review → merge → delete branch.
* ✅ Fix review comments by pushing more commits to the **same branch**.
* ✅ Merge styles: merge commit, **squash**, or rebase.
* ✅ A **fork** is your own copy of someone else's repo. Remotes: `origin` = your fork, `upstream` = the original.

**Next:** [Session 9 · Power Tools](09-power-tools.md).
