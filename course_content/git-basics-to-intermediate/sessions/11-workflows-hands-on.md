# Session 11 · Workflows Hands-On

**⏱ about 120 minutes (do one lab per sitting if you like) · 🧰 you need: [Session 10](10-git-workflows.md) read**

## The big idea

Reading about workflows is one thing; *feeling* them is another. In this session you will **play every role yourself**: you are Asha **and** Ravi, two teammates. We will run each of the six workflows with real commands, and you do not even need GitHub. A folder on your computer will play the part of the "remote".

**Everyday example:** a fire drill. Nobody is in danger, but when the real alarm rings, everyone already knows the steps.

## The training ground

A **bare repository** is a repo without a working folder: only history, no files to edit. It is exactly what GitHub keeps on its servers, so it makes a perfect stand-in for "GitHub".

```bash
cd ~/git-lab
mkdir workflows && cd workflows

git init --bare shop.git           # our pretend GitHub
git clone shop.git asha            # Asha's laptop
git clone shop.git ravi            # Ravi's laptop
```

(Git warns that you cloned an empty repository. That is fine.) Give the project its first commit from Asha's side, and let Ravi download it:

```bash
cd asha
echo "# Shop" > README.md
git add . && git commit -m "Add readme"
git push -u origin main
cd ../ravi
git pull
```

```{raw} html
:file: ../diagrams/g07-remote.html
```

Your folders now look like this:

```text
~/git-lab/workflows/
├── shop.git/   ← the shared "GitHub" (bare)
├── asha/       ← Asha's laptop
└── ravi/       ← Ravi's laptop
```

:::{tip}
Open **two terminal windows** side by side, one in `asha`, one in `ravi`. It makes the roles easy to follow. Each lab says *who* does each step: **(Asha)** or **(Ravi)**.
:::

---

## Lab 1 · Centralized workflow

**Goal:** both commit to `main`; learn what happens when pushes collide.

**(Asha)** adds a homepage and pushes:

```bash
cd ~/git-lab/workflows/asha
echo "<h1>Shop</h1>" > index.html
git add . && git commit -m "Add homepage"
git push
```

**(Ravi)** did not know. He adds a contact page and tries to push:

```bash
cd ~/git-lab/workflows/ravi
echo "<p>contact us</p>" > contact.html
git add . && git commit -m "Add contact page"
git push
```

```text
 ! [rejected]        main -> main (fetch first)
error: failed to push some refs to '.../shop.git'
hint: Updates were rejected because the remote contains work that you do not
hint: have locally. ...
```

This is the central rule of the workflow in action: **you must integrate the latest work before you share yours**.

```bash
git pull --no-edit       # merges Asha's homepage in (no editor window)
git push                 # now accepted
```

**(Asha)** catches up and looks at the result:

```bash
cd ~/git-lab/workflows/asha
git pull
git log --oneline --graph
```

```text
*   4bf700c Merge branch 'main' of .../shop
|\
| * 49849c9 Add homepage
* | dafb682 Add contact page
|/
* dc400fa Add readme
```

✅ **What you learned:** in a centralized flow, "pull, then push" is everything. The small diamond is a merge commit created by the collision.

---

## Lab 2 · Feature Branch workflow

**Goal:** each person works on their own branch; `main` only receives finished work.

**(Asha)** builds the cart page on a branch:

```bash
cd ~/git-lab/workflows/asha
git switch -c feature/cart-page
echo "<h2>Cart</h2>" > cart.html
git add . && git commit -m "Add cart page"
git push -u origin feature/cart-page
```

**(Ravi)** builds search, at the same time, on his branch:

```bash
cd ~/git-lab/workflows/ravi
git switch -c feature/search
echo "<input type=search>" > search.html
git add . && git commit -m "Add search page"
git push -u origin feature/search
```

`main` has not changed. Neither person disturbed the other. 🧘

Now the **"pull request"**. With real GitHub you would click *Merge*. Here the maintainer (Ravi) does the equivalent by hand, `--no-ff` so a merge commit records each feature:

**(Ravi)**

```bash
git switch main
git pull
git fetch origin
git merge --no-ff feature/search -m "Merge feature/search"
git push

git merge --no-ff origin/feature/cart-page -m "Merge feature/cart-page"
git push
```

Clean up:

```bash
git branch -d feature/search
git push origin --delete feature/search
git push origin --delete feature/cart-page
git log --oneline --graph
```

```text
*   d6e9a97 Merge feature/cart-page
|\
| * beb8e5d Add cart page
* |   a56135a Merge feature/search
|\ \
| |/
|/|
| * 2f344c2 Add search page
|/
* ...
```

✅ **What you learned:** each feature is a visible "bubble" in the history; `main` only ever received finished work.

---

## Lab 3 · GitHub Flow

**Goal:** branch → commit → PR → squash-merge → deploy marker → delete. A bug fix, fast.

**(Asha)** gets the latest `main` and fixes a pricing bug on a branch with two small commits:

```bash
cd ~/git-lab/workflows/asha
git switch main
git pull
git switch -c fix/rounding
echo "round to 2 decimals" > price.txt
git add . && git commit -m "Fix price rounding"
echo "test: 9.999 -> 10.00" >> price.txt
git commit -am "Add a test for rounding"
git push -u origin fix/rounding
```

On real GitHub you would now **open a PR**, wait for CI, get an approval, and click **Squash and merge**. Locally, the same result is:

```bash
git switch main
git merge --squash fix/rounding        # stages all branch changes as ONE change, no commit yet
git commit -m "Fix price rounding (#1)"
git push
```

Mark the **deploy**, and clean up:

```bash
git tag -a deploy-1 -m "Deployed to production"
git push origin deploy-1
git branch -D fix/rounding             # -D because squash leaves the branch "unmerged" to Git
git push origin --delete fix/rounding
git log --oneline -3
```

```text
2f6e09c (HEAD -> main, tag: deploy-1, origin/main) Fix price rounding (#1)
d6e9a97 Merge feature/cart-page
...
```

✅ **What you learned:** the two small commits became **one tidy commit** on `main`. `main` stays deployable at every commit, and a tag marks what is live.

:::{note}
Why `-D`? A squash merge copies the *content* but not the original commits, so Git cannot tell the branch was merged and refuses `-d`. This is expected.
:::

---

## Lab 4 · Git Flow

**Goal:** `develop` + feature + release + hotfix, with tags. Still in **Asha's** folder.

```{raw} html
:file: ../diagrams/g10-gitflow.html
```

**Step 1 · create `develop`** (once):

```bash
cd ~/git-lab/workflows/asha
git switch -c develop main
git push -u origin develop
```

**Step 2 · a feature** (branch from and merge to `develop`):

```bash
git switch -c feature/wishlist develop
echo "<h2>Wishlist</h2>" > wishlist.html
git add . && git commit -m "Add wishlist"
git switch develop
git merge --no-ff feature/wishlist -m "Merge feature/wishlist"
git branch -d feature/wishlist
```

**Step 3 · release 1.0.0.** Branch from `develop`, fix only small things (here: set the version), then merge to **`main` and `develop`**, tag `main`:

```bash
git switch -c release/1.0.0 develop
echo "1.0.0" > VERSION
git add . && git commit -m "Bump version to 1.0.0"

git switch main
git merge --no-ff release/1.0.0 -m "Release 1.0.0"
git tag -a v1.0.0 -m "Release 1.0.0"

git switch develop
git merge --no-ff release/1.0.0 -m "Merge release/1.0.0 back"
git branch -d release/1.0.0
```

**Step 4 · urgent hotfix** (branch from **`main`**, because that is what is in production):

```bash
git switch -c hotfix/1.0.1 main
echo "1.0.1" > VERSION
git commit -am "Fix crash, bump to 1.0.1"

git switch main
git merge --no-ff hotfix/1.0.1 -m "Hotfix 1.0.1"
git tag -a v1.0.1 -m "Hotfix 1.0.1"

git switch develop
git merge --no-ff hotfix/1.0.1 -m "Merge hotfix/1.0.1 back"
git branch -d hotfix/1.0.1
```

**Step 5 · publish everything:**

```bash
git push origin main develop --tags
git log --oneline --graph --all --decorate
```

Look at the graph. You will see two long lines (`main`, `develop`) with tagged commits `v1.0.0` and `v1.0.1` on `main`, and bubbles for the feature, release and hotfix, exactly like the diagram.

✅ **What you learned:** why Git Flow is called *heavy*. A single hotfix is **two merges and a tag**. Also *why* the hotfix goes into `develop`: so the next release will not bring the crash back.

---

## Lab 5 · Forking workflow

**Goal:** contribute to a project you cannot write to. Everything stays local. We create:

* `official.git`: the maintainer's repo (you cannot push to it),
* `ravi-fork.git`: Ravi's fork (a copy he *can* push to).

```bash
cd ~/git-lab/workflows

# the official project
git init --bare official.git
git clone official.git maintainer
cd maintainer
echo "# Project" > README.md
echo "Helo world" > hello.txt          # note the typo!
git add . && git commit -m "Initial"
git push -u origin main
cd ..

# "Fork" it: a full copy that Ravi owns (on GitHub this is one click)
git clone --bare official.git ravi-fork.git
```

**(Ravi)** clones **his fork**, adds the original as `upstream`, and fixes the typo on a branch:

```bash
git clone ravi-fork.git ravi-project
cd ravi-project
git remote add upstream ../official.git
git remote -v
```

```text
origin    .../ravi-fork.git (fetch)
origin    .../ravi-fork.git (push)
upstream  ../official.git (fetch)
upstream  ../official.git (push)
```

```bash
git switch -c fix/typo
echo "Hello world" > hello.txt
git commit -am "Fix typo in hello.txt"
git push -u origin fix/typo            # to HIS fork
```

**The pull request.** On GitHub, Ravi would click *Compare & pull request*. Here the **maintainer** plays the reviewer: look at his fork's branch, then merge it:

```bash
cd ../maintainer
git remote add ravi ../ravi-fork.git
git fetch ravi
git log --oneline ravi/fix/typo -2             # review the proposed change
git merge --no-ff ravi/fix/typo -m "Merge PR: fix typo"
git push
```

**(Ravi)** syncs his fork with the original afterwards:

```bash
cd ../ravi-project
git fetch upstream
git switch main
git merge upstream/main
git log --oneline -3
```

```text
1c057f9 Merge PR: fix typo
1fae451 Initial
db6de37 Fix typo in hello.txt
```

✅ **What you learned:** Ravi **never had write access** to `official.git`. Trust lived in the review. And he kept his fork current with `fetch upstream` + `merge`.

---

## Lab 6 · Trunk-based development

**Goal:** tiny commits to `main`, integrated constantly; an unfinished feature hidden behind a flag.

**(Asha)** adds a feature flag that is **off**, and pushes straight away. The code is safe because nothing uses the flag yet:

```bash
cd ~/git-lab/workflows/asha
git switch main
git pull --rebase
echo "cart_v2=off" > flags.conf
git add . && git commit -m "Add flag cart_v2 (off)"
git pull --rebase
git push
```

**(Ravi)** makes his own small change and integrates it with the same rhythm:

```bash
cd ~/git-lab/workflows/ravi
git switch main
git pull --rebase
echo "search tweak" >> search.html
git commit -am "Tweak search"
git pull --rebase
git push
```

Over the next days **(Asha)** merges more small pieces of the new cart code (each one hidden by the flag). When ready, she releases by flipping the flag, a one-line change:

```bash
cd ~/git-lab/workflows/asha
git pull --rebase
sed -i 's/off/on/' flags.conf          # macOS: sed -i '' 's/off/on/' flags.conf
git commit -am "Turn on cart_v2"
git push
git log --oneline -4
```

```text
4e82a39 Turn on cart_v2
044fc77 Tweak search
a6edc35 Add flag cart_v2 (off)
...
```

✅ **What you learned:** a **straight line** of tiny commits, no long-lived branches, and `pull --rebase` replaying your commit on the newest trunk. The feature was *deployed before it was visible*, which is how trunk-based teams ship safely.

---

## Comparing what you built

Look at the three histories side by side:

```bash
cd ~/git-lab/workflows/asha
git log --oneline --graph --all --decorate
```

| Lab | Shape of the history |
|---|---|
| 1 Centralized | one line with an accidental diamond from the collision |
| 2 Feature branch | bubbles: each feature merged with a merge commit |
| 3 GitHub Flow | one tidy commit per pull request (squash) |
| 4 Git Flow | two long lines with many bubbles and tagged releases |
| 5 Forking | work arrives from another repo via fetch and merge |
| 6 Trunk-based | a perfectly straight line of tiny commits |

## Common mistakes

| Mistake | Fix |
|---|---|
| `fatal: ... does not appear to be a git repository` | Check the path in `git clone` / `git remote add`; run `ls` to confirm the `.git` folders exist. |
| Typing a command in the wrong person's folder | Check your prompt or run `pwd` first. Name your terminal windows. |
| A merge opens an editor and "hangs" | Save and close it (nano: `Ctrl+O`, Enter, `Ctrl+X`), or add `-m "message"`. |
| Lab results differ from the book | Normal: commit IDs always differ. Compare the *shape*, not the numbers. |
| Want to start a lab again | `cd ~/git-lab && rm -rf workflows` then redo *The training ground*. |

## Hands-on exercises

**Tryout 1 · Conflict in a team.** Reset the training ground. **(Asha)** and **(Ravi)** both change line 1 of `README.md` differently and commit. Asha pushes; Ravi pulls and resolves the conflict. Which of the six workflows did you just use?

<details class="solution">
<summary>Answer</summary>

Ravi's `git pull` stops with `CONFLICT (content)`. He edits `README.md` (removing `<<<<<<<`, `=======`, `>>>>>>>`), runs `git add README.md`, `git commit`, then `git push`. Working directly on `main` like this is the **Centralized workflow**: it shows why teams add branches and reviews as they grow.

</details>

**Tryout 2 · Your own flow.** Repeat Lab 3 (GitHub Flow) for a change called `docs/update-readme`. Squash two commits into one and tag it `deploy-2`.

<details class="solution">
<summary>Answer</summary>

```bash
git switch main && git pull
git switch -c docs/update-readme
echo "More docs" >> README.md && git commit -am "Describe the project"
echo "Even more" >> README.md && git commit -am "Add usage notes"
git switch main
git merge --squash docs/update-readme
git commit -m "Update the readme (#2)"
git tag -a deploy-2 -m "Deployed"
git push && git push origin deploy-2
git branch -D docs/update-readme
```

</details>

**Tryout 3 · Pick for a client.** A client's team has six developers, a web app, good automated tests and wants to release several times a week. Write down which workflow you would recommend, the three rules you would enforce on `main`, and the branch-name pattern.

<details class="solution">
<summary>Answer</summary>

**GitHub Flow** (feature branches + PRs + frequent deploys). Rules on `main`: (1) only via pull request, (2) at least one approval, (3) CI must pass. Branch names: `feature/<ticket>-<short-name>`, `fix/<ticket>-<short-name>`. Squash-merge and delete branches after merging.

</details>

## Recap

* ✅ A **bare repo** is a good local stand-in for GitHub; two clones are two teammates.
* ✅ **Centralized**: pull before push. **Feature branch**: merge finished work with `--no-ff`.
* ✅ **GitHub Flow**: branch, PR, **squash**, deploy, delete. **Git Flow**: `develop`/`release`/`hotfix`, merging back and tagging.
* ✅ **Forking**: `origin` = your fork, `upstream` = original; maintainers merge from your fork.
* ✅ **Trunk-based**: `pull --rebase` and tiny commits, with a **feature flag** hiding unfinished work.

**Next:** [Session 12 · Rescue Missions and Good Habits](12-rescue-and-good-habits.md).
