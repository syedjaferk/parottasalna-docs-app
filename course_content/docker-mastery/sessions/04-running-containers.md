# Session 4 · Running your first containers

## The big idea

`docker run` is the command you will type most. It creates a container from an image and runs a
command in it. The container lives **exactly as long as its main process**: when that command finishes,
the container stops. That one rule explains most beginner surprises.

**Everyday example:** a taxi booked for a single trip. It comes, drives where you asked, and the
booking ends when the ride ends. A container is booked for one command; when the command is done, it is done.
(If you want a "taxi on standby", run a command that keeps going, like a web server.)

```{raw} html
:file: ../diagrams/run-lifecycle.html
```

## Run, look around, run more

```{literalinclude} ../code/04-run.sh
:language: bash
```

```{literalinclude} ../code/04-run.out
:language: text
```

What happened:

- **`--rm`** deleted the container as soon as it exited, so nothing was left to clean up.
- **A private world.** Inside, `hostname` is a random id and `ps` shows only one process (PID 1),
  not your host's hundreds. Containers have their own process list.
- **Main process = lifetime.** The `sh -c '... sleep 1 ...'` ran for a second, then the container
  showed `Exited (0)`. Exit code 0 means success.
- **`docker exec`** runs an extra command in a container that is *already running*. We started one with
  `sleep 30`, then ran another shell command inside it.
- Both `hostname` values differ because those are two different containers.

## Interactive mode

For a shell you can type into, add `-it`: `docker run -it alpine sh`. `-i` keeps input open and `-t` gives a
terminal. Type `exit` to leave; the container stops because its main process (the shell) ended.

## Reading `docker ps`

`docker ps` lists **running** containers; `docker ps -a` also lists the stopped ones. The columns you
will use most are `NAMES` (the handle you type in other commands), `IMAGE` (what it was made from) and
`STATUS` (`Up 5 minutes`, or `Exited (0) 2 minutes ago`). If you do not give `--name`, Docker invents a
funny name like `quirky_hopper`. Naming containers yourself makes commands readable, and you'll do that
properly in the next session.

## Common mistakes

- **Expecting a container to stay up.** `docker run alpine` exits immediately because the default
  command has nothing to do. Give it a long-running command or a server.
- **Forgetting `-it` for a shell.** Without it `sh` sees no input and exits at once.
- **Typing `exec` on a stopped container.** `docker exec` needs a running container. Use `docker run` or `docker start` first.
- **Never cleaning up.** Each `docker run` without `--rm` leaves a stopped container. Check `docker ps -a`.
- **Reading exit codes wrongly.** `0` is success, anything else is an error (`137` means it was killed).

## Hands-on exercises

**Exercise 1.** Run a container that prints today's date and then disappears.

<details class="solution"><summary>Solution</summary>

```bash
docker run --rm alpine date
```

It prints the date (in UTC) and leaves nothing behind, since `--rm` removed it.

</details>

**Exercise 2.** Start an Alpine container that sleeps for 60 seconds in the background, run `cat /etc/alpine-release`
inside it, then remove it.

<details class="solution"><summary>Solution</summary>

```bash
docker run -d --name nap alpine sleep 60
docker exec nap cat /etc/alpine-release
docker rm -f nap
```

On this machine the version printed was `3.24.1` (yours may differ). `rm -f` stops and removes in one step.

</details>

**Exercise 3.** Run a container whose command fails and read its exit code.

<details class="solution"><summary>Solution</summary>

```bash
docker run --name bad alpine sh -c 'exit 3'
docker ps -a --filter name=bad --format '{{.Status}}'
docker rm bad
```

The status shows `Exited (3)`: the container's exit code is the command's exit code.

</details>

## Practice

Take the **Session 4 quiz**. The original BusyBox "Hello, World" adventure is in the reference section.
