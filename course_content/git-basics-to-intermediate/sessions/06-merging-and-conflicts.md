# Session 6 · Merging and Conflicts

**⏱ about 75 minutes · 🧰 you need: [Session 5](05-branches.md) done**

## The big idea

**Merging** brings the work of one branch into another. You finish your feature on a branch, then merge it into `main`, and `main` now has the feature.

**Everyday example:** two editors each edit a copy of the same article. A merge is the person who combines both sets of edits into one article. If the two editors changed *different paragraphs*, it is easy and automatic. If both rewrote the *same sentence* in different ways, a human must decide which wins. That clash is a **merge conflict**, and it is not an error. It is Git politely asking you to choose.

## 1. The rule of merging

> You stand on the branch that should **receive** the work, and say which branch to bring in.

```bash
git switch main            # I am the receiver
git merge cart-page        # bring cart-page's work into me
```

## 2. Two kinds of merge

### a) Fast-forward: the easy case

If `main` has not moved since the branch split off, Git just slides the `main` label forward. No new commit is needed.

```{raw} html
:file: ../diagrams/g06-ff.html
```

Try it in a fresh repo:

```bash
cd ~/git-lab
mkdir merge-lab && cd merge-lab
git init
echo "# Recipes" > README.md
git add . && git commit -m "Add readme"
git switch -c feature/soup
echo "Tomato soup: tomatoes, water, salt" > soup.txt
git add soup.txt && git commit -m "Add soup recipe"
git switch main
git merge feature/soup
```

```text
Updating 8a8a8a8..9b9b9b9
Fast-forward
 soup.txt | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 soup.txt
```

The word **Fast-forward** says it all. Clean up the finished branch:

```bash
git branch -d feature/soup
```

### b) Three-way merge: when both sides moved

If `main` *also* got new commits, the histories have diverged. Git finds the **common ancestor**, compares both sides to it, and creates a **merge commit** with **two parents**.

```{raw} html
:file: ../diagrams/g06-3way.html
```

```bash
git switch -c feature/salad
echo "Greek salad: cucumber, tomato, feta" > salad.txt
git add salad.txt && git commit -m "Add salad recipe"

git switch main
echo "Rice: rice, water" > rice.txt
git add rice.txt && git commit -m "Add rice recipe"

git merge feature/salad
```

Git opens your editor with the message `Merge branch 'feature/salad'`. Save and close:

```text
Merge made by the 'ort' strategy.
 salad.txt | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 salad.txt
```

```bash
git log --oneline --graph
```

```text
*   e1e1e1e (HEAD -> main) Merge branch 'feature/salad'
|\
| * d0d0d0d Add salad recipe
* | c9c9c9c Add rice recipe
|/
* 9b9b9b9 Add soup recipe
* 8a8a8a8 Add readme
```

The two lines join back together at the merge commit.

| Option | Effect |
|---|---|
| `git merge x` | fast-forward if possible, otherwise a merge commit |
| `git merge --no-ff x` | **always** make a merge commit (keeps a visible record that a branch existed) |
| `git merge --squash x` | squash all of x's commits into one staged change that **you** commit |
| `git merge --abort` | cancel a merge in progress and go back to before it |

## 3. Merge conflicts

A conflict happens when **both branches changed the same lines** of the same file (or one deleted a file the other edited). Git cannot know which version is right.

```{raw} html
:file: ../diagrams/g06-conflict.html
```

Let us create one on purpose. Both branches will change the *same line* of `soup.txt`:

```bash
git switch -c feature/spicy
echo "Tomato soup: tomatoes, water, salt, chilli" > soup.txt
git commit -am "Make soup spicy"

git switch main
echo "Tomato soup: tomatoes, stock, salt, basil" > soup.txt
git commit -am "Use stock and basil in soup"

git merge feature/spicy
```

```text
Auto-merging soup.txt
CONFLICT (content): Merge conflict in soup.txt
Automatic merge failed; fix conflicts and then commit the result.
```

Do not panic. Ask Git where you are:

```bash
git status
```

```text
On branch main
You have unmerged paths.
  (fix conflicts and run "git commit")
  (use "git merge --abort" to abort the merge)

Unmerged paths:
  (use "git add <file>..." to mark resolution)
	both modified:   soup.txt
```

Open `soup.txt`. Git wrote **conflict markers** into it:

```text
<<<<<<< HEAD
Tomato soup: tomatoes, stock, salt, basil
=======
Tomato soup: tomatoes, water, salt, chilli
>>>>>>> feature/spicy
```

| Marker | Meaning |
|---|---|
| `<<<<<<< HEAD` | start; below it is **your** side (the branch you are on: `main`) |
| `=======` | the divider |
| `>>>>>>> feature/spicy` | end; above it is the **incoming** side |

### Resolve it in four steps

1. **Edit the file** to the version you want: keep one side, the other, or a mix. **Delete all three marker lines.**
2. **Stage** the file to say "resolved".
3. **Commit** to finish the merge.
4. **Check** the result.

Edit `soup.txt` so it contains the best of both:

```text
Tomato soup: tomatoes, stock, salt, basil, chilli
```

```bash
git add soup.txt
git commit                # the message "Merge branch 'feature/spicy'" is pre-filled; save and close
git log --oneline --graph
```

Conflict solved. 🎉

:::{tip}
**VS Code** shows buttons above each conflict: *Accept Current*, *Accept Incoming*, *Accept Both*. Use them if you like, but still read the result and remove any leftover `<<<<<<<` lines. To find leftover markers: `grep -rn "<<<<<<<" .`
:::

### Handy conflict commands

| Command | Use |
|---|---|
| `git status` | lists the files still in conflict |
| `git diff` | shows the conflict in detail |
| `git merge --abort` | **bail out**: return to the state before the merge |
| `git checkout --ours file` | take **your** version of the whole file (`--theirs` = incoming) |
| `git log --merge -p file` | what each side changed in that file |

## 4. Reducing conflicts (the best cure is prevention)

* **Merge often.** Small, frequent merges mean small conflicts.
* **Pull the latest `main` into your branch regularly** (`git merge main` while on your branch).
* **Keep branches short-lived** and focused on one thing.
* **Talk to teammates** before two people rewrite the same file.
* **Do not reformat whole files** in a feature commit. It makes every line "changed".

## 5. Merge vs rebase (a preview)

Merging keeps the true history (with branches and merge commits). Session 9 shows **rebase**, a way to replay your commits on top of the latest `main` for a straighter history. Both are valid; teams pick one and stay consistent.

## Common mistakes

| Mistake | Fix |
|---|---|
| Leaving `<<<<<<<` markers in the file and committing | Search for `<<<<<<<` before `git add`. Tests and builds will break otherwise. |
| Using `git commit` before `git add` of the fixed file | Git says "unmerged paths". Stage the file first. |
| Merging the wrong way round | You must be **on the receiving branch**. If unsure: `git status` shows the branch; `git merge --abort` undoes it. |
| "I made it worse" during a conflict | `git merge --abort` returns you to the state before the merge. Start again. |
| Fear of conflicts | They are normal. A conflict is information, not failure. |

## Tryouts

**Tryout 1 · Fast-forward.** Make a branch `feature/dessert`, add `dessert.txt`, commit, and merge it into `main`. Confirm there is **no** merge commit (look at `git log --oneline --graph`).

<details class="solution">
<summary>Answer</summary>

```bash
git switch main
git switch -c feature/dessert
echo "Payasam: milk, vermicelli, sugar" > dessert.txt
git add . && git commit -m "Add dessert recipe"
git switch main
git merge feature/dessert
git log --oneline --graph -3
```

Since `main` did not move in between, it is a fast-forward.

</details>

**Tryout 2 · Force a merge commit.** Do the same with `feature/drinks` but make sure a merge commit is created even though a fast-forward would be possible.

<details class="solution">
<summary>Answer</summary>

```bash
git switch -c feature/drinks
echo "Lemon juice: lemon, sugar, water" > drinks.txt
git add . && git commit -m "Add drinks recipe"
git switch main
git merge --no-ff feature/drinks -m "Merge feature/drinks"
git log --oneline --graph -4
```

</details>

**Tryout 3 · Conflict.** Create a conflict in `README.md` (one branch changes the title to `# My Recipes`, the other to `# Family Recipes`). Merge, then resolve it with the title `# Our Family Recipes`.

<details class="solution">
<summary>Answer</summary>

```bash
git switch -c feature/title-a
echo "# My Recipes" > README.md
git commit -am "Title A"
git switch main
echo "# Family Recipes" > README.md
git commit -am "Title B"
git merge feature/title-a        # CONFLICT
echo "# Our Family Recipes" > README.md    # overwrite, which also removes the markers
git add README.md
git commit -m "Merge feature/title-a with combined title"
```

</details>

## Recap

* ✅ **Merge** = bring another branch's commits into the branch you are on.
* ✅ **Fast-forward** when `main` has not moved; **merge commit** (two parents) when both moved.
* ✅ A **conflict** = both sides changed the same lines. Edit → remove markers → `git add` → `git commit`.
* ✅ `git merge --abort` is the escape hatch.
* ✅ Short branches and frequent merges mean fewer conflicts.

**Next:** [Session 7 · Remotes and GitHub](07-remotes-and-github.md).
