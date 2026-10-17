# Session 3 · Images, containers and registries

## The big idea

An **image** is a read-only template: files plus the instructions to start a program. A **container**
is a running (or stopped) instance made from an image. You can start many containers from one image,
and each gets its own private, writable layer.

**Everyday example:** a bakery. The **recipe and dough** is the image: you can't eat it, and it never
changes. The **cookies** you bake are containers. Bake ten cookies from one recipe; eating or breaking
one doesn't change the recipe or the other cookies. The **registry** is the recipe shop where
bakeries buy and share recipes.

```{raw} html
:file: ../diagrams/image-container.html
```

## One image, several containers

```{literalinclude} ../code/03-images.sh
:language: bash
```

```{literalinclude} ../code/03-images.out
:language: text
```

What to take from it:

- `docker create` makes two containers (`dm-a`, `dm-b`) from the *same* image. They are `Created`, not running.
- `docker start -a` runs each one and shows its output.
- A file written in one container (`/note.txt`) is **gone in a brand-new container** from the same image.
  Changes belong to the container's writable layer, not the image.
- `docker history` lists the layers: a tiny Alpine root filesystem (7.81MB) plus a start command
  (`CMD ["/bin/sh"]`, 0 bytes). Images are stacks of layers, and identical layers are shared between images.

## Where images come from

Images reach your machine in two ways. You **pull** one that someone else published (`docker pull
nginx:alpine`), or you **build** your own from a Dockerfile (Session 7). Either way it is stored locally
as layers. When you `docker run` a name you don't have, Docker pulls it for you first. That is why the
first run of a new image is slow and the second is instant.

A tag such as `3.20` or `alpine` is just a label pointing at one image. The same image can have several
tags, and a tag can later be moved to a newer image. If you need something exact, you can name an image by
its digest (`alpine@sha256:...`), which never changes.

## Useful commands for this session

| Command | What it does |
|---|---|
| `docker pull nginx:alpine` | Download an image from the registry |
| `docker images` | List local images |
| `docker ps` / `docker ps -a` | Running containers / all containers |
| `docker rm NAME` | Delete a container |
| `docker rmi IMAGE` | Delete an image (no container may use it) |
| `docker history IMAGE` | Show an image's layers |

## Common mistakes

- **Mixing up image and container.** Deleting a container does not delete the image, and an image
  can't "run"; you run a container made from it.
- **Saving data inside a container.** It disappears with the container (Session 8 fixes this).
- **Piling up stopped containers.** `docker ps -a` shows them all. Use `--rm` for throwaway runs, or
  `docker container prune` to clear stopped ones.
- **Trying to remove an image that a container still uses.** Remove the container first.
- **Thinking `docker pull` updates running containers.** It only fetches the new image. Recreate the
  container to use it.

## Hands-on exercises

**Exercise 1.** Create two containers from `alpine` that each print their own name, run both, and
remove them.

<details class="solution"><summary>Solution</summary>

```bash
docker create --name one alpine echo "I am one"
docker create --name two alpine echo "I am two"
docker start -a one
docker start -a two
docker rm one two
```

Each `start -a` prints that container's line. The image is shared; the containers are separate.

</details>

**Exercise 2.** Prove that a file created in one container is not visible in another.

<details class="solution"><summary>Solution</summary>

```bash
docker run --name first alpine sh -c 'echo hi > /x.txt'
docker run --rm alpine cat /x.txt
docker rm first
```

The second command fails with `cat: can't open '/x.txt': No such file or directory`.

</details>

**Exercise 3.** How many layers does `alpine:3.20` have, and which one is the largest?

<details class="solution"><summary>Solution</summary>

```bash
docker history alpine:3.20 --format '{{.CreatedBy}}  {{.Size}}'
```

On this machine it shows two entries: the `CMD` line (0B) and the root filesystem `ADD` (7.81MB), which is
the largest.

</details>

## Practice

Take the **Session 3 quiz**. The original bakery story is in the reference section.
