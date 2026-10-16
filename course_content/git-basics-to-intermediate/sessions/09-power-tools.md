# Session 9 · Power Tools: Stash, Rebase, Cherry-pick and Tags

**⏱ about 90 minutes · 🧰 you need: [Session 8](08-collaborating.md) done**

## The big idea

You now know enough Git to work in a team. This session adds four tools that separate comfortable users from beginners:

| Tool | Problem it solves | Everyday comparison |
|---|---|---|
| **stash** | "I am mid-work and need to switch tasks *now*" | putting half-written papers in a drawer |
| **rebase** | "My branch is behind `main`; I want a clean, straight history" | re-writing your edits on top of the newest version of the document |
| **cherry-pick** | "I want just *that one* commit from another branch" | photocopying one page from a colleague's notebook |
| **tag** | "Mark this exact commit as release v1.0" | a bookmark with a name on it |

## 1. `git stash`: a shelf for unfinished work

You are halfway through a change when your boss says *"urgent bug on main, fix it now!"*. Your edits are not ready to commit, and Git will not let you switch branches with conflicting changes. Stash them:

```{raw} html
:file: ../diagrams/g09-stash.html
```

```bash
cd ~/git-lab
mkdir power-lab && cd power-lab
git init
echo "version 1" > app.txt && git add . && git commit -m "Add app"

echo "half-finished idea" >> app.txt         # work in progress
git stash
```

```text
Saved working directory and index state WIP on main: 1a1a1a1 Add app
```

```bash
git status
cat app.txt
```

```text
On branch main
nothing to commit, working tree clean
version 1
```

The folder is clean. Go fix the urgent bug (`git switch -c hotfix/x`, commit, merge...). Then bring your work back:

```bash
git stash pop
```

```text
On branch main
Changes not staged for commit:
	modified:   app.txt
Dropped refs/stash@{0} (3c3c3c3...)
```

Commit it so the lab folder is clean for the later steps:

```bash
git commit -am "Add idea to app"
```

| Command | What it does |
|---|---|
| `git stash` | shelve tracked changes |
| `git stash -u` | also shelve **untracked** (new) files |
| `git stash push -m "login form WIP"` | stash with a description |
| `git stash list` | see the shelf: `stash@{0}`, `stash@{1}`... |
| `git stash pop` | bring back the newest stash **and remove it** from the shelf |
| `git stash apply` | bring it back but **keep** it on the shelf |
| `git stash show -p stash@{0}` | peek at what is inside |
| `git stash drop stash@{0}` | delete one |
| `git stash clear` | delete them all |

## 2. `git rebase`: replay your work on a newer base

When your feature branch was created, `main` was at commit 3. Since then, `main` got new work. You have two ways to catch up:

* **merge** `main` into your branch: simple and truthful, but adds a merge commit.
* **rebase** your branch onto `main`: Git lifts your commits, moves your branch to the tip of `main`, and **replays** your commits on top. The result looks like you started from the newest code all along.

```{raw} html
:file: ../diagrams/g09-rebase.html
```

Notice that `A'` and `B'` are **new commits** (new IDs) with the same changes. The old `A` and `B` are abandoned.

```bash
cd ~/git-lab
mkdir rebase-lab && cd rebase-lab
git init
echo "base" > base.txt && git add . && git commit -m "Base commit"

git switch -c feature/login
echo "login form" > login.txt && git add . && git commit -m "Add login form"

git switch main
echo "news" > news.txt && git add . && git commit -m "Add news page"

git log --oneline --graph --all
```

```text
* 7e7e7e7 (HEAD -> main) Add news page
| * 6d6d6d6 (feature/login) Add login form
|/
* 5c5c5c5 Base commit
```

Now rebase the feature branch onto `main`:

```bash
git switch feature/login
git rebase main
```

```text
Successfully rebased and updated refs/heads/feature/login.
```

```bash
git log --oneline --graph --all
```

```text
* 8f8f8f8 (HEAD -> feature/login) Add login form
* 7e7e7e7 (main) Add news page
* 5c5c5c5 Base commit
```

A straight line, with `Add login form` having a **new ID** (`8f8f8f8`). Finally merge it. It is a clean fast-forward:

```bash
git switch main
git merge feature/login
```

### If a rebase hits a conflict

It stops at the commit that conflicts, just like a merge:

```bash
# edit the file, remove the markers, then:
git add file.txt
git rebase --continue
# or give up and go back to how things were:
git rebase --abort
```

### The golden rule of rebase

:::{danger}
**Never rebase commits that other people already have** (commits pushed to a shared branch such as `main`). Rebase gives your commits new IDs; teammates who built on the old ones will be thrown into confusion. Rebase **your own, unshared** feature branches only.
:::

If you rebased a branch you already pushed (your own feature branch), the remote now disagrees, and you must update it with:

```bash
git push --force-with-lease
```

### Merge or rebase?

| | Merge | Rebase |
|---|---|---|
| History | true, branched, with merge commits | straight line |
| Old commits | unchanged | replaced by copies |
| Safe on shared branches | ✅ | ❌ |
| Conflicts | resolve **once** | may resolve **per commit** |
| Good for | integrating finished work into `main` | tidying your own branch before a PR |

A popular combination: **rebase your feature branch on `main` while you work, then merge (or squash-merge) via a pull request.**

### Interactive rebase: tidy your commits

`git rebase -i HEAD~3` opens a list of your last 3 commits so you can **reorder, squash (combine), reword or drop** them before sharing:

```text
pick 1a1a1a1 Add login form
pick 2b2b2b2 wip
pick 3c3c3c3 fix typo
```

Change `pick` to `squash` (or `s`) on the lines to fold into the one above, save, and write one good message. Useful to turn "wip, wip, fix, fix" into one clean commit. (Again: only before pushing, or on your own branch.)

## 3. `git cherry-pick`: copy one commit

Sometimes you want a single commit from another branch, not the whole branch. For example a bug fix that lives in a half-finished feature branch.

```{raw} html
:file: ../diagrams/g09-cherry.html
```

```bash
cd ~/git-lab/power-lab
git switch -c feature/big
echo "A" > a.txt && git add . && git commit -m "Add A"
echo "fix the typo" > fix.txt && git add . && git commit -m "Fix typo in header"
echo "C" > c.txt && git add . && git commit -m "Add C"
git log --oneline
```

```text
b3b3b3b (HEAD -> feature/big) Add C
a2a2a2a Fix typo in header
9f9f9f9 Add A
0e0e0e0 Add idea to app
1a1a1a1 Add app
```

Bring only the typo fix to `main`:

```bash
git switch main
git cherry-pick a2a2a2a
```

```text
[main e4e4e4e] Fix typo in header
 1 file changed, 1 insertion(+)
```

`main` now has the fix (with a **new** ID `e4e4e4e`) but not `A` or `C`.

| Command | Use |
|---|---|
| `git cherry-pick <id>` | copy one commit |
| `git cherry-pick <id1> <id2>` | copy several |
| `git cherry-pick <a>..<b>` | copy a range (after `a`, up to and including `b`) |
| `git cherry-pick --abort` / `--continue` | when it conflicts |

Use it sparingly: copied commits can cause confusing duplicates when the branches are later merged. Typical uses: **backporting a fix** to an older release branch, or rescuing a commit from the wrong branch.

## 4. Tags: bookmarks for releases

A branch label moves as you commit. A **tag** is a label that **stays put**, pointing at one commit forever. Use tags for **releases**: `v1.0.0`, `v2.3.1`.

```bash
git switch main
git tag v1.0.0                                  # lightweight tag
git tag -a v1.1.0 -m "Release 1.1.0: login"     # annotated tag (recommended: has author, date, message)
git tag
```

```text
v1.0.0
v1.1.0
```

| Command | What it does |
|---|---|
| `git tag` | list tags |
| `git tag -a v1.2.0 -m "msg"` | create an annotated tag on the current commit |
| `git tag -a v1.0.1 <commit-id> -m "msg"` | tag an older commit |
| `git show v1.1.0` | see the tag and its commit |
| `git push origin v1.1.0` | publish one tag (tags are **not** pushed automatically) |
| `git push origin --tags` | publish all tags |
| `git tag -d v1.0.0` | delete a local tag |
| `git switch --detach v1.0.0` | go and look at the code as it was in that release |

**Semantic Versioning** (`MAJOR.MINOR.PATCH`) is the common naming: `2.4.1` → bump **MAJOR** for breaking changes, **MINOR** for new features, **PATCH** for bug fixes. On GitHub, a tag can be turned into a **Release** with notes and downloads.

## Common mistakes

| Mistake | Fix |
|---|---|
| `git stash` then forgetting about it | `git stash list` regularly. Give stashes a name with `-m`. |
| New files not stashed | They are untracked: use `git stash -u`. |
| Rebasing a branch teammates are using | Do not. Merge instead. |
| `git push` rejected after rebasing your own branch | Use `git push --force-with-lease`, never plain `--force`. |
| Rebase conflict panic | `git rebase --abort` returns to the state before. |
| Tag not visible on GitHub | You forgot `git push origin <tag>` (or `--tags`). |

## Tryouts

**Tryout 1 · Stash.** In `power-lab`, edit `app.txt`, stash with the message `trying something`, confirm the folder is clean, list the stash, and pop it back.

<details class="solution">
<summary>Answer</summary>

```bash
echo "experiment" >> app.txt
git stash push -m "trying something"
git status           # clean
git stash list       # stash@{0}: On main: trying something
git stash pop
```

</details>

**Tryout 2 · Straighten.** Create `feature/footer` from `main`, commit once. Add a different commit on `main`. Rebase `feature/footer` onto `main` and show that the graph is a straight line.

<details class="solution">
<summary>Answer</summary>

```bash
git switch -c feature/footer
echo "footer" > footer.txt && git add . && git commit -m "Add footer"
git switch main
echo "header" > header.txt && git add . && git commit -m "Add header"
git switch feature/footer
git rebase main
git log --oneline --graph --all
```

</details>

**Tryout 3 · Release.** Tag the current commit `v1.0.0` (annotated), then add a commit and tag `v1.0.1`. Use `git log --oneline --decorate` to see both tags.

<details class="solution">
<summary>Answer</summary>

```bash
git switch main
git tag -a v1.0.0 -m "First release"
echo "bugfix" >> app.txt && git commit -am "Fix a bug"
git tag -a v1.0.1 -m "Patch release"
git log --oneline --decorate -3
```

</details>

## Recap

* ✅ **stash** shelves unfinished work (`stash`, `stash -u`, `stash list`, `stash pop`).
* ✅ **rebase** replays your commits on top of a newer base for a straight history. Only on commits not yet shared.
* ✅ `rebase -i` lets you squash and reword commits before you share them.
* ✅ **cherry-pick** copies a single commit onto the current branch.
* ✅ **tags** permanently mark releases (`git tag -a v1.0.0 -m "..."`, `git push origin --tags`).

**Next:** [Session 10 · Git Workflows](10-git-workflows.md).
