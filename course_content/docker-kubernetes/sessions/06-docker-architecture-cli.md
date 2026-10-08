# Session 6 · Docker Architecture & CLI

## The big idea

Docker is a **client–server** system. The `docker` command you type is only the **client**. It
sends your request to the **Docker daemon** (`dockerd`), a background service that does the real
work: pulling images, creating containers, setting up networks. Images come from a **registry**
such as Docker Hub.

**Everyday example:** a TV remote. The remote (`docker` CLI) doesn't play anything itself. It sends
a signal to the TV (`dockerd`), and the TV streams shows from the internet (the registry).

```{raw} html
:file: ../diagrams/s06-architecture.html
```

## The three parts

| Part | What it is | Example |
|---|---|---|
| **Client** | the `docker` command | `docker run nginx` |
| **Daemon** (`dockerd`) | the background service that manages images, containers, networks and volumes | `systemctl status docker` |
| **Registry** | a store for images | Docker Hub (`hub.docker.com`), GitHub Container Registry, AWS ECR |

The client talks to the daemon through a socket file, `/var/run/docker.sock`. That's why you need
to be in the `docker` group (or use `sudo`):

```bash
docker version     # shows both "Client" and "Server" sections
```

:::{warning}
Access to `/var/run/docker.sock` is the same as **root access** to the machine: anyone who can
talk to the daemon can start a container that mounts your whole disk. Only add trusted users to
the `docker` group.
:::

## Image names

```text
docker.io/library/nginx:alpine
└─registry─┘ └─repo──┘ └tag─┘
```

- No registry given → **Docker Hub** (`docker.io`).
- No user or organisation → `library/`, the official images.
- No tag → **`latest`**. Always write a tag; `latest` changes without warning.

## The container lifecycle

```{raw} html
:file: ../diagrams/s06-lifecycle.html
```

A container moves through these states: **created → running → (paused) → stopped (exited) →
removed**.

| Command | What it does |
|---|---|
| `docker pull nginx:alpine` | download an image |
| `docker images` | list images on this machine |
| `docker create --name web nginx:alpine` | make a container but don't start it |
| `docker start web` / `docker stop web` | start / stop it (stop sends SIGTERM, then SIGKILL after 10 s) |
| `docker run …` | **pull + create + start** in one step |
| `docker ps` / `docker ps -a` | running containers / all containers, including stopped |
| `docker logs -f web` | follow a container's output |
| `docker exec -it web sh` | open a shell inside a running container |
| `docker inspect web` | every detail, as JSON |
| `docker rm web` / `docker rm -f web` | remove a stopped container / force-remove a running one |
| `docker rmi nginx:alpine` | remove an image |

Useful `docker run` flags:

| Flag | Meaning |
|---|---|
| `-d` | detached: run in the background |
| `--name web` | give it a name instead of a random one |
| `-p 8080:80` | port mapping: **host port 8080 → container port 80** |
| `-v /host/dir:/container/dir` | bind mount a folder (Session 2) |
| `-e KEY=value` | set an environment variable |
| `--rm` | delete the container automatically when it exits |
| `-it` | interactive with a terminal (for shells) |

## Class demo: serve your own page with nginx

In class we served a folder from the laptop using the official nginx image. Create
`html/index.html` with any text (the class version is below), then:

```bash
docker run -d --name web -p 8080:80 \
  -v "$PWD/html:/usr/share/nginx/html:ro" nginx:alpine
curl localhost:8080
```

**Output:**

```text
1
2
3
syed jafer
```

Now edit `html/index.html` on your laptop and `curl` again: the change shows up immediately,
because the bind mount means it's the same folder. `:ro` makes it read-only inside the container.

```bash
docker logs web          # nginx access log, one line per request
docker exec -it web sh   # look around inside; type exit to leave
docker stop web && docker rm web
```

## Common mistakes

- **`docker run` again and again** creates a *new* container every time. Use `docker start` to
  restart an existing one, and `--rm` for throwaway runs.
- **"port is already allocated"**: another container or program already uses that host port. Pick
  another one, like `-p 8081:80`.
- **The container exits right away**: a container lives only as long as its main process (PID 1).
  `docker run alpine` exits at once because its default command, `sh`, has no terminal to read.
  Check `docker logs` and `docker ps -a`.

## Try it yourself

1. Run `docker run -d --name web2 -p 9090:80 nginx:alpine` and open <http://localhost:9090>.
2. Find web2's IP address with `docker inspect`.

   <details class="solution">
   <summary>Answer</summary>

   ```bash
   docker inspect --format '{{.NetworkSettings.IPAddress}}' web2
   ```

   </details>

3. Walk web2 through its lifecycle: `pause`, `unpause`, `stop`, `start`, `rm -f`. Check
   `docker ps -a` after each step and note the STATUS column.

## Class files

<details class="source">
<summary>html/index.html</summary>

```{literalinclude} ../code/06-docker-cli/html/index.html
:language: html
```

</details>
