# Chapter 8 · Image Optimization, Multi-Stage Builds & Container Lifecycle

% Add the class video here once it is uploaded (same iframe block as the other chapters).

## The big idea

A working container is not the same as a **production-ready** one. Two things separate them:

1. **The image:** is it small, scanned and free of build tools? Small images pull and deploy fast,
   and have fewer things for an attacker to use.
2. **The shutdown:** when Docker, Kubernetes or you say "stop", does your app finish its work and
   close its connections, or is it cut off mid-request?

**Everyday example:** a food truck. Before the festival you take out the heavy kitchen equipment you
only needed for prep (**a smaller image**). At closing time you finish serving the people already in
the queue, switch off the gas and lock up (**a graceful shutdown**), instead of the owner pulling the
plug while customers are mid-order.

:::{note}
Every number in this chapter was measured on one small FastAPI app (code in *Class files*), with
Docker 28, Trivy 0.68 and Dive 0.12. Your exact numbers will differ a little, because base images
and the vulnerability database change daily. The **pattern** stays the same.
:::

## Part 1 · Image optimization

### Why image size matters

| Smaller image means | Why you care |
|---|---|
| faster `docker pull` and `docker push` | every new server or Kubernetes node pulls it first |
| faster deploys and scale-up | a new copy of your app starts sooner |
| less disk and registry bandwidth | adds up with many images and versions |
| **fewer packages, fewer CVEs** | every extra package is something that can have a security hole |

A smaller image does **not** make your code run faster. The savings are before the app starts, and in
what an attacker can find.

### Four base images, one app

We built the same FastAPI app four ways and ran `docker images`:

```{raw} html
:file: ../diagrams/ch08-base-images.html
```

| Base image | Size | What it is |
|---|---|---|
| `python:3.12` | **1.14 GB** | full Debian with compilers, headers and many tools |
| `python:3.12-slim` | **142 MB** | Debian without the extras, still glibc and `apt` |
| `python:3.12-alpine` | **79.2 MB** | Alpine Linux: **musl** libc and BusyBox |
| `distroless/python3-debian12` | **68.4 MB** | no shell, no package manager: only Python and your files |

How to choose:

| | **slim** | **alpine** | **distroless** |
|---|---|---|---|
| Works with most pip wheels | ✅ (glibc) | ⚠️ musl: some packages need compiling or behave differently | ✅ (glibc) |
| Has a shell to debug with | ✅ | ✅ (`sh`) | ❌ |
| Attack surface | medium | small | smallest |
| Good default for | most teams | tiny images, simple dependencies | hardened production images |

:::{tip}
**Start with `-slim`.** It is the safe default. Move to Alpine if you know your dependencies work on
musl, and to distroless when you want the smallest attack surface and have another way to debug
(for example a separate debug image with a shell, or `kubectl debug` in Kubernetes).
:::

:::{warning}
**No shell means no `docker exec -it … sh`.** On distroless this fails with
`exec: "sh": executable file not found`. That is the point (an attacker has no shell either), but
plan your debugging before you need it.
:::

### Look inside an image with Dive

`docker images` shows one number. **Dive** shows what each layer added.

```bash
dive kube-demo-opt:slim          # interactive: arrow keys move between layers
CI=true dive kube-demo-opt:slim  # no UI: prints a score, useful in CI
```

**Output (CI mode, `slim` image):**

```text
efficiency: 97.2481 %
wastedBytes: 5650309 bytes (5.7 MB)
PASS: highestUserWastedPercent
```

What to look for in the interactive view:

- **Layers (left):** which instruction added how much. In the `slim` image, the single
  `RUN pip install` layer is **23 MB**, and your `COPY main.py` is about 1 kB.
- **Layer contents (right):** the files that layer added, changed (yellow) or removed (red).
- **Efficiency and wasted space:** files added in one layer and deleted in a later one still take
  space, because layers only add. Deleting a file in a *later* `RUN` does not shrink the image.

:::{important}
**Clean up in the same `RUN` line** that created the mess:
`RUN apt-get update && apt-get install -y gcc && … && rm -rf /var/lib/apt/lists/*`. A separate
`RUN rm …` afterwards hides the files but they stay in the earlier layer. Multi-stage builds (below)
avoid the problem completely.
:::

### Scan an image with Trivy

**Trivy** compares everything inside an image with a database of known vulnerabilities (CVEs).

```bash
trivy image kube-demo-opt:slim                              # full report
trivy image --severity HIGH,CRITICAL kube-demo-opt:slim     # only the serious ones
trivy image --exit-code 1 --severity CRITICAL myapp:1.0     # fail a CI job on CRITICAL
```

We scanned the four images (OS packages + Python packages):

| Image | OS findings | of which CRITICAL / HIGH |
|---|---|---|
| `python:3.12` (full, Debian 13) | **3,277** | 16 / 317 |
| `python:3.12-slim` (Debian 13) | 166 | 0 / 44 |
| `python:3.12-alpine` | **1** | 0 / 0 |
| distroless (Debian 12) | 291 | 2 / 60 |

Three lessons from these numbers:

1. **Fewer packages means fewer findings.** Full to slim cut the findings by about 20 times.
2. **Smaller is not automatically safer.** The distroless image is the smallest, yet has more findings
   than slim: it is built on the *older* Debian 12 with Python 3.11. The **age of the base image**
   matters as much as its size. Scan and compare; don't assume.
3. **Trivy also scans your Python packages.** In every image it flagged `starlette 0.41.3`
   (3 HIGH findings, for example a denial-of-service in `CVE-2025-62727`, fixed in 0.49.1) and the
   `pip` that ships with the base image. The fix for a library finding is to **upgrade the
   library**, rebuild, and scan again.

:::{note}
A finding is not always exploitable in *your* app, and many have no fix yet. Use the report to **find
what to upgrade** and to **block CRITICAL ones in CI**, not to chase a score of zero.
:::

### Multi-stage builds

To **build** an app you often need compilers and tools; to **run** it you only need the result. A
multi-stage Dockerfile uses a first stage to build and a second, clean stage that copies in only the
finished result.

```{raw} html
:file: ../diagrams/ch08-multistage.html
```

```dockerfile
# Stage 1 "builder": has pip and compilers. Thrown away at the end.
FROM python:3.12-slim AS builder
WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2 "runtime": only the finished virtual environment and your code
FROM python:3.12-slim AS runtime
RUN useradd --system --create-home --uid 10001 appuser
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY --chown=appuser app/main.py .
ENV PATH="/opt/venv/bin:$PATH" PYTHONUNBUFFERED=1
USER appuser
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -f Dockerfile.multistage -t kube-demo-opt:multistage .
docker build -f Dockerfile.multistage --target builder -t kube-demo-opt:builder .   # stop after stage 1
docker images kube-demo-opt
docker run --rm kube-demo-opt:multistage sh -c 'which gcc make || echo "no gcc, no make"; id -un'
```

**Output:**

```text
multistage   145MB
builder      457MB
no gcc, no make
appuser
```

What happened:

- `AS builder` names a stage; **`COPY --from=builder`** copies a folder out of it.
- **Only the last stage becomes the image.** The 457 MB builder (with `gcc`) is thrown away. The
  runtime image has no compiler, and it runs as `appuser`, not root.
- `--target builder` stops after stage 1, so you can inspect it or run tests inside it.
- A virtual environment (`/opt/venv`) is easy to copy as one folder. For distroless, we install to
  `--target=/packages` and set `PYTHONPATH` instead (see `Dockerfile.distroless`).

:::{important}
**Be honest about when multi-stage helps.** Our app only needs pure-Python packages, so the
multi-stage image (145 MB) is about the same size as plain `slim` (142 MB). The win appears as soon
as the **build** needs compilers or tools that the **runtime** doesn't: C extensions, `npm`, Go,
Java or Rust builds. In the Go example in [Chapter 7](07-dockerfile.md) the image went from 278 MB
to 2 MB. Even when the size is the same, multi-stage still gives you a clean runtime, a non-root
user, and a stage you can test.
:::

### The checklist: a production-ready image

1. **Pick a small, current base** (`-slim` by default) and pin a tag (`python:3.12-slim`, not `latest`).
2. **Multi-stage:** build in one stage, copy only the result into the last one.
3. **Order layers** from "changes least" to "changes most": requirements, install, then your code
   ([Chapter 7](07-dockerfile.md)).
4. **`--no-cache-dir`** for pip, and delete apt lists in the same `RUN`.
5. **`.dockerignore`** for `.git`, `.venv`, `.env`, `__pycache__`.
6. **Run as a non-root `USER`.**
7. **Exec-form `CMD`**, and an app that handles SIGTERM (Part 2).
8. **Scan with Trivy**, fail CI on CRITICAL, and **rebuild regularly** to pick up base-image fixes.

## Part 2 · Container lifecycle and graceful shutdown

### What happens when a container stops

`docker stop` is **polite first, then forceful**:

```{raw} html
:file: ../diagrams/ch08-stop-timeline.html
```

- **SIGTERM (signal 15)** goes to **PID 1** of the container. It is a request: the app may catch it,
  finish its work and exit.
- Docker then **waits 10 seconds** (the *grace period*).
- If the container is still running, Docker sends **SIGKILL (signal 9)**. It cannot be caught or
  ignored. The kernel ends the process at once, with no cleanup.

| How it ended | Exit code | Meaning |
|---|---|---|
| app exited by itself | `0` | clean shutdown |
| stopped by SIGTERM | `143` = 128 + 15 | no handler, the default action ended it |
| killed by SIGKILL | `137` = 128 + 9 | the grace period ran out |

Change the grace period with `docker stop -t 30 web` or `docker run --stop-timeout 30 …`. In
Kubernetes the same idea is `terminationGracePeriodSeconds` (30 s by default).

### PID 1 and signals

This is why signals matter in containers ([Chapter 2](02-linux-prerequisites.md) introduced PID 1).
`docker stop` only signals **PID 1**. Two things go wrong:

```{raw} html
:file: ../diagrams/ch08-pid1.html
```

1. **PID 1 is a shell.** The **shell form** `CMD uvicorn main:app …` runs as `/bin/sh -c "…"`. The
   shell is PID 1, it does not forward SIGTERM to uvicorn, and your app never hears the request.
2. **PID 1 has no handler.** For any other process, SIGTERM ends it by default. The kernel gives
   **PID 1 no default action**, so a PID 1 with no SIGTERM handler simply **ignores** the signal.

We proved it. We started the same app in two containers, started a 5-second request
(`/slow?seconds=5`), and ran `docker stop` one second later:

| Dockerfile | PID 1 (from `/proc/1/cmdline`) | `docker stop` took | Exit code | Shutdown hook ran? |
|---|---|---|---|---|
| exec form: `CMD ["uvicorn", …]` | `python3.12 /usr/local/bin/uvicorn main:app …` | **5.5 s** | **0** | ✅ "shutdown: done, bye" |
| shell form: `CMD uvicorn …` | `/bin/sh -c uvicorn main:app …` | **10.9 s** | **137** | ❌ nothing logged |

The exec-form container waited for the running request, ran the cleanup and exited with 0. The
shell-form container ignored the request to stop, then was killed after the full 10 seconds. Every
deploy of that app would be 10 s slower, with no cleanup at all.

:::{important}
**Rule:** write `CMD` and `ENTRYPOINT` in the **exec form** (a JSON list), and make sure the app
handles SIGTERM. Web servers like Uvicorn and Gunicorn already do. If you can't change the app, run
it with `docker run --init`: a tiny init program (`tini`, shown as `docker-init`) becomes PID 1,
forwards the signal to your app and cleans up zombie processes.
:::

### Graceful shutdown with FastAPI and Uvicorn

**Graceful** means: stop taking new work, finish what is in progress, release resources, then exit.

```{raw} html
:file: ../diagrams/ch08-graceful.html
```

Uvicorn does steps 1 to 3 for you. You add step 4 with FastAPI's **lifespan**: code **before**
`yield` runs at startup, code **after** it runs at shutdown.

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("startup: ready for traffic", flush=True)    # open DB pools, load models ...
    yield
    print("shutdown: closing connections, flushing logs", flush=True)   # close them here
    await asyncio.sleep(0.5)                           # pretend cleanup
    print("shutdown: done, bye", flush=True)

app = FastAPI(lifespan=lifespan)
```

**Run it and stop it while a request is running:**

```bash
docker run -d --name web -p 8000:8000 kube-demo-opt:multistage
curl "localhost:8000/slow?seconds=5" &      # a request that takes 5 seconds
docker stop web                             # SIGTERM now
docker logs web
docker inspect -f '{{.State.ExitCode}}' web
```

**Output:**

```text
{"finished":true,"took":5.0}                        ← the curl got its full answer
INFO:     Shutting down
INFO:     Waiting for connections to close. (CTRL+C to force quit)
INFO:     172.17.0.1:46900 - "GET /slow?seconds=5 HTTP/1.1" 200 OK
INFO:     Waiting for application shutdown.
shutdown: closing connections, flushing logs
INFO:     Application shutdown complete.
INFO:     Finished server process [1]
shutdown: done, bye
0
```

Read the log in order: Uvicorn **stops listening**, waits for the open request, **then** runs your
shutdown code, then exits with `0`. `Finished server process [1]` also confirms that uvicorn *is*
PID 1.

:::{warning}
**The whole shutdown must fit inside the grace period.** If a request takes 20 s but Docker waits 10 s,
SIGKILL arrives mid-request. Either shorten the work, raise the timeout (`docker stop -t 30`), or
both. Uvicorn can also be told how long to wait with `--timeout-graceful-shutdown 8`: set it a
little **below** the Docker timeout, so uvicorn gives up cleanly before Docker kills it.
:::

### Container lifecycle at a glance

```text
docker create → Created
docker start  → Running ──docker pause──▶ Paused
docker stop   → SIGTERM, wait, SIGKILL ──▶ Exited (state and files kept)
docker rm     → Removed (writable layer deleted)
```

`docker kill` skips the polite step and sends SIGKILL (or another signal with `-s`) straight away.
`docker restart` is a stop followed by a start, so it needs a graceful shutdown too. See also the
lifecycle diagram in [Chapter 4](04-docker-commands.md).

## Common mistakes

- **Shell-form `CMD`.** `docker stop` takes 10 s and ends in exit code 137. Use `CMD ["…", "…"]`.
- **`CMD ["sh", "-c", "uvicorn …"]` or a start script with no `exec`.** Same problem, with the shell
  in the way. In a script, end with `exec uvicorn …` so the app replaces the shell.
- **Scanning once.** A new CVE can appear tomorrow against an image you built last month. Rebuild
  and rescan regularly.
- **`FROM python:latest`.** Today's `latest` is not tomorrow's, so builds stop being repeatable.
  Pin at least the minor version (`python:3.12-slim`).
- **Mixing Python versions with distroless.** The packages you copy in must be built for the same
  Python version as the distroless image (`python3-debian12` is 3.11), or imports fail.
- **Cleaning up in a later `RUN`.** The files stay in the earlier layer. Clean up in the same `RUN`,
  or use a multi-stage build.
- **Running as root "because it works".** If someone breaks into the app, they are root in the
  container. Add `USER`.
- **Cleanup that is slower than the grace period.** The work is cut off by SIGKILL and you never see it
  in the logs.

## Try it yourself

1. Build all four base-image Dockerfiles from the class files and compare them with
   `docker images kube-demo-opt`. Which is smallest? Which would you choose for this app, and why?

   <details class="solution">
   <summary>Answer</summary>

   Distroless was smallest (68 MB), then Alpine (79 MB), slim (142 MB) and the full image
   (1.14 GB). **slim** is a sensible default: tiny difference from Alpine in practice, glibc-compatible
   and debuggable. Choose distroless when hardening matters more than easy debugging.

   </details>

2. Run `trivy image --severity HIGH,CRITICAL` on the `slim` image. Find the `starlette` findings.
   Upgrade `fastapi` in `requirements.txt` to a current release, rebuild and scan again. What changed?

   <details class="solution">
   <summary>Answer</summary>

   `fastapi==0.115.6` requires an old `starlette`. A newer `fastapi` allows a newer `starlette`, and the
   three HIGH findings for it disappear after the rebuild. (The OS findings don't change: they come from
   the base image.)

   </details>

3. Run `dive kube-demo-opt:slim` and find the layer with the most space. Which instruction made it?

   <details class="solution">
   <summary>Answer</summary>

   The `RUN pip install …` layer (about 23 MB). Your own code (`COPY app/main.py .`) is about
   1 kB. Almost all of an image is dependencies, which is why base image and dependencies matter most.

   </details>

4. Build with `--target builder`, then without. How much smaller is the final image? Check that
   `gcc` is missing from the final one.

   <details class="solution">
   <summary>Answer</summary>

   457 MB for the builder against 145 MB for the final image. `docker run --rm IMAGE which gcc`
   finds `/usr/bin/gcc` in the builder and finds nothing in the final image.

   </details>

5. Start `Dockerfile.shellform` and `Dockerfile.multistage` images in two containers. For each, run
   `docker exec NAME cat /proc/1/cmdline | tr '\0' ' '` and then time `docker stop`.

   <details class="solution">
   <summary>What you should see</summary>

   PID 1 is `/bin/sh -c uvicorn …` for the shell form and `uvicorn …` for the exec form. The shell
   form takes about 10 s and exits with 137. The exec form stops in about 1 second when idle
   (uvicorn's half-second of cleanup plus shutdown), with exit code 0.

   </details>

6. Run the exec-form container, start `curl "localhost:8000/slow?seconds=15"`, then `docker stop web`.
   What happens, and how do you fix it?

   <details class="solution">
   <summary>Answer</summary>

   After 10 s SIGKILL arrives: the container exits with **137**, `curl` fails with
   `curl: (52) Empty reply from server`, and there is no "shutdown: done" line. Fix: give Docker
   more time, `docker stop -t 30 web`, or start with `--stop-timeout 30`, and set uvicorn's
   `--timeout-graceful-shutdown 25`.

   </details>

7. Run `Dockerfile.shellform` with `docker run -d --init …`. Is `/bin/sh` still PID 1? Is the stop graceful?

   <details class="solution">
   <summary>Answer</summary>

   No. PID 1 is `docker-init` (tini), with `/bin/sh` as its child and uvicorn as the grandchild. We
   measured `docker stop` at 0.3 s with exit code **143**, so it looks fast. But the logs show **no
   "Shutting down" and no "shutdown: done"**: tini's SIGTERM ended the shell and uvicorn never got a
   chance to clean up. A fast stop is not the same as a graceful one. The exec form is the real fix.

   </details>

8. Add a second item to the lifespan: a pretend database connection that you open at startup and close
   at shutdown. Prove from `docker logs` that it closed.

## Class files

<details class="source">
<summary>app/main.py</summary>

```{literalinclude} ../code/08-image-optimization/app/main.py
:language: python
```

</details>

<details class="source">
<summary>app/requirements.txt and .dockerignore</summary>

```{literalinclude} ../code/08-image-optimization/app/requirements.txt
:language: text
```

```{literalinclude} ../code/08-image-optimization/app/.dockerignore
:language: text
```

</details>

<details class="source">
<summary>Dockerfile.fat (full image)</summary>

```{literalinclude} ../code/08-image-optimization/Dockerfile.fat
:language: dockerfile
```

</details>

<details class="source">
<summary>Dockerfile.slim</summary>

```{literalinclude} ../code/08-image-optimization/Dockerfile.slim
:language: dockerfile
```

</details>

<details class="source">
<summary>Dockerfile.alpine</summary>

```{literalinclude} ../code/08-image-optimization/Dockerfile.alpine
:language: dockerfile
```

</details>

<details class="source">
<summary>Dockerfile.multistage</summary>

```{literalinclude} ../code/08-image-optimization/Dockerfile.multistage
:language: dockerfile
```

</details>

<details class="source">
<summary>Dockerfile.distroless</summary>

```{literalinclude} ../code/08-image-optimization/Dockerfile.distroless
:language: dockerfile
```

</details>

<details class="source">
<summary>Dockerfile.shellform (the anti-pattern)</summary>

```{literalinclude} ../code/08-image-optimization/Dockerfile.shellform
:language: dockerfile
```

</details>

Build any of them from the `08-image-optimization` folder:

```bash
docker build -f Dockerfile.multistage -t kube-demo-opt:multistage .
```

- {download}`main.py <../code/08-image-optimization/app/main.py>` ·
  {download}`requirements.txt <../code/08-image-optimization/app/requirements.txt>` ·
  {download}`Dockerfile.fat <../code/08-image-optimization/Dockerfile.fat>` ·
  {download}`Dockerfile.slim <../code/08-image-optimization/Dockerfile.slim>` ·
  {download}`Dockerfile.alpine <../code/08-image-optimization/Dockerfile.alpine>` ·
  {download}`Dockerfile.multistage <../code/08-image-optimization/Dockerfile.multistage>` ·
  {download}`Dockerfile.distroless <../code/08-image-optimization/Dockerfile.distroless>` ·
  {download}`Dockerfile.shellform <../code/08-image-optimization/Dockerfile.shellform>`
