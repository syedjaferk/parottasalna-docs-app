# Session 4 · Undoing Things

**⏱ about 75 minutes · 🧰 you need: [Session 3](03-looking-back.md) done**

## The big idea

The best thing about Git is that **almost nothing is permanent**. You can undo a commit, un-stage a file, fix a typo in the last message,
or even recover work you thought you deleted. The skill is knowing **which undo tool fits which situation**.

**Everyday example:** writing with a pencil, a pen, and a marker. Pencil mistakes (not staged yet) are erased with `restore`. A wrong
page in the album (a commit) can be removed (`reset`) or cancelled with a new page saying "ignore the previous page" (`revert`).

First, a safe playground:

```bash
cd ~/git-lab
mkdir undo-lab && cd undo-lab
git init
echo "line 1" > story.txt && git add story.txt && git commit -m "Add story"
echo "line 2" >> story.txt && git commit -am "Add line 2"
echo "line 3" >> story.txt && git commit -am "Add line 3"
git log --oneline
```

```text
c3c3c3c (HEAD -> main) Add line 3
b2b2b2b Add line 2
a1a1a1a Add story
```

## Which undo do I need? (the cheat map)

| Situation | Command |
|---|---|
| I edited a file and want to **throw the edit away** | `git restore story.txt` |
| I ran `git add` too early, **un-stage** it | `git restore --staged story.txt` |
| My last commit has a **typo in the message** or I forgot a file | `git commit --amend` |
| Undo the last commit(s) **but keep my work** | `git reset --soft HEAD~1` (or `--mixed`) |
| Undo the last commit(s) and **throw the work away** | `git reset --hard HEAD~1` |
| Undo a commit that is **already shared** with others | `git revert <commit>` |
| I lost a commit or did a bad reset | `git reflog` |

## 1. Throw away edits in a file: `git restore`

```bash
echo "oops, a terrible line" >> story.txt
git status -s
```

```text
 M story.txt
```

```bash
git restore story.txt
cat story.txt
```

```text
line 1
line 2
line 3
```

The file is back to its last committed state.

:::{danger}
**`git restore <file>` cannot be undone.** Git has no copy of edits you never committed or staged. Check `git diff` first.
:::

## 2. Un-stage a file: `git restore --staged`

```bash
echo "line 4" >> story.txt
echo "draft" > secret-notes.txt
git add .
git status -s
```

```text
M  story.txt
A  secret-notes.txt
```

Oops, `secret-notes.txt` should not be in this commit. Take it out of the packing box (the file itself stays on disk):

```bash
git restore --staged secret-notes.txt
git status -s
```

```text
M  story.txt
?? secret-notes.txt
```

```{raw} html
:file: ../diagrams/g02-areas.html
```

(Red arrows: `git restore` pulls a file from staging back into the folder; `git restore --staged` pulls it from the last commit back into staging.)

Finish the commit and clean up:

```bash
git commit -m "Add line 4"
rm secret-notes.txt
```

## 3. Fix the last commit: `git commit --amend`

Typo in the message? Forgot a file? Amend **replaces** the last commit with a better one:

```bash
git commit --amend -m "Add line four to the story"
git log --oneline -1
```

```text
d4d4d4d (HEAD -> main) Add line four to the story
```

Notice the ID changed (`c3...` style → `d4d4d4d`): amend creates a *new* commit and drops the old one. To add a forgotten file:

```bash
echo "credits" > credits.txt
git add credits.txt
git commit --amend --no-edit      # keep the same message
```

:::{warning}
**Only amend commits you have not pushed.** Amending rewrites history; if teammates already have the old commit, their copies will conflict with yours.
:::

## 4. Undo commits with `git reset`

`reset` moves your **branch label** back to an older commit. Imagine the branch is a bookmark; reset slides the bookmark backwards.
There are three strengths, and what differs is **what happens to your changes**:

```{raw} html
:file: ../diagrams/g04-reset.html
```

| Mode | The commit | Staging area | Your files | Use it when |
|---|---|---|---|---|
| `--soft` | undone | **kept** (still staged) | kept | "I want to re-commit it differently / combine commits" |
| `--mixed` (default) | undone | emptied | kept | "Undo the commit and unstage, let me redo `add`" |
| `--hard` | undone | emptied | **overwritten** | "Throw it all away" |

Try the safe ones first. Make a commit you regret:

```bash
echo "a bad idea" >> story.txt
git commit -am "Add a bad idea"
git log --oneline -2
```

```text
e5e5e5e (HEAD -> main) Add a bad idea
d4d4d4d Add line four to the story
```

Undo the commit but **keep the change** in your folder:

```bash
git reset --soft HEAD~1
git status -s
```

```text
M  story.txt
```

The commit is gone, but the change is still staged. Edit, then commit again properly. Now the hard version:

```bash
git commit -m "Add a bad idea"
git reset --hard HEAD~1
cat story.txt
```

The bad idea is gone from history *and* from the file.

:::{danger}
`--hard` throws away **uncommitted** work too. If you reset hard by mistake after committing, `git reflog` (below) can still save you. But uncommitted edits are gone for good.
:::

### Reset a single commit by ID

`HEAD~1` means "one commit before now". You can also name a commit:

```bash
git reset --hard a1a1a1a      # go back to the "Add story" snapshot
```

## 5. Undo a shared commit safely: `git revert`

`reset` rewrites history. That is fine on your own laptop but dangerous once teammates have your commits. **`git revert` does not rewrite anything**: it adds a *new* commit that does the exact opposite of an earlier one.

```bash
git reset --hard d4d4d4d          # (or the ID of "Add line four") to be in a known place
echo "buggy change" >> story.txt
git commit -am "Add buggy change"
git revert HEAD
```

Git opens your editor with the message `Revert "Add buggy change"`. Save and close.

```text
[main f6f6f6f] Revert "Add buggy change"
 1 file changed, 1 deletion(-)
```

```bash
git log --oneline -3
```

```text
f6f6f6f (HEAD -> main) Revert "Add buggy change"
9a9a9a9 Add buggy change
d4d4d4d Add line four to the story
```

```{raw} html
:file: ../diagrams/g04-revert.html
```

| | `reset` | `revert` |
|---|---|---|
| History | rewritten (commit disappears) | kept (new "undo" commit added) |
| Safe on shared branches? | ❌ no | ✅ yes |
| Use for | cleaning up **local, unpushed** work | undoing something **already pushed** |

## 6. The safety net: `git reflog`

Git quietly records **every place your HEAD has been** for about 90 days, even after a hard reset. This log is called the *reflog*.

```bash
git reset --hard HEAD~2        # "oh no, I meant HEAD~1"
git reflog
```

```text
d4d4d4d (HEAD -> main) HEAD@{0}: reset: moving to HEAD~2
f6f6f6f HEAD@{1}: revert: Revert "Add buggy change"
9a9a9a9 HEAD@{2}: commit: Add buggy change
d4d4d4d HEAD@{3}: reset: moving to d4d4d4d
...
```

Find the line from before your mistake and jump back to it:

```bash
git reset --hard f6f6f6f
git log --oneline -3          # everything is back
```

Reflog only records **committed** states. That is one more reason to commit early and often.

## 7. Other small rescues

| Need | Command |
|---|---|
| Rename or move a tracked file | `git mv old.txt new.txt` |
| Delete a tracked file | `git rm file.txt` (then commit) |
| Stop tracking but keep the file | `git rm --cached file.txt` |
| Remove untracked files (dry run first!) | `git clean -n` then `git clean -f` |
| Get one file from an older commit | `git restore --source=HEAD~2 story.txt` |

## Common mistakes

| Mistake | Fix |
|---|---|
| Used `reset --hard` and panicked | Stay calm and run `git reflog`. |
| Amended or reset a commit that was already pushed | Do not force-push on a shared branch. Use `git revert` instead. |
| `git restore` cleared an edit you wanted | Cannot be recovered. From now on check `git diff` first, or commit/stash before experimenting. |
| `git clean -f` deleted files | `git clean` is permanent. Always run `git clean -n` (dry run) first. |

## Tryouts

**Tryout 1 · Erase.** In `undo-lab`, add a line `junk` to `story.txt`, then discard it with one command. Prove it is gone.

<details class="solution">
<summary>Answer</summary>

```bash
echo "junk" >> story.txt
git restore story.txt
git status        # working tree clean
```

</details>

**Tryout 2 · Fix a message.** Commit with the message `Add chapter tow` (typo), then correct it to `Add chapter two` **without** creating an extra commit.

<details class="solution">
<summary>Answer</summary>

```bash
echo "chapter two" >> story.txt
git commit -am "Add chapter tow"
git commit --amend -m "Add chapter two"
git log --oneline -2
```

</details>

**Tryout 3 · Rescue.** Make two commits, run `git reset --hard HEAD~2`, then bring both commits back using the reflog.

<details class="solution">
<summary>Answer</summary>

```bash
echo "one" >> story.txt && git commit -am "Commit one"
echo "two" >> story.txt && git commit -am "Commit two"
git reset --hard HEAD~2
git reflog                      # find the line "commit: Commit two"
git reset --hard HEAD@{1}       # or use that commit's ID
git log --oneline -3
```

</details>

## Recap

* ✅ `git restore <file>` discards edits (permanent!). `git restore --staged <file>` un-stages.
* ✅ `git commit --amend` fixes the last commit (only if unpushed).
* ✅ `git reset --soft | --mixed | --hard` moves the branch back; hard also wipes your files.
* ✅ `git revert <commit>` safely undoes a commit by adding a new one. Use it on shared history.
* ✅ `git reflog` is the safety net for committed work.

**Next:** [Session 5 · Branches](05-branches.md).
