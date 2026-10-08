# Session 7 · Image Mechanics

## The big idea

An image is not one big file. It's a **stack of read-only layers**, each layer holding the files
that one build step added or changed. When a container starts, Docker puts one thin
**writable layer** on top. Because layers are read-only and identified by their content, many
images and containers can **share** them, which saves disk space and download time.

**Everyday example:** transparent sheets on an overhead projector. Each sheet adds a bit to the
picture. You can't change the sheets underneath, but you can draw on a fresh sheet on top. Ten
people can share the same bottom sheets and each draw on their own top sheet.

```{raw} html
:file: ../diagrams/s07-layers.html
```

## Layers and the writable layer

```bash
docker pull nginx:alpine
docker image inspect nginx:alpine --format '{{len .RootFS.Layers}} layers'
docker history nginx:alpine
```

- Each `RUN`, `COPY` or `ADD` in a Dockerfile creates a new layer (Session 8).
- When a container changes a file from a lower layer, the file is first **copied up** into the
  container's writable layer, then changed there. This is **copy-on-write**.
- Deleting the container deletes its writable layer. The image is untouched.

See what a container changed:

```bash
docker run -d --name cow nginx:alpine
docker exec cow sh -c 'echo hi > /tmp/new.txt'
docker diff cow
```

**Output (shortened):**

```text
C /tmp
A /tmp/new.txt
```

`A` = added, `C` = changed, `D` = deleted. Remove it with `docker rm -f cow`.

## Storage drivers: overlay2

The **storage driver** is the code that stacks the layers into one folder. On modern Linux it's
**overlay2**:

```bash
docker info --format '{{.Driver}}'      # overlay2
```

overlay2 uses the kernel's OverlayFS: the read-only image layers are the **lower** directories, the
container's writable layer is the **upper** directory, and the container sees the **merged** view.

## Image ID vs digest

```{raw} html
:file: ../diagrams/s07-id-digest.html
```

| | Image ID | Digest |
|---|---|---|
| **What it's a hash of** | the image's **config** (its settings and list of layers) | the image's **manifest** in a registry |
| **Where you see it** | `docker images`, `docker image inspect` | `docker images --digests`, after a pull or push |
| **Used for** | referring to an image on your machine | pulling **exactly** the same image anywhere |

```bash
docker image inspect alpine:3.20 --format 'Id: {{.Id}}'
docker images --digests alpine
```

**Output (shortened):**

```text
Id: sha256:bf8527…
REPOSITORY   TAG    DIGEST              IMAGE ID
alpine       3.20   sha256:d9e853…      bf8527…
```

Both are SHA-256 hashes of the content. Change one byte and the hash changes completely.

## Tags move; digests never do

A **tag** like `alpine:3.20` is just a label. The publisher can point it at a new image tomorrow
(say, with a security fix). A **digest** always means the exact same bytes:

```bash
docker pull nginx@sha256:df221d…     # always this exact image (use the full digest)
```

:::{tip}
In production, pin images by digest (or at least by a specific tag like `3.20`, never `latest`),
so the image you tested is exactly the image you run.
:::

## Images are immutable

Once built, an image **never changes**. "Updating" an image really means building a **new** image
(new layers, new ID) and moving the tag to it. The old image still exists until you delete it.
That's why rollbacks are easy: just run the previous image again.

Clean up old images:

```bash
docker image ls -f dangling=true    # untagged leftovers from rebuilds
docker image prune                  # remove them
docker system df                    # how much disk images, containers and volumes use
```

## Try it yourself

1. Pull `python:3.12-slim` and `python:3.12-alpine`. Compare their sizes with `docker images python`.
2. Start a container, create a file in it, and check `docker diff`. Then start a **second**
   container from the same image. Is the file there?

   <details class="solution">
   <summary>Answer</summary>

   No. Each container has its own writable layer; the image underneath is shared and unchanged.

   </details>

3. Find the digest of `nginx:alpine` on your machine, then run nginx using that digest instead of
   the tag.

   <details class="solution">
   <summary>Answer</summary>

   ```bash
   docker images --digests nginx
   docker run --rm -d --name pinned nginx@sha256:<the digest you saw>
   docker rm -f pinned
   ```

   </details>
