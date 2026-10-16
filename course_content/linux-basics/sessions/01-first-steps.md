# Session 1 · First Steps in the Terminal

**⏱ about 60 minutes · 🧰 you need: [Setup](../setup.md) finished**

## The big idea

Most people use a computer by **pointing and clicking**. The **terminal** lets you use it by **typing instructions**. It feels
strange for ten minutes and then feels like a superpower: instead of clicking through five windows, you type one line, and you can
repeat, share and automate it.

**Everyday example:** clicking is like ordering food by *pointing at the menu* in a restaurant. The terminal is like
*telling the chef exactly what you want*: *"two idlis, one vada, extra sambar"*. It is faster, it is precise, and the chef
(the computer) does exactly what you said, so choose your words carefully.

```{raw} html
:file: ../diagrams/l01-layers.html
```

Three words you'll hear all the time:

| Word | What it is |
|---|---|
| **Terminal** | the *window* where you type and read text |
| **Shell** | the *program inside the window* that understands what you type. The most common shell is **bash** |
| **Command** | one instruction for the shell, like `ls` or `date` |

## 1. Reading the prompt

When you open the terminal you see something like this:

```text
asha@laptop:~$
```

| Part | Meaning |
|---|---|
| `asha` | **who you are** (your user name) |
| `@` | "at" |
| `laptop` | the **computer's name** (hostname) |
| `:` | separator |
| `~` | **where you are**: `~` means your *home folder* |
| `$` | "I'm ready for your command." (If you see `#` instead, you are the **administrator** (root). Be extra careful.) |

In this course, commands you type are shown **without** the prompt, like this:

```bash
whoami
```

and the output you should see comes in a separate block like this:

```text
asha
```

You type only `whoami`, then press **Enter**. The shell runs it and shows the result, then shows a new prompt.

## 2. Your first commands

Try each one. Your output will have your own name, computer and dates.

```bash
whoami
```

```text
asha
```

*Who am I?* Prints your user name.

```bash
hostname
```

```text
laptop
```

*What is this computer called?*

```bash
date
```

```text
Thu Oct 15 11:42:08 IST 2026
```

*What are the date and time?*

```bash
echo Hello, Linux!
```

```text
Hello, Linux!
```

`echo` simply **repeats** what you give it. It looks silly now, but you'll use it constantly, to print messages and to write text into files.

```bash
uname -a
```

```text
Linux laptop 6.8.0-45-generic #45-Ubuntu SMP PREEMPT_DYNAMIC x86_64 x86_64 x86_64 GNU/Linux
```

*What system is this?* `Linux` is the **kernel** name (the core of the operating system) and the rest describes the version and your CPU type.

```bash
clear
```

Clears the screen. (Shortcut: **Ctrl + L**.) Nothing is deleted. The old text just scrolls out of view.

## 3. The anatomy of a command

Every command follows the same pattern:

```{raw} html
:file: ../diagrams/l01-anatomy.html
```

```bash
ls -l /home
```

| Part | Name | Meaning |
|---|---|---|
| `ls` | **command** | *what to do* (list files) |
| `-l` | **option** (also called a flag or switch) | *how to do it* (use the long format) |
| `/home` | **argument** | *what to do it to* (this folder) |

Rules of thumb:

* **Spaces separate the parts.** `ls-l` (no space) is one weird word that doesn't exist.
* Short options start with **one dash** (`-l`); long options start with **two** (`--help`).
* You can combine short options: `ls -l -a -h` is the same as `ls -lah`.
* Not every command needs options or arguments: `date` and `whoami` work alone.

## 4. Getting help (you will use this forever)

Nobody remembers every option. Experts just know **how to look them up**.

### `--help`: a quick summary

```bash
date --help
```

```text
Usage: date [OPTION]... [+FORMAT]
  or:  date [-u|--utc|--universal] [MMDDhhmm[[CC]YY][.ss]]
Display date and time in the given FORMAT.
...
```

Most commands print a short guide when you add `--help`. If the output is long, it scrolls past. We fix that in Session 4 with `less`.

### `man`: the full manual

```bash
man ls
```

This opens the **manual page** for `ls` in a reader. Inside it:

| Key | What it does |
|---|---|
| `↓` `↑` or `j` `k` | scroll |
| `Space` | next page |
| `/word` then `Enter` | search for *word* (press `n` for the next match) |
| `q` | **quit** (you'll need this: the page doesn't close by itself!) |

(On a minimal Docker image `man` may be missing. Install it with `apt install man-db`.)

### `type` and `which`: *what is this command?*

```bash
type ls
```

```text
ls is aliased to `ls --color=auto'
```

```bash
which date
```

```text
/usr/bin/date
```

`which` tells you **where** the program file lives.

## 5. Work faster: five tricks every user knows

| Trick | How | Why it matters |
|---|---|---|
| **Tab completion** | type the first letters, press **Tab** | finishes names for you and prevents typos. Press Tab twice to see all matches |
| **Up arrow** | press `↑` | brings back your previous commands (`↓` goes forward) |
| **`history`** | type `history` | shows a numbered list of everything you typed |
| **Ctrl + C** | press it | **stops** a running command (an escape hatch when something hangs) |
| **Ctrl + R** | press, then type a few letters | *searches* your history for an old command |

More shortcuts on the command line itself:

| Shortcut | Effect |
|---|---|
| `Ctrl + A` / `Ctrl + E` | jump to the **start** / **end** of the line |
| `Ctrl + U` | delete everything **before** the cursor |
| `Ctrl + W` | delete the previous **word** |
| `Ctrl + L` | clear the screen |
| `Ctrl + D` | end of input: closes the terminal if the line is empty |

Try it: type `echo ab`, press **Ctrl + A**, type `hello `, press **Enter**.

```text
hello ab
```

## 6. Your first file: with `echo` and `>`

Remember `echo` repeats text? You can **redirect** that text into a file with `>`:

```bash
cd ~/linux-lab/playground
echo "Linux is fun" > hello.txt
cat hello.txt
```

```text
Linux is fun
```

* `cd ~/linux-lab/playground`: go to your sandbox (next session explains `cd`).
* `>` means *"send the output into this file instead of the screen"*. The file is **created** (or **overwritten**).
* `cat hello.txt` shows what is inside.

## Common mistakes

| You typed / saw | What it means | Fix |
|---|---|---|
| `bash: hello: command not found` | the shell doesn't know that word | check the spelling; is it installed? |
| `bash: syntax error near unexpected token` | a quote or bracket is missing | check that every `"` has a partner |
| `ls -l/home` | missing space | write `ls -l /home` |
| `Date` | commands are **case-sensitive** | use lowercase: `date` |
| the screen is stuck after `man` | you're inside the reader | press **q** |
| the prompt disappeared | a program is still running | press **Ctrl + C** |
| you pasted text and it ran immediately | pasted a newline | always read what you paste |

## Tryouts

Do these in `~/linux-lab/playground`. Then run `bash ~/linux-lab/check.sh 1`.

**Tryout 1 · Warm-up.** Run `whoami`, `hostname` and `date`. Write down what each shows.

**Tryout 2 · Build.** Create a file `hello.txt` in the playground that contains a sentence **you** invent (at least 3 words).

<details class="solution">
<summary>Answer</summary>

```bash
cd ~/linux-lab/playground
echo "I am learning Linux today" > hello.txt
cat hello.txt
```

</details>

**Tryout 3 · Challenge.** Create `whoami.txt` that contains **only your user name** (hint: you don't have to type the name. Let a command produce the text).

<details class="solution">
<summary>Answer</summary>

```bash
whoami > whoami.txt
cat whoami.txt
```

`>` sends the **output of any command** into a file, not only `echo`.

</details>

```bash
bash ~/linux-lab/check.sh 1
```

```text
Session 1 · First steps
  [ OK ] ~/linux-lab/playground/hello.txt exists
  [ OK ] hello.txt contains your own sentence (3+ words)
  [ OK ] playground/whoami.txt holds your user name

Done: 3 OK, 0 still to do.
```

## Quiz

Take **"Session 1 · Quiz"** from the portal's **Quizzes** page.

## Recap

- ✅ **Terminal** = the window, **shell** (bash) = the program that understands your commands.
- ✅ A command is `command -options arguments`, separated by spaces, and case-sensitive.
- ✅ `whoami`, `hostname`, `date`, `echo`, `uname -a`, `clear` are safe first commands.
- ✅ Get help with `--help` and `man` (quit with **q**); find a program with `which`.
- ✅ **Tab**, **↑**, **history** and **Ctrl + C / R** make you fast.
- ✅ `>` sends a command's output into a file.

**Next:** [Session 2 · Files and Directories](02-files-and-directories.md): where things live and how to get there.

## Session materials

- {download}`lab.sh <../code/lab.sh>`
- {download}`check.sh <../code/check.sh>`
