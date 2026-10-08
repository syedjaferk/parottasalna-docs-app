# Under the hood · Namespaces

:::{note}
**Extra reading, no video yet.** Builds on [Chapter 2 · Linux prerequisites](../sessions/02-linux-prerequisites.md). Read it after Chapter 2 to see how a container gets its private view.
:::

## The big idea

A **namespace** gives a process its own private copy of one part of the system: its own process
list, its own hostname, its own network, its own files. Put a process into several namespaces at
once and it *believes* it's alone on its own machine. That's a container.

**Everyday example:** a hotel room. You have your own door number, your own bathroom and your own
TV, and you can't see into the other rooms. But it's the same building, the same plumbing and the
same electricity underneath. Namespaces are the walls; the shared building is the Linux kernel.

```{raw} html
:file: ../diagrams/s03-namespaces.html
```

## The namespaces

| Namespace | Isolates | Inside the container you see… |
|---|---|---|
| **PID** | process IDs | only your own processes; your app is **PID 1** |
| **NET** | network | your own network card, IP address, ports and routing |
| **MNT** | mounts / files | your own root folder `/` (the image's files) |
| **UTS** | hostname | your own hostname |
| **IPC** | shared memory, message queues | your own IPC objects |
| **USER** | user and group IDs | "root" inside can map to a normal user outside |
| **cgroup** | cgroup tree | only your own cgroup  |

## PID namespace: "I am PID 1"

```bash
docker run --rm alpine ps
```

**Output:**

```text
PID   USER     TIME  COMMAND
    1 root      0:00 ps
```

Inside the container, `ps` sees **only itself**, as PID 1. On the host the same process has a
normal, large PID. Open two terminals to see both views:

```bash
docker run -d --name sleeper alpine sleep 600     # terminal 1
docker exec sleeper ps                             # inside: sleep is PID 1
ps -ef | grep "sleep 600"                          # on the host: some PID like 48211
docker rm -f sleeper
```

## UTS namespace: your own hostname

```bash
docker run --rm --hostname kube-box alpine hostname
```

**Output:**

```text
kube-box
```

Your laptop's hostname didn't change. Only the container's view did.

## NET namespace: your own network

```bash
docker run --rm alpine ip addr
```

You'll see a loopback (`lo`) and an `eth0` with an address like `172.17.0.2`. That's the
container's own network card, separate from your laptop's. Port mapping (`-p 8080:80`) connects the
two; [Chapter 6](../sessions/06-docker-networking.md) goes deeper.

## MNT namespace: your own files

```bash
docker run --rm alpine ls /
docker run --rm alpine cat /etc/os-release
```

The container sees the **image's** files as `/`, not your laptop's. Even on Ubuntu, `os-release`
says Alpine.

## Build a "container" by hand with `unshare`

Docker uses the same kernel features you can call yourself. `unshare` starts a program in new
namespaces (run this in a Linux shell, not Docker Desktop's Windows/macOS terminal):

```bash
sudo unshare --pid --fork --mount-proc --uts bash
```

Now, in that new shell:

```bash
ps aux                 # only bash and ps: bash is PID 1
hostname my-box        # change the hostname...
hostname               # my-box
exit
```

Back on the host, `hostname` still shows your real hostname, because the change only happened
inside the new UTS namespace.

## Seeing namespaces in `/proc`

Every process lists its namespaces in `/proc/<PID>/ns`:

```bash
ls -l /proc/$$/ns
```

**Output (shortened):**

```text
mnt -> 'mnt:[4026531841]'
net -> 'net:[4026531840]'
pid -> 'pid:[4026531836]'
uts -> 'uts:[4026531838]'
```

Two processes in the same namespace show the same number. A container's processes show different
numbers from your shell's.

:::{warning}
**Namespaces hide things; they don't limit things.** A container can still use all your CPU and
memory unless you limit it. That's the job of cgroups, in [cgroups](cgroups.md).
:::

## Try it yourself

1. Run `docker run --rm alpine ps` and `docker run --rm alpine sh -c "sleep 1 & ps"`. How many
   processes does each show, and which is PID 1?
2. Start a container with `docker run -d --name ns-demo alpine sleep 600`, then compare
   `docker exec ns-demo ls -l /proc/1/ns` with `ls -l /proc/$$/ns` on the host. Which numbers differ?
3. Use `unshare` to change the hostname in a new UTS namespace and prove the host didn't change.

   <details class="solution">
   <summary>Answer</summary>

   ```bash
   sudo unshare --uts bash -c 'hostname inside-ns; hostname'   # inside-ns
   hostname                                                    # your real hostname
   ```

   </details>
