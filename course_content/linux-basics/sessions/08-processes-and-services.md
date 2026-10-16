# Session 8 · Processes and Services

**⏱ about 75 minutes · 🧰 you need: [Session 7](07-users-and-permissions.md) done**

## The big idea

Every program that is running on Linux is a **process**. Your terminal is a process; the clock is a process; the web server is a
process. Linux gives each one a number, the **PID** (process ID), and lets you **see**, **pause**, **stop** and **schedule** them.

**Everyday example:** a busy kitchen. Each **dish being cooked** is a process with an order number (PID). The head chef (you, or the
system) can *check which dishes are cooking*, *take one off the stove* or *schedule one to start at 6 pm*.

```{raw} html
:file: ../diagrams/l08-processes.html
```

## 1. See processes: `ps`

```bash
ps
```

```text
    PID TTY          TIME CMD
   2410 pts/0    00:00:00 bash
   2873 pts/0    00:00:00 ps
```

By default `ps` shows **only the processes in your terminal**. To see **everything** on the system:

```bash
ps aux | head -n 5
```

```text
USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root           1  0.0  0.1 168312 12040 ?        Ss   09:00   0:02 /sbin/init
root           2  0.0  0.0      0     0 ?        S    09:00   0:00 [kthreadd]
asha        2410  0.0  0.1  11672  5400 pts/0    Ss   09:30   0:00 -bash
asha        2873  0.0  0.0  13400  3600 pts/0    R+   09:31   0:00 ps aux
```

| Column | Meaning |
|---|---|
| `USER` | who runs it |
| `PID` | the process ID (the number you use to control it) |
| `%CPU`, `%MEM` | how much processor / memory it uses |
| `STAT` | state: `S` sleeping, `R` running, `Z` zombie, `T` stopped |
| `COMMAND` | what was started |

(Your list will be different, with many more lines.) PID **1** is the first process; everything else descends from it.

**Find one process by name:**

```bash
ps aux | grep bash
pgrep -l bash        # a shortcut: PIDs of processes named bash
```

## 2. Live view: `top` and `htop`

```bash
top
```

`top` shows a **live, updating** list sorted by CPU use. The first lines summarise the machine: *load average*, tasks, CPU and memory.

| Key in `top` | Does |
|---|---|
| `q` | **quit** |
| `M` | sort by memory |
| `P` | sort by CPU |
| `k` | kill a process (asks for the PID) |
| `1` | show each CPU core |

`htop` is a prettier, friendlier version (`sudo apt install htop`). Use whichever you have.

**Memory and uptime at a glance:**

```bash
uptime
free -h
```

```text
 11:42:08 up 2:41,  1 user,  load average: 0.15, 0.20, 0.18
               total        used        free      shared  buff/cache   available
Mem:           7.6Gi       2.1Gi       3.0Gi       190Mi       2.5Gi       5.2Gi
Swap:          2.0Gi          0B       2.0Gi
```

(*Load average* is how many processes wanted the CPU in the last 1, 5, 15 minutes. If it is higher than your number of CPU cores for long, the machine is overloaded.
`available` is the memory you can still use.)

## 3. Running things in the background

When you start a program, the terminal **waits** for it to finish. For long jobs you can put them **in the background**:

```bash
sleep 300 &
```

```text
[1] 2955
```

* `sleep 300` just waits for 300 seconds (a harmless practice program).
* The `&` at the end means *"run it in the background and give me my prompt back"*.
* `[1]` is the **job number** in this terminal; `2955` is its **PID**.

| Command | Does |
|---|---|
| `jobs` | list background jobs of this terminal |
| `fg` / `fg %1` | bring a job to the **foreground** |
| `bg` | resume a paused job in the background |
| **Ctrl + Z** | **pause** (suspend) the current foreground program |
| **Ctrl + C** | **stop** the current foreground program |

```bash
jobs
```

```text
[1]+  Running                 sleep 300 &
```

Try the pause trick:

```bash
sleep 200          # runs in the foreground; the prompt is gone
# press Ctrl + Z
```

```text
[2]+  Stopped                 sleep 200
```

```bash
bg                 # let it continue in the background
jobs
```

```text
[1]-  Running                 sleep 300 &
[2]+  Running                 sleep 200 &
```

:::{note}
Background jobs belong to **this terminal**. If you close the terminal, they end. To keep a program running after you log out, start it with
`nohup command &` (output goes to `nohup.out`), or use `tmux` / a service (below).
:::

## 4. Stop a process: `kill`

```bash
kill 2955
```

`kill PID` sends a **signal** asking the process to finish politely (signal `TERM`).

```{raw} html
:file: ../diagrams/l08-signals.html
```

| Command | Signal | Meaning |
|---|---|---|
| `kill PID` | `TERM` (15) | *"please shut down"* (the process may clean up first) |
| `kill -9 PID` | `KILL` (9) | *"stop immediately!"* The process **cannot** refuse or clean up |
| `kill -STOP PID` / `kill -CONT PID` | pause / resume | |
| `killall name` / `pkill name` | by **name** | e.g. `pkill sleep` |

**Golden rule:** try plain `kill PID` first. Use `kill -9` only if it ignores you.

```bash
sleep 300 &
echo $!                 # $! holds the PID of the last background job
kill $!                 # stop it
jobs
```

```text
[1]+  Terminated              sleep 300
```

You can only kill **your own** processes (unless you use `sudo`). Killing the wrong thing with `sudo` can crash the system. Check the PID twice.

## 5. Services: programs that run all the time

Web servers, databases and SSH run in the background as **services** (also called *daemons*). Most Linux systems manage them with **systemd**, and its tool is **`systemctl`**.

```bash
systemctl status ssh
```

```text
● ssh.service - OpenBSD Secure Shell server
     Loaded: loaded (/usr/lib/systemd/system/ssh.service; enabled; preset: enabled)
     Active: active (running) since Thu 2026-10-15 09:00:11 IST; 2h 41min ago
   Main PID: 912 (sshd)
```

(Names differ: `ssh` on Ubuntu/Debian, `sshd` on Fedora. In WSL and Docker, systemd may be off, and `systemctl` won't work until you enable it.)

| Command | Does |
|---|---|
| `systemctl status NAME` | is it running? (press **q** to leave) |
| `sudo systemctl start NAME` | start it **now** |
| `sudo systemctl stop NAME` | stop it **now** |
| `sudo systemctl restart NAME` | stop, then start (after changing settings) |
| `sudo systemctl enable NAME` | **start automatically at boot** |
| `sudo systemctl disable NAME` | don't start at boot |
| `systemctl list-units --type=service` | list services |

Two ideas that confuse beginners: **start/stop** = *right now*; **enable/disable** = *at every boot*. They are independent.

## 6. Scheduled jobs: `cron`

**cron** runs commands automatically at times you choose, such as a nightly backup.

```bash
crontab -e        # edit YOUR schedule (choose nano if it asks)
crontab -l        # show it
```

Each line is: **minute hour day-of-month month day-of-week command**

```{raw} html
:file: ../diagrams/l08-cron.html
```

```text
# m  h  dom mon dow   command
30  2  *   *   *     /home/asha/linux-lab/scripts/backup.sh
0   9  *   *   1-5   echo "Good morning" >> /home/asha/morning.log
*/15 * *   *   *     date >> /home/asha/heartbeat.log
```

| Line | Means |
|---|---|
| `30 2 * * *` | at **02:30 every day** |
| `0 9 * * 1-5` | at **09:00 on weekdays** (Mon-Fri) |
| `*/15 * * * *` | **every 15 minutes** |
| `@reboot cmd` | once, when the computer starts |

Tips: use **full paths** in cron (it has a tiny `PATH`); redirect output to a log (`>> file.log 2>&1`); test the command by hand first.

## Common mistakes

| Problem | Why | Fix |
|---|---|---|
| `kill: (1234) - No such process` | it already finished (PIDs change!) | `ps` again |
| `kill: Operation not permitted` | not your process | use `sudo` only if you're sure |
| program closed when I closed the terminal | it was a child of that terminal | `nohup`, `tmux`, or a service |
| `systemctl: command not found` / "System has not been booted with systemd" | WSL/Docker without systemd | use `service NAME status`, or enable systemd in WSL |
| zombie (`Z`) processes | a finished child nobody collected | they vanish when the parent ends; don't `kill -9` them |
| cron job never runs | wrong path or environment | full paths; check `grep CRON /var/log/syslog` |
| `top` won't quit | you're inside it | press **q** |
| killed the wrong PID | PIDs are reused | look at `ps` right before killing |

## Tryouts

Work in `~/linux-lab/playground`. Check with `bash ~/linux-lab/check.sh 8`.

**Tryout 1 · Warm-up.** Run `ps aux | wc -l` (the number of processes), `uptime` and `free -h`. What is your **load average**, and how much memory is **available**?

<details class="solution">
<summary>Answer</summary>

It depends on your machine. On an idle laptop the load average is usually below 1.0 and a good fraction of memory is available. If the load average is above the number of CPU cores (check with `nproc`) for a long time, the machine is overloaded.

</details>

**Tryout 2 · Build.** Start `sleep 300` in the background, save its PID into `my-pid.txt` (hint: `$!`), confirm it is running with `ps -p`, then **stop it** with `kill`. Check that it's gone.

<details class="solution">
<summary>Answer</summary>

```bash
cd ~/linux-lab/playground
sleep 300 &
echo $! > my-pid.txt
ps -p $(cat my-pid.txt)          # shows the sleep process
kill $(cat my-pid.txt)
sleep 1
ps -p $(cat my-pid.txt)          # now shows only the header: it's gone
```

`$(...)` runs a command and drops its output in place (*command substitution*).

</details>

**Tryout 3 · Challenge.** Start two `sleep` jobs in the background. List them with `jobs`, bring the second to the foreground with `fg %2`, pause it with **Ctrl + Z**, then kill **both** with a single command (`pkill sleep`).

<details class="solution">
<summary>Answer</summary>

```bash
sleep 400 &
sleep 500 &
jobs
fg %2              # now in the foreground; press Ctrl+Z
pkill sleep
jobs               # both gone (Terminated)
```

</details>

```bash
bash ~/linux-lab/check.sh 8
```

## Quiz

Take **"Session 8 · Quiz"** from the portal's **Quizzes** page.

## Recap

- ✅ A **process** has a **PID**; `ps aux` lists them, `top`/`htop` show them live, `uptime` and `free -h` give a health check.
- ✅ `command &` runs in the background; `jobs`, `fg`, `bg`, **Ctrl + Z** (pause), **Ctrl + C** (stop).
- ✅ `kill PID` is polite; `kill -9` is the last resort; `pkill name` by name.
- ✅ **Services** via `systemctl status|start|stop|restart|enable`. *start* = now, *enable* = at boot.
- ✅ **cron**: `crontab -e`, five time fields, full paths.

**Next:** [Session 9 · Packages and Network](09-packages-and-network.md).
