# Docker & Kubernetes Systems Engineering

Welcome! Over 50 live sessions you'll go from "what even is a container?" to running a production
AI Agent platform on Kubernetes. We start with the Linux ideas that make containers possible,
master Docker, then move on to Kubernetes.

These notes follow the class session by session. Each page explains the idea in simple words,
shows the commands to run (with the output you should see), and ends with exercises.

:::{note}
**What is a container, in one line?** A normal Linux process that has been given its own private
view of the system (its own files, network and process list) and a limit on how much CPU and
memory it may use. Sessions 2–5 show exactly how that works.
:::

## How each session page works

1. **The big idea**: the concept in two sentences, with an everyday example.
2. **Step by step**: simple explanations, diagrams, and commands with real output.
3. **Common mistakes**: what usually goes wrong, so you can avoid it.
4. **Try it yourself**: short exercises, with answers you can reveal.
5. **Class files**: the code and whiteboards from the live session.

:::{tip}
New here? Do **[Setup](setup.md)** first so Docker is ready on your machine, then follow the
sessions in order. The **[Course map](course-map.md)** shows all 50 sessions.
:::

```{toctree}
:maxdepth: 1
:caption: Getting started

setup
course-map
```

```{toctree}
:maxdepth: 1
:caption: Phase 1 · Docker & container fundamentals

sessions/01-why-docker
sessions/02-linux-prerequisites
sessions/03-namespaces
sessions/04-cgroups
sessions/05-container-runtimes
```

```{toctree}
:maxdepth: 1
:caption: Phase 2 · Docker mastery & packaging

sessions/06-docker-architecture-cli
sessions/07-image-mechanics
sessions/08-dockerfile-fundamentals
sessions/09-dockerfile-deep-dive
```
