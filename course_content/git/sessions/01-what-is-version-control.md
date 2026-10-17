# Session 1 · What is version control?

## The big idea

A **version control system** (VCS) records every change to a set of files: **what** changed, **who**
changed it, **when**, and **why**. You can compare any two versions, go back to an old one, and let
several people work on the same project without overwriting each other. **Git** is the VCS almost everyone
uses today.

**Everyday example:** the "final" folder. We all know `report_final.docx`, `report_final_v2.docx`,
`report_final_v2_REALLY_final.docx`. Nobody knows which is newest, what changed between them, or who
edited which. Version control replaces that pile with **one file and a labelled history**.

```{raw} html
:file: ../diagrams/copies-vs-history.html
```

## Copies versus a history, for real

`01-versions.sh` first makes the "hopeful names" mess, then does the same job with Git. Hashes such as
`460c381` are the ids Git gives each snapshot (called a *commit*).

```{literalinclude} ../code/01-versions.sh
:language: bash
```

```{literalinclude} ../code/01-versions.out
:language: text
```

What changed when we used Git:

- **One file** (`report.txt`), not four. The versions live in Git's history, not in the folder.
- **`git log`** lists each version with an id, an author and a message saying *why* it exists.
- **`git diff`** shows exactly what changed between two versions: one line removed (`-`), one added (`+`).
- **`git show HEAD~2:report.txt`** printed the first draft from two versions ago without touching the
  current file. Nothing is lost.

## Where Git came from

Version control has gone through three generations:

```{raw} html
:file: ../diagrams/vcs-generations.html
```

1. **Local** (SCCS in 1972, then RCS): history for single files on one computer. Only one person could
   edit a file at a time.
2. **Centralized** (CVS, Subversion): one server holds the official history and everyone connects to it.
   Teams could finally share, but if the server was down, nobody could commit, and history was not on your machine.
3. **Distributed** (Git, Mercurial): every developer has a **complete copy of the history**. You can commit,
   browse history and create branches offline, then share with others later.

Git was created in 2005 by Linus Torvalds for the Linux kernel after the tool the kernel team used
(BitKeeper) changed its licence. The goals were speed, simple branching and safety for a huge project.
The full story is in the reference pages at the end of the course.

## What to expect from a good tool

A good VCS lets you: undo mistakes, see who changed a line and why, work on a risky idea without breaking
the stable version (branches), collaborate without overwriting, and keep the whole project history safe.
The next sessions turn each of those into commands.

## Common mistakes

- **"Git is GitHub."** Git is the tool on your computer. GitHub, GitLab and Bitbucket are websites that host
  Git repositories so people can share them.
- **Using version control only for code.** It works for any text: documents, notes, configs, even this course.
- **Treating Git as a backup.** A repository on one disk is still lost if the disk dies. Push to a remote
  as well.
- **Committing rarely and in huge chunks.** A history of "update" commits is no better than `final_v2`.
  Commit small, with clear messages.
- **Believing binary files behave like text.** Git can store images and videos but cannot show line-by-line
  differences for them.

## Hands-on exercises

**Exercise 1.** Name three problems with keeping versions as `file_v1`, `file_v2` copies that Git solves.

<details class="solution"><summary>Solution</summary>

(1) You can't tell what changed between versions. Git shows it with `git diff`. (2) You can't tell who
made a change or why. Git records an author and message. (3) Two people copying the folder produce two
diverging "finals". Git can merge their work.

</details>

**Exercise 2.** Which generation of VCS is Git, and what does that give you when the network is down?

<details class="solution"><summary>Solution</summary>

Distributed. Every clone has the full history, so you can commit, view the log and create branches
offline. You only need the network to push or pull.

</details>

**Exercise 3.** In a scratch folder, repeat the demo: make `notes.txt`, commit three versions, then print
version one using `git show`.

<details class="solution"><summary>Solution</summary>

```bash
mkdir vc-demo && cd vc-demo && git init
echo "v1" > notes.txt && git add notes.txt && git commit -m "v1"
echo "v2" > notes.txt && git commit -am "v2"
echo "v3" > notes.txt && git commit -am "v3"
git show HEAD~2:notes.txt
```

The last command prints `v1`. (Set `user.name` and `user.email` first; Session 2 shows how.)

</details>

## Practice

Take the **Session 1 quiz**. The original history pages (before the '70s, the BitKeeper saga, Mercurial
versus Git) are in the reference section.
