# Session 9 · Packages, Archives and the Network

**⏱ about 90 minutes · 🧰 you need: [Session 8](08-processes-and-services.md) done, an internet connection**

## The big idea

On Windows you install software by downloading a setup file from a website. On Linux you ask a **package manager** (a trusted app store
in the terminal) to install, update and remove everything, safely and with one command. In this session you'll also learn to
**download** files, **zip** things up, understand **environment variables** and **PATH**, and poke around the **network**.

**Everyday example:** a supermarket with a very good delivery service. Instead of visiting every farm (website) yourself, you tell the supermarket
(the package manager) *"I want onions"* and it brings them, checks they're fresh (verified), and later tells you when there's a newer batch.

```{raw} html
:file: ../diagrams/l09-package-manager.html
```

## 1. Package managers

| Family | Examples | Tool |
|---|---|---|
| **Debian / Ubuntu / Mint / WSL Ubuntu** | `.deb` packages | **`apt`** |
| **Fedora / RHEL / Rocky / Alma / CentOS** | `.rpm` packages | **`dnf`** (older: `yum`) |
| **Arch** | | `pacman` |
| **Alpine** (Docker) | | `apk` |

Check which one you have: `cat /etc/os-release`.

### The `apt` routine (Ubuntu/Debian)

| Task | Command |
|---|---|
| refresh the list of available packages | `sudo apt update` |
| upgrade everything installed | `sudo apt upgrade` |
| **search** for a package | `apt search tree` |
| see details of a package | `apt show tree` |
| **install** | `sudo apt install tree` |
| **remove** (keep settings) | `sudo apt remove tree` |
| remove **and** settings | `sudo apt purge tree` |
| remove unused leftovers | `sudo apt autoremove` |
| what is installed? | `apt list --installed \| head` |

```bash
sudo apt update
sudo apt install -y tree
tree --version
```

```text
tree v2.1.1 (c) 1996 - 2023 by Steve Baker, Thomas Moore, Francesc Rocher, Florian Sesser, Kyle Bubp
```

(`-y` answers "yes" to the confirmation question. Use it once you know what you're installing.)

**Why `update` then `upgrade`?** `update` only **refreshes the catalogue** (what's available). `upgrade` actually **installs** the newer versions.

### The same on Fedora / RHEL

| Task | Command |
|---|---|
| install | `sudo dnf install tree` |
| remove | `sudo dnf remove tree` |
| search | `dnf search tree` |
| update everything | `sudo dnf upgrade` |

### Good habits

* Install from your distribution's repositories first. They are **verified and signed**.
* Don't run random `curl ... | sudo bash` lines you found online without reading them.
* Package names can differ between distributions (`apache2` on Ubuntu, `httpd` on Fedora).

## 2. Downloading things: `curl` and `wget`

```bash
curl -s "https://api.open-meteo.com/v1/forecast?latitude=13.08&longitude=80.27&current_weather=true"
```

```text
{"latitude":13.11,"longitude":80.25,... "current_weather":{"temperature":28.4,...}}
```

`curl` talks to web servers. It prints what comes back (here JSON from a weather API).

| Command | Does |
|---|---|
| `curl URL` | print the page/response |
| `curl -s URL` | **s**ilent: no progress bar |
| `curl -I URL` | only the **headers** (status, type) |
| `curl -o file URL` | save into `file` |
| `curl -O URL` | save with the **original** file name |
| `curl -L URL` | **f**ollow redirects |
| `wget URL` | download a file (shows progress) |

```bash
curl -sI https://example.com | head -n 3
```

```text
HTTP/2 200
date: Thu, 15 Oct 2026 17:48:55 GMT
content-type: text/html; charset=utf-8
```

`200` means *OK*. (`404` is *not found*, `500` is *server problem*. You met these in the log lessons.)

## 3. Archives: `tar`, `gzip`, `zip`

An **archive** bundles many files into one. **Compressing** makes it smaller. On Linux you'll see `.tar.gz` (also `.tgz`) everywhere.

```{raw} html
:file: ../diagrams/l09-tar.html
```

### `tar` (the one to memorise)

```bash
cd ~/linux-lab/playground
tar -czf archive.tar.gz -C ~/linux-lab docs data
ls -lh archive.tar.gz
```

```text
-rw-rw-r-- 1 asha asha 515 Oct 15 23:18 archive.tar.gz
```

**Create = `c`, eXtract = `x`, Test (list) = `t`.** The letters of `czf`:

| Letter | Means |
|---|---|
| `c` | **c**reate an archive |
| `z` | compress with g**z**ip |
| `f` | the next word is the **f**ile name |
| `-C dir` | first go **into** this directory (keeps the paths short) |

**Look inside before extracting:**

```bash
tar -tzf archive.tar.gz
```

```text
docs/
docs/readme.txt
docs/notes.md
data/
data/people.csv
data/fruits.txt
```

**Extract:**

```bash
mkdir -p extract
tar -xzf archive.tar.gz -C extract
ls extract
```

```text
data  docs
```

Easy to remember: **c**reate = **czf**, e**x**tract = **xzf**, **t**est = **tzf**, always followed by the archive name.

### `gzip` and `zip`

```bash
cp ../data/fruits.txt f.txt
gzip f.txt          # f.txt becomes f.txt.gz (the original is replaced)
gunzip f.txt.gz     # and back again
```

```bash
zip -r docs.zip ~/linux-lab/docs      # make a .zip (works with Windows too)
unzip docs.zip -d unzipped            # open it into a folder
```

(Install with `sudo apt install zip unzip` if missing.)

## 4. Environment variables and `PATH`

A **variable** is a named box holding text. The shell itself uses many:

```bash
echo $HOME
echo $USER
echo $SHELL
```

```text
/home/asha
asha
/bin/bash
```

Make your own:

```bash
GREETING="hello"         # a shell variable (no spaces around =)
echo $GREETING
export GREETING          # export = also visible to programs you start
bash -c 'echo inside: $GREETING'
```

```text
hello
inside: hello
```

| Command | Does |
|---|---|
| `printenv` | list all environment variables |
| `printenv HOME` | show one |
| `export NAME=value` | set it for this terminal **and** its child programs |
| `unset NAME` | remove it |

### The most important variable: `PATH`

```bash
echo $PATH
```

```text
/home/asha/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```

`PATH` is a **colon-separated list of folders** where the shell **looks for programs**. When you type `ls`, the shell checks each folder in order until it finds an
`ls` file. If a program isn't in any of them you get `command not found`. To run your own scripts from anywhere, put them in a folder that is **on the PATH**:

```bash
mkdir -p ~/bin
cp ~/linux-lab/scripts/hello.sh ~/bin/hello
chmod +x ~/bin/hello
export PATH="$HOME/bin:$PATH"       # add ~/bin to the front (this terminal only)
hello
```

```text
Hello from a script!
```

**Make it permanent** by adding the `export` line to the end of `~/.bashrc` (the file bash reads each time you open a terminal):

```bash
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc        # apply it now, in this terminal
```

## 5. Network basics

| Question | Command |
|---|---|
| What are **my IP addresses**? | `ip addr` (short: `ip -br addr`) |
| Can I **reach** that computer? | `ping -c 3 example.com` |
| What does a **domain name** point to? | `dig example.com +short` (or `nslookup`) |
| Which **ports are my computer listening on**? | `ss -tln` |
| Download / call a web address | `curl` |

```bash
ip -br addr
```

```text
lo      UNKNOWN   127.0.0.1/8 ::1/128
wlp2s0  UP        192.168.1.5/24 fe80::3222:b454:5aec:9c91/64
```

* `lo` is the **loopback**: the computer talking to itself (`127.0.0.1`, also called `localhost`).
* `wlp2s0` (or `eth0`, `enp3s0`) is a real network card. `192.168.1.5` is the machine's address on your home network.

```bash
ping -c 2 127.0.0.1
```

```text
PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.
64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.090 ms
...
2 packets transmitted, 2 received, 0% packet loss
```

`ping` sends tiny test messages and times the reply. **0% packet loss** means a healthy connection. (`-c 2` = send two, then stop. Without it, ping never ends. Use **Ctrl + C**.)

```bash
ss -tln
```

```text
State   Recv-Q  Send-Q  Local Address:Port   Peer Address:Port
LISTEN  0       4096        127.0.0.1:8123        0.0.0.0:*
LISTEN  0       128           0.0.0.0:22          0.0.0.0:*
```

`ss -tln` = **t**cp, **l**istening, **n**umeric. It shows which programs are waiting for connections (for example, port `22` is SSH and `80`/`443` are web servers).

## 6. Remote machines: `ssh` and `scp`

**SSH** gives you a terminal **on another computer** (a cloud server, a Raspberry Pi) over an encrypted connection.

```bash
ssh asha@203.0.113.10
```

(Replace the user and address with a server you have access to.) The first time, SSH asks *"Are you sure you want to continue connecting?"*. Type `yes` after checking it's the right server.

```bash
scp report.txt asha@203.0.113.10:/home/asha/         # copy a file TO the server
scp asha@203.0.113.10:/home/asha/report.txt .        # copy a file FROM the server
```

**Keys instead of passwords** (safer):

```bash
ssh-keygen -t ed25519          # creates ~/.ssh/id_ed25519 (private!) and id_ed25519.pub (public)
ssh-copy-id asha@203.0.113.10  # installs your PUBLIC key on the server
```

:::{caution}
**Never share the private key** (`id_ed25519` without `.pub`). Keep it `chmod 600`. Share only the `.pub` file.
:::

## Common mistakes

| Problem | Why | Fix |
|---|---|---|
| `E: Could not get lock /var/lib/dpkg/lock` | another install is running | wait, or reboot; don't delete the lock |
| `E: Unable to locate package xyz` | list is old, or wrong name | `sudo apt update`; `apt search xyz` |
| `Permission denied` installing | you forgot `sudo` | `sudo apt install ...` |
| `tar: Cowardly refusing to create an empty archive` | no file names given | add what to archive |
| `tar: Removing leading '/' from member names` | harmless warning | it's a safety feature |
| `command not found` for your script | its folder isn't on `PATH` | `./script` or add the folder to PATH |
| PATH reset every time | `export` only lasts for that terminal | put it in `~/.bashrc` |
| `ping: unknown host` | DNS or internet is down | check Wi-Fi; try `ping 8.8.8.8` (an IP) |
| `curl: (6) Could not resolve host` | same | check the spelling of the URL |
| ssh `Permission denied (publickey)` | wrong user/key | check the user name; `ssh -v` for details |

## Tryouts

Work in `~/linux-lab/playground`. Check with `bash ~/linux-lab/check.sh 9`.

**Tryout 1 · Warm-up.** Run `cat /etc/os-release`. Which distribution is it, and which package manager does it use? Then use `apt search` (or `dnf search`) for the word `htop` and read the first result.

<details class="solution">
<summary>Answer</summary>

On Ubuntu/Debian/WSL you'll see `NAME="Ubuntu"` (or Debian) and use **apt**. On Fedora/RHEL you'll see `NAME="Fedora Linux"` and use **dnf**.

</details>

**Tryout 2 · Build.** Make `archive.tar.gz` containing the `docs` folder of the lab (use `-C ~/linux-lab`), list its contents with `tar -tzf`, then extract it into a new folder `extract`. Also save your **PATH** into `path.txt`.

<details class="solution">
<summary>Answer</summary>

```bash
cd ~/linux-lab/playground
tar -czf archive.tar.gz -C ~/linux-lab docs
tar -tzf archive.tar.gz
mkdir -p extract
tar -xzf archive.tar.gz -C extract
ls extract/docs
echo $PATH > path.txt
```

</details>

**Tryout 3 · Challenge.** Create `~/bin/hello` from `~/linux-lab/scripts/hello.sh`, put `~/bin` on your `PATH` (for this terminal), and run `hello` from **a different folder** (for example `/tmp`). Then use `which hello` to show where Linux found it.

<details class="solution">
<summary>Answer</summary>

```bash
mkdir -p ~/bin
cp ~/linux-lab/scripts/hello.sh ~/bin/hello
chmod +x ~/bin/hello
export PATH="$HOME/bin:$PATH"
cd /tmp
hello                 # Hello from a script!
which hello           # /home/asha/bin/hello
```

</details>

```bash
bash ~/linux-lab/check.sh 9
```

## Quiz

Take **"Session 9 · Quiz"** from the portal's **Quizzes** page.

## Recap

- ✅ **apt** (Debian/Ubuntu) / **dnf** (Fedora/RHEL): `update`, `install`, `remove`, `search`. `update` refreshes the list; `upgrade` installs newer versions.
- ✅ `curl` and `wget` download; `curl -I` shows headers.
- ✅ **tar**: `czf` create, `tzf` list, `xzf` extract; `gzip`/`zip` for single files and Windows-friendly archives.
- ✅ **Variables** (`export`, `printenv`); **`PATH`** is the list of folders searched for commands; persist changes in `~/.bashrc`.
- ✅ `ip addr`, `ping -c`, `ss -tln`, `dig`; `ssh` and `scp` for remote machines; keys beat passwords.

**Next:** [Session 10 · Shell Scripting](10-shell-scripting.md): automate everything you've learned.
