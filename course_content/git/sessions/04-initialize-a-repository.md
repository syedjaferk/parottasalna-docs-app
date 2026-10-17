# Session 4 · Initialize a repository

## The big idea

`git init` turns any folder into a Git repository by creating a hidden `.git` folder inside it. From then
on Git can watch that folder. Nothing is saved yet: a new repository is empty until you make your first commit.

**Everyday example:** opening a new notebook. The notebook exists and has a cover (the `.git` folder), but
there is nothing written in it. `git status` is you flipping through it to see what is inside and what is
not recorded yet.

```{raw} html
:file: ../diagrams/three-areas.html
```

## Create `MyProject`

```{literalinclude} ../code/04-init.sh
:language: bash
```

```{literalinclude} ../code/04-init.out
:language: text
```

What happened:

- **The long `hint:` block** appears when you have not chosen a default branch name. Git used `master`,
  as you can see in `On branch master`. The hint tells you how to change it. Run
  `git config --global init.defaultBranch main` once and every new repository starts on `main`.
- **`Initialized empty Git repository`** confirms `.git` was created.
- **`git status`** says `No commits yet` and `nothing to commit`. The repository is valid, just empty.
- **`ls -A`** shows that the only thing `init` added is `.git`. Inside it live `HEAD` (which branch you are
  on), `config` (this repository's settings), `objects` (the stored snapshots) and `refs` (branch names).
- After the setting, the second repository's branch is `main`.
- **Outside a repository**, `git status` fails with `fatal: not a git repository`. That message simply means you
  are in the wrong folder.

## What lives inside `.git`

You rarely need to open `.git`, but knowing what is in it removes the mystery. `objects` holds every
snapshot you will ever commit, stored compactly and addressed by hash. `refs` holds the names (branches and
tags) that point at those snapshots. `HEAD` is a one-line file saying which branch you are on. `config` is
the local settings file from Session 2. Because all of this sits in one folder, you can copy a project with its
whole history just by copying the folder, and you can delete the history by deleting `.git`.

The files next to `.git` (your actual project files) are called the **working folder**. Git compares the working
folder with what is stored in `.git` every time you run `git status`.

## Where to run `git init`

Run it once, in the **top folder of the project**, not in every subfolder and never in your whole home
directory. A repository inside another repository confuses Git, and an accidental `git init` in `~` makes
`git status` list everything you own.

## Common mistakes

- **`git init` inside an existing repository** (or a subfolder of one). You create a nested repository.
  Check with `git status` first.
- **Running `git init` in the wrong folder**, such as your home or Downloads folder. Delete the stray `.git` folder.
- **Forgetting the first commit.** Until you commit, `git log` fails with "does not have any commits yet".
- **Confusing `git init` with `git clone`.** Init starts a new empty history; clone copies an existing one.
- **Ignoring the branch-name hint.** `master` and `main` mixed across projects confuses scripts. Pick one default.

## Hands-on exercises

**Exercise 1.** Create `MyProject`, initialise it and confirm with `git status`.

<details class="solution"><summary>Solution</summary>

```bash
mkdir MyProject
cd MyProject
git init
git status
```

Expected: `Initialized empty Git repository ...` then `On branch main` (or `master`), `No commits yet`.

</details>

**Exercise 2.** Make a second repository `Other` and a project-specific identity `ProjectUser` just for it. Prove that `MyProject` is unaffected.

<details class="solution"><summary>Solution</summary>

```bash
git init Other && cd Other
git config user.name "ProjectUser"
git config user.email "projectuser@example.com"
cd ../MyProject
git config user.name        # prints your global name, not ProjectUser
```

Local settings live in each repository's own `.git/config`.

</details>

**Exercise 3.** Find out which branch a new repository starts on and change the default for all future ones.

<details class="solution"><summary>Solution</summary>

```bash
git init try1 && git -C try1 branch --show-current
git config --global init.defaultBranch main
git init try2 && git -C try2 branch --show-current
```

Before the setting an older Git prints `master` (as in the output above); after it, `main`.

</details>

## Practice

Take the **Session 4 quiz**. The original *Q1 Initialize a Repository and Basic Configurations* page is in the
reference section.
