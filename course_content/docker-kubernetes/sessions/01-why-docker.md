# Chapter 1 · Introduction to Docker and Its Need

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/wKEk5kNXllA"
  title="Episode 1: Introduction to Docker and its need" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 **Episode 1** of the [Kube Engineering playlist](https://www.youtube.com/playlist?list=PLMtFsmo8jrN8) (Tamil) · [watch on YouTube](https://www.youtube.com/watch?v=wKEk5kNXllA)

## The big idea

"It works on my machine!" is the oldest problem in software. Your app depends on a specific
language version, libraries and settings, and the next machine is always a little different.
**Docker packages your app together with everything it needs** into one box that runs the same way
everywhere: your laptop, a teammate's laptop, a test server, the cloud.

**Everyday example:** a **shipping container**. Before standard containers, every port loaded
sacks, barrels and crates differently. Once everything went into the same standard box, any ship,
truck or crane could move any cargo. Docker does that for software.



## Three ways to run an app

```{raw} html
:file: ../diagrams/s01-stack.html
```

| | Bare metal | Virtual machine (VM) | Container |
|---|---|---|---|
| **What it is** | your app directly on a physical server | a whole pretend computer, with its own OS | an isolated process sharing the host's OS kernel |
| **Size** | n/a | gigabytes (full OS each) | megabytes (just the app and its libraries) |
| **Start time** | n/a | minutes (boots an OS) | seconds or less (starts a process) |
| **Isolation** | none: apps fight over libraries | very strong: separate kernels | strong enough for most apps: separate view, shared kernel |
| **Good for** | one big dedicated workload | running different operating systems | packaging and shipping applications |

### Bare metal: one server, one app

Run two apps on the same server and they start to fight: app A needs Python 3.8, app B needs
Python 3.12; one upgrade breaks the other. So companies bought one server per app, and most
servers sat idle most of the day.

### Virtual machines: a computer inside a computer

A **hypervisor** (VMware, VirtualBox, KVM) splits one physical server into several pretend
computers. Each VM has its own operating system, so apps no longer fight. But every VM carries a
full OS (gigabytes of disk and RAM) and takes minutes to boot.

### Containers: just enough isolation

A container doesn't pretend to be a whole computer. It's a **normal process on the host** that
Linux gives a private view: its own files, network and process list, plus limits on CPU and
memory. All containers share the host's kernel, so there's no extra OS to boot.

:::{note}
**Kernel** = the core of the operating system that talks to the hardware. Containers on one host
share the same Linux kernel. That's why a Linux container needs a Linux kernel underneath, and why
Docker Desktop runs a small Linux VM on Windows and macOS.
:::

## What Docker gives you

- **Portability:** build once, run anywhere Docker runs. The image carries its dependencies.
- **Consistency:** dev, test and production run the *same* image, so there are no surprises.
- **Speed:** containers start in seconds, so you can run many on one machine.
- **Isolation:** each app has its own libraries and versions; no more conflicts.
- **A shared vocabulary:** a `Dockerfile` describes how to build the app, so anyone can rebuild it.

## Where Docker fits: DevOps and Kubernetes

```text
write code → docker build (image) → push to a registry → run anywhere
                                                          ├─ your laptop
                                                          ├─ a test server
                                                          └─ Kubernetes (many machines)
```

- **DevOps / CI/CD:** the pipeline builds one image per change and the *same* image moves from
  test to production. No "it worked in testing" surprises.
- **Kubernetes:** once you have many containers on many machines, someone has to start them,
  restart them when they crash, and spread them out. That's Kubernetes, the second half of this
  course. Kubernetes runs **containers**, so Docker skills come first.

## Three words to remember

| Word | In simple words | Everyday example |
|---|---|---|
| **Image** | a read-only template: app + libraries + settings | a recipe, or a class in programming |
| **Container** | a running instance of an image | the cooked dish, or an object made from a class |
| **Registry** | a store for images, like Docker Hub | an app store |

One image can start **many** containers, just like one recipe can feed many plates.

## Try it yourself

1. Install Docker using [Setup](../setup.md) and run `docker run hello-world`. Read every line of
   the message it prints.
2. Time how long a container takes to start:

   ```bash
   time docker run --rm alpine echo "hi"
   ```

   The first run includes downloading the image. Run it again: it's usually well under a second.
3. In your own words, explain to a friend why a VM is "heavier" than a container.

   <details class="solution">
   <summary>Answer</summary>

   A VM runs a complete operating system of its own (its own kernel, system services and memory),
   so it needs gigabytes and boots like a computer. A container is just a process that shares the
   host's kernel, so it only carries the app and its libraries and starts like a normal program.

   </details>

## Materials from the class

- [Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/) (official docs)
- Blog: [Virtual machine and the grand house](https://parottasalna.com/2024/08/04/virtual-machine-and-the-grand-house/)
- Blog: [Virtual machines vs containers](https://parottasalna.com/2024/08/12/virtual-machines-vs-containers/)
