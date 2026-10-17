# Session 3 · Looking Back

**⏱ about 60 minutes · 🧰 you need: [Session 2](02-your-first-repository.md) done (the `my-website` repo)**

## The big idea

A time machine is only useful if you can **look around** in the past. This session teaches the "reading" commands: see the history in
different ways, see *exactly what changed*, and tell Git which files to ignore.

**Everyday example:** flipping through the photo album. `git log` is the list of captions, `git show` opens one page, and `git diff`
is the "spot the difference" puzzle between two photos.

```bash
cd ~/git-lab/my-website
```

## 1. `git log` in useful shapes

```bash
git log --oneline
```

```text
1a9b0f6 (HEAD -> main) Add about page
8c4d7e2 Add greeting to homepage
3f2a1b9 Add homepage
```

| Command | What you get |
|---|---|
| `git log --oneline` | one line per commit |
| `git log -3` | only the last 3 commits |
| `git log --stat` | which files changed in each commit, and how many lines |
| `git log -p` | the full changes (a *patch*) in each commit |
| `git log --author="Asha"` | only commits by a person |
| `git log --since="2 days ago"` | commits from a time window |
| `git log --grep="login"` | commits whose message contains a word |
| `git log -- index.html` | only commits that touched this file |
| `git log --oneline --graph --all` | a text drawing of all branches (very handy from Session 5) |

```bash
git log --stat -2
```

```text
commit 1a9b0f6... (HEAD -> main)
Author: Asha Kumar <asha@example.com>
Date:   Fri Oct 16 10:42:11 2026 +0530

    Add about page

 about.html | 1 +
 1 file changed, 1 insertion(+)

commit 8c4d7e2...
    Add greeting to homepage

 index.html | 1 +
 1 file changed, 1 insertion(+)
```

:::{tip}
A set-and-forget shortcut for the graph view: `git config --global alias.lg "log --oneline --graph --all --decorate"`.
After that, `git lg` does it.
:::

## 2. `git show`: open one page of the album

```bash
git show 8c4d7e2
```

```text
commit 8c4d7e2...
Author: Asha Kumar <asha@example.com>
Date:   Fri Oct 16 10:41:50 2026 +0530

    Add greeting to homepage

diff --git a/index.html b/index.html
index 4b2c1a0..9d3e7f1 100644
--- a/index.html
+++ b/index.html
@@ -1 +1,2 @@
 <h1>Welcome to my website</h1>
+<p>Hello from Chennai!</p>
```

You can use the short ID, or relatives of `HEAD` (HEAD is "the commit I am on now"):

| Name | Meaning |
|---|---|
| `HEAD` | the latest commit on your current branch |
| `HEAD~1` (or `HEAD^`) | one commit before that (the parent) |
| `HEAD~3` | three commits back |

```bash
git show HEAD~1
```

## 3. How to read a diff

Every `diff` uses the same notation:

```text
@@ -1 +1,2 @@
 <h1>Welcome to my website</h1>      ← no sign: unchanged line (context)
+<p>Hello from Chennai!</p>          ← + : line ADDED
-<p>Old text</p>                     ← - : line REMOVED
```

A changed line appears as one `-` (old) and one `+` (new). `@@ -1 +1,2 @@` says "starting at line 1 of the old file, 1 line;
starting at line 1 of the new file, 2 lines". You can ignore the numbers at first and just look for `+` and `-`.

## 4. `git diff`: what did I change?

Make a change but do not commit:

```bash
echo "<footer>(c) 2026</footer>" >> index.html
git diff
```

```text
diff --git a/index.html b/index.html
--- a/index.html
+++ b/index.html
@@ -1,2 +1,3 @@
 <h1>Welcome to my website</h1>
 <p>Hello from Chennai!</p>
+<footer>(c) 2026</footer>
```

Three versions of "the file" exist at the same time (working folder, staging, last commit), so Git has three diffs:

```{raw} html
:file: ../diagrams/g03-diff.html
```

| Command | Compares | Use it to answer |
|---|---|---|
| `git diff` | working folder ↔ staging area | "What have I changed but **not yet staged**?" |
| `git diff --staged` | staging area ↔ last commit | "What **will go into** my next commit?" |
| `git diff HEAD` | working folder ↔ last commit | "Everything changed since my last commit?" |
| `git diff 3f2a1b9 1a9b0f6` | any two commits | "What changed between these versions?" |
| `git diff --stat` | add to any of the above | a summary: files and line counts only |

```bash
git add index.html
git diff            # prints nothing: nothing is unstaged now
git diff --staged   # shows the footer line: it is staged
```

:::{important}
**Habit to build:** before every commit run `git status` and `git diff --staged`. It takes five seconds and catches stray debug lines,
passwords and wrong files.
:::

Commit it:

```bash
git commit -m "Add footer to homepage"
```

## 5. Telling Git to ignore files: `.gitignore`

Some files should **never** be in your history: secrets (`.env`), downloaded libraries (`node_modules/`), compiled files, editor
settings, logs. Create a file named `.gitignore` listing patterns:

```bash
mkdir logs
echo "debug output" > logs/app.log
echo "SECRET_KEY=abc123" > .env
git status
```

```text
Untracked files:
	.env
	logs/
```

```bash
cat > .gitignore <<'EOF'
# secrets
.env

# logs
logs/
*.log

# macOS / editor noise
.DS_Store
.vscode/
EOF
git status
```

```text
Untracked files:
	.gitignore
```

`.env` and `logs/` vanished from the list. Commit the `.gitignore` itself so the whole team shares it:

```bash
git add .gitignore
git commit -m "Add .gitignore"
```

| Pattern | Matches |
|---|---|
| `*.log` | every file ending in `.log`, anywhere |
| `logs/` | the folder `logs` and everything in it |
| `/build` | only a `build` in the top folder |
| `!keep.log` | **exception**: do not ignore this file |
| `# text` | a comment |

:::{warning}
`.gitignore` only affects files Git is **not yet tracking**. If you committed `.env` earlier, ignoring it later does not remove it.
Stop tracking it (keeping the file on disk) with `git rm --cached .env`, commit, and **change any secret that was exposed**, because
it is still in the history (see Session 12).
:::

## 6. Other useful look-around commands

| Command | Use |
|---|---|
| `git status -s` | short status: `M` modified, `A` added, `??` untracked |
| `git ls-files` | list every file Git tracks |
| `git blame index.html` | who last changed **each line**, and in which commit |
| `git shortlog -sn` | commits per author |

```bash
git blame index.html
```

```text
3f2a1b9 (Asha Kumar 2026-10-16 10:40:12 +0530 1) <h1>Welcome to my website</h1>
8c4d7e2 (Asha Kumar 2026-10-16 10:41:50 +0530 2) <p>Hello from Chennai!</p>
b7e9c01 (Asha Kumar 2026-10-16 11:05:33 +0530 3) <footer>(c) 2026</footer>
```

## Common mistakes

| Mistake | Fix |
|---|---|
| `git diff` shows nothing, yet `status` shows a change | The change is **staged**. Use `git diff --staged`. |
| `git log` is "stuck" on a screen | It opened a pager. Press `q` to quit, `space` for the next page. |
| `.gitignore` does not hide a file | The file is already tracked. Use `git rm --cached <file>`. |
| Named the file `gitignore.txt` or `.gitignore.txt` | It must be exactly `.gitignore`. |

## Hands-on exercises

**Tryout 1 · Find.** In `my-website`, list only the commits whose message contains the word `about`, one per line.

<details class="solution">
<summary>Answer</summary>

```bash
git log --oneline --grep="about" -i
```

(`-i` ignores upper/lower case.)

</details>

**Tryout 2 · Compare.** Show what changed between the **first** and the **latest** commit, as a summary of files and line counts.

<details class="solution">
<summary>Answer</summary>

```bash
git log --oneline            # note the first commit's ID, e.g. 3f2a1b9
git diff --stat 3f2a1b9 HEAD
```

</details>

**Tryout 3 · Ignore.** Create a file `notes.tmp` and a folder `cache/` with a file inside. Make Git ignore both without ignoring `.gitignore`. Verify with `git status`.

<details class="solution">
<summary>Answer</summary>

```bash
echo "x" > notes.tmp
mkdir cache && echo "y" > cache/data
printf "*.tmp\ncache/\n" >> .gitignore
git status -s
```

Only `M .gitignore` appears. Commit it: `git commit -am "Ignore tmp files and cache"`.

</details>

## Recap

* ✅ `git log` (`--oneline`, `--stat`, `-p`, `--graph`, `--author`, `--grep`) reads history.
* ✅ `git show <commit>` opens one commit. `HEAD~1` means "one before".
* ✅ In a diff, `+` is added and `-` is removed.
* ✅ `git diff` (unstaged), `git diff --staged` (about to commit), `git diff HEAD` (everything).
* ✅ `.gitignore` keeps secrets and junk out. `git blame` tells who changed a line.

**Next:** [Session 4 · Undoing Things](04-undoing-things.md).
