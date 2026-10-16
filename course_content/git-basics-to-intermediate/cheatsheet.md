# Git Cheatsheet

Keep this open while you practise. Each group links to the session that teaches it.

## The picture to remember

```{raw} html
:file: diagrams/g02-areas.html
```

## Set up (Session 1, Setup)

| Command | What it does |
|---|---|
| `git config --global user.name "Name"` | your name on commits |
| `git config --global user.email "me@x.com"` | your email on commits |
| `git config --global init.defaultBranch main` | new repos start on `main` |
| `git config --global --list` | show your settings |
| `git help <command>` / `git <command> -h` | manual / short help |

## Start a repository (Session 2)

| Command | What it does |
|---|---|
| `git init` | make the current folder a repository |
| `git clone <url> [folder]` | download a repository |
| `git status` / `git status -s` | what is changed? (long / short) |
| `git add <file>` / `git add .` / `git add -p` | stage a file / everything / piece by piece |
| `git commit -m "message"` | save the staged changes |
| `git commit -am "message"` | stage modified tracked files and commit |

## Look around (Session 3)

| Command | What it does |
|---|---|
| `git log --oneline` | one line per commit |
| `git log --oneline --graph --all` | draw all branches |
| `git log -p` / `--stat` | with full changes / file summary |
| `git log --author="x"` / `--grep="x"` / `--since="2 days ago"` | filter history |
| `git show <commit>` | one commit in detail |
| `git diff` | unstaged changes |
| `git diff --staged` | what the next commit will contain |
| `git diff HEAD` | all changes since last commit |
| `git diff <a> <b>` | between two commits |
| `git blame <file>` | who changed each line |
| `git ls-files` | files Git tracks |

`HEAD` = current commit · `HEAD~1` = one before · `HEAD~3` = three before.

## Ignore files (Session 3)

```text
.env          # one file
*.log         # by pattern
logs/         # a folder
!keep.log     # exception
```

Already tracked? `git rm --cached <file>`.

## Undo (Session 4)

| Situation | Command |
|---|---|
| Discard edits in a file | `git restore <file>` |
| Un-stage a file | `git restore --staged <file>` |
| Fix the last commit (message / forgotten file) | `git commit --amend` |
| Undo commit, keep changes staged | `git reset --soft HEAD~1` |
| Undo commit, keep changes unstaged | `git reset HEAD~1` |
| Undo commit and discard changes | `git reset --hard HEAD~1` |
| Safely undo a **pushed** commit | `git revert <commit>` |
| Find lost commits | `git reflog` |
| Delete untracked files (dry run first) | `git clean -n` then `git clean -f` |
| Remove / rename a tracked file | `git rm <f>` / `git mv <old> <new>` |

## Branches (Session 5)

| Command | What it does |
|---|---|
| `git branch` / `git branch -a` | list local / all branches |
| `git switch <name>` | go to a branch |
| `git switch -c <name>` | create and go to a branch |
| `git switch -` | go back to the previous branch |
| `git branch -m <old> <new>` | rename |
| `git branch -d <name>` / `-D` | delete (safe / force) |
| `git branch --merged` | branches already merged (safe to delete) |

## Merge and conflicts (Session 6)

| Command | What it does |
|---|---|
| `git merge <branch>` | bring `<branch>` into the current branch |
| `git merge --no-ff <branch>` | always create a merge commit |
| `git merge --squash <branch>` | stage all its changes as one; you commit |
| `git merge --abort` | cancel a merge in progress |

**Resolve a conflict:** edit the file → remove `<<<<<<<`, `=======`, `>>>>>>>` → `git add <file>` → `git commit`.

## Remotes (Session 7)

| Command | What it does |
|---|---|
| `git remote -v` | list remotes |
| `git remote add origin <url>` | link a remote |
| `git remote set-url origin <url>` | change its URL |
| `git push -u origin <branch>` | first push; sets upstream |
| `git push` / `git pull` | share / catch up (pull = fetch + merge) |
| `git fetch` | download only, change nothing |
| `git push origin --delete <branch>` | delete a remote branch |
| `git fetch --prune` | forget deleted remote branches |
| `git push --force-with-lease` | the **safer** force-push (own branches only) |

## Pull requests and forks (Session 8)

| Step | Command / place |
|---|---|
| Branch | `git switch main && git pull && git switch -c feature/x` |
| Publish | `git push -u origin feature/x` |
| Open PR | GitHub → *Compare & pull request* |
| Update PR | commit + `git push` on the same branch |
| Clean up | `git switch main && git pull && git branch -d feature/x` |
| Fork setup | `git remote add upstream <original-url>` |
| Sync fork | `git fetch upstream && git merge upstream/main` |

## Power tools (Session 9)

| Command | What it does |
|---|---|
| `git stash` / `git stash -u` | shelve changes (and untracked files) |
| `git stash list` / `pop` / `apply` / `drop` | manage the shelf |
| `git rebase main` | replay my branch on top of `main` |
| `git rebase -i HEAD~3` | tidy the last 3 commits |
| `git rebase --continue` / `--abort` | during a rebase conflict |
| `git cherry-pick <commit>` | copy one commit here |
| `git tag -a v1.0.0 -m "msg"` | annotated tag on this commit |
| `git push origin --tags` | publish tags |

:::{warning}
**Rebase, amend, reset and force-push rewrite history. Use them only on commits nobody else has.**
:::

## Workflows at a glance (Sessions 10 and 11)

| Workflow | Remember it as | Main branches |
|---|---|---|
| **Centralized** | everyone on `main` | `main` |
| **Feature Branch** | a branch per task | `main` + `feature/*` |
| **GitHub Flow** | feature branch + PR + deploy | `main` + short branches |
| **Git Flow** | versioned releases | `main`, `develop`, `feature/*`, `release/*`, `hotfix/*` |
| **Forking** | PRs from your own copy | upstream + your fork |
| **Trunk-based** | tiny commits, feature flags | `main` only |

## Rescue (Session 12)

| Problem | First aid |
|---|---|
| Lost? | `git status`, `git log --oneline --graph --all`, `git reflog` |
| Committed on the wrong branch | `git branch feature/x` then `git reset --hard origin/main` |
| Detached HEAD, want to keep work | `git switch -c new-branch` |
| Bad merge, not pushed | `git reset --hard ORIG_HEAD` |
| Bad merge, pushed | `git revert -m 1 <merge-commit>` |
| Pushed a secret | **rotate the secret first**, then scrub history |
| Which commit broke it? | `git bisect start`, `bad`, `good <id>`, … `reset` |
| Backup before anything risky | `git branch backup` |

## Good commit message

```text
Fix wrong total when a coupon is applied      ← imperative, ≈ 50 characters

Why it was wrong and how this fixes it. Fixes #87.
```
