# Git & GitHub: Basics to Intermediate

Almost every software team on Earth uses **Git**. It is the tool that lets ten people edit the same project at the same time without
overwriting each other, and lets you go back to *yesterday's version* when something breaks today.

This course takes you from *"what is Git?"* to *"I can branch, merge, fix conflicts, collaborate through pull requests, and I know
which team workflow to pick"*. You learn by **doing**: every session has commands to type, the output you should see, a plain-language
explanation, diagrams, and small **tryouts** with hidden answers.

:::{note}
**You do not need to know anything about Git.** You need a computer, a terminal and curiosity. If you have never used a terminal,
spend an hour on the *Linux Basics* course first (sessions 1 to 4 are enough). Mistakes are part of learning, and everything in
the practice folder is disposable.
:::

:::{tip}
This course is the practical, hands-on companion to the *Git & Version Control* course, which tells the **history** of version control
(BitKeeper, Mercurial, why Linus wrote Git). You do not need that one first.
:::

## What you will be able to do

```{raw} html
:file: diagrams/g00-journey.html
```

| After this course you can... | Sessions |
|---|---|
| Explain what Git is and why teams use it, install it and set it up | 1 |
| Create a repository, make commits and read the three areas (working folder, staging, repository) | 2 |
| Look back at history, compare versions and keep files out of Git | 3 |
| Undo almost any mistake: restore, amend, reset, revert, reflog | 4 |
| Create and switch branches and understand what `HEAD` is | 5 |
| Merge branches and resolve merge conflicts calmly | 6 |
| Connect to GitHub: clone, push, pull, fetch, SSH keys | 7 |
| Collaborate with pull requests, forks and code reviews | 8 |
| Use rebase, stash, cherry-pick and tags | 9 |
| Describe and compare **six team workflows** and choose one | 10 |
| Practise each workflow with commands, using only your own computer | 11 |
| Rescue a project: detached HEAD, wrong branch, leaked secret, bisect; plus good habits | 12 |

## How each session works

1. **The big idea** with an everyday comparison, so the concept makes sense before the commands appear.
2. **Try it**: commands to type in your practice folder, with the real output shown.
3. **What just happened?** Each command explained piece by piece, with diagrams.
4. **Common mistakes** and what the error messages mean.
5. **Tryouts**: three small jobs with answers hidden, so you try first.
6. **Recap** of what you can now do.

:::{tip}
**Type every command yourself.** Copy-paste teaches your clipboard, not your fingers. And whenever you are unsure what state
you are in, run `git status`. It is the most useful command in Git, and it is always safe.
:::

## Before you begin

Do the **[Setup](setup.md)** first (20 minutes): install Git, introduce yourself to it, and create the `~/git-lab` practice folder.
Keep the **[Cheatsheet](cheatsheet.md)** open in a tab.

```{toctree}
:maxdepth: 1
:caption: Start here

setup
cheatsheet
```

```{toctree}
:maxdepth: 1
:caption: Part 1 · Foundations

sessions/01-meet-git
sessions/02-your-first-repository
sessions/03-looking-back
sessions/04-undoing-things
```

```{toctree}
:maxdepth: 1
:caption: Part 2 · Branching and merging

sessions/05-branches
sessions/06-merging-and-conflicts
```

```{toctree}
:maxdepth: 1
:caption: Part 3 · Teamwork and power tools

sessions/07-remotes-and-github
sessions/08-collaborating
sessions/09-power-tools
```

```{toctree}
:maxdepth: 1
:caption: Part 4 · Workflows and real life

sessions/10-git-workflows
sessions/11-workflows-hands-on
sessions/12-rescue-and-good-habits
```
