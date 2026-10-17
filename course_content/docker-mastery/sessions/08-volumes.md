# Session 8 · Volumes: keeping data safe

## The big idea

Everything a container writes goes into its own writable layer, and **that layer is deleted with the
container**. For a database, uploads or logs that is a disaster. A **volume** is a folder managed by Docker
that lives *outside* any one container. Mount it into a container and the data survives restarts,
removals and upgrades. A **bind mount** is the simpler cousin: it shows an ordinary folder from your
computer inside the container.

**Everyday example:** a hotel room and a locker. Everything you leave loose in the room is cleared
when you check out (the container is removed). Valuables kept in the hotel's locker (a volume) are
still there for your next stay, and any room can be given the locker key.

```{raw} html
:file: ../diagrams/volumes.html
```

## Losing data, then keeping it

```{literalinclude} ../code/08-volumes.sh
:language: bash
```

```{literalinclude} ../code/08-volumes.out
:language: text
```

Step by step:

1. **Without a volume**, the file written by the first container was gone for the next one. That is the
   problem.
2. **`docker volume create dm-data`** made a named volume. `-v dm-data:/data` mounts it at `/data`
   inside a container. The note written there was read back by a *different* container.
3. **Sharing:** a second container appended `note 2` to the same file, and the next container saw both lines.
   One volume can be used by several containers (be careful with two writers at once).
4. **`docker volume ls`** lists it with the `local` driver, meaning it lives on this machine.
5. **Bind mount:** `-v /tmp/dm-bind:/mnt` showed the host file `hello.txt` inside the container. Edit it on
   the host and the container sees the change straight away. This is perfect for development.

## Volume or bind mount?

| | Named volume | Bind mount |
|---|---|---|
| You name | A volume (`dm-data`) | A host path (`/tmp/dm-bind`) |
| Managed by | Docker | You |
| Best for | Databases, app data in production | Source code while developing, config files |
| Portable between machines | Yes (via Docker) | No, depends on the host path |

The pattern for databases is exactly this: for MySQL or PostgreSQL, mount a volume at the data folder
(`-v pgdata:/var/lib/postgresql/data`). The container can then be upgraded or recreated and the data stays.

## Common mistakes

- **Relying on the container's own disk for important data.** Anything not on a volume is temporary.
- **Mixing the two syntaxes.** `-v dm-data:/data` (no slash at the start) is a named volume;
  `-v /tmp/dm-bind:/mnt` (a path) is a bind mount. A typo in the name silently creates a new, empty volume.
- **Deleting a volume by accident.** `docker volume rm` and `docker volume prune` delete data for good.
  `docker rm -v` removes anonymous volumes attached to a container.
- **Permission errors on bind mounts.** The container's user must be allowed to write to the host folder.
- **Backing up never.** A volume is not a backup. Copy it out regularly (for example by tar-ing it from a throwaway container).

## Hands-on exercises

**Exercise 1.** Create a volume `dm-notes`, write `hello` to a file in it from one container, and read it from another.

<details class="solution"><summary>Solution</summary>

```bash
docker volume create dm-notes
docker run --rm -v dm-notes:/n alpine sh -c 'echo hello > /n/a.txt'
docker run --rm -v dm-notes:/n alpine cat /n/a.txt
docker volume rm dm-notes
```

The second command prints `hello`.

</details>

**Exercise 2.** Show that a container sees live changes to a bind-mounted file.

<details class="solution"><summary>Solution</summary>

```bash
mkdir -p /tmp/dm-live && echo one > /tmp/dm-live/f.txt
docker run -d --name dm-live -v /tmp/dm-live:/mnt alpine sleep 30
docker exec dm-live cat /mnt/f.txt
echo two > /tmp/dm-live/f.txt
docker exec dm-live cat /mnt/f.txt
docker rm -f dm-live; rm -rf /tmp/dm-live
```

First `one`, then `two`, without restarting the container.

</details>

**Exercise 3.** Run PostgreSQL with a volume so its data survives deleting the container. Which folder do you mount?

<details class="solution"><summary>Solution</summary>

```bash
docker run -d --name pg -e POSTGRES_PASSWORD=secret -v pgdata:/var/lib/postgresql/data postgres:17-alpine
```

`/var/lib/postgresql/data` is where PostgreSQL keeps its files. Remove the container, start a new one with the same `-v pgdata:...`, and your
databases are still there.

</details>

## Practice

Take the **Session 8 quiz**. The original volumes guide and the MySQL volume task are in the reference section.
