# Chapter 4 · Your First Docker Commands (Hands-On)

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/9NRT2YsOT3Q"
  title="Episode 4: Your first Docker commands" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 **Episode 4** of the [Kube Engineering playlist](https://www.youtube.com/playlist?list=PLMtFsmo8jrN8) (Tamil) · [watch on YouTube](https://www.youtube.com/watch?v=9NRT2YsOT3Q)

## The big idea

Theory done; now the commands you'll type every day. Almost everything comes down to a short loop:
**pull** an image, **run** a container from it, **look** at it (`ps`, `logs`, `exec`), then
**stop** and **remove** it.

**Everyday example:** a music app. You **download** a song (pull), **play** it (run), check
**what's playing** (ps), **pause or stop** it (stop), and **delete** it to free space (rm / rmi).

## Pulling and listing images

```bash
docker pull nginx:alpine      # download an image
docker images                 # list images on this machine
```

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
| `-v /host/dir:/container/dir` | bind mount a folder ([Chapter 3](03-permissions-bind-mounts-architecture.md)) |
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

## Cleaning up

```bash
docker rm web                 # remove one stopped container
docker rm -f web              # stop + remove in one step
docker container prune        # remove ALL stopped containers
docker rmi nginx:alpine       # remove an image (no container may use it)
docker image prune            # remove dangling (untagged) images
docker system df              # what is using disk space
docker system prune           # stopped containers, unused networks, dangling images, build cache
```

:::{warning}
`prune` commands ask for confirmation and **can't be undone**. Read the list before you type `y`.
:::

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

```{literalinclude} ../code/04-docker-commands/html/index.html
:language: html
```

</details>
