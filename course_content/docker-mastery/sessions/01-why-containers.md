# Session 1 · Why containers? Virtual machines versus containers

## The big idea

Software works on your laptop and breaks on the server because the two machines differ: another
Python version, a missing library, a different setting. A **container** packs your program together
with everything it needs into one unit that runs the same everywhere. It is lighter than a virtual
machine because containers **share the host's operating-system kernel** instead of each carrying a
whole OS.

**Everyday example:** the grand house. Many families once shared one big house: one kitchen, one
bathroom, constant clashes over the stove. Giving every family its own separate house (a **virtual
machine**) ended the fights but cost a lot, because each house needs its own foundation, roof and
plumbing. Apartments in one building (**containers**) give each family a private flat with its own
door and its own kitchen, while sharing the foundation and the pipes. Cheaper, quicker to build, still private.

```{raw} html
:file: ../diagrams/vm-vs-container.html
```

## Proof: the container uses the host's kernel

Below, the same command runs on the host and inside an Alpine Linux container. The kernel version
is identical, because there is only one kernel. Yet the *distribution* inside is Alpine, because
the container brings its own files and libraries.

```{literalinclude} ../code/01-kernel.sh
:language: bash
```

```{literalinclude} ../code/01-kernel.out
:language: text
```

What this shows:

- Host and container report the **same kernel** (`6.8.0-138-generic` on this machine). A VM would
  report its own.
- The container is a **separate Alpine userland** (`NAME="Alpine Linux"`) even though the host is
  something else. That is the isolation: its own files, its own libraries.
- The whole Alpine image is **under 9 MB**. A typical VM image is gigabytes.
- Starting, running and removing a container took **about a quarter of a second** on this machine
  (your time will differ). Booting a VM takes seconds to minutes.

## When to choose which

| | Virtual machine | Container |
|---|---|---|
| Isolation | Strong (own OS) | Good (shared kernel) |
| Size | Gigabytes | Megabytes |
| Start time | Seconds to minutes | Under a second |
| Run a different OS (Windows on Linux) | Yes | No, same kernel as the host |
| Typical use | Whole servers, strong separation | Apps and services, many per machine |

They are not rivals: cloud providers often run containers *inside* VMs.

## Common mistakes

- **"A container is a small VM."** It is not. It is an ordinary process on the host, fenced off so it
  sees only its own files, processes and network.
- **Expecting a Windows container on a Linux host** (or the reverse). Containers share the host kernel,
  so the OS family must match.
- **Thinking containers are automatically secure.** A shared kernel means a kernel bug can matter more
  than in a VM. Don't run untrusted code as root.
- **Treating a container like a pet server.** Don't log in and tweak it by hand; rebuild it from a
  recipe (the Dockerfile, Session 7).

## Hands-on exercises

**Exercise 1.** Run `docker run --rm alpine uname -a` and `uname -a` on your host. What is the same and
what is different?

<details class="solution"><summary>Solution</summary>

The kernel release (e.g. `6.8.0-138-generic`) is identical, because they share the kernel. The hostname
differs: the container gets a random id as its hostname.

</details>

**Exercise 2.** Which of these needs a VM and which can use a container: (a) running a Windows-only app
on a Linux server, (b) running five copies of a Flask API side by side?

<details class="solution"><summary>Solution</summary>

(a) needs a VM (or a Windows host), because the Windows kernel is needed. (b) is ideal for containers:
five identical, light, quickly started copies.

</details>

**Exercise 3.** Find out how large the `alpine` image is on your machine and compare it with any VM image
file you have.

<details class="solution"><summary>Solution</summary>

```bash
docker images alpine --format '{{.Repository}}:{{.Tag}}  {{.Size}}'
```

On this machine `alpine:latest` was 8.42MB. A VM disk image is usually several GB, hundreds of times larger.

</details>

## Practice

Take the **Session 1 quiz**. The original story page is kept in the reference section as
*Virtual Machine and The Grand House*.
