# Session 6 · Ways to exclude files

## The big idea

Some files should never go into a repository: passwords, logs, build output, editor settings, the
`node_modules` folder. A **`.gitignore`** file lists patterns for files Git should pretend not to see.
Ignored files do not show in `git status` and `git add .` skips them.

**Everyday example:** the "do not photocopy" tray at an office. Confidential papers, rough drafts and the
tea-stained scribbles go in it. When someone says "copy everything on my desk", the clerk skips that tray.

```{raw} html
:file: ../diagrams/ignore-flow.html
```

## Ignore rules at work

```{literalinclude} ../code/06-ignore.sh
:language: bash
```

```{literalinclude} ../code/06-ignore.out
:language: text
```

Reading the output:

- **Before `.gitignore`** seven things appear as untracked, including `secrets.env` and the `build/` folder.
- **After**, only `.gitignore`, `app.py` and `important.txt` remain. `important.txt` survived thanks to the
  negation rule `!important.txt`, which re-includes a file that `*.txt` would have ignored.
- **`git check-ignore -v`** tells you *which rule in which line* ignores a file, the quickest way to debug a
  pattern. For `important.txt` it printed nothing and exit code 1, meaning "not ignored".
- **`git status --ignored`** lists the ignored files (marked `!!`) in case you want to see them.
- **The `secrets.env` trap.** We force-added it and committed, and *then* ignore rules stopped working for it:
  editing it showed ` M secrets.env`. An ignore rule only affects **untracked** files.
- **`git rm --cached`** removed it from Git's tracking but kept the file on disk; after that it is ignored again.
  (If a secret was already pushed, assume it is public: change the password. Removing it from history is a
  separate, harder job.)
- **`.git/info/exclude`** works like `.gitignore` but is private to your clone and is never committed. The
  `scratch/` folder is hidden from `git status` without touching the shared file.

## Pattern cheat sheet

| Pattern | Matches |
|---|---|
| `*.log` | Any file ending in `.log`, in any folder |
| `build/` | The folder `build` and everything inside |
| `/todo.txt` | Only `todo.txt` in the top folder |
| `!important.txt` | Re-include a file an earlier rule ignored |
| `docs/**/*.pdf` | PDFs anywhere under `docs` |
| `# comment` | A comment line |

Three places for rules: the project's `.gitignore` (shared with the team, committed), `.git/info/exclude`
(just you, this clone) and a global file (`git config --global core.excludesFile ~/.gitignore_global`) for things
like `.DS_Store` that you never want in any repository.

## Other ways to leave files out of one commit

- `git add -- ':!README.md'` skips a file for this `add` only (Session 5).
- `git restore --staged FILE` takes it back out of the staging area.
- `git update-index --skip-worktree FILE` asks Git to stop noticing local edits to a **tracked** file, handy for a
  personal copy of a config file. Undo with `--no-skip-worktree`.

## Common mistakes

- **Adding the pattern after the file is committed.** It has no effect; use `git rm --cached` as shown.
- **Ignoring `.gitignore` itself.** You want it committed so teammates get the same rules.
- **Expecting `*.txt` to be re-included by a later `!file` inside an ignored folder.** If a *folder* is ignored,
  Git never looks inside it, so a negation for a file inside will not work.
- **Committing secrets "just once".** Once pushed, treat the secret as leaked.
- **Writing `build` when you mean `build/`.** Without the slash it also matches a *file* called `build`.

## Hands-on exercises

**Exercise 1.** Ignore all `.log` files and the `dist/` folder. Prove it with `git check-ignore -v`.

<details class="solution"><summary>Solution</summary>

```bash
printf '*.log\ndist/\n' > .gitignore
touch app.log && mkdir dist && touch dist/bundle.js
git check-ignore -v app.log dist/bundle.js
```

It prints the rule and line for each: `.gitignore:1:*.log	app.log` and `.gitignore:2:dist/	dist/bundle.js`.

</details>

**Exercise 2.** Ignore every `.txt` file except `keep.txt`.

<details class="solution"><summary>Solution</summary>

```bash
printf '*.txt\n!keep.txt\n' > .gitignore
touch a.txt keep.txt
git status -s
```

`a.txt` is hidden; `keep.txt` (and `.gitignore`) show as `??`.

</details>

**Exercise 3.** You committed `.env` by mistake. Stop tracking it but keep it on your disk.

<details class="solution"><summary>Solution</summary>

```bash
echo ".env" >> .gitignore
git rm --cached .env
git add .gitignore
git commit -m "Stop tracking .env"
```

The file remains in the folder, is ignored from now on, and the commit removes it from the project going forward. If it
contained a real password, change that password, because it is still in the earlier history.

</details>

## Practice

Take the **Session 6 quiz**. The original *Ways to Exclude Files in Git* page is in the reference section.
