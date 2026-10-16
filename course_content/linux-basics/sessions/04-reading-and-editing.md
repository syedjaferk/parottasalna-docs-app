# Session 4 · Reading and Editing Files

**⏱ about 75 minutes · 🧰 you need: [Session 3](03-working-with-files.md) done**

## The big idea

In Linux, **almost everything is a text file**: settings, logs, scripts, even lists of users. So reading and editing text is the
most useful skill you can have. You'll learn to **look** at files (small and huge), **count** them, and **write** to them, both with
a simple editor and straight from the command line.

**Everyday example:** a library. `cat` is like photocopying a whole page onto the table. `less` is reading the book page by page.
`head` is reading only the first page. `tail` is reading the last page (and waiting for new pages to be added). `nano` is
writing in the margin with a pencil.

```{raw} html
:file: ../diagrams/l04-viewers.html
```

Your sample files for this session:

```bash
cd ~/linux-lab
ls logs data docs
```

```text
data:
fruits.txt  people.csv

docs:
notes.md  readme.txt

logs:
access.log  app.log
```

## 1. Show a file: `cat`

```bash
cat docs/readme.txt
```

```text
Welcome to the Linux lab!
This folder is safe. Break things here.
```

`cat` (short for *concatenate*) prints a file on the screen. With several files it joins them one after another:

```bash
cat docs/readme.txt docs/notes.md
```

Add `-n` to show line numbers:

```bash
cat -n docs/notes.md
```

```text
     1	# My notes
     2	
     3	- learn ls
     4	- learn cd
     5	- learn grep
```

`cat` is great for **short** files. For long ones it floods your screen. Use the next tools.

## 2. Page by page: `less`

```bash
less logs/access.log
```

You are now *inside* the reader:

| Key | Does |
|---|---|
| `Space` / `b` | next page / previous page |
| `↓` `↑` or `j` `k` | one line down / up |
| `g` / `G` | jump to the **start** / **end** |
| `/word` + `Enter` | **search** for *word*; `n` next match, `N` previous |
| `q` | **quit** |

`less` never loads the whole file into memory, so it opens even a 10 GB log instantly. (There is an older cousin called `more`. Use `less`:
"less is more".)

## 3. The first and last lines: `head` and `tail`

```bash
head -n 3 logs/access.log
```

```text
10.0.0.5 - - [15/Oct/2026:08:00:00 +0530] "GET / HTTP/1.1" 200 500
10.0.0.7 - - [15/Oct/2026:08:11:00 +0530] "GET /missing HTTP/1.1" 404 637
192.168.1.20 - - [15/Oct/2026:08:22:00 +0530] "GET /cart HTTP/1.1" 200 774
```

```bash
tail -n 2 logs/app.log
```

```text
2026-10-15 09:59:59 ERROR database connection lost
2026-10-15 10:00:02 INFO  connected to database
```

* `head -n N` shows the **first** N lines. (Default 10.)
* `tail -n N` shows the **last** N lines. (Default 10.)

### Watching a log grow: `tail -f`

`tail -f file` ("follow") **keeps running** and prints new lines as they are added. It is how admins watch a live server log.

Try it with two terminals (or two tabs). In terminal 1:

```bash
cd ~/linux-lab/playground
touch live.log
tail -f live.log
```

In terminal 2:

```bash
echo "first event" >> ~/linux-lab/playground/live.log
echo "second event" >> ~/linux-lab/playground/live.log
```

Terminal 1 instantly shows:

```text
first event
second event
```

Stop it with **Ctrl + C**. (`>>` is explained in section 6.)

## 4. Count things: `wc`

```bash
wc data/fruits.txt
```

```text
12 12 76 data/fruits.txt
```

The three numbers are **lines, words, bytes**. Ask for one at a time:

```bash
wc -l logs/*.log
```

```text
  60 logs/access.log
  13 logs/app.log
  73 total
```

| Option | Counts |
|---|---|
| `-l` | **l**ines |
| `-w` | **w**ords |
| `-c` | bytes (**c**haracters) |

## 5. Know what a file is: `file` and `stat`

```bash
file data/people.csv docs/readme.txt
```

```text
data/people.csv: CSV text
docs/readme.txt: ASCII text
```

Linux doesn't trust file extensions. `file` looks *inside* a file to tell you what it really is. `stat file` shows its details: size, permissions, timestamps.

## 6. Writing text from the command line

You met `>` in Session 1. Now the full family (**redirection**):

```{raw} html
:file: ../diagrams/l04-redirect.html
```

| You type | Effect |
|---|---|
| `command > file` | **overwrite**: the file is replaced with the output |
| `command >> file` | **append**: the output is added to the end |
| `command < file` | feed the file *into* the command |

```bash
cd ~/linux-lab/playground
echo "milk" > shopping.txt        # creates it (or empties and rewrites it!)
echo "eggs" >> shopping.txt       # adds a line
echo "bread" >> shopping.txt
cat shopping.txt
```

```text
milk
eggs
bread
```

:::{caution}
**`>` silently destroys** whatever was in the file. If you meant to *add* a line, use `>>`. This is the most common beginner accident.
:::

### Writing several lines: a "here document"

```bash
cat > notes.txt <<'EOF'
Line one
Line two
Line three
EOF
cat notes.txt
```

```text
Line one
Line two
Line three
```

Everything between `<<'EOF'` and the lone `EOF` goes into the file. Handy for creating a config file or a script in one go.

## 7. Editing with `nano`

`nano` is the friendly terminal editor: the keys are listed at the bottom of the screen.

```bash
nano shopping.txt
```

| Keys | Does |
|---|---|
| (just type) | edit text |
| `Ctrl + O` then `Enter` | **save** ("write **O**ut") |
| `Ctrl + X` | **exit** (it asks to save if you forgot) |
| `Ctrl + W` | **search** |
| `Ctrl + K` / `Ctrl + U` | **cut** a line / paste it |
| `Ctrl + G` | help |

(`^` in the bottom bar means the Ctrl key.) Add *"rice"* and *"tea"* to the list, save and exit. Then:

```bash
cat shopping.txt
```

## 8. `vim` survival guide (you will meet it)

Many servers have **vim** (or `vi`) as the default editor. It is powerful but strange: it has **modes**. You only need to
survive:

| Step | Keys |
|---|---|
| open a file | `vim file.txt` |
| start typing | press **`i`** (insert mode) |
| stop typing | press **`Esc`** |
| **save and quit** | `Esc`, then type `:wq` and press `Enter` |
| **quit without saving** | `Esc`, then `:q!` and `Enter` |

If you get stuck in vim: press **Esc** a few times, then type `:q!` and Enter. 😄

## Common mistakes

| Problem | Why | Fix |
|---|---|---|
| my file became empty | you used `>` on an existing file | use `>>` to add; check before overwriting |
| `cat` flooded the screen | file is huge | use `less`, `head` or `tail` |
| `less` seems stuck | you're inside it | press **q** |
| `nano: command not found` | not installed (minimal systems) | `sudo apt install nano` |
| `tail -f` never ends | that's what `-f` does | **Ctrl + C** |
| accents/emoji look broken | wrong encoding | files should be UTF-8 |
| vim "won't let me type" | you're in normal mode | press `i` first |

## Tryouts

Work in `~/linux-lab/playground`. Check with `bash ~/linux-lab/check.sh 4`.

**Tryout 1 · Warm-up.** How many lines are in `logs/app.log`? How many **words** are in `docs/readme.txt`? (Use `wc` with the right option.)

<details class="solution">
<summary>Answer</summary>

```bash
wc -l ~/linux-lab/logs/app.log        # 13 lines
wc -w ~/linux-lab/docs/readme.txt     # 12 words
```

</details>

**Tryout 2 · Build.** Create `shopping.txt` with **five** items, one per line, using `>` for the first and `>>` for the rest. Then make a copy (`cp shopping.txt shopping2.txt`), open the **copy** in `nano`, add a sixth item and save. (The checker looks for exactly five lines in `shopping.txt`, so practise editing on the copy.)

<details class="solution">
<summary>Answer</summary>

```bash
cd ~/linux-lab/playground
echo "milk"  > shopping.txt
echo "eggs"  >> shopping.txt
echo "bread" >> shopping.txt
echo "tea"   >> shopping.txt
echo "rice"  >> shopping.txt
wc -l shopping.txt          # 5 shopping.txt
cp shopping.txt shopping2.txt
nano shopping2.txt
```

</details>

**Tryout 3 · Challenge.** Using `head`, `tail` and `>`: save the **first 3 lines** of `logs/app.log` into `summary.txt`, and the **last 2 lines** into `last-lines.txt` (both in the playground).

<details class="solution">
<summary>Answer</summary>

```bash
cd ~/linux-lab/playground
head -n 3 ../logs/app.log > summary.txt
tail -n 2 ../logs/app.log > last-lines.txt
cat summary.txt last-lines.txt
```

(`..` goes up from `playground` to `linux-lab`.)

</details>

```bash
bash ~/linux-lab/check.sh 4
```

## Quiz

Take **"Session 4 · Quiz"** from the portal's **Quizzes** page.

## Recap

- ✅ `cat` (whole file), `less` (page by page, **q** quits), `head`/`tail` (ends), `tail -f` (follow a live log).
- ✅ `wc -l/-w/-c` counts; `file` tells you what a file really is.
- ✅ `>` overwrites, `>>` appends, `<<'EOF'` writes many lines.
- ✅ `nano`: **Ctrl + O** save, **Ctrl + X** exit. `vim`: **i** to type, **Esc** `:wq` to save, `:q!` to escape.

**Next:** [Session 5 · Pipes and Text](05-pipes-and-text.md), the superpower: combine tiny commands into powerful ones.
