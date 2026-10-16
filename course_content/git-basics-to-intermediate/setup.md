# Setup

Before Session 1, install Git, tell it who you are, and create a practice folder. It takes about **20 minutes**, once.

## Step 1 · Open a terminal

| Your computer | How to open a terminal |
|---|---|
| **Windows** | Install **Git for Windows** (next step). It includes **Git Bash**, a terminal where every command in this course works. Open it from the Start menu. (If you already use WSL, open Ubuntu and follow the Linux steps.) |
| **macOS** | Open **Terminal** (Applications → Utilities). |
| **Linux** | Press `Ctrl + Alt + T`. |

## Step 2 · Install Git

First check whether you already have it:

```bash
git --version
```

```text
git version 2.43.0
```

Any version from **2.30** onward is fine. If you see `command not found`, install it:

**Ubuntu / Debian / WSL**

```bash
sudo apt update
sudo apt install -y git
```

**macOS** (this also offers to install the developer tools)

```bash
git --version
```

or, with Homebrew: `brew install git`.

**Windows:** download the installer from [git-scm.com/download/win](https://git-scm.com/download/win). Click *Next* through the
questions. Two choices worth making: pick **"Use Visual Studio Code as Git's default editor"** (or Nano) when asked about the editor,
and keep **"Override the default branch name"** set to **`main`**.

Run `git --version` again to confirm.

## Step 3 · Introduce yourself to Git

Every save (commit) in Git is stamped with **who made it**. Tell Git your name and email, once per computer:

```bash
git config --global user.name "Asha Kumar"
git config --global user.email "asha@example.com"
```

:::{note}
Use the **same email you will use for GitHub** (Session 7), so GitHub can link your commits to your account. If you want to keep your
address private, GitHub offers a no-reply address in its email settings.
:::

Three more settings that make life easier:

```bash
git config --global init.defaultBranch main    # new repos start on a branch called "main"
git config --global core.editor "nano"         # editor used for commit messages (or "code --wait")
git config --global pull.rebase false          # pull = fetch + merge (we explain this in Session 7)
```

Check what you set:

```bash
git config --global --list
```

```text
user.name=Asha Kumar
user.email=asha@example.com
init.defaultbranch=main
core.editor=nano
pull.rebase=false
```

## Step 4 · Create the practice folder

All the exercises happen inside one folder, so nothing you do can touch your real projects:

```bash
mkdir ~/git-lab
cd ~/git-lab
pwd
```

```text
/home/asha/git-lab
```

:::{tip}
**To reset everything** at any time (for example to redo a session), run `rm -rf ~/git-lab` and `mkdir ~/git-lab` again. Be careful
with `rm -rf`: it deletes without asking. Only use it on this practice folder.
:::

## Step 5 · Make a GitHub account (needed from Session 7)

Go to [github.com](https://github.com) and sign up with a free account. You can do this now or when you reach Session 7. Pick a
username you are happy to show on a CV.

## You are ready

```bash
git --version
git config user.name
git config user.email
```

If all three print something sensible, begin with **[Session 1 · Meet Git](sessions/01-meet-git.md)**.

## If something goes wrong

| You see | Meaning and fix |
|---|---|
| `git: command not found` | Git is not installed, or the terminal was opened before installing it. Close the terminal, open a new one. |
| `Author identity unknown` | You skipped Step 3. Run the two `git config --global user.*` commands. |
| `Permission denied` when installing | Put `sudo` in front (Linux). On Windows, run the installer as administrator. |
| The commit message editor looks strange | That is `vim`. Press `Esc`, type `:q!` and press Enter to leave, then set `core.editor` as in Step 3. |
