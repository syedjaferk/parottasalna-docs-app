# Session 2 · How Docker is built: client, daemon, registry

## The big idea

When you type `docker run`, the `docker` program does very little itself. It is a **client** that
sends your request to the **Docker daemon** (`dockerd`), a background service that does the real work:
pulling images, creating containers, managing networks and volumes. Images come from a **registry**
such as Docker Hub.

**Everyday example:** the magic kitchen, or a tea kadai. You (the customer) tell the waiter "one tea".
The waiter (the **client**) never makes the tea. He passes the order to the master in the kitchen
(the **daemon**), who does the work. If an ingredient is missing, the master sends someone to the
wholesale market (the **registry**) to fetch it. You never see the kitchen, only the waiter.

```{raw} html
:file: ../diagrams/docker-architecture.html
```

## Seeing the pieces

```{literalinclude} ../code/02-architecture.sh
:language: bash
```

```{literalinclude} ../code/02-architecture.out
:language: text
```

Read the output:

- **Two versions.** The client and the server are separate programs that happen to be installed
  together. They can even be on different machines.
- **`unix:///var/run/docker.sock`** is where the client sends requests: a socket file on this computer.
  Point it at another host and the same commands drive a remote Docker.
- **`docker info`** is the daemon describing itself: how many containers and images it manages and
  which storage driver (`overlay2`) keeps image layers.
- **The last line proves the client is just an HTTP client.** `curl` asked the daemon `/_ping` over
  the socket and got `OK`. The `docker` command does the same, with nicer wrapping.

## What happens on `docker run alpine echo hi`

1. The client sends "create and start a container from `alpine`" to the daemon.
2. The daemon looks for the `alpine` image locally. If missing, it **pulls** it from the registry.
3. It creates the container (a writable layer on top of the image), sets up isolation, and starts
   the command.
4. Output streams back to your terminal through the client.

## Registry, repository, tag

An image name has three parts: `registry/repository:tag`, for example `docker.io/library/nginx:alpine`.
The registry is the server (Docker Hub by default), the repository groups versions of one image
(`nginx`), and the tag picks a version (`alpine`). With no tag, you get `latest`, which is just a
name and not a guarantee of "newest".

## Common mistakes

- **"docker: command not found" versus "Cannot connect to the Docker daemon".** The first means the
  client is not installed. The second means the client works but the daemon is not running (or you lack
  permission to the socket). Start the daemon or add yourself to the `docker` group.
- **Assuming the CLI does the work.** If the daemon stops, every `docker` command fails.
- **Relying on `latest`.** It changes over time. Pin a version (`python:3.12-slim`) so builds stay
  repeatable.
- **Exposing the daemon on the network without protection.** Access to the socket is effectively root
  on the host.

## Hands-on exercises

**Exercise 1.** Show the client and server versions in one line.

<details class="solution"><summary>Solution</summary>

```bash
docker version --format 'client {{.Client.Version}}   server {{.Server.Version}}'
```

Output on this machine: `client 28.1.1   server 28.1.1`.

</details>

**Exercise 2.** Break `docker` on purpose: stop the daemon (or point `DOCKER_HOST` somewhere wrong) and read the
error. Which program printed it?

<details class="solution"><summary>Solution</summary>

```bash
DOCKER_HOST=unix:///tmp/nothing.sock docker ps
```

The client prints an error saying it cannot connect to the Docker daemon at that socket. The client is
fine; there is just no daemon where it looked.

</details>

**Exercise 3.** Name the registry, repository and tag in `ghcr.io/acme/web:2.1`.

<details class="solution"><summary>Solution</summary>

Registry `ghcr.io` (GitHub's), repository `acme/web`, tag `2.1`.

</details>

## Practice

Take the **Session 2 quiz**. The original kitchen and tea-kadai stories are in the reference section.
