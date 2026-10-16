# Session 7 · Users and Permissions

**⏱ about 75 minutes · 🧰 you need: [Session 6](06-finding-things.md) done**

## The big idea

Linux was built for **many people sharing one computer**. So every file has an **owner** and a set of **rules about who may read,
change or run it**. This is why a stranger (or a buggy program) can't wipe the system. And it's why beginners hit **"Permission denied"**
so often. By the end of this session you'll know exactly what that message means and how to fix it safely.

**Everyday example:** an office building with key cards. *You* can enter your own room and read your own papers. People in *your team*
may enter the team room. *Everybody else* can only use the lobby. The **security desk** (the administrator, **root**) can open every door.

```{raw} html
:file: ../diagrams/l07-owner-group-others.html
```

## 1. Who am I? Users and groups

```bash
whoami
id
```

```text
asha
uid=1000(asha) gid=1000(asha) groups=1000(asha),27(sudo),100(users)
```

| Part | Meaning |
|---|---|
| `uid=1000(asha)` | your **user ID** and name |
| `gid=1000(asha)` | your **primary group** |
| `groups=...` | every **group** you belong to. `sudo` here means you may use `sudo` (below) |

* A **user** is an account. Real people and also *programs* (like the web server) have users.
* A **group** is a set of users that share access (for example `developers`).
* The all-powerful administrator is **`root`** (user ID 0).

Linux keeps the user list in a plain text file:

```bash
head -n 2 /etc/passwd
```

```text
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
```

Fields: `name:password-placeholder:UID:GID:comment:home:shell`. Passwords are **not** in this file (they're hashed in `/etc/shadow`, readable only by root):

```bash
cat /etc/shadow
```

```text
cat: /etc/shadow: Permission denied
```

That is permissions protecting a secret. 🔒

## 2. Reading permissions

```bash
cd ~/linux-lab
ls -l scripts/hello.sh
```

```text
-rw-rw-r-- 1 asha asha 48 Oct 15 23:13 scripts/hello.sh
```

The first column is a 10-character code:

```{raw} html
:file: ../diagrams/l07-permissions.html
```

```text
-  rw-  rw-  r--
│  │    │    └─ others (everyone else)
│  │    └────── group
│  └─────────── owner (user)
└────────────── type: - file, d directory, l link
```

Each triplet is **r** (read), **w** (write), **x** (execute), or `-` when not allowed:

| Letter | On a **file** | On a **directory** |
|---|---|---|
| `r` read | see the contents | **list** the files inside (`ls`) |
| `w` write | change the contents | **create, delete, rename** files inside |
| `x` execute | **run** it as a program/script | **enter** it (`cd`) and reach what's inside |

So `-rw-rw-r--` means: a **file**; the owner and the group can **read and write**; everyone else can only **read**. Nobody can *run* it
(no `x`).

## 3. Change permissions: `chmod`

`chmod` = **ch**ange **mod**e. There are two ways to say it.

### Way 1: symbols (easy to read)

Format: **who** `+` or `-` or `=` **what**.

| Who | | Action | | What | |
|---|---|---|---|---|---|
| `u` user (owner) | | `+` add | | `r` read | |
| `g` group | | `-` remove | | `w` write | |
| `o` others | | `=` set exactly | | `x` execute | |
| `a` all | | | | | |

```bash
chmod +x scripts/hello.sh       # add execute for everybody
ls -l scripts/hello.sh
```

```text
-rwxrwxr-x 1 asha asha 48 Oct 15 23:13 scripts/hello.sh
```

```bash
chmod go-rwx scripts/hello.sh   # remove ALL rights from group and others
ls -l scripts/hello.sh
```

```text
-rwx------ 1 asha asha 48 Oct 15 23:13 scripts/hello.sh
```

### Way 2: numbers (what everyone writes)

Each permission has a value: **r = 4, w = 2, x = 1**. Add them per group of people:

```{raw} html
:file: ../diagrams/l07-octal.html
```

| Number | Math | Meaning |
|---|---|---|
| **7** | 4+2+1 | `rwx` |
| **6** | 4+2 | `rw-` |
| **5** | 4+1 | `r-x` |
| **4** | 4 | `r--` |
| **0** | 0 | `---` |

Three digits = **owner, group, others**:

| Mode | Means | Used for |
|---|---|---|
| **644** | `rw-r--r--` | normal files everyone can read |
| **600** | `rw-------` | **private** files (SSH keys, secrets) |
| **755** | `rwxr-xr-x` | programs/scripts and public folders |
| **700** | `rwx------` | a private folder |
| **777** | `rwxrwxrwx` | **everyone can do anything.** ❌ almost never use it |

```bash
cd playground
echo "my secret" > secret.txt
chmod 600 secret.txt
ls -l secret.txt
```

```text
-rw------- 1 asha asha 10 Oct 15 23:17 secret.txt
```

```bash
stat -c "%a %A %U %n" secret.txt
```

```text
600 -rw------- asha secret.txt
```

(`stat -c "%a ..."` is a handy way to see the **number** of a file's permissions.)

## 4. Running scripts: why `./hello.sh` says "Permission denied"

```bash
cd ~/linux-lab/scripts
chmod 644 hello.sh        # make it a plain, non-executable file
./hello.sh
```

```text
bash: ./hello.sh: Permission denied
```

```bash
chmod +x hello.sh
./hello.sh
```

```text
Hello from a script!
```

A script is just text. Without `x`, Linux **refuses to run** it. (You can still run it by naming the interpreter: `bash hello.sh`, which only needs *read*.)
The `./` means *"the file in this folder"*. Linux doesn't search the current folder for programs, on purpose, for safety.

## 5. Ownership: `chown` and `chgrp`

Every file has an **owner** and a **group**. Changing them needs administrator rights:

```bash
sudo chown asha file.txt              # change the owner
sudo chown asha:developers file.txt   # owner AND group
sudo chown -R asha:asha myfolder/     # a whole folder (-R recursive)
```

## 6. Becoming the administrator: `sudo`

`sudo` = **s**uper**u**ser **do**: *"run just this one command with administrator power."*

```bash
sudo apt update
```

It asks for **your own** password (not root's). Rules:

* Use `sudo` **only when a command truly needs it** (installing software, editing `/etc`, changing system files).
* **Never** put `sudo` in front of a command you don't understand. `sudo` removes the safety net.
* `sudo` is logged: admins can see who ran what.
* Prefer to **fix the permission** (`chmod`) rather than "just sudo everything".

```bash
sudo whoami
```

```text
root
```

| Command | Does |
|---|---|
| `sudo command` | run one command as root |
| `sudo -i` | open a root shell (**careful**: prompt shows `#`; type `exit` to leave) |
| `su - otheruser` | switch to another user (needs *their* password) |
| `exit` | leave the shell / go back |

Add a user and group (needs sudo; try only on your own machine or VM):

```bash
sudo adduser meena            # create a user
sudo usermod -aG sudo meena   # give them sudo rights (-aG = ADD to Group)
groups meena
```

## 7. New files get default permissions: `umask`

```bash
umask
touch u.txt
mkdir ud
ls -ld u.txt ud
```

```text
0002
drwxrwxr-x 2 asha asha 4096 Oct 15 23:17 ud
-rw-rw-r-- 1 asha asha    0 Oct 15 23:17 u.txt
```

New files start from `666` and new folders from `777`, **minus** the `umask`. With `0022` (common on many systems) you'd get `644` and `755`;
with `0002` (Ubuntu's default for personal groups) you get `664` and `775`. You rarely change it. It explains *why* new files look the way they do.

## 8. A peek at special permission bits

```bash
ls -l /usr/bin/passwd
```

```text
-rwsr-xr-x 1 root root 59976 Feb  6  2024 /usr/bin/passwd
```

The `s` in place of `x` is the **setuid** bit: this program runs **as its owner (root)** even when *you* start it. That is how a normal user can change their own
password (which lives in a root-only file). You don't need to set these yourself. Just know what the `s` means.

## Common mistakes

| You saw | Meaning | Fix |
|---|---|---|
| `Permission denied` running `./script.sh` | no `x` bit | `chmod +x script.sh` |
| `Permission denied` reading a file | no `r` for you | check `ls -l`; `chmod` it if you own it |
| `Permission denied` creating a file | no `w` on the **folder** | check `ls -ld folder` |
| `cd: Permission denied` | no `x` on the **folder** | `chmod +x folder` (if yours) |
| `Operation not permitted` on chown | you're not root | `sudo` |
| `chmod 777` "fixes" everything | it opens a security hole | find the exact right mode instead (644/755) |
| `sudo: command not found` | minimal container | install it, or you may already be root |
| SSH says *"UNPROTECTED PRIVATE KEY FILE"* | key file too open | `chmod 600 ~/.ssh/id_rsa` |
| `sudo rm -rf` anything | no safety net | **don't** |

## Tryouts

Work in `~/linux-lab/playground`. Check with `bash ~/linux-lab/check.sh 7`.

**Tryout 1 · Warm-up.** Read these and say what each permits: `-rwxr-xr-x`, `-rw-------`, `drwxr-x---`.

<details class="solution">
<summary>Answer</summary>

* `-rwxr-xr-x` (755): a file the owner can read/write/run; everyone else can read and run it. A typical **program**.
* `-rw-------` (600): a file only the owner can read or write. A typical **secret**.
* `drwxr-x---` (750): a **directory**; the owner has full access, the group can list and enter it, others can't touch it.

</details>

**Tryout 2 · Build.** Create `secret.txt` (any text) that **only you** can read and write (`600`), and create `shared.txt` that **everyone can read but only you can change** (`644`). Show both with `ls -l`.

<details class="solution">
<summary>Answer</summary>

```bash
cd ~/linux-lab/playground
echo "only for me" > secret.txt
chmod 600 secret.txt
echo "for everyone" > shared.txt
chmod 644 shared.txt
ls -l secret.txt shared.txt
```

```text
-rw------- 1 asha asha 12 Oct 15 23:30 secret.txt
-rw-r--r-- 1 asha asha 13 Oct 15 23:30 shared.txt
```

</details>

**Tryout 3 · Challenge.** Make `~/linux-lab/scripts/hello.sh` **executable** and run it with `./hello.sh`. Then take away execute permission with the **symbolic** form (not numbers), and prove `./hello.sh` fails again. Finally restore it.

<details class="solution">
<summary>Answer</summary>

```bash
cd ~/linux-lab/scripts
chmod +x hello.sh && ./hello.sh          # Hello from a script!
chmod -x hello.sh && ./hello.sh          # Permission denied
chmod +x hello.sh                        # restore (the checker wants it executable)
```

</details>

```bash
bash ~/linux-lab/check.sh 7
```

## Quiz

Take **"Session 7 · Quiz"** from the portal's **Quizzes** page.

## Recap

- ✅ Every file has an **owner**, a **group** and rules for **others**: `rwx` for each.
- ✅ `chmod` with symbols (`u+x`, `go-rwx`) or numbers (**r=4 w=2 x=1** → `644`, `600`, `755`).
- ✅ On **directories**: `r` = list, `w` = create/delete inside, `x` = enter.
- ✅ A script needs `x` to run as `./script.sh`.
- ✅ `sudo` = one command as root: use it deliberately. `chown` changes the owner.
- ✅ **Never `chmod 777`**: find the exact permission instead.

**Next:** [Session 8 · Processes and Services](08-processes-and-services.md).
