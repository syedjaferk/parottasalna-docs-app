# Session 7 · Writing a Dockerfile

## The big idea

A **Dockerfile** is a recipe: a text file of instructions that Docker follows to build an image.
Instead of installing things by hand inside a container, you write them down once, and anyone can
rebuild the same image with `docker build`. Each instruction adds a **layer**, and Docker caches layers,
so rebuilds are fast when little has changed.

**Everyday example:** a recipe card for biryani. "Take basmati rice. Add masala. Add chicken. Cook 30
minutes." Anyone who follows the card gets the same dish. If you only change the salt in the last
step, you don't re-buy the rice; you reuse everything before it. That reuse is the layer cache.

```{raw} html
:file: ../diagrams/dockerfile-layers.html
```

## A small app and its Dockerfile

`app.py` is a tiny web server that greets you and counts visits.

```{literalinclude} ../code/app/app.py
:language: python
```

The Dockerfile, five instructions:

```{literalinclude} ../code/app/Dockerfile
:language: dockerfile
```

| Instruction | Meaning |
|---|---|
| `FROM` | The base image to start from (always first) |
| `WORKDIR` | The folder inside the image where later commands run |
| `COPY` | Copy files from your folder into the image |
| `ENV` | Set an environment variable (a default setting) |
| `EXPOSE` | Document which port the app uses (it does **not** publish it) |
| `CMD` | The command to run when a container starts |

## Build it, run it, change it

```{literalinclude} ../code/07-dockerfile.sh
:language: bash
```

```{literalinclude} ../code/07-dockerfile.out
:language: text
```

What it shows:

- **`docker build -t dm-app:1.0 .`** built the image; `-t` gives it a name and tag, and `.` is the folder
  with the Dockerfile and files.
- **`docker history`** lists the layers newest first: `CMD`, `EXPOSE`, `ENV`, `COPY`, `WORKDIR`, and below
  them the layers of `python:3.12-slim`. One instruction, one layer.
- The app answered twice with `visit 1` then `visit 2`. The counter lives in memory, so it resets when the
  container restarts (state belongs in a volume or database, Session 8).
- **`-e GREETING=Vanakkam`** replaced the default setting from `ENV` at run time without rebuilding.
- **A second build with nothing changed** shows `CACHED` lines: Docker reused the layers.

## Order matters for the cache

If you change `app.py`, the `COPY` layer and every layer after it must rebuild; the layers above stay
cached. So put what changes **least** (base image, dependency install) first and what changes **most**
(your code) last. In bigger apps the usual pattern is: copy `requirements.txt`, run `pip install`, and
only then copy the source code.

## Common mistakes

- **Forgetting the `.dockerignore` file.** Without it `COPY . .` sends everything, including `.git`
  and secrets, into the image.
- **Using `latest` as the base.** Your build changes silently. Pin a version, as `python:3.12-slim` does here.
- **Thinking `EXPOSE` opens the port.** You still need `-p` at `docker run`.
- **`CMD python app.py` (shell form) versus `CMD ["python", "app.py"]` (exec form).** Prefer the list form,
  so the app is PID 1 and receives stop signals.
- **Baking secrets into the image** with `ENV PASSWORD=...`. Anyone with the image can read it. Pass secrets at run time.
- **Installing build tools and leaving them in.** Bigger image, bigger attack surface. Use a slim base, or
  multi-stage builds for compiled programs.

## Hands-on exercises

**Exercise 1.** Build the image as `dm-app:2.0` and run it on host port 9100. Call it once.

<details class="solution"><summary>Solution</summary>

```bash
cd code/app
docker build -t dm-app:2.0 .
docker run -d --name dm-app-2 -p 9100:8000 dm-app:2.0
sleep 1; curl -s http://localhost:9100/
docker rm -f dm-app-2
```

It prints `Hello from Docker! visit 1`.

</details>

**Exercise 2.** Change the default greeting to `Welcome` in the Dockerfile, rebuild, and look at the build
output. Which steps are cached?

<details class="solution"><summary>Solution</summary>

Edit `ENV GREETING=Welcome` and run `docker build --progress=plain -t dm-app:2.0 .`. `FROM`, `WORKDIR` and
`COPY` are still `CACHED` because nothing above the changed line differs; only `ENV` and the steps after
it rebuild.

</details>

**Exercise 3.** Why is `CMD ["python", "app.py"]` better than `CMD python app.py`?

<details class="solution"><summary>Solution</summary>

The list (exec) form starts Python directly as PID 1, so `docker stop` signals reach it and it shuts down
cleanly. The shell form wraps it in `/bin/sh -c`, and the shell may not pass the signal on.

</details>

## Practice

Take the **Session 7 quiz**. The original *Detailed Structure of a Dockerfile* page and the six Docker
tasks are in the reference section.
