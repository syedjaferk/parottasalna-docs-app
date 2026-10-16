# Session 2 · Your First Repository

**⏱ about 60 minutes · 🧰 you need: [Session 1](01-meet-git.md) done**

## The big idea

A **repository** (or *repo*) is just a normal folder that Git has been told to watch. The moment you run `git init`, Git creates a hidden
folder called `.git` inside it. That hidden folder *is* the album: all history lives in it. Delete `.git` and the folder is an ordinary folder again.

**Everyday example:** you hire a very careful assistant to watch a desk. They do nothing until you say *"put these papers in the album"*.
Then they photograph the desk exactly as it is and write your caption underneath.

```bash
cd ~/git-lab
mkdir my-website
cd my-website
```

## 1. `git init`: start watching a folder

```bash
git init
```

```text
Initialized empty Git repository in /home/asha/git-lab/my-website/.git/
```

```bash
ls -a
```

```text
.  ..  .git
```

That `.git` folder is the whole repository. Never edit things inside it by hand.

## 2. `git status`: the command you will type most

```bash
git status
```

```text
On branch main

No commits yet

nothing to commit (create/copy files and use "git add" to track)
```

`git status` tells you three things: which **branch** you are on (`main`), whether there are commits yet, and what has changed.
It never changes anything, so run it whenever you are unsure.

## 3. Create a file

```bash
echo "<h1>Welcome to my website</h1>" > index.html
git status
```

```text
On branch main

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	index.html

nothing added to commit but untracked files present (use "git add" to track)
```

**Untracked** means Git can see the file but has been told nothing about it yet.

## 4. `git add`: put it in the packing box

```bash
git add index.html
git status
```

```text
On branch main

No commits yet

Changes to be committed:
  (use "git rm --cached <file>..." to unstage)
	new file:   index.html
```

The file is now **staged**: green and ready ("Changes to be committed").

| You type | Meaning |
|---|---|
| `git add file.txt` | stage one file |
| `git add file1 file2` | stage several files |
| `git add folder/` | stage everything in a folder |
| `git add .` | stage **everything** changed in the current folder (and below) |
| `git add -p` | go through changes piece by piece and choose (very useful later) |

## 5. `git commit`: seal the box and file it

```bash
git commit -m "Add homepage"
```

```text
[main (root-commit) 3f2a1b9] Add homepage
 1 file changed, 1 insertion(+)
 create mode 100644 index.html
```

* `-m "..."` gives the message on the spot. Without `-m`, Git opens your editor.
* `3f2a1b9` is the short ID of your first snapshot.
* `(root-commit)` means: this is the very first commit, with no parent.

```bash
git status
```

```text
On branch main
nothing to commit, working tree clean
```

**Working tree clean** means: the folder matches the last commit exactly. 🎉

## 6. The rhythm: edit → add → commit

Add a second file and change the first, then save them as two **separate** commits:

```bash
echo "<p>About me page</p>" > about.html
echo "<p>Hello from Chennai!</p>" >> index.html
git status
```

```text
On branch main
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   index.html

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	about.html

no changes added to commit (use "git add" and/or "git commit -a")
```

Two different kinds of change: `index.html` is **modified** (Git already tracks it) and `about.html` is **untracked**. We want separate
commits, because each commit should tell **one story**:

```bash
git add index.html
git commit -m "Add greeting to homepage"

git add about.html
git commit -m "Add about page"
```

```text
[main 8c4d7e2] Add greeting to homepage
 1 file changed, 1 insertion(+)
[main 1a9b0f6] Add about page
 1 file changed, 1 insertion(+)
 create mode 100644 about.html
```

This is why the staging area exists: two changes were sitting in the folder, but you chose which went into which commit.

### The life of a file

```{raw} html
:file: ../diagrams/g02-lifecycle.html
```

## 7. `git log`: see your history

```bash
git log
```

```text
commit 1a9b0f6c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f70 (HEAD -> main)
Author: Asha Kumar <asha@example.com>
Date:   Fri Oct 16 10:42:11 2026 +0530

    Add about page

commit 8c4d7e2a1b2c3d4e5f60718293a4b5c6d7e8f901
Author: Asha Kumar <asha@example.com>
Date:   Fri Oct 16 10:41:50 2026 +0530

    Add greeting to homepage

commit 3f2a1b9...
```

Newest first. A shorter view:

```bash
git log --oneline
```

```text
1a9b0f6 (HEAD -> main) Add about page
8c4d7e2 Add greeting to homepage
3f2a1b9 Add homepage
```

(Session 3 shows many more ways to read history.)

## 8. Good commit messages

A commit message is a note to your future self and your teammates.

| ❌ Weak | ✅ Better |
|---|---|
| `update` | `Fix broken link on the contact page` |
| `changes` | `Add login form validation` |
| `asdf` | `Remove unused images to speed up page load` |

Rules of thumb: start with a verb (*Add, Fix, Remove, Rename*), keep the first line under about 50 characters, describe **what and why**,
and make one commit tell **one story**.

:::{tip}
You can write a longer message too. Run `git commit` without `-m`, type the short summary on line 1, leave line 2 blank, and write the
details below. Save and close the editor to finish.
:::

## 9. Commit shortcuts (use with care)

| Command | What it does |
|---|---|
| `git commit -am "message"` | stage **all modified tracked files** *and* commit. It does **not** include brand-new (untracked) files. |
| `git add . && git commit -m "msg"` | add everything, including new files, then commit |

Handy, but if you always use `add .`, you lose the main benefit of staging (choosing what goes in). Run `git status` before committing.

## Common mistakes

| Mistake | What happens | Fix |
|---|---|---|
| `git commit` with nothing staged | `nothing added to commit but untracked files present` | You forgot `git add`. |
| Running `git init` inside a folder that is already a repo | creates a nested repo, confusing things | run `git status` first; if you see `On branch...`, you are already in a repo. |
| `git init` in your home folder | Git tries to watch *everything* | Delete the stray `.git` with `rm -rf ~/.git` (only if it is the accidental one!), then `cd` into the right project. |
| Vague messages like "fix" | History is unreadable later | Say *what* you fixed. |
| Committing before checking `git status` | You commit a file you did not mean to | Look first. Fix afterwards with Session 4. |

## Tryouts

**Tryout 1 · Build.** Create a folder `~/git-lab/notes`, make it a repo, create `todo.txt` with two lines, and make your first commit with the message `Add todo list`.

<details class="solution">
<summary>Answer</summary>

```bash
cd ~/git-lab
mkdir notes && cd notes
git init
printf "buy milk\ncall mom\n" > todo.txt
git add todo.txt
git commit -m "Add todo list"
git log --oneline
```

</details>

**Tryout 2 · Two stories.** In `notes`, add a third line to `todo.txt` **and** create `ideas.txt`. Make two separate commits: `Add third todo` and `Add ideas file`.

<details class="solution">
<summary>Answer</summary>

```bash
echo "pay bills" >> todo.txt
echo "learn Git" > ideas.txt
git add todo.txt
git commit -m "Add third todo"
git add ideas.txt
git commit -m "Add ideas file"
git log --oneline
```

</details>

**Tryout 3 · Challenge.** Change `todo.txt` again and run `git status`, then `git commit -am "Update todos"`. Does `-am` also commit a brand-new file `new.txt` that you created before? Test it and explain.

<details class="solution">
<summary>Answer</summary>

```bash
echo "water plants" >> todo.txt
echo "hello" > new.txt
git commit -am "Update todos"
git status
```

`new.txt` is still **untracked**: `-a` only stages files Git *already tracks*. A new file needs `git add new.txt` once.

</details>

## Recap

* ✅ `git init` turns a folder into a repository (it creates the hidden `.git`).
* ✅ `git status` shows branch and changes. Run it constantly.
* ✅ `git add` stages; `git commit -m "..."` saves. **edit → add → commit.**
* ✅ `git log --oneline` shows history.
* ✅ One commit = one story, with a clear message.

**Next:** [Session 3 · Looking Back](03-looking-back.md).
