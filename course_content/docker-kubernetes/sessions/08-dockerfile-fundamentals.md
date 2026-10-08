# Session 8 · Dockerfile Fundamentals

## The big idea

A **Dockerfile** is a recipe: a text file of step-by-step instructions that tells Docker how to
build an image. `docker build` reads it top to bottom, and each step adds a layer (Session 7). The
result is an image you can run anywhere.

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
- Use both together: ENTRYPOINT is the program, CMD gives default arguments. [Session 9](09-dockerfile-deep-dive.md)
  has the hands-on demo.

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

## Class files

<details class="source">
<summary>Dockerfile</summary>

```{literalinclude} ../code/08-dockerfile/app/Dockerfile
:language: dockerfile
```

</details>

<details class="source">
<summary>app.py</summary>

```{literalinclude} ../code/08-dockerfile/app/app.py
:language: python
```

</details>

<details class="source">
<summary>requirements.txt</summary>

```{literalinclude} ../code/08-dockerfile/app/requirements.txt
:language: text
```

</details>

- {download}`Dockerfile <../code/08-dockerfile/app/Dockerfile>` ·
  {download}`app.py <../code/08-dockerfile/app/app.py>` ·
  {download}`requirements.txt <../code/08-dockerfile/app/requirements.txt>`
- {download}`Whiteboard: Dockerfile instructions <../code/08-dockerfile/whiteboard-dockerfile.excalidraw>`
  (open at [excalidraw.com](https://excalidraw.com))
