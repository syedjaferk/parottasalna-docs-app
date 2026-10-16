# Session 3 · Working with Files

**⏱ about 75 minutes · 🧰 you need: [Session 2](02-files-and-directories.md) done**

## The big idea

You know where things are. Now you'll **make, copy, move, rename and delete** them. Five small commands do almost all file
work in Linux:

| Command | Means | Everyday comparison |
|---|---|---|
| `mkdir` | **m**a**k**e **dir**ectory | buying a new empty folder |
| `touch` | create an empty file (or refresh its timestamp) | putting a blank sheet in the folder |
| `cp` | **c**o**p**y | photocopying a paper |
| `mv` | **m**o**v**e (and **rename**) | moving a paper to another folder, or relabelling it |
| `rm` | **r**e**m**ove | putting a paper into a shredder |

```{raw} html
:file: ../diagrams/l03-copy-move.html
```

:::{important}
**`rm` has no recycle bin.** When you delete, it's gone. So we learn it *last*, and we practise only inside
`~/linux-lab/playground`. Before pressing Enter on any `rm`, read the command twice.
:::

Start every exercise in the sandbox:

```bash
cd ~/linux-lab/playground
```

## 1. Make folders: `mkdir`

```bash
mkdir projects
mkdir -p projects/website/css
ls projects
```

```text
website
```

* `mkdir name` makes one folder.
* `mkdir -p a/b/c` makes **the whole chain**, and doesn't complain if parts already exist.

## 2. Make files: `touch`

```bash
cd projects/website
touch index.html about.html
ls
```

```text
about.html  css  index.html
```

`touch` creates an **empty** file. (If the file exists, `touch` just updates its "last modified" time.) You can create many at once:

```bash
touch notes1.txt notes2.txt notes3.txt
```

## 3. Copy: `cp`

```bash
cp index.html home.html
ls
```

```text
about.html  css  home.html  index.html  notes1.txt  notes2.txt  notes3.txt
```

The pattern is **`cp  SOURCE  DESTINATION`**.

```bash
cp -v index.html css/       # copy INTO a folder, and be verbose
```

```text
'index.html' -> 'css/index.html'
```

**Copying a folder** needs `-r` (**r**ecursive: the folder *and everything inside it*):

```bash
cd ..
cp -r website website-backup
ls
```

```text
website  website-backup
```

Without `-r`:

```text
cp: -r not specified; omitting directory 'website'
```

## 4. Move and rename: `mv`

`mv` does **two jobs** with the same command:

```bash
cd website
mv home.html main.html           # RENAME (same folder, new name)
mv about.html css/               # MOVE into a folder
ls
```

```text
css  index.html  main.html  notes1.txt  notes2.txt  notes3.txt
```

* If the destination is an **existing folder**, the file is **moved into it**.
* Otherwise the destination is the **new name**.
* `mv -v` shows what it did: `renamed 'home.html' -> 'main.html'`.
* A moved file **disappears from the old place**. (Compare: `cp` leaves the original.)

## 5. Wildcards: act on many files at once

The shell expands special characters *before* the command runs:

| Wildcard | Matches | Example |
|---|---|---|
| `*` | **any** characters (including none) | `ls *.txt` → all files ending in `.txt` |
| `?` | **exactly one** character | `ls notes?.txt` → `notes1.txt`, `notes2.txt` ... |
| `[abc]` | **one** of the listed characters | `ls notes[12].txt` → only 1 and 2 |
| `[0-9]` | one character in a range | `ls notes[0-9].txt` |

```bash
ls *.txt
```

```text
notes1.txt  notes2.txt  notes3.txt
```

```bash
mkdir notes
mv notes*.txt notes/
ls notes
```

```text
notes1.txt  notes2.txt  notes3.txt
```

`mv notes*.txt notes/` moved **three** files with one command.

**Brace expansion** `{a,b,c}` is a shortcut for typing lists:

```bash
mkdir -p ~/linux-lab/playground/demo/{css,js,images}
touch ~/linux-lab/playground/demo/report-{jan,feb,mar}.txt
ls ~/linux-lab/playground/demo
```

```text
css  images  js  report-feb.txt  report-jan.txt  report-mar.txt
```

## 6. Delete: `rm` and `rmdir` (carefully!)

```bash
cd ~/linux-lab/playground/demo
rm report-jan.txt
ls
```

```text
css  images  js  report-feb.txt  report-mar.txt
```

| Command | Does | Notes |
|---|---|---|
| `rm file` | deletes a file | **permanent** |
| `rm -i file` | asks first: *remove 'file'?* | great while learning |
| `rm -v file` | tells you what it removed | |
| `rmdir folder` | deletes an **empty** folder only | the safe one |
| `rm -r folder` | deletes a folder **and everything in it** | dangerous |

```bash
rmdir css
```

(works, `css` is empty). But try a folder with something inside:

```bash
mkdir -p tmp/x
rmdir tmp
```

```text
rmdir: failed to remove 'tmp': Directory not empty
```

`rmdir` protects you. To remove it anyway, you must say so clearly:

```bash
rm -r tmp
```

:::{caution}
**The three deadliest habits:**

1. `rm -rf /` or `rm -rf ~`: deletes the whole system or your whole home. (Modern systems block `/`, but not `~`.)
2. `rm -rf $FOLDER/*` when `$FOLDER` is **empty**: becomes `rm -rf /*`.
3. **Wildcards in `rm`:** `rm *` removes everything *here*. Always run `ls *` **first** to see what a wildcard will match, then repeat the pattern with `rm`.

**Safe habit:** `ls pattern` → check → `rm pattern`. When unsure, use `rm -i`.
:::

## 7. Quotes: spaces and special characters

```bash
touch "my file.txt"       # one file with a space
ls
rm "my file.txt"
```

| Quotes | Behaviour |
|---|---|
| `"double"` | keeps spaces together; **variables are replaced** (`"$HOME"` becomes your home path) |
| `'single'` | **everything is literal** (`'$HOME'` stays `$HOME`) |
| `\ ` (backslash) | "treat the next character as plain text" (`my\ file.txt`) |

## Putting it together: a small website folder

```bash
cd ~/linux-lab/playground
mkdir -p projects/website/{css,js,images}
touch projects/website/index.html projects/website/style.css
mv projects/website/style.css projects/website/css/
cp -r projects/website projects/website-backup
ls -R projects/website
```

```text
projects/website:
css  images  index.html  js

projects/website/css:
style.css

projects/website/images:

projects/website/js:
```

## Common mistakes

| You saw | Meaning | Fix |
|---|---|---|
| `cp: cannot stat 'a.txt': No such file or directory` | the source doesn't exist *here* | `ls` to check the name and place |
| `cp: -r not specified; omitting directory` | copying a folder | add `-r` |
| `mv: cannot stat ...` | wrong source name | check spelling (case!) |
| `rm: cannot remove 'x': Is a directory` | `rm` alone doesn't delete folders | `rmdir x` (empty) or `rm -r x` |
| `touch: cannot touch ...: No such file or directory` | the **folder** doesn't exist | `mkdir -p` it first |
| `mv` overwrote my file! | `mv` and `cp` silently replace existing files | use `mv -i` / `cp -i` to be asked |
| `mkdir: cannot create directory ‘a/b’: No such file` | the parent `a` doesn't exist | `mkdir -p a/b` |

## Tryouts

Work inside `~/linux-lab/playground`. Check with `bash ~/linux-lab/check.sh 3`.

**Tryout 1 · Warm-up.** Create `practice/` with files `one.txt`, `two.txt`, `three.txt` **in one `touch` command**, then list only the `.txt` files with a wildcard.

<details class="solution">
<summary>Answer</summary>

```bash
mkdir practice && cd practice
touch one.txt two.txt three.txt
ls *.txt
```

</details>

**Tryout 2 · Build.** Build the website folder from the *"Putting it together"* section: `projects/website` with `css`, `js`, `images`, an `index.html`, and `style.css` **moved** into `css/`. Then make a **backup copy** `projects/website-backup`.

<details class="solution">
<summary>Answer</summary>

```bash
cd ~/linux-lab/playground
mkdir -p projects/website/{css,js,images}
touch projects/website/index.html projects/website/style.css
mv projects/website/style.css projects/website/css/
cp -r projects/website projects/website-backup
```

</details>

**Tryout 3 · Challenge.** Create an empty folder `projects/old`, then delete it with the **safest** command (the one that refuses to remove folders with content). Then confirm it's gone.

<details class="solution">
<summary>Answer</summary>

```bash
mkdir projects/old
rmdir projects/old
ls projects
```

`rmdir` only removes **empty** folders, so a typo can't destroy your data.

</details>

```bash
bash ~/linux-lab/check.sh 3
```

## Quiz

Take **"Session 3 · Quiz"** from the portal's **Quizzes** page.

## Recap

- ✅ `mkdir` (add `-p` for chains), `touch`, `cp` (add `-r` for folders), `mv` (move **and** rename), `rm`, `rmdir`.
- ✅ Wildcards `*` `?` `[ ]` and braces `{a,b}` act on many files at once.
- ✅ Quote names with spaces; `"double"` expands variables, `'single'` doesn't.
- ✅ **No recycle bin.** `ls` the wildcard first, use `rm -i` when unsure, prefer `rmdir`.

**Next:** [Session 4 · Reading and Editing Files](04-reading-and-editing.md).
