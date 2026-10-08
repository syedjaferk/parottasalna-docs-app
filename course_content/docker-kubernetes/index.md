# Docker & Kubernetes Systems Engineering

Welcome! Over 50 live sessions you'll go from "what even is a container?" to running a production
AI Agent platform on Kubernetes. We start with the Linux ideas that make containers possible,
master Docker, then move on to Kubernetes.

These notes follow the **[Kube Engineering YouTube playlist](https://www.youtube.com/playlist?list=PLMtFsmo8jrN8)**
(Tamil): **one chapter per episode**, with the video at the top. Each page explains the idea in
simple words, shows the commands to run (with the output you should see), and ends with exercises.

:::{note}
**What is a container, in one line?** A normal Linux process that has been given its own private
view of the system (its own files, network and process list) and a limit on how much CPU and
memory it may use. Chapter 2 and the *Under the hood* pages show exactly how that works.
:::

## How each chapter works

1. **The video** of the class, followed by **the big idea**: the concept in two sentences, with an everyday example.
2. **Step by step**: simple explanations, diagrams, and commands with real output.
3. **Common mistakes**: what usually goes wrong, so you can avoid it.
4. **Try it yourself**: short exercises, with answers you can reveal.
5. **Class files**: the code and whiteboards from the live session.

:::{tip}
New here? Do **[Setup](setup.md)** first so Docker is ready on your machine, then follow the
chapters in order. The **[Course map](course-map.md)** shows all 50 syllabus sessions.
:::

```{toctree}
:maxdepth: 1
:caption: Getting started

setup
course-map
```

```{toctree}
:maxdepth: 1
:caption: Docker fundamentals · Episodes 1–4

sessions/01-why-docker
sessions/02-linux-prerequisites
sessions/03-permissions-bind-mounts-architecture
sessions/04-docker-commands
```

```{toctree}
:maxdepth: 1
:caption: Networking · Episodes 5–6

sessions/05-ip-addressing-subnets
sessions/06-docker-networking
```

```{toctree}
:maxdepth: 1
:caption: Building images · Episode 7

sessions/07-dockerfile
```

```{toctree}
:maxdepth: 1
:caption: Under the hood · extra reading

deep-dives/namespaces
deep-dives/cgroups
deep-dives/container-runtimes
deep-dives/image-mechanics
```
