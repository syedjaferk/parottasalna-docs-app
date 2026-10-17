# Session 5 · Background containers, names, logs and inspect

## The big idea

Real services (web servers, databases) must keep running while you do other things. Run them **detached**
with `-d`, give them a **name**, and then use `docker logs` to read what they print, `docker inspect` to
see their settings, and `docker stop` / `docker rm` to end them. These four commands are your day-to-day
toolkit.

**Everyday example:** a CCTV camera at a shop. It runs in the background all day; you don't stand and
watch it. When something happens you play back the **recording** (logs), check the camera's **settings
page** (inspect), and switch it **off** (stop) when closing. You also label each camera ("Entrance",
"Cash counter") so you know which is which.

```{raw} html
:file: ../diagrams/run-lifecycle.html
```

## The commands in action

```{literalinclude} ../code/05-detached.sh
:language: bash
```

```{literalinclude} ../code/05-detached.out
:language: text
```

Reading the output:

- **`-d`** printed nothing but the container id (we hid it) and gave the terminal back. `docker ps`
  shows it `Up`.
- **`docker logs`** replays everything the main process wrote to standard output: ticks 1 to 5. Add `-f` to
  follow live and `--tail 20` for the last lines only.
- **`docker inspect --format`** pulls single facts from the long JSON: state, image, command. Without
  `--format` you get the full document (networks, mounts, environment).
- **Exit code 137** after `docker stop`: Docker first asks the process to stop (SIGTERM), waits 10 seconds,
  then kills it (SIGKILL = 128 + 9 = 137). Our `sleep` did not react to SIGTERM, so it was killed. A well-behaved
  server exits with 0 straight away.
- **Unique names.** Starting a second container called `dm-ticker` is refused until the first is removed
  or renamed.

## Naming and cleaning

| Task | Command |
|---|---|
| Start in the background, named | `docker run -d --name web nginx:alpine` |
| Follow the log live | `docker logs -f web` |
| Stop politely | `docker stop web` |
| Stop and delete in one go | `docker rm -f web` |
| Delete all stopped containers | `docker container prune` |
| Rename | `docker rename web web-old` |

## Common mistakes

- **Running a server without `-d`.** It blocks your terminal (Ctrl+C stops it).
- **A detached container that exits at once.** Check `docker logs NAME` first: the error is almost always
  printed there.
- **Reusing a name.** Remove the old container (`docker rm NAME`) or choose a new name.
- **Reading old logs after a rebuild.** Logs belong to a container; a new container starts with a clean log.
- **Using `docker kill` as the normal way to stop.** It skips graceful shutdown. Use `docker stop` and
  fix programs that ignore it.

## Hands-on exercises

**Exercise 1.** Start `alpine` in the background so that it prints "ping" every second, forever, then show
only the last 3 lines of its log.

<details class="solution"><summary>Solution</summary>

```bash
docker run -d --name pinger alpine sh -c 'while true; do echo ping; sleep 1; done'
sleep 4
docker logs --tail 3 pinger
docker rm -f pinger
```

The last three log lines are each `ping`.

</details>

**Exercise 2.** Use `docker inspect` to print only the image name of a running container.

<details class="solution"><summary>Solution</summary>

```bash
docker run -d --name nap alpine sleep 30
docker inspect --format '{{.Config.Image}}' nap
docker rm -f nap
```

It prints `alpine`.

</details>

**Exercise 3.** Why does `docker stop` take about 10 seconds on `sleep 60` but is instant for most web
servers?

<details class="solution"><summary>Solution</summary>

`docker stop` sends SIGTERM and waits up to 10 seconds before SIGKILL. As PID 1 in a container, `sleep`
ignores SIGTERM unless it has a handler, so Docker has to wait out the timeout. Servers that handle
SIGTERM shut down at once.

</details>

## Practice

Take the **Session 5 quiz**. The original page *Diving Deeper with Detached Mode, Naming and Inspections* is in
the reference section.
