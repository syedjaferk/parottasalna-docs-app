# Session 2 · Files and Directories

**⏱ about 60 minutes · 🧰 you need: [Session 1](01-first-steps.md) done, `~/linux-lab` created**

## The big idea

Everything in Linux lives in **one big tree of folders**. (Linux calls folders **directories**: same thing.)
To work in the terminal you must always know two things: **where am I?** and **how do I get to where I want to be?**

**Everyday example:** an apartment complex. A *full address* ("Block C, Floor 3, Flat 302") works from anywhere. A *relative
direction* ("go two doors left") only works if you know where you're standing. Linux has both kinds of addresses: **absolute
paths** and **relative paths**.

```{raw} html
:file: ../diagrams/l02-tree.html
```

## 1. The shape of the file system

There is a single starting point, the **root**, written `/`. Everything hangs under it. The important branches:

| Path | What lives there | Windows comparison |
|---|---|---|
| `/` | the root of everything | `C:\` |
| `/home/asha` | **your home folder**: your files, settings | `C:\Users\asha` |
| `/etc` | system **configuration** files | (registry-ish) |
| `/var/log` | **logs** (what the system and programs did) | Event Viewer |
| `/tmp` | temporary files (cleared on reboot) | `%TEMP%` |
| `/usr/bin`, `/bin` | the **programs** (commands) | `C:\Program Files` |
| `/dev` | devices shown as files (disks, terminals) | Device Manager |
| `/proc` | live information about the system and processes | Task Manager |

:::{note}
There are **no drive letters** (`C:`, `D:`). A second disk or USB stick is **mounted** somewhere *inside* the one tree, often under
`/mnt` or `/media`. In WSL your Windows C: drive appears at `/mnt/c`.
:::

## 2. Where am I? `pwd`

```bash
pwd
```

```text
/home/asha
```

`pwd` = **p**rint **w**orking **d**irectory. The terminal is *always* "inside" one directory, the **current directory**. At
the start it is your **home folder**, which has a short name: `~`.

## 3. What is here? `ls`

```bash
cd ~/linux-lab
ls
```

```text
data  docs  logs  playground  scripts
```

`ls` lists the contents of the current directory. Options make it more useful:

```bash
ls -l data
```

```text
total 8
-rw-rw-r-- 1 asha asha  76 Oct 15 23:13 fruits.txt
-rw-rw-r-- 1 asha asha 278 Oct 15 23:13 people.csv
```

```bash
ls -la
```

```text
total 28
drwxrwxr-x 7 asha asha 4096 Oct 15 23:13 .
drwxrwxr-x 3 asha asha 4096 Oct 15 23:13 ..
drwxrwxr-x 2 asha asha 4096 Oct 15 23:13 data
drwxrwxr-x 2 asha asha 4096 Oct 15 23:13 docs
drwxrwxr-x 2 asha asha 4096 Oct 15 23:13 logs
drwxrwxr-x 2 asha asha 4096 Oct 15 23:13 playground
drwxrwxr-x 2 asha asha 4096 Oct 15 23:13 scripts
```

```bash
ls -lh logs
```

```text
total 12K
-rw-rw-r-- 1 asha asha 4.5K Oct 15 23:13 access.log
-rw-rw-r-- 1 asha asha  652 Oct 15 23:13 app.log
```

| Option | Meaning |
|---|---|
| `-l` | **l**ong format: permissions, owner, size, date |
| `-a` | **a**ll: also show **hidden** files (names starting with a dot, like `.bashrc`) |
| `-h` | **h**uman-readable sizes (`4.5K` instead of `4608`) |
| `-t` | sort by modification **t**ime (newest first) |
| `-R` | **r**ecursive: also list everything inside sub-folders |
| `-d` | list the folder itself, not its contents |

You can combine them: `ls -lah`, `ls -ltr` (oldest first).

### Reading one line of `ls -l`

```text
-rw-rw-r-- 1 asha asha  76 Oct 15 23:13 fruits.txt
│└─┬──┘    │ │    │     │  └─────┬─────┘ └──┬─────┘
│  │       │ │    │     │        │          └ name
│  │       │ │    │     │        └ last modified
│  │       │ │    │     └ size in bytes
│  │       │ │    └ group
│  │       │ └ owner
│  │       └ number of links
│  └ permissions (Session 7)
└ type: - file, d directory, l link
```

## 4. Moving around: `cd`

`cd` = **c**hange **d**irectory.

```bash
cd data
pwd
```

```text
/home/asha/linux-lab/data
```

```bash
cd ..
pwd
```

```text
/home/asha/linux-lab
```

The shortcuts you need:

| Shortcut | Meaning |
|---|---|
| `.` | **this** directory |
| `..` | the **parent** directory (one level up) |
| `~` | your **home** directory |
| `/` | the **root** |
| `-` | the directory you were **just in** (`cd -` flips back) |
| (nothing) | `cd` alone takes you **home** from anywhere |

```bash
cd /var/log      # an absolute path
pwd
cd ~             # back home
cd -             # and back to /var/log
```

## 5. Absolute and relative paths

```{raw} html
:file: ../diagrams/l02-paths.html
```

A **path** is the address of a file or directory.

* **Absolute path:** starts with `/`. Works from anywhere. Example: `/home/asha/linux-lab/data/fruits.txt`.
* **Relative path:** does *not* start with `/`. It is counted from where you are now. Example (from `~/linux-lab`): `data/fruits.txt`.

```bash
cd ~/linux-lab
ls data/            # relative: "data" inside where I am now
ls /home/$USER/linux-lab/data/    # absolute: the full address
ls ../              # the parent of where I am
```

(`$USER` is a **variable** that holds your user name, so the same command works for everyone.)

**Which to use?** Absolute when you want to be sure ("this exact place"). Relative when working near where you are (shorter to type).

Two helper commands split a path into its parts:

```bash
basename /home/asha/linux-lab/data/fruits.txt
dirname /home/asha/linux-lab/data/fruits.txt
```

```text
fruits.txt
/home/asha/linux-lab/data
```

## 6. Spaces in names, and hidden files

Linux file names *can* contain spaces, but then the shell thinks they are **two** words. Wrap such names in quotes (or avoid spaces: use `my_notes.txt` or `my-notes.txt`):

```bash
cd ~/linux-lab/playground
mkdir "my folder"      # one folder with a space
ls
cd "my folder"
```

Names that start with a **dot** are **hidden**: `ls` doesn't show them unless you use `-a`. Your home folder has many (`.bashrc`, `.profile`): settings files.

```bash
ls -a ~ | head
```

## 7. See the whole tree

The `tree` command draws a folder as a tree (install it with `sudo apt install tree` if it is missing):

```bash
cd ~/linux-lab
tree
```

```text
.
├── data
│   ├── fruits.txt
│   └── people.csv
├── docs
│   ├── notes.md
│   └── readme.txt
├── logs
│   ├── access.log
│   └── app.log
├── playground
└── scripts
    └── hello.sh

5 directories, 6 files
```

Without `tree`, `ls -R` (recursive) gives a similar overview.

## Common mistakes

| You saw | What it means | Fix |
|---|---|---|
| `cd: data: No such file or directory` | there is no `data` *here* | `pwd` and `ls` to check where you are |
| `cd: too many arguments` | a space in a name | quote it: `cd "my folder"` |
| `ls: cannot access 'Data'` | wrong capital letter | names are case-sensitive |
| you "lost" yourself | you can't tell where you are | `pwd`, then `cd ~` to go home |
| `cd /home/asha/..` confusion | `..` is "go up" | `/home/asha/..` is `/home` |
| files "missing" | they are hidden | `ls -a` |

## Tryouts

Work in `~/linux-lab/playground`. Check with `bash ~/linux-lab/check.sh 2`.

**Tryout 1 · Warm-up.** Use only `cd` and `pwd`: go to `/etc`, then `/var/log`, then back home in **one** command, then to the previous place using `-`.

<details class="solution">
<summary>Answer</summary>

```bash
cd /etc
cd /var/log
cd          # or: cd ~
cd -        # back to /var/log
pwd
```

</details>

**Tryout 2 · Build.** Create the folder chain `playground/map/a/b/c` **with one command** (hint: `mkdir -p`). Then use a **relative** `cd` to enter `c` in one go, and `pwd` to see where you are.

<details class="solution">
<summary>Answer</summary>

```bash
cd ~/linux-lab/playground
mkdir -p map/a/b/c
cd map/a/b/c
pwd
```

`-p` means *create all the parents as needed*, so you don't have to make `a`, `b`, `c` one by one.

</details>

**Tryout 3 · Challenge.** Without leaving `~/linux-lab`, save the list of files in your **home folder** into `playground/map/home-copy.txt` and the **current directory** into `playground/map/where.txt` (use `ls`, `pwd` and `>`).

<details class="solution">
<summary>Answer</summary>

```bash
cd ~/linux-lab
ls ~ > playground/map/home-copy.txt
pwd > playground/map/where.txt
cat playground/map/where.txt
```

`ls ~` lists a folder **you are not in**: any command can be pointed at any path.

</details>

```bash
bash ~/linux-lab/check.sh 2
```

## Quiz

Take **"Session 2 · Quiz"** from the portal's **Quizzes** page.

## Recap

- ✅ One tree starting at `/`; your home is `~`; no drive letters.
- ✅ `pwd` (where am I), `ls` (what's here: `-l -a -h`), `cd` (go there).
- ✅ `.` here, `..` up, `~` home, `-` previous, `cd` alone = home.
- ✅ **Absolute** paths start with `/`; **relative** paths start from where you are.
- ✅ Hidden files start with a dot; spaces in names need quotes.
- ✅ `mkdir -p` creates a whole chain at once.

**Next:** [Session 3 · Working with Files](03-working-with-files.md): create, copy, move and delete (carefully!).
