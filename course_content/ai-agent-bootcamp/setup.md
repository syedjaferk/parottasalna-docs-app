# Setup

Before Session 1, let's get your computer ready. You do this **once**. It takes about **30 minutes**
the first time, and every session after that just works.

You do **not** need to be an expert. Every step below tells you exactly what to type, what you
should see, and what to do if you see something else. Each step has a **🐧 Linux** version and a
**🪟 Windows** version. (macOS users: follow the Linux steps. The commands are the same.)

:::{note}
**What are we installing, and why?**

| What | In one line | Why we need it |
|---|---|---|
| **Python 3.10+** | the language we write everything in | all course code is Python |
| **A code editor (VS Code)** | a notepad made for code | easier than typing code in a plain notepad |
| **Git** | a tool that downloads and tracks code | Hermes (Session 6) needs it on Windows |
| **A virtual environment** | a private box for this course's packages | keeps your computer tidy |
| **A free AI API key** | a "password" that lets your code talk to an AI model | the AI "brain" lives on a server |
| **A Telegram account** | a chat app | your agent will talk to you there (Session 8) |
:::

```{raw} html
:file: diagrams/setup-overview.html
```

## Step 1 · Open a terminal

A **terminal** is a window where you type commands instead of clicking buttons. Don't be scared of
it. It is just a very literal assistant: you type one instruction, press **Enter**, and it does it.

**🐧 Linux.** Press `Ctrl + Alt + T`, or search for "Terminal" in your applications.

**🪟 Windows.** Press the **Windows key**, type `PowerShell`, and open **Windows PowerShell**
(or **Terminal** on Windows 11). *Do not* use the old black "Command Prompt" window; we use PowerShell.

You'll see a line ending with `$` (Linux) or `>` (Windows). That's the **prompt**: the terminal is
waiting for you. In this course, lines you should type look like this:

```bash
echo "hello"
```

You type only the command, not the `$` or `>`. Try it now. You should see:

```text
hello
```

## Step 2 · Install Python

First, check whether Python is already there.

**🐧 Linux**

```bash
python3 --version
```

**🪟 Windows**

```powershell
python --version
```

You want to see `Python 3.10.x` or higher (for example `Python 3.12.3`).

* **Version is 3.10 or higher?** Great, skip to Step 3.
* **"command not found" or a lower version?** Install it:

**🐧 Linux (Ubuntu / Debian / Linux Mint)**

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git curl
```

`sudo` means "run as administrator". It will ask for your password. You won't see the letters as
you type; that is normal. Press Enter when done.

**🐧 Linux (Fedora)**

```bash
sudo dnf install -y python3 python3-pip git curl
```

**🪟 Windows (easiest: winget, built into Windows 10/11)**

```powershell
winget install -e --id Python.Python.3.12
```

Close PowerShell and open it again, then run `python --version`.

**🪟 Windows (alternative: the installer)**
Download Python from [python.org/downloads](https://www.python.org/downloads/), run it, and on the
very first screen tick **"Add python.exe to PATH"** *before* clicking Install. If you forget this,
the terminal won't find Python. (Fix: run the installer again, choose **Modify**, and tick it.)

:::{important}
On Windows the command is **`python`**. On Linux and macOS it is **`python3`**. Throughout this course
we write `python`. If that doesn't work on Linux/macOS, use `python3` instead. Once your virtual
environment is on (Step 5), plain `python` works on every system.
:::

## Step 3 · Install VS Code (the editor)

Download it from [code.visualstudio.com](https://code.visualstudio.com/) and install it.

**🐧 Linux (Ubuntu/Debian)**: download the `.deb` file, then:

```bash
sudo apt install ./code_*.deb
```

**🪟 Windows:** run the installer and keep the defaults (tick *"Add to PATH"* if it asks).

Open VS Code, click the **Extensions** icon on the left (four squares), search for **Python** (by
Microsoft), and click **Install**.

## Step 4 · Install Git

Git downloads code from the internet and remembers changes. We need it in Session 6, and on Windows
Hermes uses it behind the scenes.

**🐧 Linux:** already installed in Step 2. Check: `git --version`

**🪟 Windows:**

```powershell
winget install -e --id Git.Git
```

Close and re-open PowerShell, then check:

```powershell
git --version
```

Expected: something like `git version 2.45.1`.

## Step 5 · Make your project folder and a virtual environment

All your work for the course will live in **one folder**. We'll call it `ai-agent-bootcamp`.

A **virtual environment** ("venv") is like a separate toolbox for this one project. Packages you
install inside it don't touch the rest of your computer, and deleting the folder removes everything.

**🐧 Linux**

```bash
cd ~
mkdir ai-agent-bootcamp
cd ai-agent-bootcamp
python3 -m venv .venv
source .venv/bin/activate
```

**🪟 Windows (PowerShell)**

```powershell
cd ~
mkdir ai-agent-bootcamp
cd ai-agent-bootcamp
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If Windows says *"running scripts is disabled on this system"*, run this **once**, answer `Y`,
then try the `Activate.ps1` line again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

**How do you know it worked?** Your prompt now starts with `(.venv)`:

```text
(.venv) user@computer:~/ai-agent-bootcamp$
```

:::{tip}
**Every time you open a new terminal for the course**, go to the folder and turn the venv on again:
`cd ~/ai-agent-bootcamp` and then `source .venv/bin/activate` (Linux) or `.\.venv\Scripts\Activate.ps1`
(Windows). If you ever see "ModuleNotFoundError", this is the first thing to check.
:::

Now install the two packages we need on Day 1 (the venv must be on, you see `(.venv)`):

```bash
pip install requests python-dotenv
```

Save the list so you can reinstall any time. Create a file named `requirements.txt` in VS Code
(**File → Open Folder → ai-agent-bootcamp**, then **New File**) with:

```text
requests
python-dotenv
```

## Step 6 · Get a free AI key

Your Python program can't run a giant AI model on a laptop. Instead, it **sends a message over the
internet to a company's computer** that runs the model, and gets the answer back. To prove it's you, you
send a secret **API key** (like a library card number). We use **free tiers**, so it costs nothing.

You need **one** of these. Pick the first if you are unsure.

### Option A · Groq (recommended: fast and free)

1. Go to [console.groq.com](https://console.groq.com/) and sign in (Google account works).
2. Click **API Keys → Create API Key**. Give it a name such as `bootcamp`.
3. **Copy the key now.** It starts with `gsk_`. You can't see it again later.

Your settings for the `.env` file (next step):

```text
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.1-8b-instant
```

### Option B · OpenRouter (many free models)

1. Go to [openrouter.ai](https://openrouter.ai/) and sign in.
2. Open **Keys → Create Key**, and copy it (starts with `sk-or-`).
3. Choose a model whose name ends in `:free` from the [model list](https://openrouter.ai/models?q=free).

```text
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=<a model name ending in :free>
```

### Option C · Ollama (runs on your own computer, no internet needed after download)

Good if your internet is slow or you hit free-tier limits. It needs about **8 GB RAM**.

**🐧 Linux**

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2
```

**🪟 Windows:** download the installer from [ollama.com/download](https://ollama.com/download), run
it, then in PowerShell:

```powershell
ollama pull llama3.2
```

```text
LLM_BASE_URL=http://localhost:11434/v1
LLM_API_KEY=ollama
LLM_MODEL=llama3.2
```

:::{note}
**Why do all three work with the same code?** Groq, OpenRouter and Ollama all copy the same "language"
for talking to AI (the *OpenAI-compatible API*). So you write your code **once** and change only three
lines in `.env` to switch provider. You'll see this clearly in Session 3.
:::

:::{caution}
Model names change over time. If a name stops working, `check_setup.py` (Step 8) prints the names that
*are* available. Just copy one into `LLM_MODEL`.
:::

## Step 7 · Create your `.env` file

An **`.env` file** is a small text file where you keep secrets (like your API key) **outside** your
code. Your code reads from it. This way you never paste a key into a program and accidentally share it.

In VS Code, create a **new file called exactly `.env`** (with the dot, no `.txt`) inside
`ai-agent-bootcamp` and put:

```text
LLM_API_KEY=paste-your-key-here
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.1-8b-instant
```

Replace `paste-your-key-here` with your real key. **No quotes, no spaces** around the `=`.

Also create a file named **`.gitignore`** so the secret is never uploaded if you share your code:

```text
.env
.venv/
__pycache__/
```

:::{caution}
**Never share your `.env` file or post your key** on WhatsApp, GitHub or screenshots. If you leak a
key by accident, open the provider's website, delete the key, and create a new one. It takes a minute.
:::

**🪟 Windows tip.** Notepad likes to save `.env` as `.env.txt`. In VS Code this doesn't happen. To
check, run `dir -Force` in PowerShell, and make sure you see `.env` and not `.env.txt`.

## Step 8 · Run the check

Download the checker and save it in your `ai-agent-bootcamp` folder:

* {download}`check_setup.py <code/01-python-for-ai/check_setup.py>`

Then run it (venv on!):

```bash
python check_setup.py
```

**Expected output (all good):**

```text
[ OK ] Python 3.12.3
[ OK ] Virtual environment is active
[ OK ] requests 2.32.3
[ OK ] python-dotenv is installed
[ OK ] .env file found
[ OK ] LLM_API_KEY is set
[ OK ] LLM_BASE_URL = https://api.groq.com/openai/v1
[ OK ] LLM_MODEL = llama-3.1-8b-instant
[ OK ] The provider accepted your key (20 models available)
[ OK ] Model 'llama-3.1-8b-instant' is available

All good! You are ready.
```

Any line that says `[FAIL]` is followed by an arrow `->` that tells you what to fix. Fix it and run the
script again until everything is `[ OK ]`.

## Step 9 · A Telegram account (for Day 2)

Install **Telegram** on your phone and/or computer from [telegram.org](https://telegram.org/) and sign
in. That's all for now. You'll create your bot in Session 8.

## Things you'll install later (not now!)

| When | What | Session |
|---|---|---|
| Day 1 evening | **Hermes Agent** | [Session 6](sessions/06-meet-hermes.md) |
| Day 1 homework | **Laya** (a small, fast AI decision model, about 1.5 GB) | [Session 9](sessions/09-system1-vs-system2.md) |

## If something goes wrong

| What you see | What it means | What to do |
|---|---|---|
| `python: command not found` (Linux) | Python is `python3` there | use `python3`, or activate the venv |
| `'python' is not recognized` (Windows) | Python is not on PATH | re-run the installer, tick **Add to PATH**, reopen PowerShell |
| `No module named 'requests'` | venv is off, or package not installed | activate the venv, then `pip install requests python-dotenv` |
| `running scripts is disabled` (Windows) | PowerShell safety setting | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `externally-managed-environment` (Linux) | You ran `pip` outside a venv | activate the venv (Step 5) first |
| `401` / "provider rejected your key" | key is wrong or has extra spaces | copy it again; no quotes in `.env` |
| `429` / "rate limit" | free tier is busy | wait a minute, or use another option |
| `.env file found` is FAIL | you are in the wrong folder | `cd ~/ai-agent-bootcamp` and run again |

More fixes are in the [Troubleshooting guide](troubleshooting.md).

:::{tip}
Ready? Go to **[Session 1 · Python for AI](sessions/01-python-for-ai.md)**.
:::
