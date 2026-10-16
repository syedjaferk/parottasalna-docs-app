# Session 5 · Pipes and Text

**⏱ about 90 minutes · 🧰 you need: [Session 4](04-reading-and-editing.md) done**

## The big idea

Linux commands are tiny and each does **one thing well**: `sort` sorts, `grep` filters, `wc` counts. The magic is the **pipe**
`|`, which connects the output of one command to the input of the next. Chain three small tools and you can answer real questions
about a million-line log in one line.

**Everyday example:** a factory assembly line. One worker takes the raw material and passes it along; the next worker sorts it; the
next one counts it. No single worker does everything, but together they produce the result.

```{raw} html
:file: ../diagrams/l05-pipe.html
```

```bash
cd ~/linux-lab
```

## 1. Three streams: input, output, errors

Every command has three "pipes" attached to it:

| Stream | Number | Default | Meaning |
|---|---|---|---|
| **stdin** | 0 | keyboard | where input comes **from** |
| **stdout** | 1 | screen | where normal **results** go |
| **stderr** | 2 | screen | where **error messages** go |

```{raw} html
:file: ../diagrams/l05-streams.html
```

You can redirect each one:

| You type | Effect |
|---|---|
| `cmd > file` | stdout → file (overwrite) |
| `cmd >> file` | stdout → file (append) |
| `cmd 2> errors.txt` | only **errors** → file |
| `cmd > out.txt 2>&1` | **both** → the same file |
| `cmd > /dev/null` | throw the output away (`/dev/null` is a black hole) |
| `cmd 2> /dev/null` | hide the error messages |

```bash
ls data nothing-here
```

```text
ls: cannot access 'nothing-here': No such file or directory
data:
fruits.txt  people.csv
```

```bash
ls data nothing-here 2> /dev/null
```

```text
data:
fruits.txt  people.csv
```

The error message vanished; the real result stayed.

## 2. The pipe `|`

```bash
cat data/fruits.txt | wc -l
```

```text
12
```

`cat` sent the 12 fruits into `wc -l`, which counted them. The output of the left command is the input of the right command. You can chain
as many as you like.

## 3. `grep`: find lines that match

`grep PATTERN file` prints only the lines containing the pattern.

```bash
grep ERROR logs/app.log
```

```text
2026-10-15 09:07:42 ERROR payment failed for order 1042
2026-10-15 09:31:12 ERROR cannot send email to user chitra
2026-10-15 09:59:59 ERROR database connection lost
```

| Option | Meaning | Example |
|---|---|---|
| `-i` | **i**gnore case | `grep -i user logs/app.log` |
| `-v` | in**v**ert: lines that do **not** match | `grep -v INFO logs/app.log` |
| `-c` | **c**ount matching lines | `grep -c ERROR logs/app.log` → `3` |
| `-n` | show line **n**umbers | `grep -n WARN logs/app.log` |
| `-r` | **r**ecursive: search a whole folder | `grep -r "order" logs/` |
| `-w` | match whole **w**ords only | |
| `-E` | extended patterns (`a\|b`) | `grep -E "ERROR\|WARN" logs/app.log` |

```bash
grep -n WARN logs/app.log
```

```text
3:2026-10-15 09:02:11 WARN  slow query took 2.4s
8:2026-10-15 09:15:09 WARN  disk usage at 81%
```

```bash
grep -v INFO logs/app.log
```

```text
2026-10-15 09:02:11 WARN  slow query took 2.4s
2026-10-15 09:07:42 ERROR payment failed for order 1042
2026-10-15 09:15:09 WARN  disk usage at 81%
2026-10-15 09:31:12 ERROR cannot send email to user chitra
2026-10-15 09:59:59 ERROR database connection lost
```

`grep` also works on a pipe: `command | grep word`. It is the most-used filter on Linux.

## 4. `sort` and `uniq`: order and count

```bash
sort data/fruits.txt | head -n 4
```

```text
apple
apple
apple
banana
```

`uniq` removes **neighbouring** duplicates, so you **sort first**. `uniq -c` adds a count:

```bash
sort data/fruits.txt | uniq -c
```

```text
      3 apple
      2 banana
      2 cherry
      1 grape
      1 kiwi
      2 mango
      1 orange
```

Sort that by the count, biggest first:

```bash
sort data/fruits.txt | uniq -c | sort -nr
```

```text
      3 apple
      2 mango
      2 cherry
      2 banana
      1 orange
      1 kiwi
      1 grape
```

| `sort` option | Meaning |
|---|---|
| (none) | alphabetical |
| `-n` | sort as **n**umbers (so 10 comes after 9) |
| `-r` | **r**everse |
| `-u` | keep only **u**nique lines |
| `-k2` | sort by the 2nd column |

**The "count and rank" pattern `sort | uniq -c | sort -nr` is one of the most useful lines in Linux.** Learn it by heart.

## 5. Columns: `cut` and `awk`

The CSV table `data/people.csv` has fields separated by commas.

```bash
cut -d, -f1,2 data/people.csv | head -n 4
```

```text
name,city
Asha,Chennai
Bala,Madurai
Chitra,Chennai
```

* `-d,` the **d**elimiter is a comma.
* `-f1,2` keep **f**ields 1 and 2.

For anything smarter, use **`awk`**, a tiny programming language for columns. `awk -F, '{print $1}'` means *"fields separated by comma; print field 1"*:

```bash
awk -F, 'NR>1 {print $1, $3}' data/people.csv | head -n 3
```

```text
Asha 29
Bala 34
Chitra 41
```

(`NR>1` skips the header line, `$1` is column 1, `$3` is column 3.) Awk can also **filter by a number**:

```bash
awk -F, 'NR>1 && $3>35 {print $1}' data/people.csv
```

```text
Chitra
Farook
Hari
Jeeva
```

*"Names of people older than 35."* One line.

## 6. Replace text: `tr` and `sed`

```bash
tr a-z A-Z < docs/readme.txt
```

```text
WELCOME TO THE LINUX LAB!
THIS FOLDER IS SAFE. BREAK THINGS HERE.
```

`tr` translates single characters (here, lowercase to uppercase). `sed 's/old/new/'` **replaces** text:

```bash
sed 's/INFO/information/' logs/app.log | head -n 2
```

```text
2026-10-15 09:00:01 information  server started on port 8080
2026-10-15 09:00:05 information  connected to database
```

(`s/old/new/` replaces the **first** match on each line; add `g` at the end, `s/old/new/g`, for **all** matches. Sed doesn't change the file unless you use `-i`.)

## 7. Real questions about real logs

Now combine everything. `logs/access.log` is a web-server log. Column 9 is the HTTP **status code**, column 1 the visitor's **IP address**.

**How often does each status code appear?**

```bash
awk '{print $9}' logs/access.log | sort | uniq -c | sort -nr
```

```text
     34 200
      7 500
      7 404
      6 403
      6 301
```

(34 successful visits, and 7 server errors (500), and 7 "page not found" (404).)

**Who visits most?**

```bash
awk '{print $1}' logs/access.log | sort | uniq -c | sort -nr | head -n 3
```

```text
     20 10.0.0.5
     10 203.0.113.8
     10 192.168.1.20
```

**Which pages are missing (404)?**

```bash
grep ' 404 ' logs/access.log | awk '{print $7}' | sort | uniq -c
```

```text
      7 /missing
```

Four pipes, one question each, and you analysed a log. On a real server these exact lines work on millions of rows.

**Which city has the most people?**

```bash
cut -d, -f2 data/people.csv | tail -n +2 | sort | uniq -c | sort -nr
```

```text
      4 Chennai
      2 Trichy
      2 Madurai
      2 Coimbatore
```

(`tail -n +2` means "start from line 2": it skips the header.)

## 8. `tee` and `xargs`

* **`tee file`** copies the stream to a file **and** passes it on: *a T-junction*.

```bash
grep ERROR logs/app.log | tee errors-copy.txt | wc -l
```

```text
3
```

The three error lines were saved *and* counted.

* **`xargs`** turns lines of input into **arguments** for another command:

```bash
echo "a.txt b.txt c.txt" | xargs touch
```

Creates three files. Typical use: `find . -name "*.tmp" | xargs rm` (Session 6).

## 9. Joining commands: `;` `&&` `||`

| Symbol | Meaning |
|---|---|
| `a ; b` | run `a`, then `b` (always) |
| `a && b` | run `b` **only if `a` succeeded** |
| `a \|\| b` | run `b` **only if `a` failed** |

```bash
mkdir playground/test && echo "created!"
mkdir playground/test || echo "could not create (maybe it exists)"
```

## Common mistakes

| Problem | Why | Fix |
|---|---|---|
| `uniq` doesn't remove all repeats | it only removes **neighbouring** duplicates | `sort` first |
| numbers sorted as 1, 10, 2 | sorted as text | `sort -n` |
| `grep` finds nothing | wrong case, or spaces | try `-i`; quote the pattern |
| `grep` waits forever | you forgot the file name, so it reads your keyboard | **Ctrl + C**, add the file or pipe into it |
| `> file` wiped my file | `>` overwrites | use `>>` or write to a new name |
| `awk` prints wrong column | wrong separator | `-F,` for CSV; default is whitespace |
| `sed -i` broke a file | it edits in place | test **without** `-i` first |
| the pipe seems to ignore errors | pipes carry **stdout** only | `2>&1 \|` to include errors |

## Tryouts

Work in `~/linux-lab/playground`. Check with `bash ~/linux-lab/check.sh 5`.

**Tryout 1 · Warm-up.** How many lines of `logs/access.log` contain `/login`? (Use `grep` and `wc` or `grep -c`.)

<details class="solution">
<summary>Answer</summary>

```bash
grep -c '/login' ~/linux-lab/logs/access.log
# or
grep '/login' ~/linux-lab/logs/access.log | wc -l
```

</details>

**Tryout 2 · Build.** Save only the `ERROR` lines of `app.log` into `errors.txt`. Save the ranked fruit counts (`sort | uniq -c | sort -nr`) into `fruit-counts.txt`.

<details class="solution">
<summary>Answer</summary>

```bash
cd ~/linux-lab/playground
grep ERROR ../logs/app.log > errors.txt
sort ../data/fruits.txt | uniq -c | sort -nr > fruit-counts.txt
cat fruit-counts.txt
```

</details>

**Tryout 3 · Challenge.** Save the four people who live in **Chennai** (the whole CSV lines) into `chennai.txt`, then print only their **names** and **roles** from that file.

<details class="solution">
<summary>Answer</summary>

```bash
cd ~/linux-lab/playground
grep Chennai ../data/people.csv > chennai.txt
cut -d, -f1,4 chennai.txt
```

```text
Asha,developer
Chitra,manager
Farook,developer
Indu,designer
```

</details>

```bash
bash ~/linux-lab/check.sh 5
```

## Quiz

Take **"Session 5 · Quiz"** from the portal's **Quizzes** page.

## Recap

- ✅ Three streams: stdin, stdout, stderr. `>` `>>` `2>` `2>&1` `/dev/null`.
- ✅ The **pipe** `|` feeds one command's output into the next.
- ✅ `grep` (filter lines: `-i -v -c -n -r`), `sort` (`-n -r -u`), `uniq -c`, `cut`, `awk`, `tr`, `sed`, `wc`.
- ✅ The ranking pattern: `... | sort | uniq -c | sort -nr`.
- ✅ `tee` saves while passing on; `xargs` turns input into arguments; `&&` `||` `;` join commands.

**Next:** [Session 6 · Finding Things](06-finding-things.md).
