# Session 5 · Branches

**⏱ about 60 minutes · 🧰 you need: [Session 4](04-undoing-things.md) done**

## The big idea

A **branch** is a separate line of work. It lets you try a new feature, fix a bug or run an experiment **without touching the stable
version** of your project. When the work is good, you bring it back (a *merge*, next session). If it is bad, you delete the branch and nothing is lost.

**Everyday example:** you are writing a book. Instead of scribbling directly in the master manuscript, you photocopy it, write a risky
new chapter on the copy, and only if the editor likes it do you paste it into the master. The master is `main`; the photocopy is a branch.

In real life you never pause the main project while someone builds a feature. Branches make it possible for ten people to work on ten
features at once.

## 1. A branch is just a sticky label

This is the one fact that makes branches click:

> **A branch is only a movable label that points at one commit.** Nothing is copied. Creating a branch takes a few milliseconds.

```{raw} html
:file: ../diagrams/g05-branch.html
```

* `main` is the label on the latest commit of the main line.
* `feature` is another label; it has two commits `main` does not have.
* When you commit while on a branch, the **label moves forward** to the new commit.

## 2. `HEAD`: "you are here"

Git needs to know which branch you are on. A special pointer called **`HEAD`** says so. HEAD points to a branch; the branch points to a commit.

```{raw} html
:file: ../diagrams/g05-head.html
```

Your next commit is added to **whatever HEAD's branch is**, and that branch's label moves forward.

## 3. Try it: create and switch

Start from a fresh repo:

```bash
cd ~/git-lab
mkdir branch-lab && cd branch-lab
git init
echo "<h1>My Shop</h1>" > index.html
git add . && git commit -m "Add shop homepage"
echo "<p>Contact: shop@example.com</p>" >> index.html
git commit -am "Add contact line"
```

See your branches:

```bash
git branch
```

```text
* main
```

The `*` marks the branch you are on. Create a new branch and move onto it:

```bash
git switch -c cart-page
```

```text
Switched to a new branch 'cart-page'
```

`-c` means **c**reate. It is the shortcut for two steps: `git branch cart-page` (make the label) then `git switch cart-page` (move HEAD to it).

```bash
git branch
```

```text
* cart-page
  main
```

## 4. Work on the branch

```bash
echo "<h2>Your cart</h2>" > cart.html
git add cart.html
git commit -m "Add cart page"
echo "<p>0 items</p>" >> cart.html
git commit -am "Show item count in cart"
git log --oneline --graph --all
```

```text
* 5c5c5c5 (HEAD -> cart-page) Show item count in cart
* 4b4b4b4 Add cart page
* 2a2a2a2 (main) Add contact line
* 1a1a1a1 Add shop homepage
```

`cart-page` is two commits ahead of `main`. Now **go back to main**:

```bash
git switch main
ls
```

```text
index.html
```

`cart.html` is **gone** from your folder! It is not lost: it lives on the `cart-page` branch. When you switch, Git rewrites your working folder to match that branch's snapshot.

```bash
git switch cart-page
ls
```

```text
cart.html  index.html
```

It is back. 🎩

:::{important}
**Before switching branches, commit (or stash) your work.** If you have uncommitted changes that conflict with the other branch, Git refuses to switch and tells you why. (Session 9 shows `git stash`, a safe shelf for half-done work.)
:::

## 5. Everyday branch commands

| Command | What it does |
|---|---|
| `git branch` | list local branches (`*` = current) |
| `git branch -a` | also list branches on the remote |
| `git branch -v` | list branches with their latest commit |
| `git switch name` | move to an existing branch |
| `git switch -c name` | create a branch **and** move to it |
| `git switch -c name <start-point>` | create it starting from a specific commit or branch |
| `git branch -m old new` | **m**ove / rename a branch |
| `git branch -d name` | delete a branch that is already merged (safe) |
| `git branch -D name` | **force** delete, even unmerged (careful) |
| `git log --oneline --graph --all` | draw all branches |

:::{note}
Older tutorials use `git checkout branch` and `git checkout -b branch`. They still work. `git switch` (for branches) and `git restore` (for files) are the newer, clearer commands that replaced the two jobs of `checkout`.
:::

## 6. A branch splits when both lines get new commits

```bash
git switch main
echo "<footer>shop@example.com</footer>" >> index.html
git commit -am "Add footer to homepage"
git log --oneline --graph --all
```

```text
* 7d7d7d7 (HEAD -> main) Add footer to homepage
| * 5c5c5c5 (cart-page) Show item count in cart
| * 4b4b4b4 Add cart page
|/
* 2a2a2a2 Add contact line
* 1a1a1a1 Add shop homepage
```

The history has **diverged**: both `main` and `cart-page` have commits the other lacks. Joining them is the job of **merging**, the next session.

## 7. Naming branches

Good branch names say what the work is. Common team conventions:

| Pattern | Example |
|---|---|
| `feature/<what>` | `feature/cart-page`, `feature/login` |
| `bugfix/<what>` | `bugfix/wrong-total` |
| `hotfix/<what>` | `hotfix/payment-crash` |
| `release/<version>` | `release/1.4.0` |
| `docs/<what>` | `docs/update-readme` |
| with a ticket number | `feature/SHOP-142-cart-page` |

Use lower case, no spaces (use `-`). Short, but specific.

## Common mistakes

| Mistake | Fix |
|---|---|
| "My file disappeared!" after switching | It lives on the other branch. `git switch -` goes back to where you were. |
| Committing on `main` by accident | Create a branch from here: `git switch -c feature/x`, then move `main` back (Session 12, *wrong branch*). |
| `error: Your local changes would be overwritten by checkout` | Commit first, or `git stash` (Session 9). |
| Deleting a branch with `-D` and losing unmerged work | Reflog can find the commit (Session 4). Prefer `-d`, which refuses to delete unmerged work. |
| Working for weeks on one huge branch | Merging gets painful. Keep branches short and merge often. |

## Hands-on exercises

**Tryout 1 · Branch out.** In `branch-lab`, create a branch `feature/search` from `main`, add a file `search.html`, and commit it. Then return to `main` and confirm `search.html` is not there.

<details class="solution">
<summary>Answer</summary>

```bash
git switch main
git switch -c feature/search
echo "<input type=search>" > search.html
git add search.html
git commit -m "Add search page"
git switch main
ls                      # no search.html
```

</details>

**Tryout 2 · Draw.** Run `git log --oneline --graph --all`. How many branches have commits that `main` lacks?

<details class="solution">
<summary>Answer</summary>

Two: `cart-page` (2 commits) and `feature/search` (1 commit). Both split off the line of `main`, so each shows as a side branch in the graph.

</details>

**Tryout 3 · Rename and delete.** Rename `feature/search` to `feature/site-search`, then try to delete it with the *safe* option. What does Git say, and why?

<details class="solution">
<summary>Answer</summary>

```bash
git branch -m feature/search feature/site-search
git branch -d feature/site-search
```

```text
error: the branch 'feature/site-search' is not fully merged.
```

Git protects you: its commit is not on any other branch yet. Use `-D` only if you really want to discard it.

</details>

## Recap

* ✅ A **branch** is a movable label on a commit. Creating one is instant and free.
* ✅ **HEAD** says which branch you are on; new commits move that branch's label.
* ✅ `git switch -c name` creates and moves; `git switch name` moves; `git branch` lists.
* ✅ Switching branches changes the files in your folder to match that branch.
* ✅ Use clear names such as `feature/...` and `bugfix/...`.

**Next:** [Session 6 · Merging and Conflicts](06-merging-and-conflicts.md).
