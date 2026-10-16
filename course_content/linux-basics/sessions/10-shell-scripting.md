# Session 10 · Shell Scripting

**⏱ about 90 minutes · 🧰 you need: [Session 9](09-packages-and-network.md) done**

## The big idea

A **shell script** is a text file of commands that you've been typing by hand. Put them in a file once, and you can run the whole thing again
with **one word**: every day, on every server, by cron. Scripting is where Linux stops being a tool you *use* and becomes a tool you *program*.

**Everyday example:** a recipe card. The first time you cook a dish you improvise; once it works you **write the steps down** so anyone (including
you, next week) can repeat it exactly. A script is the recipe card for your computer.

```{raw} html
:file: ../diagrams/l10-script-flow.html
```

## 1. Your first script

```bash
cd ~/linux-lab/scripts
nano first.sh
```

Type:

```bash
#!/usr/bin/env bash
# first.sh - my first script
echo "Hello! Today is $(date +%A)."
echo "You are $(whoami) in $(pwd)."
```

Save (`Ctrl + O`, `Enter`, `Ctrl + X`), make it executable, run it:

```bash
chmod +x first.sh
./first.sh
```

```text
Hello! Today is Thursday.
You are asha in /home/asha/linux-lab/scripts.
```

| Part | Meaning |
|---|---|
| `#!/usr/bin/env bash` | the **shebang**: the first line tells Linux *which program should run this file* (bash) |
| `# comment` | a note for humans; ignored by bash |
| `$(command)` | **command substitution**: runs the command and puts its output right there |
| `chmod +x` | scripts need the execute bit (Session 7) |
| `./first.sh` | run the file from this folder |

## 2. Variables and quoting

```bash
name="Asha"            # NO spaces around =
echo "Hello, $name"    # double quotes: variable replaced
echo 'Hello, $name'    # single quotes: literal text
echo "Hello, ${name}s" # braces mark where the name ends
```

```text
Hello, Asha
Hello, $name
Hello, Ashas
```

**Always put variables in double quotes** (`"$name"`). Otherwise a value with spaces (`my file.txt`) falls apart into two words, and that's the #1 scripting bug.

Do maths with `$(( ))`:

```bash
count=5
count=$((count + 1))
echo "$count"        # 6
```

## 3. Arguments: giving the script input

Words after the script name arrive as `$1`, `$2`, ...:

| Variable | Holds |
|---|---|
| `$0` | the script's own name |
| `$1` `$2` ... | the 1st, 2nd ... argument |
| `$#` | **how many** arguments |
| `$@` | **all** arguments |
| `$?` | the **exit code** of the last command (0 = success) |

## 4. Decisions: `if`

```{raw} html
:file: ../diagrams/l10-exit-codes.html
```

Create `greet.sh`:

```{literalinclude} ../code/greet.sh
:language: bash
```

```bash
chmod +x greet.sh
./greet.sh
./greet.sh Meena
```

```text
Usage: ./greet.sh NAME
Hello, Meena!
```

How it works:

* `if [ -z "$name" ]; then ... fi`: if the variable is **z**ero-length (empty). Every `if` ends with `fi`.
* `exit 1` stops the script and reports **failure** to whoever ran it.
* `exit 0` (or just reaching the end) means **success**.

**Check the exit code:**

```bash
./greet.sh; echo "exit code: $?"
./greet.sh Meena; echo "exit code: $?"
```

```text
Usage: ./greet.sh NAME
exit code: 1
Hello, Meena!
exit code: 0
```

### Tests you will use (inside `[ ... ]`; **spaces are required** inside the brackets)

| Test | True when |
|---|---|
| `-f file` | file exists (regular file) |
| `-d dir` | directory exists |
| `-z "$x"` / `-n "$x"` | text is empty / not empty |
| `"$a" = "$b"` | text equal |
| `$a -eq $b` / `-ne` / `-gt` / `-lt` / `-ge` / `-le` | **numbers**: equal / not equal / greater / less... |
| `! test` | the opposite |

Combine with `&&` (and) and `||` (or): `[ "$x" -gt 3 ] && [ "$x" -lt 10 ]`.

```bash
if [ -f /etc/passwd ]; then
    echo "found it"
elif [ -d /etc ]; then
    echo "at least the folder exists"
else
    echo "nothing"
fi
```

## 5. Loops: repeat work

Create `counter.sh`:

```{literalinclude} ../code/counter.sh
:language: bash
```

```bash
chmod +x counter.sh && ./counter.sh
```

```text
Round 1
Round 2
Round 3
countdown: 3
countdown: 2
countdown: 1
Lift off!
```

* `for i in 1 2 3; do ... done` repeats for each item in the list.
* `while [ test ]; do ... done` repeats **as long as** the test is true.

**Loop over files**, the most useful form:

```bash
for f in ~/linux-lab/data/*.txt; do
    echo "file: $(basename "$f") has $(wc -l < "$f") lines"
done
```

```text
file: fruits.txt has 12 lines
```

Also: `for i in $(seq 1 5)`, and `for line in $(cat file)` (words, not lines. For lines use `while read -r line; do ... done < file`).

## 6. Functions

A **function** is a named block you can call many times. Create `report.sh`:

```{literalinclude} ../code/report.sh
:language: bash
```

```bash
chmod +x report.sh && ./report.sh
```

```text
Report for /home/asha/linux-lab/logs/app.log
  INFO : 8
  WARN : 2
  ERROR: 3
```

* `count_level() { ...; }` defines the function; `$1` inside it is **its** first argument.
* `echo ... >&2` sends a message to **stderr** (the error channel from Session 5), the right place for errors.
* `exit 2` uses a **different code** so callers can tell problems apart.

## 7. A real script: backup

Create `backup.sh`:

```{literalinclude} ../code/backup.sh
:language: bash
```

```bash
chmod +x backup.sh
./backup.sh
./backup.sh /nope; echo "exit code: $?"
```

```text
Backed up /home/asha/linux-lab/data -> /home/asha/linux-lab/backup-2026-10-15_2319
Nothing to back up: /nope is not a folder
exit code: 1
```

New ideas:

| Code | Meaning |
|---|---|
| `set -eu` | **safety net**: stop at the first error (`-e`) and treat unset variables as errors (`-u`). Always add it to real scripts |
| `SRC="${1:-$HOME/linux-lab/data}"` | **default value**: use argument 1, or this folder if none is given |
| `$(date +%F_%H%M)` | a timestamp like `2026-10-15_2319` so each backup has its own name |
| quotes around `"$SRC"` | works even if the path has spaces |

Run it **automatically** with cron (Session 8): `crontab -e`, then add

```text
0 2 * * * /home/asha/linux-lab/scripts/backup.sh >> /home/asha/backup.log 2>&1
```

## 8. Debugging scripts

| Tool | Use |
|---|---|
| `bash -x script.sh` | prints **every command** as it runs (lines start with `+`) |
| `set -x` / `set +x` inside a script | turn tracing on/off for a section |
| `echo "DEBUG: x=$x"` | the classic print-debugging |
| `shellcheck script.sh` | a free tool that spots mistakes (`sudo apt install shellcheck`) |

```bash
bash -x greet.sh Asha
```

```text
+ name=Asha
+ '[' -z Asha ']'
+ echo 'Hello, Asha!'
Hello, Asha!
```

## 9. Reading input and arrays (a taste)

```bash
read -r -p "Your name? " who     # asks the user; stores the answer in $who
echo "Nice to meet you, $who"

fruits=(apple banana cherry)     # an array
echo "${fruits[1]}"              # banana (counting starts at 0)
echo "${#fruits[@]}"             # 3 (how many)
for f in "${fruits[@]}"; do echo "- $f"; done
```

## Common mistakes

| Problem | Why | Fix |
|---|---|---|
| `Permission denied` | no `x` bit | `chmod +x script.sh` |
| `bad interpreter: /bin/bash^M` | the file has **Windows line endings** | `sed -i 's/\r$//' script.sh` (or `dos2unix`) |
| `[: missing ]` / `unary operator expected` | missing spaces or unquoted empty variable | `[ "$x" = "y" ]`, spaces around brackets, quote variables |
| `x = 5` → `command not found` | spaces around `=` | `x=5` |
| script works by hand, fails in cron | different PATH and folder | use full paths; `cd` first |
| `if [ $a > 5 ]` creates a file named `5` | `>` is redirection | use `-gt`: `[ "$a" -gt 5 ]` |
| the script keeps going after an error | no safety net | `set -eu` at the top |
| `rm -rf "$DIR/"*` when `$DIR` is empty | deletes from `/` | `set -u` and check `[ -n "$DIR" ]` first |

## Tryouts

Work in `~/linux-lab/scripts`. Check with `bash ~/linux-lab/check.sh 10`.

**Tryout 1 · Warm-up.** Write `hello2.sh` that prints `Hello, <your user name>! It is <the date>.` using `$(whoami)` and `$(date)`. Run it.

<details class="solution">
<summary>Answer</summary>

```bash
#!/usr/bin/env bash
echo "Hello, $(whoami)! It is $(date)."
```

```bash
chmod +x hello2.sh && ./hello2.sh
```

</details>

**Tryout 2 · Build.** Create `greet.sh` (as in the lesson) that prints `Hello, NAME!` for the argument you pass and shows a usage message and **exit code 1** if no name is given. Make it executable.

<details class="solution">
<summary>Answer</summary>

```bash
cd ~/linux-lab/scripts
cat > greet.sh <<'EOF'
#!/usr/bin/env bash
name="$1"
if [ -z "$name" ]; then
    echo "Usage: $0 NAME"
    exit 1
fi
echo "Hello, $name!"
EOF
chmod +x greet.sh
./greet.sh Meena
```

</details>

**Tryout 3 · Challenge.** Create `backup.sh` that copies `~/linux-lab/data` into `~/linux-lab/backup-DATE`, prints where it went, and refuses (exit 1) if the source folder doesn't exist. Run it twice on different minutes, then use `ls` to see both backups. *(Bonus: schedule it in cron every night at 02:30.)*

<details class="solution">
<summary>Answer</summary>

Use the `backup.sh` shown in the lesson. Make it executable (`chmod +x backup.sh`) and run `./backup.sh`. With the minute in the folder name (`%H%M`), two runs in different minutes create two folders. Cron line:

```text
30 2 * * * /home/asha/linux-lab/scripts/backup.sh >> /home/asha/backup.log 2>&1
```

</details>

```bash
bash ~/linux-lab/check.sh 10
```

## Quiz

Take **"Session 10 · Quiz"** from the portal's **Quizzes** page.

## Recap

- ✅ A script = shebang `#!/usr/bin/env bash` + commands + `chmod +x`.
- ✅ Variables `name="x"` (no spaces), **quote them** `"$name"`; arguments `$1 $2 $# $@`; **exit code** `$?` (0 = success).
- ✅ `if [ test ]; then ... fi`, `for ... do ... done`, `while ... do ... done`, functions `name() { ...; }`.
- ✅ **`set -eu`** stops mistakes early; `bash -x` and `shellcheck` find bugs.
- ✅ Combine with cron to automate.

**Next (last):** [Session 11 · Troubleshooting](11-troubleshooting.md): disks, memory, logs, and what to do when things break.
