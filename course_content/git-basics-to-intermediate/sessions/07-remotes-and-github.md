# Session 7 · Remotes and GitHub

**⏱ about 75 minutes · 🧰 you need: [Session 6](06-merging-and-conflicts.md) done, a free GitHub account**

## The big idea

So far everything lived on **your computer**. To work with other people, or just to keep a backup, you need a copy somewhere else that everyone can reach. That shared copy is called a **remote**, and the most popular home for remotes is **GitHub**.

**Everyday example:** a shared Google Drive folder. Everyone keeps a working copy on their own laptop; the Drive folder is the "official" copy. You **upload** (push) your changes and **download** (pull) other people's.

Git is **distributed**: every clone is a *complete* repository with the whole history. The remote is not special technically. It is simply the copy everyone agrees to share.

```{raw} html
:file: ../diagrams/g07-remote.html
```

## 1. The vocabulary

| Word | Meaning |
|---|---|
| **remote** | a named link to another copy of the repo (usually on GitHub) |
| **origin** | the default name of the remote you cloned from |
| **clone** | download a whole repo (and its history) for the first time |
| **push** | upload your commits to the remote |
| **fetch** | download new commits from the remote, but **do not** touch your files or branches |
| **pull** | fetch **plus** merge into your current branch |
| **upstream** (branch) | the remote branch your local branch is linked to, e.g. `origin/main` |

## 2. Create a repo on GitHub

1. Log in to [github.com](https://github.com) and click **New** (top left, green) → *Create a new repository*.
2. Name it `hello-git`. Keep it **Public** (or Private). **Do not** tick "Add a README" (we already have code to push).
3. Click **Create repository**. GitHub shows you the commands below.

## 3. Connect with SSH (once per computer)

GitHub needs to know it is really you. The safest way for daily use is an **SSH key**: a matched pair of files, a *private* key that stays on your computer (never share it), and a *public* key you give to GitHub, like a lock you hand out whose only key you keep.

```bash
ssh-keygen -t ed25519 -C "asha@example.com"
```

Press Enter to accept the default location. A passphrase is optional but recommended. Then show the **public** key:

```bash
cat ~/.ssh/id_ed25519.pub
```

```text
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... asha@example.com
```

Copy the whole line. On GitHub: **Settings → SSH and GPG keys → New SSH key**, paste it, save. Test:

```bash
ssh -T git@github.com
```

```text
Hi asha-kumar! You've successfully authenticated, but GitHub does not provide shell access.
```

:::{important}
Copy only the file ending in **`.pub`**. The file *without* `.pub` is your private key. Never paste it anywhere.
:::

:::{note}
**HTTPS instead of SSH:** you can use `https://github.com/you/repo.git` URLs. GitHub no longer accepts account passwords for Git; you need a **personal access token** (Settings → Developer settings → Tokens) or the *GitHub CLI* (`gh auth login`). SSH avoids this, which is why we use it here.
:::

## 4. Push an existing project to GitHub

Make a small local repo (or reuse one), then link it to the empty GitHub repo:

```bash
cd ~/git-lab
mkdir hello-git && cd hello-git
git init
echo "# Hello Git" > README.md
git add . && git commit -m "Add readme"

git remote add origin git@github.com:YOUR-USERNAME/hello-git.git
git remote -v
```

```text
origin	git@github.com:asha-kumar/hello-git.git (fetch)
origin	git@github.com:asha-kumar/hello-git.git (push)
```

`git remote add <name> <url>` just saves a nickname for a URL. Now upload:

```bash
git push -u origin main
```

```text
Enumerating objects: 3, done.
Writing objects: 100% (3/3), 220 bytes | 220.00 KiB/s, done.
To github.com:asha-kumar/hello-git.git
 * [new branch]      main -> main
branch 'main' set up to track 'origin/main'.
```

* `origin` = which remote. `main` = which branch.
* `-u` (*set upstream*) links your local `main` to `origin/main`, so later a plain `git push` and `git pull` work with no extra words. You need `-u` only the first time for each branch.

Refresh the GitHub page: your README is there. 🎉

## 5. Clone: get a project that exists on GitHub

```bash
cd ~/git-lab
git clone git@github.com:YOUR-USERNAME/hello-git.git hello-git-copy
cd hello-git-copy
git log --oneline
git remote -v
```

`git clone` downloads everything, checks out the default branch and sets `origin` for you. The last argument is the folder name (optional).

## 6. The daily loop with a remote

```text
git pull          ← start of day: get what others did
 ... edit, git add, git commit ...
git push          ← share your commits
```

Try it. In `hello-git-copy`:

```bash
echo "Learning Git!" >> README.md
git commit -am "Update readme from the copy"
git push
```

Now pretend to be a teammate who uses the *other* folder (`hello-git`):

```bash
cd ~/git-lab/hello-git
git pull
```

```text
Updating 2a2a2a2..3b3b3b3
Fast-forward
 README.md | 1 +
 1 file changed, 1 insertion(+)
```

## 7. Fetch vs pull

`git pull` is really two commands in one:

```{raw} html
:file: ../diagrams/g07-fetchpull.html
```

```bash
git fetch                 # download new commits; nothing in your folder changes
git log --oneline main..origin/main    # peek at what is new
git merge origin/main     # now bring them in (git pull = these two steps)
```

| | `git fetch` | `git pull` |
|---|---|---|
| Downloads new commits | ✅ | ✅ |
| Changes your branch and files | ❌ | ✅ (merges) |
| Risk of conflicts | none | possible |
| Use it when | you want to **look before you merge** | you just want to catch up |

`origin/main` is a **remote-tracking branch**: your computer's last-known picture of `main` on GitHub. It only updates when you fetch, pull or push.

## 8. When a push is rejected

```bash
git push
```

```text
 ! [rejected]        main -> main (fetch first)
error: failed to push some refs to 'github.com:asha-kumar/hello-git.git'
hint: Updates were rejected because the remote contains work that you do not
hint: have locally. ...
```

Meaning: *someone pushed before you*. Git will not let you overwrite their work. The fix is always the same:

```bash
git pull        # merge their work in (resolve conflicts if any)
git push
```

:::{danger}
**Never use `git push --force` on a shared branch** (it overwrites other people's commits). When you truly must (for example after rebasing your *own* feature branch), use the safer form `git push --force-with-lease`, which refuses if someone else pushed in the meantime.
:::

## 9. Working with remote branches

```bash
git switch -c feature/login          # create locally
git push -u origin feature/login     # publish it
git branch -a                        # list local + remote branches
git switch feature/login             # (on another computer) after git fetch, creates a tracking branch
git push origin --delete feature/login    # delete a remote branch
git remote prune origin              # forget remote branches that were deleted
```

## 10. Authentication and other remotes

| Task | Command |
|---|---|
| See remotes | `git remote -v` |
| Add another remote | `git remote add upstream <url>` |
| Change a URL (for example HTTPS → SSH) | `git remote set-url origin git@github.com:you/repo.git` |
| Rename a remote | `git remote rename origin github` |
| Remove a remote | `git remote remove upstream` |

## Common mistakes

| Mistake | Fix |
|---|---|
| `Permission denied (publickey)` | SSH key not added to GitHub, or you copied the wrong file. Re-check Step 3 and `ssh -T git@github.com`. |
| `remote origin already exists` | You already added it. Use `git remote set-url origin <url>`. |
| `fatal: not a git repository` | You are in the wrong folder. `cd` into the project. |
| `src refspec main does not match any` | You have no commits yet (or your branch is named `master`). Commit first; check `git branch`. |
| Committing the `.env` / passwords and pushing | The secret is now public. Rotate the secret immediately, then see Session 12. |
| Pulling with uncommitted changes | Commit or stash first. |

## Tryouts

**Tryout 1 · Publish.** Push a repo to GitHub with a README and one more file. Confirm both are visible on the website.

<details class="solution">
<summary>Answer</summary>

```bash
echo "print('hi')" > app.py
git add app.py && git commit -m "Add app.py"
git push
```

Refresh the repository page on GitHub.

</details>

**Tryout 2 · Two copies.** Using the two folders (`hello-git` and `hello-git-copy`), make a change in each (to *different* files), push from one, and pull in the other. Then make a change to the same line in both and see what happens on the second push.

<details class="solution">
<summary>Answer</summary>

1. Edit `a.txt` in one folder, commit, push. Edit `b.txt` in the other, commit, `git pull` (clean merge), `git push`.
2. Edit line 1 of `README.md` differently in both and commit in both. Push from the first. In the second `git push` is rejected; run `git pull`, get a **conflict**, resolve it as in Session 6, commit, push.

</details>

**Tryout 3 · Look before you leap.** Make a commit in one folder and push it. In the other folder use `git fetch` and `git log main..origin/main --oneline` to see it *without* changing your files. Then `git merge origin/main`.

<details class="solution">
<summary>Answer</summary>

```bash
git fetch
git log main..origin/main --oneline     # shows the new commit
git status                              # "Your branch is behind 'origin/main' by 1 commit"
git merge origin/main
```

</details>

## Recap

* ✅ A **remote** is a shared copy of the repo; `origin` is the usual name. GitHub hosts them.
* ✅ SSH keys prove who you are: **public** key to GitHub, **private** key stays with you.
* ✅ `git clone` (first time), `git push` (upload), `git pull` (fetch + merge), `git fetch` (look only).
* ✅ `git push -u origin <branch>` links a branch to its remote twin.
* ✅ A rejected push means: `git pull` first. Avoid `--force`.

**Next:** [Session 8 · Collaborating](08-collaborating.md).
