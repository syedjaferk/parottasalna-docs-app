# Session 9 · Dockerfile Deep Dive

## The big idea

Three small details decide whether your images are fast to build, small, and well-behaved:

1. **How you write `CMD`/`ENTRYPOINT`** (exec form vs shell form) decides whether your app hears
   `docker stop`.
2. **The build context** decides what gets sent to Docker, and `.dockerignore` keeps junk and
   secrets out.
3. **The order of instructions** decides whether a rebuild takes 2 seconds or 2 minutes (layer
   caching).

**Everyday example:** packing for a trip. Pack the things that never change (toiletries) first and
the things you keep changing (today's clothes) last, and leave out what you don't need. That's
caching and `.dockerignore`.

## 1. ENTRYPOINT + CMD together

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

## 2. Exec form vs shell form

```dockerfile
CMD ["python", "app.py"]     # exec form: JSON list, run directly
CMD python app.py            # shell form: run as  /bin/sh -c "python app.py"
```

The difference matters because of **PID 1** and **signals** (Session 2). `docker stop` sends
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

## 3. The build context and `.dockerignore`

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

## 4. Layer caching

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

## Try it yourself

1. Build the class `alpine.Dockerfile` and make it print `Hello World Parottasalna`. Then make it
   print `bye` instead of `Hello World …`.

   <details class="solution">
   <summary>Answer</summary>

   ```bash
   docker run --rm kube-demo-hello Parottasalna
   docker run --rm --entrypoint echo kube-demo-hello bye
   ```

   </details>

2. Change the Flask Dockerfile's last line to the shell form `CMD python app.py`, rebuild, and
   time `docker stop`. Then change it back and compare.

   <details class="solution">
   <summary>What you should see</summary>

   With the shell form, `docker stop` takes about **10 seconds**: `/bin/sh` is PID 1 and doesn't
   pass on SIGTERM, so Docker falls back to SIGKILL. With the exec form, Flask's server is PID 1.
   (Flask's development server has no SIGTERM handler, so add one, or use `--init`, to see a
   fast stop.)

   </details>

3. Swap the order in the Flask Dockerfile so `COPY app.py .` comes before `RUN pip install`. Edit
   `app.py` and rebuild twice. Which steps are rebuilt?

   <details class="solution">
   <summary>Answer</summary>

   With `COPY app.py .` before the install, every change to `app.py` invalidates the cache from
   that line on, so `pip install` runs again on every build. In the original order it stays
   `CACHED`.

   </details>

4. Create a 200 MB junk file in your project folder (`fallocate -l 200M junk.bin`) and build.
   Note the "transferring context" size. Add `junk.bin` to `.dockerignore` and build again.

## Class files

<details class="source">
<summary>alpine.Dockerfile</summary>

```{literalinclude} ../code/09-dockerfile-deep-dive/alpine.Dockerfile
:language: dockerfile
```

</details>

- {download}`alpine.Dockerfile <../code/09-dockerfile-deep-dive/alpine.Dockerfile>`
- {download}`Whiteboard: CMD vs ENTRYPOINT, stop signals, cache order <../code/09-dockerfile-deep-dive/whiteboard-cmd-entrypoint-cache.excalidraw>`
  (open at [excalidraw.com](https://excalidraw.com))
