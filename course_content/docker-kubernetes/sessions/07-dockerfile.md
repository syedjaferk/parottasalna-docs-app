# Chapter 7 · Master the Dockerfile from Scratch

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/sjBSV0HRAD8"
  title="Episode 7: Master Dockerfile from scratch" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 **Episode 7** of the [Kube Engineering playlist](https://www.youtube.com/playlist?list=PLMtFsmo8jrN8) (Tamil) · [watch on YouTube](https://www.youtube.com/watch?v=sjBSV0HRAD8)

## The big idea

A **Dockerfile** is a recipe: a text file of step-by-step instructions that tells Docker how to
build an image. `docker build` reads it top to bottom, and each step adds a layer (see [Under the hood · Image layers](../deep-dives/image-mechanics.md)). The
result is an image you can run anywhere.

This chapter goes from the basics to the details that make images small, fast to build and
well-behaved.

**Everyday example:** a recipe card. "Start with this base (FROM), go to the kitchen counter
(WORKDIR), bring in the ingredients (COPY), cook them (RUN), and here's how to serve it (CMD)."

```{raw} html
:file: ../diagrams/s08-flow.html
```

## The class app

A tiny Flask app that greets you with two environment variables:

```python
@app.route("/")
def home():
    return f"{os.getenv('GREETING', 'Hello Vanakamungoo')} from {os.getenv('APP_ENV', 'dev')}!"
```

And its Dockerfile:

```dockerfile
FROM python:3.12-slim
ARG APP_VERSION
ENV APP_ENV=${APP_VERSION} \
    GREETING="Hello Docker"
WORKDIR /application
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
EXPOSE 5111
CMD ["python", "app.py"]
```

Build and run it:

```bash
docker build --build-arg APP_VERSION=qa -t kube-demo-flask:qa .
docker run --rm -d --name flask -p 5111:5111 kube-demo-flask:qa
curl localhost:5111
```

**Output:**

```text
Hello Docker from qa!
```

Override an environment variable at run time with `-e`:

```bash
docker rm -f flask
docker run --rm -d --name flask -p 5111:5111 -e GREETING=Vanakkam kube-demo-flask:qa
curl localhost:5111       # Vanakkam from qa!
docker rm -f flask
```

## Every instruction, in plain words

| Instruction | Runs when | What it does |
|---|---|---|
| `FROM` | build | the base image to start from. Always the first line. |
| `ARG` | build | a variable you pass with `--build-arg`. **Gone** after the build. |
| `ENV` | build **and** run | an environment variable baked into the image; your app sees it. |
| `WORKDIR` | build | `cd` into a folder (creating it if needed) for every later step. |
| `COPY` | build | copy files from your folder (the build context) into the image. |
| `ADD` | build | like COPY, but also unpacks local `.tar` files and can download URLs. |
| `RUN` | build | run a command **while building**, such as installing packages. Adds a layer. |
| `EXPOSE` | (documentation) | says which port the app listens on. It does **not** publish it; `-p` does. |
| `CMD` | run | the **default** command when a container starts. Easy to replace. |
| `ENTRYPOINT` | run | **the** program the container runs. Arguments are added to it. |

### Choosing a base image (`FROM`)

| Tag | Approx. size | Notes |
|---|---|---|
| `python:3.12` | ~1 GB | full Debian with compilers. Easy, but big. |
| `python:3.12-slim` | ~150 MB | Debian with only the essentials. **A good default.** |
| `python:3.12-alpine` | ~55 MB | tiny, but uses musl libc, so some Python packages need compiling. |

Always **pin a tag** (`3.12-slim`), never rely on `latest`.

### `RUN`: chain commands and clean up in the same step

```dockerfile
# ❌ three layers, and the apt cache stays in the image
RUN apt-get update
RUN apt-get install -y curl
RUN rm -rf /var/lib/apt/lists/*

# ✅ one layer, cache removed before the layer is saved
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*
```

A file deleted in a *later* layer still takes space in the earlier one. Clean up in the **same**
`RUN`.

### `WORKDIR` instead of `RUN cd`

`RUN cd /app` only changes folder for that one `RUN`. `WORKDIR /app` applies to every instruction
after it, and to the running container.

### `COPY` vs `ADD`

Prefer **COPY**: it does exactly one obvious thing. Use `ADD` only when you really want a local
`.tar.gz` unpacked.

### `ARG` vs `ENV`

- **ARG** exists only during the build. Use it to build different flavours from one Dockerfile:
  `--build-arg APP_VERSION=dev|qa|prod`.
- **ENV** stays in the image, so the running app can read it. Copy an ARG into an ENV (as the
  class app does) when the app needs to know the value.
- Change an ENV at run time with `docker run -e KEY=value`.

:::{danger}
**Never put secrets (passwords, API keys) in `ENV` or `ARG`.** Anyone with the image can read them
with `docker history` or `docker inspect`. Pass secrets at run time instead (`-e`, `--env-file`,
or Kubernetes Secrets later in the course).
:::

### `CMD` vs `ENTRYPOINT`

```{raw} html
:file: ../diagrams/s08-cmd-entrypoint.html
```

- **CMD** = the *default* command. `docker run image something-else` **replaces** it.
- **ENTRYPOINT** = *the* program. `docker run image extra args` **appends** the args to it.
- Use both together: ENTRYPOINT is the program, CMD gives default arguments. The
  hands-on demo is in *ENTRYPOINT + CMD together*, below.

## Look inside what you built

```bash
docker history kube-demo-flask:qa
```

**Output (newest layer first, shortened):**

```text
CMD ["python" "app.py"]                         0B
EXPOSE map[5111/tcp:{}]                         0B
COPY app.py . # buildkit                        252B
RUN |1 APP_VERSION=qa /bin/sh -c pip install…   13.8MB
COPY requirements.txt . # buildkit              109B
WORKDIR /application                            0B
ENV APP_ENV=qa GREETING=Hello Docker            0B
ARG APP_VERSION=qa                              0B
```

Only `RUN`, `COPY` and `ADD` add real bytes. The other instructions only change the image's
settings (0B). And notice `APP_VERSION=qa` is visible: that's exactly why secrets don't belong in
ARG or ENV.

## ENTRYPOINT + CMD together

The class example:

```dockerfile
FROM alpine:3.20
ENTRYPOINT ["echo", "Hello World"]
CMD ["World"]
```

```bash
docker build -f alpine.Dockerfile -t kube-demo-hello .
docker run --rm kube-demo-hello
docker run --rm kube-demo-hello Jafer syed
```

**Output:**

```text
Hello World World
Hello World Jafer syed
```

- No arguments: ENTRYPOINT + CMD → `echo "Hello World" World`.
- With arguments: your arguments **replace CMD**, and ENTRYPOINT stays → `echo "Hello World" Jafer syed`.
- To replace the ENTRYPOINT itself, you have to ask explicitly: `docker run --entrypoint …`.

| You want… | Use |
|---|---|
| a default command that users often change | `CMD` only |
| the container to always run one program (a CLI tool) | `ENTRYPOINT` |
| a fixed program with default, overridable arguments | `ENTRYPOINT` + `CMD` |

## Exec form vs shell form

```dockerfile
CMD ["python", "app.py"]     # exec form: JSON list, run directly
CMD python app.py            # shell form: run as  /bin/sh -c "python app.py"
```

The difference matters because of **PID 1** and **signals** ([Chapter 2](02-linux-prerequisites.md)). `docker stop` sends
`SIGTERM` to PID 1, waits **10 seconds**, then sends `SIGKILL`.

```{raw} html
:file: ../diagrams/s09-signals.html
```

We measured `docker stop` on four versions of the same small Python app:

| Version | PID 1 is | `docker stop` took | Exit code |
|---|---|---|---|
| exec form, app handles SIGTERM | `python` | **0.1 s** | 0 (clean shutdown, logged "got SIGTERM, cleaning up") |
| shell form | `/bin/sh -c` | 10.2 s | 137 (killed) |
| exec form, **no** SIGTERM handler | `python` | 10.2 s | 137 (killed) |
| no handler, run with `--init` | `docker-init` | **0.1 s** | 143 (stopped by SIGTERM) |

What's happening:

- **Shell form:** PID 1 is `/bin/sh`, and it doesn't pass SIGTERM on to your app. Docker waits 10 s
  and kills everything. No cleanup, and every deploy is 10 s slower.
- **PID 1 is special:** the kernel doesn't apply default signal actions to PID 1. A process that is
  PID 1 and has no SIGTERM handler simply **ignores** it.
- **`--init`** puts a tiny init program (`tini`, shown as `docker-init`) at PID 1. It forwards
  signals to your app and reaps zombies.

:::{important}
**Rule:** use the **exec form** for `CMD` and `ENTRYPOINT`, and make your app handle SIGTERM (most
web servers already do). If you can't change the app, run it with `--init`.
:::

A minimal SIGTERM handler in Python:

```python
import signal, sys

def shutdown(signum, frame):
    print("got SIGTERM, cleaning up", flush=True)
    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown)
```

## The build context and `.dockerignore`

```{raw} html
:file: ../diagrams/s09-context.html
```

The `.` at the end of `docker build -t app .` is the **build context**: the folder whose files
are sent to the builder. `COPY` can only copy files from inside it.

- Everything in the context is sent, even files you never `COPY`. A forgotten `node_modules/` or
  dataset makes every build slow.
- `COPY . .` copies **everything**, including `.env` files with secrets, and `.git`.

A `.dockerignore` file (next to the Dockerfile, same syntax as `.gitignore`) leaves things out:

```text
.git
__pycache__/
.venv/
.env
**/*.log
node_modules/
```

The Dockerfile doesn't have to be called `Dockerfile` or live in the context root. Use `-f`:

```bash
docker build -f docker/Dockerfile.prod -t app:prod .
```

The context is still `.`, so the paths in `COPY` are relative to `.`, not to `docker/`.

## Layer caching

```{raw} html
:file: ../diagrams/s09-cache.html
```

Docker reuses (caches) a layer if the instruction **and** its inputs haven't changed. But once
one step changes, **every step after it is rebuilt**.

That's why the class Dockerfile copies `requirements.txt` **before** `app.py`:

```dockerfile
COPY requirements.txt .
RUN pip install -r requirements.txt   # slow, but cached until requirements.txt changes
COPY app.py .                         # you change this all the time: cheap to rebuild
```

Edit `app.py` and rebuild: the output shows `CACHED` for the pip install, and the build takes
seconds. If you wrote `COPY . .` before `RUN pip install`, every code change would reinstall all
packages.

**Order your Dockerfile from "changes least" to "changes most":** base image → system packages →
dependency list → install dependencies → your code → CMD.

```bash
docker build -t app .              # watch for CACHED lines
docker build --no-cache -t app .   # force a full rebuild
```

## Multi-stage builds

To **build** an app you often need compilers and build tools; to **run** it you only need the
result. A multi-stage Dockerfile uses one stage to build, then copies just the output into a small
final image. The build tools never reach production.

```dockerfile
# Stage 1: build
FROM golang:1.23-alpine AS build
WORKDIR /src
COPY main.go .
RUN go mod init hello && CGO_ENABLED=0 go build -o /hello .

# Stage 2: run
FROM scratch
COPY --from=build /hello /hello
ENTRYPOINT ["/hello"]
```

```bash
docker build -t hello-multistage .
docker build --target build -t hello-multistage:build .    # stop after stage 1, to compare
docker run --rm hello-multistage
docker images hello-multistage
```

**Output (sizes from our run):**

```text
Hello from a tiny image!
hello-multistage   latest   2.13MB
hello-multistage   build    278MB
```

- `AS build` names a stage; `COPY --from=build` copies files out of it.
- Only the **last** stage becomes the image. The 278 MB of Go tools are thrown away.
- `scratch` is an empty image: nothing but your program. That works for a static binary; for
  Python, use a `-slim` final stage and copy in the installed packages instead.
- Smaller image = faster pulls, less disk, and fewer things for attackers to use.

## Common mistakes

- **Forgetting `--build-arg`.** `ARG APP_VERSION` has no default here, so `APP_ENV` becomes an
  empty string and the app prints `Hello Docker from !`. Give it a default: `ARG APP_VERSION=dev`.
- **`EXPOSE` without `-p`.** The app is running but you can't reach it. EXPOSE is only a note;
  publish with `-p 5111:5111`.
- **App listens on `127.0.0.1`.** Inside a container that means "only from inside the container".
  Listen on `0.0.0.0`, as the class app does.

## Try it yourself

1. Build the app three times with `APP_VERSION` set to `dev`, `qa` and `prod`, tagging each one
   (`app:dev`, …). Run all three on ports 5001, 5002 and 5003 and `curl` each.
2. Add `ARG APP_VERSION=dev` as a default, rebuild **without** `--build-arg`, and check the output.

   <details class="solution">
   <summary>Answer</summary>

   `Hello Docker from dev!`: the ARG default is used when no `--build-arg` is given.

   </details>

3. Run `docker run --rm kube-demo-flask:qa python -c "import flask; print(flask.__version__)"`.
   What happened to `CMD ["python", "app.py"]`?

   <details class="solution">
   <summary>Answer</summary>

   It was **replaced**. Anything after the image name replaces CMD, so this prints the Flask
   version (`3.1.3`) and exits instead of starting the server.

   </details>

4. Build the class `alpine.Dockerfile` and make it print `Hello World Parottasalna`. Then make it
   print `bye` instead of `Hello World …`.

   <details class="solution">
   <summary>Answer</summary>

   ```bash
   docker run --rm kube-demo-hello Parottasalna
   docker run --rm --entrypoint echo kube-demo-hello bye
   ```

   </details>

5. Change the Flask Dockerfile's last line to the shell form `CMD python app.py`, rebuild, and
   time `docker stop`. Then change it back and compare.

   <details class="solution">
   <summary>What you should see</summary>

   With the shell form, `docker stop` takes about **10 seconds**: `/bin/sh` is PID 1 and doesn't
   pass on SIGTERM, so Docker falls back to SIGKILL. With the exec form, Flask's server is PID 1.
   (Flask's development server has no SIGTERM handler, so add one, or use `--init`, to see a
   fast stop.)

   </details>

6. Swap the order in the Flask Dockerfile so `COPY app.py .` comes before `RUN pip install`. Edit
   `app.py` and rebuild twice. Which steps are rebuilt?

   <details class="solution">
   <summary>Answer</summary>

   With `COPY app.py .` before the install, every change to `app.py` invalidates the cache from
   that line on, so `pip install` runs again on every build. In the original order it stays
   `CACHED`.

   </details>

7. Create a 200 MB junk file in your project folder (`fallocate -l 200M junk.bin`) and build.
   Note the "transferring context" size. Add `junk.bin` to `.dockerignore` and build again.

8. Turn the class Flask app into a multi-stage build: install the packages in a
   `python:3.12-slim` stage with `pip install --prefix=/install`, then `COPY --from` that folder
   into a fresh `python:3.12-slim`. Compare the sizes with `docker images`.

## Class files

<details class="source">
<summary>Dockerfile</summary>

```{literalinclude} ../code/07-dockerfile/app/Dockerfile
:language: dockerfile
```

</details>

<details class="source">
<summary>app.py</summary>

```{literalinclude} ../code/07-dockerfile/app/app.py
:language: python
```

</details>

<details class="source">
<summary>requirements.txt</summary>

```{literalinclude} ../code/07-dockerfile/app/requirements.txt
:language: text
```

</details>

- {download}`Dockerfile <../code/07-dockerfile/app/Dockerfile>` ·
  {download}`app.py <../code/07-dockerfile/app/app.py>` ·
  {download}`requirements.txt <../code/07-dockerfile/app/requirements.txt>`
- {download}`Whiteboard: Dockerfile instructions <../code/07-dockerfile/whiteboard-dockerfile.excalidraw>`
  (open at [excalidraw.com](https://excalidraw.com))

<details class="source">
<summary>alpine.Dockerfile</summary>

```{literalinclude} ../code/07-dockerfile/alpine.Dockerfile
:language: dockerfile
```

</details>

- {download}`alpine.Dockerfile <../code/07-dockerfile/alpine.Dockerfile>`
- {download}`Whiteboard: CMD vs ENTRYPOINT, stop signals, cache order <../code/07-dockerfile/whiteboard-cmd-entrypoint-cache.excalidraw>`
  (open at [excalidraw.com](https://excalidraw.com))

<details class="source">
<summary>Multi-stage example: Dockerfile and main.go</summary>

```{literalinclude} ../code/07-dockerfile/multistage/Dockerfile
:language: dockerfile
```

```{literalinclude} ../code/07-dockerfile/multistage/main.go
:language: go
```

</details>
