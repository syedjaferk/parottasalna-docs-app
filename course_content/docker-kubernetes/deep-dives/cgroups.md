# Under the hood · cgroups

:::{note}
**Extra reading, no video yet.** Read it after [Namespaces](namespaces.md). The OOM exit code 137 comes from [Chapter 2](../sessions/02-linux-prerequisites.md).
:::

## The big idea

Namespaces control what a container can **see**. **cgroups** (control groups) control how much it
can **use**: CPU, memory, disk I/O and number of processes. Without limits, one buggy container
can eat all the memory and take down everything else on the server.

**Everyday example:** a prepaid mobile plan. You can call anyone (namespaces decide *who you can
see*), but your data pack has a limit (cgroups decide *how much you can use*). Go over it and the
service stops.

```{raw} html
:file: ../diagrams/s04-cgroups.html
```

## Setting limits with Docker

```bash
docker run -d --name limited --memory=100m --cpus=0.5 nginx:alpine
docker stats limited --no-stream
```

**Output (shortened):**

```text
NAME      CPU %     MEM USAGE / LIMIT     MEM %
limited   0.00%     3.1MiB / 100MiB       3.10%
```

| Flag | Meaning |
|---|---|
| `--memory=100m` | at most 100 MB of RAM |
| `--memory-swap=100m` | same as `--memory`: no extra swap |
| `--cpus=0.5` | at most half of one CPU core |
| `--pids-limit=100` | at most 100 processes (stops fork bombs) |

## Where the limits really live

Docker just writes numbers into files under `/sys/fs/cgroup`. You can read them from inside:

```bash
docker run --rm --memory=100m --cpus=0.5 alpine sh -c 'cat /sys/fs/cgroup/memory.max /sys/fs/cgroup/cpu.max'
```

**Output:**

```text
104857600
50000 100000
```

- `104857600` bytes = 100 × 1024 × 1024 = **100 MB**.
- `50000 100000` means "50 ms of CPU time in every 100 ms period": **half a CPU**.

## cgroups v1 vs v2

| | v1 (older) | v2 (current) |
|---|---|---|
| Layout | a separate tree per resource (`/sys/fs/cgroup/memory/`, `/sys/fs/cgroup/cpu/`…) | **one unified tree** |
| Used by | older distros | Ubuntu 22.04+, Fedora, Debian 11+, and recent Docker and Kubernetes |

Check which one you have:

```bash
docker info --format '{{.CgroupVersion}}'     # 2
```

## The OOM killer

**OOM = Out Of Memory.** When a container goes over its memory limit, the kernel's OOM killer
stops it immediately with `SIGKILL`.

```bash
docker run --name oom-demo --memory=30m --memory-swap=30m python:3.12-slim \
  python -c "x = bytearray(200*1024*1024)"
echo "exit code: $?"
docker inspect --format 'OOMKilled={{.State.OOMKilled}} ExitCode={{.State.ExitCode}}' oom-demo
docker rm oom-demo
```

**Output:**

```text
exit code: 137
OOMKilled=true ExitCode=137
```

The app tried to grab 200 MB inside a 30 MB limit. **137 = 128 + 9 (SIGKILL)**, and
`OOMKilled=true` confirms the kernel did it. In Kubernetes you'll see the same thing as a pod
status of `OOMKilled`.

:::{tip}
When a container keeps dying with exit code 137, check `docker inspect` for `OOMKilled`. If it's
`true`, either raise the limit or find out why the app uses so much memory.
:::

## CPU limits slow down; memory limits kill

- **CPU** over the limit: the container is **slowed down** (throttled). It keeps running, just slower.
- **Memory** over the limit: the container is **killed**. Memory can't be "slowed down".

## Try it yourself

1. Run the OOM demo. Then change `--memory=30m` to `--memory=300m`. What happens now?
2. Start `docker run -d --name busy --cpus=0.25 alpine sh -c "while true; do :; done"`, then watch
   `docker stats busy`. What CPU % do you see? Remove it with `docker rm -f busy`.

   <details class="solution">
   <summary>Answer</summary>

   Around **25%**: the endless loop wants a full CPU, but the cgroup only gives it a quarter.

   </details>

3. Read `memory.max` inside a container started **without** `--memory`. What does it say?

   <details class="solution">
   <summary>Answer</summary>

   `max`: no limit. That's the default, and why you should always set limits in production.

   </details>
