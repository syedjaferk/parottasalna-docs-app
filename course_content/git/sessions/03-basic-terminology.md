# Session 3 · Basic terminology

## The big idea

Git has a small vocabulary and every command uses it: **repository**, **commit**, **branch**, **merge**,
**remote**, **clone**. Learn these words once and the rest of Git reads like plain English.

**Everyday example:** a recipe notebook. The **notebook** is the repository. Each time you finish a
version of a recipe you take a dated **snapshot** (a commit). Trying a spicier variation on a separate page is a
**branch**; adding the good variation back to the main recipe is a **merge**. Photocopying the whole notebook for a friend is a
**clone**, and the friend's shared copy on a shelf in the library is a **remote**.

```{raw} html
:file: ../diagrams/git-concepts.html
```

## The words, in action

`03-terminology.sh` uses every term on a tiny recipe project and prints what Git says.

```{literalinclude} ../code/03-terminology.sh
:language: bash
```

```{literalinclude} ../code/03-terminology.out
:language: text
```

## The glossary

| Term | Meaning | Seen above |
|---|---|---|
| **Repository** | Your project plus its full history, stored in a hidden `.git` folder | `ls -a` shows `.git` |
| **Commit** | A snapshot of the project with a message and an id | `544bf04 Add chai recipe` |
| **Branch** | A movable label for a line of work; the default is `main` | `add-coffee` and `main` |
| **HEAD** | "Where you are now": the commit or branch you have checked out | the `*` in `git branch` |
| **Merge** | Combine the work of one branch into another | `coffee.txt` appeared on `main` |
| **Clone** | Copy a repository, with all its history | `recipes-copy` |
| **Remote** | A repository on another computer or server; the first is called `origin` | `git remote -v` |
| **Push / Pull** | Send your commits to a remote / bring new ones down | next courses |
| **Fork** | Your own server-side copy of someone else's repository (GitHub) | |
| **Pull request** | A request to merge your branch into someone's project, with review | |
| **Merge conflict** | Two branches changed the same lines, so a human must decide | |

## What the output proves

- A repository is just a folder with a `.git` inside; delete `.git` and it is an ordinary folder again.
- After the merge, `main` has **both** recipes and the log lists both commits.
- The clone has the **full history** (2 commits) and remembers where it came from as `origin`.
- A commit's id is a hash of its contents, author, date and parent, so the same content with a different
  date or author gets a different id. That is why Git can detect any tampering.

## Common mistakes

- **Calling the working folder "the repository".** The repository is the history in `.git`; the folder is your
  working copy.
- **Mixing up `clone` and `fork`.** Clone is a Git command that copies to your computer. A fork is a copy on
  GitHub's server.
- **Thinking a branch is a copy of the files.** It is only a pointer to a commit, which is why branches are
  cheap.
- **Deleting `.git` "to clean up".** That erases the entire history.
- **Treating `master` and `main` as different things.** They are only names; `main` is the modern default.

## Hands-on exercises

**Exercise 1.** Match each: (a) "copy of a repo on my laptop with history", (b) "a line of work", (c) "a snapshot with a message".

<details class="solution"><summary>Solution</summary>

(a) clone, (b) branch, (c) commit.

</details>

**Exercise 2.** Repeat the demo in a scratch folder with your own two files, and list what `git log --oneline` prints after the merge.

<details class="solution"><summary>Solution</summary>

```bash
git init notes && cd notes
echo one > a.txt && git add a.txt && git commit -m "Add a"
git switch -c feature
echo two > b.txt && git add b.txt && git commit -m "Add b"
git switch main && git merge feature
git log --oneline
```

You see two commits, newest first. (If your default branch is `master`, use that name.)

</details>

**Exercise 3.** Run `git remote -v` in a repository you made with `git init`. Why is the output empty?

<details class="solution"><summary>Solution</summary>

A repository made with `git init` has no remote, because it was not cloned from anywhere. Only `git clone`
(or `git remote add`) creates one.

</details>

## Practice

Take the **Session 3 quiz** on the glossary. The original *Basic Terminologies* page is in the reference section.
