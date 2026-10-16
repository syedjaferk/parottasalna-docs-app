# Session 1 · Meet Git

**⏱ about 45 minutes · 🧰 you need: the [Setup](../setup.md) done**

## The big idea

Imagine writing a long report. You save a copy before every big change: `report.docx`, `report_final.docx`, `report_final_v2.docx`,
`report_final_v2_REAL.docx`. Two weeks later you cannot remember which one has the paragraph you deleted by mistake. Now imagine ten
people doing that to the same folder.

**Git is a time machine for a folder.** You tell it *"remember how the project looks right now"*, and it keeps that **snapshot** forever,
with a note about who saved it and why. Later you can look at any snapshot, compare two of them, or go back to one.

```{raw} html
:file: ../diagrams/g01-before-after.html
```

**Everyday example:** a photo album. You do not keep every photo loose on the table. You pick the moments worth remembering, stick them
in the album in order, and write a caption under each. Git's album is called a **repository**, each photo is a **commit**, and the
caption is the **commit message**.

## 1. Three words that confuse beginners

| Word | What it really is |
|---|---|
| **Version control** | The *idea*: a system that records changes to files over time. |
| **Git** | A free *program* on your computer that does version control. It works offline. |
| **GitHub** | A *website* that stores Git repositories online so teams can share them. GitLab and Bitbucket are similar sites. |

:::{important}
**Git is not GitHub.** Git is the tool; GitHub is one place to host your Git projects. You can use Git for years without GitHub.
:::

## 2. Why teams use Git

* **Undo anything.** Broke the app at 5 pm? Go back to the 4 pm snapshot.
* **Know who changed what and why.** Every line has an author and a message.
* **Work in parallel.** Each person works on their own *branch* (a private line of work) and the branches are merged later (Sessions 5 and 6).
* **Work offline.** The whole history lives on your computer. Internet is only needed to share.
* **Try ideas safely.** Experiment on a branch. If it fails, throw the branch away.

## 3. A commit is a snapshot

```{raw} html
:file: ../diagrams/g01-snapshots.html
```

A **commit** records:

1. a **snapshot** of every tracked file at that moment,
2. **who** made it and **when**,
3. a **message** saying why,
4. a pointer to its **parent**, the commit before it.

Because each commit points to the one before, commits form a **chain**. That chain is your project's **history**. Each commit
has a long unique ID such as `a1b2c3d4e5f6...` (usually shortened to the first 7 characters).

:::{note}
Git does not store "the differences". It stores snapshots, and is clever about not duplicating files that did not change. That is
why switching between versions is nearly instant.
:::

## 4. The three areas (the model to remember)

This one picture explains most of Git. You will meet it again and again.

```{raw} html
:file: ../diagrams/g02-areas.html
```

| Area | Everyday comparison | What lives there |
|---|---|---|
| **Working folder** | Your desk | The actual files you open and edit. |
| **Staging area** (also called the *index*) | A packing box | Changes you have *chosen* to include in the next save. |
| **Repository** (the `.git` folder) | The photo album | Every commit ever made. |

Saving in Git is a **two-step** action: first `git add` puts changes in the box, then `git commit` seals the box and files it in
the album. The extra step lets you decide exactly what goes into each snapshot.

## 5. Try it: check your install

```bash
cd ~/git-lab
git --version
git config user.name
git config user.email
```

```text
git version 2.43.0
Asha Kumar
asha@example.com
```

## 6. Getting help

Git has built-in manuals. They are long, but the first lines are handy:

```bash
git help commit      # opens the full manual (press q to quit)
git commit -h        # a short summary of options
```

## Common mistakes

| Mistake | Fix |
|---|---|
| Thinking Git and GitHub are the same | Git runs on your computer. GitHub is a website that hosts repos. |
| Expecting Git to save automatically | Git only records what you **commit**. Editing a file does not save it into history. |
| Using a name or email you do not want public | `git config --global user.name ...` changes it for *future* commits. Old commits keep the old values. |

## Tryouts

**Tryout 1 · Check.** Print your configured name and email.

<details class="solution">
<summary>Answer</summary>

```bash
git config user.name
git config user.email
```

</details>

**Tryout 2 · Explain.** In your own words, write one sentence each for: *repository*, *commit*, *staging area*. Compare with the tables above.

<details class="solution">
<summary>Answer</summary>

A **repository** is the project folder plus its complete history (stored in `.git`). A **commit** is one saved snapshot with an author,
date and message. The **staging area** is where you collect the changes you want in the *next* commit.

</details>

**Tryout 3 · Challenge.** Find out which editor Git will open for commit messages, and see *where* that setting is stored.

<details class="solution">
<summary>Answer</summary>

```bash
git config --show-origin core.editor
```

```text
file:/home/asha/.gitconfig	nano
```

Global settings are stored in `~/.gitconfig` (a plain text file you can open).

</details>

## Recap

* ✅ **Git** = a time machine for a folder. **GitHub** = a website that hosts Git repos.
* ✅ A **commit** is a snapshot with an author, a date, a message and a pointer to its parent.
* ✅ Three areas: **working folder → staging area → repository**.
* ✅ Saving = `git add` then `git commit`.

**Next:** [Session 2 · Your First Repository](02-your-first-repository.md).
