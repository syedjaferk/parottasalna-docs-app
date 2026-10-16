# Session 12 · Rescue Missions and Good Habits

**⏱ about 90 minutes · 🧰 you need: [Session 11](11-workflows-hands-on.md) done**

## The big idea

Everyone eventually makes a Git mistake: committing on the wrong branch, pushing a password, getting lost in a strange `detached HEAD` message. Experts are not people who never make mistakes. They know that **Git almost never loses committed work**, so they stay calm and follow a recipe.

**Everyday example:** a first-aid kit. You hope you never open it, but when you need it, you want to know where each item is and what it does.

## The calm-down checklist

When something looks wrong, **stop and run these three commands** before anything else. They change nothing:

```bash
git status                     # where am I? what is changed?
git log --oneline --graph --all -10    # what does history look like?
git reflog -10                 # where has HEAD been? (the safety net)
```

:::{important}
**Three rules for stressful moments:** (1) don't run commands you don't understand; (2) before anything risky, make a backup branch with `git branch backup-before-fix`, which costs nothing; (3) committed work can nearly always be recovered. Uncommitted edits cannot.
:::

---

## Rescue 1 · "I committed on `main` instead of a branch"

You meant to work on `feature/x`, but you are on `main` and have made a commit that has **not been pushed**.

```bash
git branch feature/x           # new branch label on your current commit (keeps the work)
git reset --hard origin/main   # move main back to where the remote is (or HEAD~1 for one commit)
git switch feature/x           # carry on there
```

The commit is safe on `feature/x`, and `main` is clean again. (If you have *no* remote, use `git reset --hard HEAD~1` instead of `origin/main`.)

---

## Rescue 2 · "I am in 'detached HEAD' state"

```text
You are in 'detached HEAD' state. You can look around, make experimental
changes and commit them, but they will not belong to any branch...
```

**What it means.** `HEAD` normally points at a branch. Here it points straight at a *commit* (for example after `git switch --detach v1.0.0` or `git checkout <id>`). New commits on it belong to **no branch**, and will be lost when you switch away.

**Just looking?** Return to your branch: `git switch main`.

**Made commits you want to keep?** Give them a branch name **now**:

```bash
git switch -c rescue-branch
```

---

## Rescue 3 · "I deleted a branch / lost commits"

```bash
git reflog
```

```text
a1b2c3d HEAD@{0}: checkout: moving from feature/login to main
f4e5d6c HEAD@{1}: commit: Add login validation
```

Find the last commit of the lost work (`f4e5d6c`) and bring it back:

```bash
git switch -c feature/login-restored f4e5d6c
```

---

## Rescue 4 · "My merge went wrong"

| Situation | Fix |
|---|---|
| Still **in the middle** of a conflicted merge and want out | `git merge --abort` |
| Merge **finished** but not pushed; undo it | `git reset --hard ORIG_HEAD` (Git remembers where you were before the merge) |
| Merge **already pushed**; undo it safely | `git revert -m 1 <merge-commit-id>` |

For a **merge commit**, `revert` needs `-m 1` to say *"keep parent 1 (the main line, usually `main`) and undo the side branch"*.

```bash
git log --oneline --graph -5          # find the merge commit
git revert -m 1 e1e1e1e
```

:::{note}
If you later want that branch back in, you must "revert the revert" first. Otherwise Git thinks it is already merged.
:::

---

## Rescue 5 · "I pushed a secret (password, API key)"

Deleting the file in a new commit **does not help**. The secret is still in the history, and bots scan GitHub within minutes.

**Do these in order:**

1. **Revoke / rotate the secret immediately** (change the password, delete the API key, and create a new one). Assume it is already stolen. *This is the only step that truly fixes it.*
2. Remove it from the current code and add the file to `.gitignore`. Store secrets in environment variables or a `.env` file that is **not** committed.
3. If you also want to scrub the history, use a purpose-built tool such as [`git filter-repo`](https://github.com/newren/git-filter-repo) or BFG Repo-Cleaner on a fresh clone, then force-push. Tell your team to re-clone. (Rewriting history is disruptive, so the rotation in step 1 matters more.)

```bash
# prevention: keep secrets out from the start
echo ".env" >> .gitignore
git rm --cached .env           # stop tracking it, keep the file on disk
git commit -m "Stop tracking .env"
```

---

## Rescue 6 · "I committed a huge or wrong file"

Not pushed yet? Simply amend:

```bash
git rm --cached big-video.mp4
git commit --amend --no-edit
```

Already pushed and large? Use the same history-rewriting tools as in Rescue 5, and consider **Git LFS** (Large File Storage) for big binaries in the future.

---

## Rescue 7 · "Wrong author name or email on my commits"

Last commit only:

```bash
git commit --amend --author="Asha Kumar <asha@example.com>" --no-edit
```

For all future commits: fix `git config --global user.name/user.email`.

---

## Rescue 8 · "Which commit broke it?" (`git bisect`)

The app worked last week and is broken today, with 40 commits in between. Instead of reading all 40, **bisect** does a binary search through history. It checks the middle commit, you say good or bad, it halves the range, and in about 6 steps (for 40 commits) it names the culprit.

Create a practice repo with a hidden bug:

```bash
cd ~/git-lab
mkdir bisect-lab && cd bisect-lab
git init
for i in 1 2 3 4 5 6 7 8; do
  echo "step $i" > progress.txt
  [ $i -ge 5 ] && echo "BUG" > bug.txt        # the bug appears at commit 5
  git add . && git commit -m "Change $i"
done
git log --oneline
```

Now find it, manually:

```bash
git bisect start
git bisect bad                    # the current commit is broken
git bisect good HEAD~7            # the first commit was fine
```

```text
Bisecting: 3 revisions left to test after this (roughly 2 steps)
[...] Change 4
```

Test the checked-out version (here: does `bug.txt` exist?), and tell Git:

```bash
ls bug.txt            # No such file → good
git bisect good
ls bug.txt            # exists → bad
git bisect bad
```

```text
<commit-id> is the first bad commit
commit <commit-id>
    Change 5
```

Finish with `git bisect reset` to return to where you started.

**Automatic mode:** give Git a command that exits `0` for good and non-zero for bad, and it does all the steps:

```bash
git bisect start HEAD HEAD~7
git bisect run sh -c '! test -f bug.txt'
git bisect reset
```

In real projects the command is usually your test suite: `git bisect run npm test`.

---

## Rescue 9 · "I need to throw everything away and match the server"

```bash
git fetch origin
git reset --hard origin/main      # DANGER: discards local commits and edits
git clean -n                      # dry run: list untracked files that would go
git clean -fd                     # actually delete them
```

Use it only when you are certain none of your local work matters. When in doubt, `git branch backup` first.

---

## Good habits that prevent most problems

### 1 · Commit small and often

One logical change per commit. Easy to review, easy to revert, easy to find with bisect.

### 2 · Write messages for humans

```text
Fix wrong total when a coupon is applied

The coupon was subtracted before tax instead of after, so orders
over 1000 rupees were undercharged. Fixes #87.
```

Subject line: imperative, about 50 characters, no full stop. Blank line. Then *why*. Some teams use **Conventional Commits**: a prefix such as `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:` (`feat: add wishlist page`), which makes changelogs and version bumps automatic.

### 3 · Pull before you start, check before you commit

```bash
git pull
git status
git diff --staged
```

### 4 · Never rewrite shared history

No `push --force` on `main` or on branches others use. If you must, use `--force-with-lease`.

### 5 · Keep branches short and delete them when merged

```bash
git branch --merged main            # branches safe to delete
git branch -d feature/old
git fetch --prune                   # forget remote branches that were deleted
```

### 6 · Use aliases to save typing

```bash
git config --global alias.st "status -sb"
git config --global alias.lg "log --oneline --graph --all --decorate"
git config --global alias.last "log -1 HEAD --stat"
git config --global alias.unstage "restore --staged"
```

Now `git st`, `git lg`, `git last` and `git unstage file` work everywhere.

### 7 · Add a good `.gitignore` from day one

GitHub offers templates for each language when you create a repo. See also [gitignore.io](https://www.toptal.com/developers/gitignore) for combinations.

### 8 · Automate checks with hooks

A **hook** is a script Git runs for you at a moment such as before each commit. Create `.git/hooks/pre-commit` (and make it executable) to block commits that contain leftover debug text:

```bash
cat > .git/hooks/pre-commit <<'EOF'
#!/bin/sh
if git diff --cached | grep -n "console.log\|TODO-REMOVE"; then
  echo "Remove debug lines before committing."
  exit 1
fi
EOF
chmod +x .git/hooks/pre-commit
```

(Hooks in `.git/` are not shared through the repo. Teams usually use a tool such as *pre-commit* or *husky* to share them.)

### 9 · Protect `main` and review everything

Branch protection plus pull requests catch mistakes **before** they reach everyone.

### 10 · Document the workflow

A `README.md` (what is this, how to run it) and a `CONTRIBUTING.md` (how we use Git) save hours for every newcomer.

## Where to go next

* Practise on a real project: contribute a small fix to an open-source repo.
* Learn **GitHub Actions** (CI/CD): run your tests on every push.
* Read about **signed commits**, **submodules**, **worktrees** (`git worktree add`) and **sparse checkout**.
* Skim the official book, *Pro Git*, free at [git-scm.com/book](https://git-scm.com/book).
* Keep the **[Cheatsheet](../cheatsheet.md)** nearby.

## Common mistakes

| Mistake | Fix |
|---|---|
| Panic-typing commands from a forum | Run the calm-down checklist, then back up with `git branch backup`. |
| Deleting the folder and re-cloning "to fix it" | Usually unnecessary: `reflog` and `reset` are faster, and you lose unpushed work. |
| Force-pushing to fix a mistake on `main` | Use `git revert` and push normally. |
| Treating a pushed secret as fixed after deleting it | **Rotate it.** History still has it. |

## Tryouts

**Tryout 1 · Wrong branch.** In a repo on `main`, make a commit `Add feature`. Move it onto a new branch `feature/oops` and put `main` back one commit.

<details class="solution">
<summary>Answer</summary>

```bash
git branch feature/oops
git reset --hard HEAD~1
git log --oneline --all --graph
```

`feature/oops` has the commit; `main` does not.

</details>

**Tryout 2 · Detached.** Detach at a commit with `git switch --detach HEAD~1`, make a commit, then save it on a branch called `saved`.

<details class="solution">
<summary>Answer</summary>

```bash
git switch --detach HEAD~1
echo "x" > x.txt && git add . && git commit -m "Made while detached"
git switch -c saved
git log --oneline --all --graph -4
```

</details>

**Tryout 3 · Bisect.** In `bisect-lab`, use `git bisect` to find the commit where `bug.txt` first appeared. Which commit message did it name?

<details class="solution">
<summary>Answer</summary>

`Change 5`. Using the automatic form: `git bisect start HEAD HEAD~7`, then `git bisect run sh -c '! test -f bug.txt'`, then `git bisect reset`.

</details>

## Final challenge · the whole course in 15 commands

Without looking back, do this from scratch: (1) create a repo, (2) add `.gitignore`, (3) commit, (4) create `feature/x`, (5) commit twice, (6) switch to `main` and commit, (7) merge `feature/x`, (8) tag `v1.0.0`, (9) push to a bare "remote" (`git init --bare ../remote.git`; `git remote add origin ../remote.git`), (10) clone it to a second folder, (11) change a file there and push, (12) pull in the first folder, (13) undo the last commit with `revert`, (14) find the first commit with `git log --oneline`, (15) delete the merged branch.

<details class="solution">
<summary>Answer (one possible solution)</summary>

```bash
cd ~/git-lab && mkdir final && cd final
git init
printf ".env\n*.log\n" > .gitignore
git add . && git commit -m "Add gitignore"
git switch -c feature/x
echo a > a.txt && git add . && git commit -m "Add a"
echo b > b.txt && git add . && git commit -m "Add b"
git switch main
echo m > m.txt && git add . && git commit -m "Add m"
git merge feature/x -m "Merge feature/x"
git tag -a v1.0.0 -m "First release"
git init --bare ../remote.git
git remote add origin ../remote.git
git push -u origin main --tags
cd .. && git clone remote.git final-copy && cd final-copy
echo c > c.txt && git add . && git commit -m "Add c" && git push
cd ../final && git pull
git revert HEAD --no-edit
git log --oneline --reverse | head -1
git branch -d feature/x
```

</details>

## Recap

* ✅ When in trouble: `git status`, `git log --graph`, `git reflog`; then make a backup branch.
* ✅ Wrong branch: `branch` + `reset --hard`. Detached HEAD: `switch -c`. Lost commit: `reflog`.
* ✅ Bad merge: `merge --abort`, `reset --hard ORIG_HEAD`, or `revert -m 1`.
* ✅ Pushed a secret: **rotate it first**; scrub history second.
* ✅ `git bisect` finds the commit that introduced a bug.
* ✅ Habits: small commits, good messages, pull before push, never rewrite shared history, protect `main`, document the workflow.

🎓 **Congratulations.** You can now use Git confidently on your own and in a team, and you know how to choose a workflow. Keep practising on real projects.
