# Session 2 · Installing and configuring Git

## The big idea

Before your first commit you tell Git **who you are**, because every commit is stamped with a name
and email. Git keeps settings at three levels (system, global, local); the most specific level wins.
You set your identity once globally, and override it in any project that needs a different one.

**Everyday example:** a visiting card and an office ID. Your personal card (global) has your own name
and email. When you work on a client's project you might hand over the client-issued ID (local) instead.
Git uses the more specific one for that project.

```{raw} html
:file: ../diagrams/config-levels.html
```

## Install Git

| System | Command |
|---|---|
| Ubuntu / Debian | `sudo apt install git` |
| macOS | `brew install git` (or install Xcode command line tools) |
| Windows | Download *Git for Windows* from git-scm.com |

Check it worked with `git --version`. Full instructions for every system are in the official
[Pro Git book](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).

## Set your identity, and override it for one project

`02-config.sh` sets a global identity, then makes a project that uses a different one. It runs in a throwaway
home folder, so your real settings are never touched.

```{literalinclude} ../code/02-config.sh
:language: bash
```

```{literalinclude} ../code/02-config.out
:language: text
```

Reading the output:

- **`--global`** wrote to `~/.gitconfig`. `git config --global --list` shows the three keys we set
  (Git prints key names in lower case).
- **No flag inside a repository** writes to that repository's `.git/config`: the *local* level.
- **`--show-origin`** reveals where each value comes from. The project has both `DevUser` (global) and
  `ProjectUser` (local); the **later, more specific one wins**.
- **`git config user.name`** prints the winning value, `ProjectUser`.
- The commit is stamped `ProjectUser <projectuser@example.com>`, proving which identity was used.

## Other settings worth knowing

| Setting | What it does |
|---|---|
| `init.defaultBranch main` | Name the first branch `main` instead of `master` |
| `core.editor "code --wait"` | Choose the editor for commit messages |
| `pull.rebase false` | Make `git pull` merge (avoids a warning) |
| `alias.st status` | Type `git st` instead of `git status` |

## Common mistakes

- **Skipping the identity.** Git refuses to commit ("Please tell me who you are") or guesses a wrong name
  from your computer.
- **Using a work email in personal projects**, or the reverse. Set a local override per project.
- **Typos in `--global` versus local.** Forgetting `--global` inside a repository sets it for that project
  only, and outside any repository it fails.
- **Changing the identity and expecting old commits to change.** Settings apply to *new* commits only.
- **Putting secrets in config.** `.git/config` and `~/.gitconfig` are plain text files.

## Hands-on exercises

**Exercise 1.** Set your name and email globally and print them back.

<details class="solution"><summary>Solution</summary>

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global user.name
git config --global user.email
```

The last two commands print what you just set.

</details>

**Exercise 2.** Make a repository whose commits use `Team Bot <bot@example.com>` without changing your global identity.

<details class="solution"><summary>Solution</summary>

```bash
git init bot-project && cd bot-project
git config user.name "Team Bot"
git config user.email "bot@example.com"
git commit --allow-empty -m "test"
git log -1 --format='%an <%ae>'
```

It prints `Team Bot <bot@example.com>`, while other repositories still use your global identity.

</details>

**Exercise 3.** Use `git config --show-origin` to find which file supplies your `user.email` in the current repository.

<details class="solution"><summary>Solution</summary>

```bash
git config --show-origin user.email
```

It prints the file path and the value: `.git/config` if you set a local override, otherwise `~/.gitconfig`.

</details>

## Practice

Take the **Session 2 quiz**. The original *Git Installation and Initial Configs* page is in the reference section.
