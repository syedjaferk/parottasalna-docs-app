# Chapter 2 · Core Linux Prerequisites: Processes, PIDs, Mounts, Signals

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/cwYNIbfwmls"
  title="Episode 2: Core Linux prerequisites" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 **Episode 2** of the [Kube Engineering playlist](https://www.youtube.com/playlist?list=PLMtFsmo8jrN8) (Tamil) · [watch on YouTube](https://www.youtube.com/watch?v=cwYNIbfwmls)

## The big idea

A container is not magic: it's **a normal Linux process with some extra rules**. So to understand
containers you need a few Linux basics: what a process is, how processes are related, how they're
told to stop (signals), how files and folders are attached (mounts)
and where Linux shows you all of this (`/proc`).

**Everyday example:** a company. Every employee (process) has an ID number (PID) and a manager
(parent). The CEO (PID 1) is at the top. Memos (signals) tell people to stop work, and the office
layout (mounts) decides which rooms each person can walk into.

## 1. Processes, parents and PIDs

- A **process** is a running instance of a program. Every process has a unique **PID** (Process ID).
- Every process except PID 1 has a **parent**, identified by its **PPID** (Parent Process ID).
- **PID 1** is the first process the kernel starts at boot (`systemd` on most systems). It is the
  ancestor of every other process.
- A process starts another with `fork()` (make a copy of itself) followed by `exec()` (replace the
  copy with the new program). That's why children inherit their parent's environment variables,
  open files and permissions.
- If a parent dies first, its child becomes an **orphan** and is adopted by PID 1.
- A finished process whose parent hasn't collected its exit status yet is a **zombie**. PID 1 is
  responsible for cleaning up ("reaping") zombies.

```{raw} html
:file: ../diagrams/s02-tree.html
```

```bash
ps -ef          # every process, with its PID and PPID
pstree -p       # the family tree, with PIDs
echo $$         # PID of your current shell
echo $PPID      # PID of your shell's parent
```

:::{important}
**Why this matters for Docker:** the command in your Dockerfile's `CMD`/`ENTRYPOINT` becomes
**PID 1 inside the container**. PID 1 has special duties, like handling stop signals and reaping
zombies. [Chapter 7](07-dockerfile.md) shows what goes wrong when it doesn't.
:::

## 2. Watching and controlling processes

```bash
ps aux                        # all processes, all users
ps aux --sort=-%mem           # biggest memory users first
ps -p <PID> -o pid,ppid,cmd   # just one process, chosen columns
top                           # live view (press q to quit)

kill <PID>                    # send SIGTERM (polite stop)
kill -9 <PID>                 # send SIGKILL (force stop)
pkill -f "python app.py"      # signal processes by command line
jobs; fg; bg                  # manage background jobs in your shell
```

## 3. Signals: messages to a process

A **signal** is a small message the kernel delivers to a process. The process can **catch** it
(run its own code), **ignore** it, or let the **default action** happen. Two signals can never be
caught or ignored: `SIGKILL` and `SIGSTOP`.

| Signal | Number | Default | When you use it |
|---|---|---|---|
| `SIGTERM` | 15 | stop | the polite "please shut down". The app can clean up first. `kill` sends this by default, and so does `docker stop`. |
| `SIGKILL` | 9 | stop | the forced stop. **Can't be caught**, so no cleanup happens. Last resort only. |
| `SIGINT` | 2 | stop | what **Ctrl+C** sends to the program in your terminal. |
| `SIGHUP` | 1 | stop | originally "the terminal hung up"; many servers (nginx, sshd) treat it as "reload your config". |
| `SIGSTOP` / `SIGCONT` | 19 / 18 | pause / resume | pause and resume a process. |

**Rule of thumb:** always try `SIGTERM` first, and use `SIGKILL` only if the process ignores it or
is stuck.

```{raw} html
:file: ../diagrams/s02-stop.html
```

:::{note}
**Exit codes tell you how a process ended.** `0` means success. When a process is killed by a
signal, the exit code is **128 + the signal number**: `137` = 128 + 9 (SIGKILL), `143` = 128 + 15
(SIGTERM). You'll see 137 a lot with containers.
:::

## 4. Mounts: attaching folders

In Linux everything lives in **one** folder tree starting at `/`. Disks, USB drives and network
shares are attached ("**mounted**") onto a folder in that tree.

```bash
findmnt          # every mount, as a tree
df -h            # mounted disks and free space
```

You'll attach your own folders into containers with **bind mounts** in
[Chapter 3](03-permissions-bind-mounts-architecture.md).

## 5. `/proc`: Linux's window into every process

`/proc` isn't a real folder on disk. The kernel generates it on the fly, with one folder per running
process, named by its PID:

```bash
ls /proc/$$                 # files describing your shell process
cat /proc/$$/status | head  # name, state, PID, PPID, memory…
cat /proc/$$/cmdline | tr '\0' ' '   # the exact command line
ls -l /proc/$$/ns           # the namespaces this process belongs to
cat /proc/1/cmdline | tr '\0' ' '    # what PID 1 is
```

Tools like `ps` and `top` simply read these files. Inside a container, `/proc` shows only the
container's own processes. You'll see why in [Under the hood · Namespaces](../deep-dives/namespaces.md).

## Try it yourself

1. Find your shell's PID with `echo $$`, then its whole family with `pstree -p -s $$`.
2. Start `sleep 300 &`, find its PID with `jobs -l`, and stop it politely with `kill`. Check its
   exit code with `wait <PID>; echo $?`.

   <details class="solution">
   <summary>What you should see</summary>

   `143`, which is 128 + 15: the process ended because of SIGTERM.

   </details>

3. Run `cat /proc/1/cmdline | tr '\0' ' '` on your machine, then inside a container:
   `docker run --rm alpine cat /proc/1/cmdline`. Why are they different?

   <details class="solution">
   <summary>Answer</summary>

   On the host, PID 1 is `systemd` (or `init`). Inside the container, PID 1 is the container's own
   command (here, `cat` itself), because the container has its own PID namespace.

   </details>

