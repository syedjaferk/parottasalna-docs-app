# Session 6 · Finding Things

**⏱ about 60 minutes · 🧰 you need: [Session 5](05-pipes-and-text.md) done**

## The big idea

Real systems have **thousands of files**. Nobody remembers where everything is. Linux gives you two search tools that answer
two different questions:

| Question | Tool |
|---|---|
| *"Where is the **file** with this name / size / age?"* | **`find`** |
| *"Which file **contains** this text?"* | **`grep -r`** |

**Everyday example:** you lose something in a big house. You can search **by what it looks like** (`find`: *the red box, bigger than a
shoebox*) or **by what is written inside** (`grep`: *the letter that mentions "refund"*).

```{raw} html
:file: ../diagrams/l06-find-grep.html
```

```bash
cd ~/linux-lab
```

## 1. `find`: search by name, type, size, age

The pattern: **`find  WHERE  CONDITIONS  [ACTION]`**.

```bash
find . -name "*.log"
```

```text
./logs/access.log
./logs/app.log
```

* `.` = start searching **here** (use `/` for the whole system, `~` for your home).
* `-name "*.log"` = names matching the pattern. **Always quote** the pattern so the shell doesn't expand it first.

(The order of results can differ on your computer. `find` lists files in the order the disk holds them.)

### The conditions you will use most

| Condition | Meaning | Example |
|---|---|---|
| `-name "pattern"` | name matches (case-sensitive) | `-name "*.txt"` |
| `-iname "pattern"` | name matches, **ignoring case** | `-iname "README*"` |
| `-type f` / `-type d` | **f**iles only / **d**irectories only | |
| `-size +1k` / `-size -10M` | bigger than / smaller than | `-size +1k` |
| `-mtime -2` / `-mtime +30` | modified **less than 2 days** ago / **more than 30** days ago | |
| `-mmin -5` | modified in the last 5 **minutes** | |
| `-maxdepth 1` | don't go deeper than this many levels | |
| `-user asha` | owned by a user | |
| `-empty` | empty files or folders | |

```bash
find . -type f -name "*.txt"
```

```text
./data/fruits.txt
./docs/readme.txt
```

```bash
find . -type f | wc -l
```

```text
7
```

*How many files are in the lab?* Seven. (You'll see more if you've already created files in `playground`.)

```bash
find . -iname "README*"
```

```text
./docs/readme.txt
```

```bash
find . -maxdepth 1 -type d
```

```text
.
./scripts
./data
./logs
./docs
./playground
```

```bash
find . -type f -size +1k
```

```text
./logs/access.log
```

### Searching by age

```bash
touch -d "3 days ago" playground/old.txt     # make a file that looks 3 days old
touch playground/new.txt
find playground -mtime +2
```

```text
playground/old.txt
```

`-mtime +2` means *modified more than 2 days ago*. Real-world use: *"find log files older than 30 days so I can delete them."*

### Doing something with the results: `-exec`

```bash
find . -name "*.log" -exec wc -l {} \;
```

```text
60 ./logs/access.log
13 ./logs/app.log
```

`-exec COMMAND {} \;` runs the command **once for each result**; `{}` is replaced by the file name and `\;` ends the command. A friendlier alternative is a pipe to `xargs`:

```bash
find . -name "*.log" | xargs wc -l
```

:::{caution}
`find ... -exec rm {} \;` **deletes** whatever matches. First run the `find` **without** the `-exec` part to look at the list. Then add the delete.
:::

**Spaces in names?** Use `find ... -print0 | xargs -0 command` to be safe.

## 2. `grep -r`: search inside files

```bash
grep -r "order" logs docs
```

```text
logs/app.log:2026-10-15 09:07:42 ERROR payment failed for order 1042
logs/app.log:2026-10-15 09:07:43 INFO  retrying payment for order 1042
logs/app.log:2026-10-15 09:07:45 INFO  payment ok for order 1042
```

The file name comes first, then the matching line. Helpful options:

| Option | Meaning |
|---|---|
| `-r` | search **r**ecursively in folders |
| `-n` | show line **n**umbers |
| `-i` | ignore case |
| `-l` | list only the **l**ist of file names that match |
| `-c` | count matches per file |
| `--include="*.py"` | only search files with this name pattern |

```bash
grep -rl ERROR .
```

```text
./logs/app.log
```

*"Which files mention ERROR?"* One file. This is how developers find *"where is this function used?"* in a big project.

## 3. Where is that *program*? `which`, `type`, `whereis`

```bash
which bash ls grep
type cd
```

```text
/usr/bin/bash
/usr/bin/ls
/usr/bin/grep
cd is a shell builtin
```

```bash
whereis ls
```

```text
ls: /usr/bin/ls /usr/share/man/man1/ls.1.gz
```

`which` shows where a command's program is. `type` also tells you if it's a *builtin* (built into the shell, like `cd`) or an *alias*. `whereis` also finds the manual page.

## 4. Fast search by name: `locate`

`locate` searches a **pre-built index**, so it is instant, but it may not know about files created today.

```bash
sudo apt install plocate      # install once (Ubuntu/Debian)
sudo updatedb                 # refresh the index
locate readme.txt
```

Use `find` for fresh, precise searches; `locate` for *"I know part of the name, just show me."*

## 5. Size detective: `du` and `ls -S`

**Which folders are eating my disk?**

```bash
du -sh .
du -h --max-depth=1 .
```

```text
56K	.
8.0K	./scripts
12K	./data
16K	./logs
12K	./docs
4.0K	./playground
56K	.
```

| Option | Meaning |
|---|---|
| `-s` | **s**ummary: one total |
| `-h` | **h**uman-readable |
| `--max-depth=1` | show each sub-folder once |

Sort by size to find the biggest:

```bash
du -ah . | sort -rh | head -n 5
```

```bash
ls -S -lh logs        # biggest file first
```

```bash
find . -type f -printf "%s %p\n" | sort -nr | head -n 3     # biggest files by bytes (GNU find)
```

```text
4511 ./logs/access.log
652 ./logs/app.log
278 ./data/people.csv
```

## Recipe cards (copy these into your notes)

| I want to... | Command |
|---|---|
| find a file by name | `find / -name "report.pdf" 2>/dev/null` |
| find all `.py` files in this folder tree | `find . -name "*.py"` |
| find files bigger than 100 MB | `find / -type f -size +100M 2>/dev/null` |
| find files changed today | `find . -type f -mtime 0` |
| find files **containing** a word | `grep -rl "word" .` |
| count lines of code | `find . -name "*.py" \| xargs wc -l` |
| delete `.tmp` files (look first!) | `find . -name "*.tmp"` then `find . -name "*.tmp" -delete` |

(`2>/dev/null` hides the many "Permission denied" messages you get when searching the whole system. It's the same trick from Session 5.)

## Common mistakes

| Problem | Why | Fix |
|---|---|---|
| `find . -name *.log` gives odd errors | the shell expanded `*.log` first | **quote** it: `"*.log"` |
| lots of `Permission denied` lines | you searched places you can't read | add `2>/dev/null` (or use `sudo` if appropriate) |
| `find` returns nothing | wrong case or place | try `-iname`; check the starting folder |
| `grep -r` is slow / prints binary junk | it searches everything | add `--include="*.txt"`, and `-I` to skip binary files |
| `locate` can't find a new file | the index is old | `sudo updatedb` |
| `find: missing argument to '-exec'` | forgot `\;` | end with `\;` (or `+`) |
| the wrong files got deleted | you ran `-delete` before checking | **always** list first |

## Tryouts

Work in `~/linux-lab/playground`. Check with `bash ~/linux-lab/check.sh 6`.

**Tryout 1 · Warm-up.** Find all **directories** under `~/linux-lab` and count them.

<details class="solution">
<summary>Answer</summary>

```bash
find ~/linux-lab -type d | wc -l
```

(Includes `~/linux-lab` itself and anything you have created. Compare with your `tree` output.)

</details>

**Tryout 2 · Build.** Save the list of all `.log` files under `~/linux-lab` into `log-files.txt`. Then save the **number of `404` lines** in `access.log` into `count-404.txt`.

<details class="solution">
<summary>Answer</summary>

```bash
cd ~/linux-lab/playground
find ~/linux-lab -name "*.log" > log-files.txt
grep -c ' 404 ' ../logs/access.log > count-404.txt
cat log-files.txt count-404.txt
```

```text
/home/asha/linux-lab/logs/access.log
/home/asha/linux-lab/logs/app.log
7
```

</details>

**Tryout 3 · Challenge.** *Detective work.* Without opening the files, answer: (a) which file in the lab is the **biggest**? (b) which files **mention the word `Chennai`**? (c) which **path** was visited most often in `access.log`?

<details class="solution">
<summary>Answer</summary>

```bash
cd ~/linux-lab
# (a) biggest file
find . -type f -printf "%s %p\n" | sort -nr | head -n 1       # ./logs/access.log
# (b) files mentioning Chennai
grep -rl Chennai .                                            # ./data/people.csv
# (c) most visited path (column 7 of each log line)
awk '{print $7}' logs/access.log | sort | uniq -c | sort -nr | head -n 1
```

</details>

```bash
bash ~/linux-lab/check.sh 6
```

## Quiz

Take **"Session 6 · Quiz"** from the portal's **Quizzes** page.

## Recap

- ✅ `find WHERE CONDITIONS [ACTION]`: `-name`, `-iname`, `-type`, `-size`, `-mtime`, `-maxdepth`, `-exec`. **Quote patterns.**
- ✅ `grep -r` searches **inside** files (`-l` for just names, `-n` for line numbers).
- ✅ `which`, `type`, `whereis` locate programs; `locate` is the fast indexed search.
- ✅ `du -sh` / `du -h --max-depth=1` / `sort -rh` hunt disk hogs.
- ✅ **Look first, then delete.**

**Next:** [Session 7 · Users and Permissions](07-users-and-permissions.md).
