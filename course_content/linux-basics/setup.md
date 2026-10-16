# Setup

Before Session 1, get a Linux terminal and create your practice folder. It takes about **15 minutes**, once.

You need **one** of the options below. Pick the one that matches your computer.

```{raw} html
:file: diagrams/l00-options.html
```

## Option A · Windows 10/11: WSL (recommended for Windows)

**WSL** (*Windows Subsystem for Linux*) runs a real Ubuntu Linux inside Windows. No dual boot, nothing to break.

1. Open **PowerShell as administrator** (Start → type `PowerShell` → right-click → *Run as administrator*).
2. Run:

```powershell
wsl --install
```

3. Restart the computer when it asks. After the restart, an **Ubuntu** window opens and asks you to choose a **username** and a **password**.
   (When you type the password you will see nothing. That is normal.) Remember both.
4. From now on, open **Ubuntu** from the Start menu whenever the course says "open a terminal".

:::{note}
If `wsl --install` says it is already installed, run `wsl --install -d Ubuntu` to add Ubuntu. If your PC doesn't support WSL,
use Option C or D.
:::

## Option B · A Linux or macOS computer

You already have a terminal.

* **Linux (Ubuntu, Mint, Fedora...):** press `Ctrl + Alt + T`, or search for **Terminal**.
* **macOS:** open **Terminal** (Applications → Utilities). Almost all commands in this course work on macOS. A few flags differ, and we mark them with 🍎.

## Option C · A virtual machine (VirtualBox)

Install [VirtualBox](https://www.virtualbox.org/), download an **Ubuntu Desktop** ISO from [ubuntu.com](https://ubuntu.com/download/desktop),
create a new VM (4 GB RAM, 25 GB disk), install Ubuntu, then press `Ctrl + Alt + T` inside it.

## Option D · Docker (if you already know it)

```bash
docker run -it --name linux-lab ubuntu:24.04 bash
```

Inside, run `apt update && apt install -y sudo nano less man-db procps curl` to get the usual tools. (This is a minimal image, so some
commands are missing until you install them.)

## Step 1 · Open the terminal and look around

Type this and press **Enter**:

```bash
echo "Hello, Linux!"
```

You should see:

```text
Hello, Linux!
```

If you see that, your terminal works. 🎉

## Step 2 · Create your practice folder

Download the lab script and run it from the folder where you saved it:

* {download}`lab.sh <code/lab.sh>`  ← creates `~/linux-lab` with sample files
* {download}`check.sh <code/check.sh>`  ← checks your tryouts

```bash
bash lab.sh
```

```text
Lab ready at /home/asha/linux-lab
data
docs
logs
playground
scripts
```

(You'll see your own username in the path.) Now move both scripts next to the lab so you always find them:

```bash
cp lab.sh check.sh ~/linux-lab/
cd ~/linux-lab
ls
```

:::{tip}
**Downloaded files in WSL?** Windows files live under `/mnt/c/Users/<you>/Downloads`. Copy them into Linux with
`cp /mnt/c/Users/<you>/Downloads/lab.sh ~` (replace `<you>` with your Windows user name).
:::

### What is inside `~/linux-lab`?

| Folder | What it contains | Used in |
|---|---|---|
| `data/` | `fruits.txt` (a messy list) and `people.csv` (a small table) | Sessions 4-5 |
| `logs/` | `access.log` (a web server's visit log) and `app.log` (an application log) | Sessions 4-6 |
| `docs/` | `readme.txt`, `notes.md` | Sessions 3-4 |
| `scripts/` | `hello.sh` (a tiny script) | Sessions 7, 10 |
| `playground/` | **empty**: your own sandbox for experiments and tryouts | every session |

**Rule of the lab:** do all your experiments inside `~/linux-lab/playground`. If you ever break something, run
`bash lab.sh --reset` to delete the lab and build it fresh.

## Step 3 · Meet the checker

Each session ends with tryouts. When you think you're done, ask the checker:

```bash
bash check.sh 1
```

At the start you'll see:

```text
Session 1 · First steps
  [TODO] ~/linux-lab/playground/hello.txt exists
  [TODO] hello.txt contains your own sentence (3+ words)
  [TODO] playground/whoami.txt holds your user name

Done: 0 OK, 3 still to do.
```

`[TODO]` turns into `[ OK ]` as you finish each job. `bash check.sh all` checks the whole course.

## Rules for staying safe

1. **Read a command before pressing Enter**, especially anything with `rm`, `sudo`, `chmod` or `>`.
2. **Experiment in `~/linux-lab/playground`.** Never practise deleting things in your home folder or `/`.
3. **Never run commands from the internet that you don't understand.**
4. **Linux is case-sensitive**: `File.txt` and `file.txt` are two different files.
5. There is **no undo and no recycle bin** for `rm`. Deleted means gone.

## Common setup problems

| Problem | Fix |
|---|---|
| `bash: lab.sh: No such file or directory` | you're not in the folder that contains it. Use `ls` to look, `cd` to move |
| `Permission denied` when running `./lab.sh` | run it as `bash lab.sh` instead |
| 🪟 WSL doesn't start | enable *Virtual Machine Platform* in *Windows Features*, and turn on virtualisation in the BIOS |
| 🪟 `wsl` is not recognised | update Windows, or use Option C |
| You forgot your WSL password | in PowerShell: `wsl -u root passwd <username>` |
| `bash: check.sh: command not found` | type `bash check.sh 1`, not `check.sh 1` |

Ready? On to **[Session 1 · First steps](sessions/01-first-steps.md)**.
