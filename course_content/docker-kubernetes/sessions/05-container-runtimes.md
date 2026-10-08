# Session 5 · Container Runtime Internals

## The big idea

When you type `docker run`, Docker doesn't create the container by itself. It's a **chain of
programs**, each with one job. Knowing the chain explains how Kubernetes can run containers
**without Docker at all**.

**Everyday example:** ordering food in a restaurant. You talk to the waiter (`docker` CLI), who
passes the order to the kitchen manager (`dockerd`), who gives it to the head chef (`containerd`),
who has a cook actually make the dish (`runc`). Once the dish is served, the cook moves on, and a
helper (the *shim*) keeps watch over your table.

```{raw} html
:file: ../diagrams/s05-runtime.html
```

## Who does what

| Program | Job |
|---|---|
| **docker** (CLI) | reads your command and sends it to the daemon over its API |
| **dockerd** (Docker Engine) | the Docker daemon: builds, networking, volumes, the Docker API |
| **containerd** | manages the container lifecycle: pulls images, stores layers, starts and stops containers |
| **containerd-shim** | one per container; keeps it running even if containerd restarts, and collects its exit code |
| **runc** | the low-level runtime: sets up namespaces and cgroups, starts the process, then exits |

See it on your machine:

```bash
docker info --format 'Default runtime: {{.DefaultRuntime}}'
ps -ef | grep -E "containerd|dockerd" | grep -v grep
```

**Output (example):**

```text
Default runtime: runc
root   1010  ...  /usr/bin/containerd
root   1240  ...  /usr/bin/dockerd -H fd:// --containerd=/run/containerd/containerd.sock
```

Start a container and look again: there's a `containerd-shim-runc-v2` process for it.

## OCI: the standards that make it all swappable

The **Open Container Initiative (OCI)** publishes open standards, so tools from different
companies work together:

| Spec | Defines | Means that |
|---|---|---|
| **Image spec** | the format of an image (layers + config + manifest) | an image built by Docker runs on Podman, containerd, Kubernetes… |
| **Runtime spec** | how to run a container from a folder of files + `config.json` | `runc`, `crun`, `gVisor` and `Kata` are interchangeable |
| **Distribution spec** | how registries push and pull images | Docker Hub, GitHub, AWS ECR and Harbor all speak the same API |

## Docker Engine vs CRI: why Kubernetes doesn't need Docker

Kubernetes talks to container runtimes through the **CRI** (Container Runtime Interface). For
years Kubernetes needed a translator ("dockershim") to talk to Docker. Since **Kubernetes 1.24**
it talks **directly to containerd** (or CRI-O) through CRI, skipping `dockerd`.

**Does that mean your Docker images don't work on Kubernetes? No.** Images follow the OCI image
spec, so an image built with `docker build` runs on any Kubernetes cluster unchanged. Only the tool
*running* it changed.

:::{note}
**`runc` exits after starting your container.** It's not a long-running daemon. It sets everything
up (namespaces from Session 3, cgroups from Session 4, the root filesystem), starts your process,
and leaves. The shim stays behind to watch the container.
:::

## Try it yourself

1. Run `docker info` and find these lines: `Server Version`, `Storage Driver`, `Cgroup Version`,
   `Runtimes` and `Default Runtime`.
2. Start `docker run -d --name rt-demo nginx:alpine`, then run `ps -ef --forest | grep -B2 -A2 nginx`.
   Can you spot the `containerd-shim` that is the parent of nginx? Remove it with `docker rm -f rt-demo`.
3. In one sentence each, explain what containerd does and what runc does.

   <details class="solution">
   <summary>Answer</summary>

   **containerd** manages containers over their whole life: it pulls and stores images and starts,
   stops and watches containers. **runc** does one thing: it creates a single container (namespaces,
   cgroups, filesystem), starts its process, and exits.

   </details>
