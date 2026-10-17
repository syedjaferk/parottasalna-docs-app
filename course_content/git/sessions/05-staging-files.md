# Session 5 · Adding and staging files

## The big idea

Git does not save everything you changed automatically. You pick what goes into the next snapshot by
**staging** it with `git add`, then `git commit` saves exactly what is staged. The **staging area** lets you build
a clean, focused commit even when you have touched many files.

**Everyday example:** packing a courier box. Your desk has many things on it (the working folder). You choose
only the items for this order, put them in the box (staging), check the box, and then seal and label it
(commit). Everything else stays on the desk for another box.

```{raw} html
:file: ../diagrams/three-areas.html
```

## Staging in practice

```{literalinclude} ../code/05-staging.sh
:language: bash
```

```{literalinclude} ../code/05-staging.out
:language: text
```

Reading `git status -s` (short status): the **left column** is the staging area, the **right column** is the
working folder.

| Code | Meaning |
|---|---|
| `??` | New file Git has never seen (untracked) |
| `A ` | New file staged for the next commit |
| `M ` | Modified and staged |
| ` M` | Modified but not staged |
| `MM` | Staged, and then modified again |

What the demo did:

1. **`git add style.css`** staged one file; `app.js` and `README.md` stayed `??`.
2. **`git add -- ':!README.md'`** staged everything except `README.md`. The `:!` is a *pathspec exclude*. Now only
   `README.md` is `??`.
3. **`git add -p`** showed the edited file one **hunk** (a block of changes) at a time. We changed line 1 and line
   20, which are far apart, so Git asked twice: `y` for the first, `n` for the second. The result `MM` means part of the file is
   staged and part is not.
4. **`git restore --staged style.css`** took the file back out of the staging area. Its edits are kept in the
   working folder (` M`).

## Useful variations

| Command | Stages |
|---|---|
| `git add FILE` | One file |
| `git add .` | Everything in this folder and below |
| `git add -u` | Only files Git already tracks (changes and deletions) |
| `git add '*.css'` | Files matching a pattern (quote it) |
| `git add -p` | Chosen hunks, with a prompt for each |
| `git restore --staged FILE` | Un-stage (keeps the edits) |

## Common mistakes

- **`git add .` without looking first.** It will happily stage logs, passwords and build output. Run `git status`
  before and after.
- **Thinking `git add` saves the file.** It only stages it. Nothing is stored in history until `git commit`.
- **Editing after staging.** Git stages the file *as it was when you added it*. Edit it again and it shows `MM`;
  add it again to include the new edits.
- **Misreading the two status columns.** Left is staged, right is not staged.
- **Using `git checkout .` or `git restore .` to "un-stage".** Those throw away your edits. To un-stage use
  `git restore --staged`.

## Hands-on exercises

**Exercise 1.** Create `app.js`, `style.css` and `README.md`. Stage only `style.css` and show the short status.

<details class="solution"><summary>Solution</summary>

```bash
touch app.js style.css README.md
git add style.css
git status -s
```

Output: `A  style.css`, then `?? README.md` and `?? app.js`.

</details>

**Exercise 2.** Stage every file except `README.md` using a pathspec.

<details class="solution"><summary>Solution</summary>

```bash
git add -- ':!README.md'
git status -s
```

`app.js` and `style.css` show `A `, and `README.md` stays `??`.

</details>

**Exercise 3.** Edit a committed file in two places far apart and stage only the first change with `git add -p`.

<details class="solution"><summary>Solution</summary>

```bash
seq -f 'line %g' 1 20 > style.css && git add style.css && git commit -m "Add styles"
sed -i -e '1s/.*/line 1 (edited)/' -e '20s/.*/line 20 (edited)/' style.css
git add -p style.css      # answer y for the first hunk, n for the second
git status -s             # MM style.css
```

`git diff --staged` then shows only the line 1 change, and plain `git diff` shows the line 20 change.

</details>

## Practice

Take the **Session 5 quiz**. The original *Q2 Adding and Staging Files* page is in the reference section.
