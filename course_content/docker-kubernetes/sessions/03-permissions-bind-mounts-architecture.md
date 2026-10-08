# Chapter 3 · File Permissions, Bind Mounts & Docker Architecture

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/MGzjSuXvBg4"
  title="Episode 3: File permissions, bind mounts and Docker architecture" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 **Episode 3** of the [Kube Engineering playlist](https://www.youtube.com/playlist?list=PLMtFsmo8jrN8) (Tamil) · [watch on YouTube](https://www.youtube.com/watch?v=MGzjSuXvBg4)

## The big idea

This chapter connects the Linux basics from [Chapter 2](02-linux-prerequisites.md) to real Docker
behaviour:

1. **File permissions** decide who may read or change a file, and they still apply when a
   container touches your files.
2. **Bind mounts** let a container use a folder from your laptop.
3. **Docker's architecture** explains what actually happens when you type a `docker` command.

**Everyday example:** a shared office cupboard. The cupboard (a bind mount) can be opened from
two rooms, your desk and the container's desk. The lock on each file (permissions) decides who may
open it, and the lock only checks your **employee number**, not your name.

## 1. File permissions

```bash
ls -l app.py
# -rw-r--r-- 1 jafer jafer 412 Oct  4 09:12 app.py
```

| Part | Meaning |
|---|---|
| `-` | type: `-` file, `d` directory, `l` link |
| `rw-` | the **owner** (jafer) can read and write |
| `r--` | the **group** (jafer) can read |
| `r--` | **everyone else** can read |

Each permission is a number: **r = 4, w = 2, x = 1**. Add them up per group of three:

| Number | Letters | Typical use |
|---|---|---|
| `755` | `rwxr-xr-x` | scripts and folders everyone may use |
| `644` | `rw-r--r--` | normal files |
| `640` | `rw-r-----` | config files only your group may read |
| `600` | `rw-------` | private keys and secrets |

```bash
chmod +x script.sh        # make a script executable
chmod 640 secret.txt      # owner rw, group r, others nothing
chown jafer:dev app.py    # change owner and group (needs sudo)
id                        # your user ID (UID), group ID (GID) and groups
```

:::{important}
**Linux stores owners as numbers, not names.** `ls -l` shows `jafer` only because `/etc/passwd`
says UID 1000 = jafer. Use `ls -ln` to see the raw numbers. Inside a container, `/etc/passwd`
is different, so the same file can show a different name. The **number** is what counts.
:::

The `root` user (**UID 0**) can do almost anything. By default, processes in a container **run
as root**.

## 2. Bind mounts

A **bind mount** makes one folder appear at a second place: the same folder, not a copy. You can
try it in plain Linux first:

```bash
mkdir -p ~/binds/src ~/binds/dest
echo "hello from src" > ~/binds/src/note.txt
sudo mount --bind ~/binds/src ~/binds/dest
cat ~/binds/dest/note.txt          # hello from src   ← same file, second place
echo "edited" > ~/binds/dest/note.txt
cat ~/binds/src/note.txt           # edited           ← it really is the same folder
sudo umount ~/binds/dest
```

Docker does exactly this with `-v host-folder:container-folder`:

```bash
docker run -d --name web -p 8080:80 -v "$PWD/html:/usr/share/nginx/html:ro" nginx:alpine
```

- Edit `html/index.html` on your laptop → nginx serves the new version straight away. No rebuild.
- `:ro` = **read-only** inside the container. The container can't change or delete your files.
- The host path must be **absolute** (`$PWD/html`, not `html`).

### Permissions meet bind mounts

```{raw} html
:file: ../diagrams/bind-mount-uid.html
```

What happens when the container creates a file in your folder?

```bash
mkdir -p data
docker run --rm -v "$PWD/data:/data" alpine touch /data/from-container.txt
ls -ln data
```

**Output:**

```text
-rw-r--r-- 1 0 0 0 Oct  8 20:22 from-container.txt
```

Owner **0** = root. The container ran as root, so the file on your laptop belongs to root, and you
can't edit or delete it without `sudo`. Fix: run the container as **your** UID and GID:

```bash
docker run --rm --user "$(id -u):$(id -g)" -v "$PWD/data:/data" alpine touch /data/as-me.txt
ls -ln data
```

**Output:**

```text
-rw-r--r-- 1 1000 1000 0 Oct  8 20:22 as-me.txt
-rw-r--r-- 1    0    0 0 Oct  8 20:22 from-container.txt
```

And with `:ro` the container can't write at all:

```bash
docker run --rm -v "$PWD/data:/data:ro" alpine touch /data/x
# touch: /data/x: Read-only file system
```

## 3. Docker architecture

```{raw} html
:file: ../diagrams/s06-architecture.html
```

Docker is a **client–server** system:

| Part | What it is | Example |
|---|---|---|
| **Docker client** | the `docker` command you type | `docker run nginx` |
| **Docker daemon** (`dockerd`) | the background service that does the work: images, containers, networks, volumes | `systemctl status docker` |
| **Docker Engine** | the daemon + its API + the CLI, installed together | `docker version` |
| **Registry** | a store for images | Docker Hub, GitHub Container Registry, AWS ECR |

```bash
docker version     # shows a "Client" section and a "Server" (Engine) section
```

### How the parts talk to each other

1. You type `docker run nginx:alpine`.
2. The **client** sends an API request to the daemon through the socket file
   **`/var/run/docker.sock`**.
3. The **daemon** checks for the image. If it's missing, it **pulls** it from the registry.
4. The daemon asks **containerd** to create the container, and containerd uses **runc** to set
   up the isolation and start the process.

```{raw} html
:file: ../diagrams/s05-runtime.html
```

The full chain (containerd, runc, shims and the OCI standards) is explained in
[Under the hood · Container runtimes](../deep-dives/container-runtimes.md).

:::{warning}
Access to `/var/run/docker.sock` is the same as **root access** to the machine: anyone who can
talk to the daemon can start a container that bind-mounts your whole disk. Only add trusted users
to the `docker` group (`sudo usermod -aG docker $USER`, then log out and in).
:::

## Common mistakes

- **"Permission denied" deleting files a container created**: they're owned by root (UID 0).
  Use `--user "$(id -u):$(id -g)"` next time; for now, `sudo rm`.
- **A relative path in `-v`** (`-v html:/data`) creates a **named volume** called `html`
  instead of mounting your folder. Use `$PWD/html`.
- **`permission denied ... /var/run/docker.sock`**: your user isn't in the `docker` group.

## Try it yourself

1. What number is `rwxr-x---`? Who can do what?

   <details class="solution">
   <summary>Answer</summary>

   `750`. Owner: read, write, execute. Group: read and execute. Others: nothing.

   </details>

2. Run nginx with your own `html` folder bind-mounted read-only, change the page, and `curl` it
   again without restarting the container.
3. Create a file through a container with and without `--user "$(id -u):$(id -g)"`, then
   compare `ls -ln`. Can you delete both without `sudo`?

   <details class="solution">
   <summary>Answer</summary>

   Only the one created with `--user`. The other belongs to UID 0 (root).

   </details>

4. Run `docker version` and find the client version, the server (Engine) version and the
   containerd version.
