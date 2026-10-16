# Cheat Sheet and Glossary

Keep this page open while you practise. Each table matches a session.

## Getting around (Sessions 1-2)

| Command | Does |
|---|---|
| `pwd` | where am I? |
| `ls`, `ls -lah` | list files (long, all, human sizes) |
| `cd dir`, `cd ..`, `cd ~`, `cd -` | go to a folder / up / home / back |
| `man cmd`, `cmd --help` | help (**q** quits `man`) |
| `whoami`, `hostname`, `date`, `uname -a` | who, where, when, what system |
| `clear` (Ctrl + L) | clear the screen |
| **Tab**, **↑**, `history`, **Ctrl + R**, **Ctrl + C** | complete, previous, list history, search history, stop |

## Files (Sessions 3-4)

| Command | Does |
|---|---|
| `mkdir -p a/b/c` | make folders (with parents) |
| `touch f` | create an empty file |
| `cp f g`, `cp -r d e` | copy file / folder |
| `mv a b` | move **or** rename |
| `rm f`, `rm -i f`, `rmdir d`, `rm -r d` | delete (no recycle bin!) |
| `cat f`, `less f`, `head -n 5 f`, `tail -n 5 f`, `tail -f f` | read files |
| `wc -l f` | count lines (`-w` words, `-c` bytes) |
| `nano f` | edit (**Ctrl + O** save, **Ctrl + X** exit) |
| `> f`, `>> f` | overwrite / append output to a file |
| `*`, `?`, `[ab]`, `{a,b}` | wildcards and braces |

## Text and pipes (Sessions 5-6)

| Command | Does |
|---|---|
| `a \| b` | pipe: output of `a` becomes input of `b` |
| `grep -i -v -n -c -r pat f` | find lines (ignore case, invert, numbers, count, recursive) |
| `sort -nr`, `uniq -c` | sort (numbers, reverse); count repeats (**sort first**) |
| `sort f \| uniq -c \| sort -nr` | the count-and-rank pattern |
| `cut -d, -f1,3 f` | pick columns |
| `awk -F, '{print $1}' f` | columns with logic |
| `sed 's/old/new/g' f` | replace text |
| `tr a-z A-Z` | translate characters |
| `2> f`, `2>&1`, `> /dev/null` | redirect errors / both / discard |
| `find . -name "*.log" -type f -mtime -7` | find files by name, type, age |
| `grep -rl word .` | which files contain a word |
| `du -sh *`, `du -ah . \| sort -rh \| head` | sizes, biggest things |

## Users and permissions (Session 7)

| Item | Meaning |
|---|---|
| `r=4 w=2 x=1` | add them per owner / group / others |
| `644` `rw-r--r--` | normal file |
| `600` `rw-------` | private file |
| `755` `rwxr-xr-x` | program or public folder |
| `chmod +x f`, `chmod 600 f`, `chmod go-rwx f` | change permissions |
| `chown user:group f` | change owner (needs `sudo`) |
| `id`, `groups` | who am I, which groups |
| `sudo cmd` | run one command as root (use carefully) |

## Processes and services (Session 8)

| Command | Does |
|---|---|
| `ps aux`, `pgrep -l name` | list / find processes |
| `top` / `htop`, `uptime`, `free -h` | live view, load, memory |
| `cmd &`, `jobs`, `fg`, `bg`, **Ctrl + Z** | background and job control |
| `kill PID`, `kill -9 PID`, `pkill name` | stop (polite / force / by name) |
| `systemctl status\|start\|stop\|restart\|enable NAME` | services |
| `crontab -e` | schedule: `m h dom mon dow command` |

## Packages and network (Session 9)

| Command | Does |
|---|---|
| `sudo apt update` / `upgrade` / `install x` / `remove x` | Debian/Ubuntu packages |
| `sudo dnf install x` | Fedora/RHEL packages |
| `curl -s URL`, `curl -I URL`, `curl -O URL`, `wget URL` | download / headers |
| `tar -czf a.tgz dir`, `tar -tzf a.tgz`, `tar -xzf a.tgz` | create / list / extract |
| `zip -r a.zip dir`, `unzip a.zip` | zip files |
| `echo $PATH`, `export X=1`, `printenv` | variables |
| `ip -br addr`, `ping -c 3 host`, `ss -tln`, `dig host +short` | network |
| `ssh user@host`, `scp file user@host:path` | remote login and copy |

## Scripts and troubleshooting (Sessions 10-11)

| Item | Meaning |
|---|---|
| `#!/usr/bin/env bash` | first line of a script |
| `"$1"`, `$#`, `$@`, `$?` | argument, count, all, exit code |
| `if [ -f f ]; then ... fi` | decisions |
| `for x in a b; do ... done` | loops |
| `set -eu` | stop on errors and unset variables |
| `bash -x script` | trace every command |
| `df -h`, `du -h --max-depth=1 . \| sort -rh` | disk space |
| `journalctl -u NAME -n 50`, `tail -f /var/log/syslog` | logs |

## Glossary

| Word | Meaning |
|---|---|
| **Kernel** | the core of the operating system; Linux is a kernel |
| **Distribution (distro)** | kernel + tools + package manager: Ubuntu, Fedora, Debian... |
| **Shell** | the program that reads your commands (bash) |
| **Terminal** | the window you type in |
| **Directory** | a folder |
| **Path** | the address of a file; **absolute** starts with `/`, **relative** doesn't |
| **Root (`/`)** | the top of the file tree; also the all-powerful **root** user |
| **Home (`~`)** | your personal folder |
| **Option / flag** | changes how a command works (`-l`, `--help`) |
| **Argument** | what the command works on |
| **stdin / stdout / stderr** | input, normal output, error output |
| **Pipe `\|`** | connects one command's output to another's input |
| **Redirect `>` `>>`** | send output to a file |
| **Permission** | who may read, write or execute |
| **Process / PID** | a running program / its number |
| **Daemon / service** | a program that runs in the background |
| **Package** | software bundled for installation |
| **Repository** | the online store a package manager downloads from |
| **Environment variable** | a named value programs can read (`PATH`, `HOME`) |
| **Shebang** | `#!` first line that says which program runs the script |
| **Exit code** | the number a program returns: 0 = success |
| **Cron** | the scheduler that runs commands at set times |
| **Log** | a file where a program records what it did |
