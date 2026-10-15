# Chapter 9 · Volumes & Persistence: Writable Layer, Volumes, Bind Mounts and tmpfs

% Add the class video here once it is uploaded (same iframe block as the other chapters).

## The big idea

A container is **disposable**. You can stop it, delete it and start a new one from the same image in
seconds. That is a great property for your *code*, and a dangerous one for your *data*. If the
database files, uploads or logs live inside the container, `docker rm` takes them with it.

Docker gives you **four places** to put files. Choosing the right one is the whole chapter:

1. **Writable layer:** the default. Easy, but it dies with the container.
2. **Volume:** storage that Docker manages **outside** the container. The right home for data.
3. **Bind mount:** a folder from **your host** shown inside the container. The right tool for development.
4. **tmpfs:** a folder that lives only in **memory**. The right place for secrets and scratch files.

**Everyday example:** a hotel stay.

- The **whiteboard in your room** (writable layer): write whatever you like, but housekeeping wipes it at checkout.
- The **hotel safe-deposit locker** (volume): the hotel looks after it, and your valuables are still there when you come back in a different room.
- **Your own suitcase** that you carry in from home (bind mount): you can open it at home or in the room, and it is the same suitcase.
- **A thing you memorise** (tmpfs): it never touches paper, and it is gone when you sleep.

```{raw} html
:file: ../diagrams/ch09-where-data-lives.html
```

:::{note}
The commands in this chapter are standard Docker CLI (Docker 23 or newer). The output blocks show
**typical** output. IDs, sizes and timings will differ on your machine, so run each step yourself and
compare. Everything uses small images (`alpine`, `python:3.12-slim`) and the FastAPI idea from
[Chapter 8](08-image-optimization-lifecycle.md).
:::

## Part 1 · The writable layer (the default)

### What it is

An image is a stack of **read-only** layers ([Chapter 7](07-dockerfile.md)). When you start a
container, Docker adds one thin **writable layer** on top, just for that container. Everything the
app writes without any special flag goes there.

```{raw} html
:file: ../diagrams/ch09-copy-on-write.html
```

This is **copy-on-write**: the first time a container changes a file that comes from the image,
Docker copies the whole file up into the writable layer and changes the copy. The image itself is
never touched, so one image can safely serve a hundred containers.

### Prove it: data survives `stop`, but not `rm`

```bash
docker run -d --name scratch alpine sh -c 'echo "order #1" > /note.txt && sleep 3600'
docker exec scratch cat /note.txt          # the file is there
docker stop scratch
docker start scratch
docker exec scratch cat /note.txt          # still there: stop/start keeps the writable layer
docker rm -f scratch
docker run --rm alpine cat /note.txt       # a brand-new container from the same image
```

**Output:**

```text
order #1
order #1
cat: can't open '/note.txt': No such file or directory
```

The file survived `stop` and `start` because it is the **same container**. It did not survive `rm`,
because the writable layer belongs to the container and is deleted with it.

```{raw} html
:file: ../diagrams/ch09-lifecycle.html
```

### See what a container changed

```bash
docker run -d --name scratch alpine sh -c 'mkdir /logs && echo hi > /logs/app.log && sleep 3600'
docker diff scratch        # A = added, C = changed, D = deleted
docker ps -s               # SIZE column: size of the writable layer, and the image in brackets
```

**Output:**

```text
A /logs
A /logs/app.log
```

`docker diff` is a quick way to answer "what is this container writing, and where?" That is useful
before you decide what needs a volume.

### Why not keep data here?

| Problem | What it means |
|---|---|
| **Lost on `docker rm`** | Redeploying, upgrading the image or recreating the container wipes it. |
| **Tied to one container** | Another container cannot easily use the same files. |
| **Hard to reach** | The data sits in an internal Docker folder, not a place you manage. |
| **Slower for heavy writes** | The copy-on-write step adds overhead. Databases suffer most. |

The writable layer is fine for small, **throwaway** files: caches, temp files, a PID file. Anything
you would be sad to lose goes on a volume.

## Part 2 · Volumes (the right home for data)

### What it is

A **volume** is a folder that Docker creates and manages **outside any container**. You attach it to
a path inside a container. Delete the container and the volume stays, ready for the next one.

```bash
docker volume create appdata
docker volume ls
docker volume inspect appdata
```

**Output:**

```text
DRIVER    VOLUME NAME
local     appdata

[
    {
        "CreatedAt": "2026-10-15T14:58:03Z",
        "Driver": "local",
        "Mountpoint": "/var/lib/docker/volumes/appdata/_data",
        "Name": "appdata",
        "Scope": "local"
    }
]
```

`Mountpoint` is where the files really live on the Docker host. You normally never touch it
directly: let containers read and write it.

:::{note}
On **Docker Desktop** (Windows and macOS), Docker runs inside a small Linux VM, so that path is inside
the VM and not on your laptop's disk. Use the helper-container trick in the backup section to reach the files.
:::

### Use it: data survives `rm`

```bash
docker run --rm -v appdata:/data alpine sh -c 'echo "order #1" > /data/note.txt'
# the container is already gone (--rm) ...
docker run --rm -v appdata:/data alpine cat /data/note.txt
```

**Output:**

```text
order #1
```

Two different containers, one shared piece of data. Compare this with Part 1, where the same test
failed.

### Two ways to write it: `-v` and `--mount`

| | `-v` / `--volume` | `--mount` |
|---|---|---|
| Style | short, colon-separated | long, `key=value` pairs |
| Volume | `-v appdata:/data` | `--mount type=volume,src=appdata,dst=/data` |
| Read-only | `-v appdata:/data:ro` | `--mount type=volume,src=appdata,dst=/data,readonly` |
| Bind mount | `-v $(pwd)/app:/app` | `--mount type=bind,src=$(pwd)/app,dst=/app` |
| tmpfs | `--tmpfs /tmp` | `--mount type=tmpfs,dst=/tmp` |
| Typo in a host path | **silently creates an empty folder** | **fails with a clear error** |

:::{tip}
`-v` is quick to type, and `--mount` is safer and easier to read. Use `--mount` in scripts and
documentation, and `-v` at the terminal. They do the same job.
:::

### Named vs anonymous volumes

```bash
docker run -d --name a -v appdata:/data  alpine sleep 3600   # NAMED: you chose the name
docker run -d --name b -v /data          alpine sleep 3600   # ANONYMOUS: Docker makes a random name
docker volume ls
```

**Output:**

```text
DRIVER    VOLUME NAME
local     appdata
local     3f9c1d0b5a7e2c8d4b6a1e9f0c3d5a7b8e2f4c6d9a1b3e5f7c8d0a2b4e6f8a1c
```

Anonymous volumes are hard to find again and easy to leave behind. Use **named** volumes for
anything you care about.

### A volume starts with the image's files

If you mount an **empty** volume onto a path that already has files in the image, Docker copies the
image's files into the volume the first time. A **bind mount does not do this**. It shows the host
folder and **hides** whatever the image had there (see Part 3).

This matters for permissions. In [Chapter 8](08-image-optimization-lifecycle.md) the app runs as
`appuser` (UID 10001). Create the data folder in the image **and give it to that user**, so that a
fresh volume inherits the right owner:

```dockerfile
FROM python:3.12-slim
RUN useradd --system --create-home --uid 10001 appuser
WORKDIR /app
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=appuser app/main.py .

# make the folder BEFORE switching user, and give it to appuser
RUN mkdir /data && chown appuser:appuser /data

USER appuser
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### A small stateful app

A counter that saves its value in `/data/count.txt`:

```python
from pathlib import Path
from fastapi import FastAPI

app = FastAPI()
COUNT_FILE = Path("/data/count.txt")

@app.get("/hit")
def hit():
    n = int(COUNT_FILE.read_text()) if COUNT_FILE.exists() else 0
    n += 1
    COUNT_FILE.write_text(str(n))
    return {"hits": n}
```

Run it **without** a volume, then **with** one, and delete the container each time:

```bash
docker build -t counter .

# 1) no volume: the count lives in the writable layer
docker run -d --name c1 -p 8000:8000 counter
curl -s localhost:8000/hit; curl -s localhost:8000/hit
docker rm -f c1
docker run -d --name c1 -p 8000:8000 counter
curl -s localhost:8000/hit        # starts again from 1
docker rm -f c1

# 2) with a named volume: the count lives outside the container
docker run -d --name c2 -p 8000:8000 -v counter-data:/data counter
curl -s localhost:8000/hit; curl -s localhost:8000/hit
docker rm -f c2
docker run -d --name c2 -p 8000:8000 -v counter-data:/data counter
curl -s localhost:8000/hit        # continues from 3
```

**Output (the last `curl` of each run):**

```text
{"hits":1}      ← no volume: count lost with the container
{"hits":3}      ← volume: count kept
```

### Share a volume, and back it up

```{raw} html
:file: ../diagrams/ch09-sharing-backup.html
```

A volume can be mounted into **several containers at once**. That is how a database and a backup job
(or a web app and a worker) share files. Mount it **read-only** (`:ro`) wherever a container only
needs to read.

**Back up** a volume with a short-lived helper container. It mounts the volume and your current
folder, then packs one into the other:

```bash
docker run --rm \
  -v counter-data:/data:ro \
  -v "$(pwd)":/backup \
  alpine tar czf /backup/counter-data.tgz -C /data .
ls -lh counter-data.tgz
```

**Restore** into a new (or empty) volume the same way, in the other direction:

```bash
docker volume create counter-data-restored
docker run --rm \
  -v counter-data-restored:/data \
  -v "$(pwd)":/backup \
  alpine tar xzf /backup/counter-data.tgz -C /data
```

The same helper trick lets you look inside a volume on Docker Desktop:
`docker run --rm -v counter-data:/data alpine ls -la /data`.

### Cleaning up volumes

| Command | What it removes |
|---|---|
| `docker rm c2` | the container only. **Named volumes stay.** |
| `docker rm -v c1` | the container **and its anonymous volumes** |
| `docker volume rm counter-data` | one volume (fails if a container still uses it) |
| `docker volume prune` | unused **anonymous** volumes (Docker 23 and newer) |
| `docker volume prune -a` | **all** unused volumes, named ones too. Be careful. |
| `docker compose down -v` | the Compose project's containers **and its named volumes** |

:::{warning}
**There is no undo.** `docker volume rm`, `prune -a` and `compose down -v` delete the data for good.
Take a backup first, and never run `prune -a` on a machine you share until you have read the list it shows.
:::

### The `VOLUME` instruction (a trap)

A Dockerfile can declare `VOLUME /data`. Docker then makes an **anonymous** volume for that path in
every container, unless you mount your own. Two surprises follow:

- You get random-named volumes piling up, one per container.
- Any `RUN` that changes `/data` **after** the `VOLUME` line is silently discarded.

Most teams skip `VOLUME` in their own Dockerfiles and mount a **named** volume when they run the
container (`-v`, or `volumes:` in Compose). Many official images (databases) do use `VOLUME`. That
is why running them without `-v` still leaves an anonymous volume behind.

## Part 3 · Bind mounts (your files, inside the container)

### What it is

A **bind mount** takes a folder that already exists on the **host** and shows it inside the
container at a path you choose. Both sides see the **same files**, live.

```bash
mkdir -p site && echo "<h1>version 1</h1>" > site/index.html

docker run -d --name web -p 8080:80 \
  --mount type=bind,src="$(pwd)/site",dst=/usr/share/nginx/html,readonly \
  nginx:alpine

curl -s localhost:8080                      # <h1>version 1</h1>
echo "<h1>version 2</h1>" > site/index.html # edit on the HOST ...
curl -s localhost:8080                      # <h1>version 2</h1>   ... no restart needed
```

You edited a file on the host and the running container served the change at once.

### The best use: development with hot reload

Mount your source code and let Uvicorn reload when a file changes:

```bash
docker run --rm -p 8000:8000 \
  --mount type=bind,src="$(pwd)/app",dst=/app \
  --user "$(id -u):$(id -g)" \
  counter \
  uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Now you edit `app/main.py` in your editor and the container picks it up. There is no `docker build`
between changes.

### Rules and pitfalls

| Pitfall | What happens | What to do |
|---|---|---|
| **It hides the image's files** | Mounting onto `/app` shows the host folder and hides whatever the image had at `/app`. | Mount only where you mean to replace. |
| **The host path must be absolute** | Relative paths are read as a volume *name* with `-v`. | Use `"$(pwd)/app"`. |
| **`-v` invents missing folders** | A typo creates an empty root-owned folder and the app starts with no data. | Prefer `--mount`, which errors. |
| **Permissions** | The container user (for example UID 10001) cannot read files owned by your host user. | Use `--user "$(id -u):$(id -g)"`, or fix ownership. |
| **Depends on the host** | The folder must exist on every machine that runs it. | Fine for dev, wrong for production data. |
| **Slower on Docker Desktop** | Files cross a VM boundary. | Keep dependencies (`node_modules`, `.venv`) in the image or a volume. |
| **Power over the host** | A read-write bind mount lets the container change real host files. | Use `readonly` unless you must write. Never mount `/` or the Docker socket casually. |

:::{important}
**Bind mount for development, volume for data.** A bind mount ties your container to a specific
folder layout on one machine. A volume does not, so it moves between machines far more easily and
works the same on Linux, macOS and Windows.
:::

## Part 4 · tmpfs (memory only)

### What it is

A **tmpfs mount** is a folder stored **in RAM**. Nothing is written to disk, and it is **emptied when
the container stops**. It exists on **Linux** hosts.

```bash
docker run -d --name t --tmpfs /scratch:rw,size=16m,mode=1777 alpine sleep 3600
docker exec t sh -c 'echo "token=abc123" > /scratch/token && df -h /scratch && cat /scratch/token'
docker stop t && docker start t
docker exec t ls -A /scratch                  # empty: tmpfs is wiped on stop
```

**Output:**

```text
Filesystem                Size      Used Available Use% Mounted on
tmpfs                    16.0M      4.0K     16.0M   0% /scratch
token=abc123
```

(The final `ls` prints nothing, because the folder is empty again.)

The long form is `--mount type=tmpfs,dst=/scratch,tmpfs-size=16777216`. Set a **size** so a
runaway process cannot use all the host's memory. tmpfs counts against memory, not disk.

### When to use it

- **Secrets and tokens** that should never reach the disk.
- **Scratch and temp files** (`/tmp`, `/run`) that are written very often and don't need to last.
- **A read-only container.** Run with `--read-only` (the root filesystem cannot be changed) and give
  the app a small tmpfs just where it needs to write. This is a strong hardening step, and a good
  partner to the non-root `USER` from [Chapter 8](08-image-optimization-lifecycle.md).

```bash
docker run -d --name hardened -p 8000:8000 \
  --read-only \
  --tmpfs /tmp:rw,size=32m \
  -v counter-data:/data \
  counter
```

Here the image is frozen, only `/tmp` (RAM) and `/data` (the volume) are writable, and everything
else is read-only. If someone breaks in, there is almost nowhere to leave anything behind.

## Choosing between the four

```{raw} html
:file: ../diagrams/ch09-decision.html
```

| | **Writable layer** | **Volume** | **Bind mount** | **tmpfs** |
|---|---|---|---|---|
| Lives in | the container | Docker-managed folder | any host folder | RAM |
| Survives `docker stop` | ✅ | ✅ | ✅ | ❌ |
| Survives `docker rm` | ❌ | ✅ | ✅ | ❌ |
| Shared between containers | ❌ | ✅ | ✅ | ❌ |
| You can edit it on the host | ❌ (awkward) | ⚠️ (via helper container) | ✅ | ❌ |
| Needs a host path | no | no | **yes** | no |
| Backup | not practical | tar via helper, or driver tools | normal host backups | not applicable |
| Speed for heavy writes | slower | good | depends on host | fastest |
| Typical use | caches, temp | **databases, uploads, state** | **dev code, config** | **secrets, scratch** |

## Putting it together in Compose

In real projects you declare all of this once in `compose.yaml`. The **top-level** `volumes:` block
creates and names the volume, and each service **mounts** it.

```yaml
services:
  web:
    build: .
    ports: ["8000:8000"]
    volumes:
      - counter-data:/data            # named volume: the data
      - ./app:/app:ro                 # bind mount: live code, read-only
    tmpfs:
      - /tmp                          # memory-only scratch
    read_only: true                   # everything else is frozen

volumes:
  counter-data:                       # created and named here
```

`docker compose up -d` makes the volume. `docker compose down` removes the containers but **keeps**
the volume. `docker compose down -v` removes both.

## The checklist: persistence done right

1. **Decide per path** what each writable folder is: data, code, secret or scratch.
2. **Data goes on a named volume.** Never leave it in the writable layer.
3. **Use named volumes**, not anonymous ones, and give them clear names (`pgdata`, not `3f9c…`).
4. **Bind mounts are for development.** Make them `readonly` unless the app must write.
5. **Create the folder in the image and `chown` it** to your non-root user, so new volumes get the right owner.
6. **Use tmpfs for secrets** and frequent temp writes, with a `size` limit.
7. **Consider `--read-only` plus tmpfs** to freeze the rest of the container.
8. **Back up volumes**, and **test a restore** at least once.
9. **Be careful with `prune -a` and `compose down -v`.** Both delete data.

## Common mistakes

- **"My data disappeared after I redeployed."** It was in the writable layer. Mount a volume at the
  path the app writes to.
- **Mounting at the wrong path.** The volume is fine, but the app writes to `/var/lib/app` and you
  mounted `/data`. Use `docker diff` to see where the app writes.
- **Anonymous volumes everywhere.** They pile up and nobody knows which holds what. Name them.
- **Bind-mounting over the app's own folder.** `-v $(pwd):/app` hides the image's `/app`, including
  installed dependencies if they live there. Check what the image had at that path.
- **`Permission denied` on a mounted folder.** The container user's UID does not own the folder.
  Fix the ownership, or set `--user`.
- **Relying on `-v` for a path that must exist.** A typo silently makes an empty root-owned folder.
  Use `--mount` so it fails loudly.
- **Treating a volume as a backup.** A volume is *storage*, not a backup. If the disk fails or
  someone runs `prune -a`, it is gone. Back it up elsewhere.
- **Putting a database's files in a bind mount on Docker Desktop.** It works, but is slow and can
  hit file-locking problems. Use a named volume.
- **Putting secrets in a volume or the image.** Use tmpfs, or your platform's secret mechanism.
- **Forgetting that tmpfs uses RAM.** An unlimited tmpfs can use memory the app needs. Set `size`.

## Try it yourself

1. Run `alpine` with `sh -c 'echo hi > /note.txt && sleep 3600'`, then `docker stop`, `docker start`,
   and read the file. Then `docker rm -f` it and start a new one. At which step did the file vanish?

   <details class="solution">
   <summary>Answer</summary>

   It survives `stop` and `start` (same container, same writable layer) and vanishes after `rm`,
   because the writable layer is deleted with the container.

   </details>

2. Create a volume `notes`. Write a file into it from one `alpine` container, then read it from a
   second one. Then run `docker volume inspect notes` and find the `Mountpoint`.

   <details class="solution">
   <summary>Answer</summary>

   `docker run --rm -v notes:/data alpine sh -c 'echo hi > /data/a'` then
   `docker run --rm -v notes:/data alpine cat /data/a` prints `hi`. The `Mountpoint` is under
   `/var/lib/docker/volumes/notes/_data` (inside the VM on Docker Desktop).

   </details>

3. Build the counter app and run it with and without `-v counter-data:/data`. Hit `/hit` twice,
   remove the container, start it again and hit once more. What does each version return?

   <details class="solution">
   <summary>Answer</summary>

   Without a volume it returns `{"hits":1}` (the count was in the deleted writable layer). With the
   volume it returns `{"hits":3}`.

   </details>

4. Start a container with `docker run -d --name w alpine sh -c 'mkdir /logs && echo x > /logs/a && sleep 3600'`
   and run `docker diff w`. Which paths would you move to a volume?

   <details class="solution">
   <summary>Answer</summary>

   `docker diff` shows `A /logs` and `A /logs/a`. If those logs matter, mount a volume at `/logs`.
   If they are only scratch, leave them or use tmpfs.

   </details>

5. Make a folder `site/` with an `index.html`. Serve it with `nginx:alpine` using a **read-only** bind
   mount, then edit the file and `curl` again. Then try to write into it from inside the container.
   What happens?

   <details class="solution">
   <summary>Answer</summary>

   The new content appears at once, with no restart. A write from inside, for example
   `docker exec web sh -c 'echo x > /usr/share/nginx/html/x'`, fails with
   `Read-only file system`, because of `readonly`.

   </details>

6. Run the same command twice, once with `-v /nonexistent/path:/data` and once with
   `--mount type=bind,src=/nonexistent/path,dst=/data`. How do they differ?

   <details class="solution">
   <summary>Answer</summary>

   `-v` silently creates an empty `/nonexistent/path` on the host and starts. `--mount` stops with an
   error saying the bind source path does not exist. That is why `--mount` is safer.

   </details>

7. Back up the `counter-data` volume to `counter-data.tgz`, delete the volume, create it again and restore the
   archive. Prove the counter continues where it left off.

   <details class="solution">
   <summary>Answer</summary>

   Use the `tar czf` helper command to back up, `docker volume rm counter-data` (after removing the
   containers that use it), `docker volume create counter-data`, then the `tar xzf` helper command to
   restore. The next `/hit` continues from the saved number.

   </details>

8. Start a container with `--read-only` and no tmpfs, and run the counter app. Then fix it.

   <details class="solution">
   <summary>Answer</summary>

   Writing to `/data` fails with `Read-only file system` unless a volume is mounted there. Add
   `-v counter-data:/data` (and `--tmpfs /tmp` if the server needs to write temp files). Mounts
   stay writable even when the root filesystem is read-only.

   </details>

## Clean up

```bash
docker rm -f scratch web t hardened c1 c2 a b 2>/dev/null
docker volume rm appdata counter-data counter-data-restored notes 2>/dev/null
docker volume prune          # removes leftover anonymous volumes
docker rmi counter
rm -f counter-data.tgz
```
