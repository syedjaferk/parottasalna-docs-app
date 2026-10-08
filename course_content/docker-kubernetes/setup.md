# Setup

Let's get Docker running on your machine. You'll do this **once**; it takes about 15 minutes.

## What you need

| You have | Install | Notes |
|---|---|---|
| **Linux** (Ubuntu, Debian, Fedora…) | Docker Engine | Best choice: every lab works, including the Linux internals sessions. |
| **Windows** | Docker Desktop with **WSL 2** | Also install Ubuntu from the Microsoft Store for the Linux labs. |
| **macOS** | Docker Desktop | For the Linux internals labs (Sessions 2–5), use a Linux VM such as [Multipass](https://multipass.run). |

:::{note}
Containers are a **Linux** feature. On Windows and macOS, Docker Desktop quietly runs a small
Linux virtual machine for you. That's why commands like `unshare` (Session 3) need a real Linux shell.
:::

## Step 1 · Install Docker

**Linux (Ubuntu/Debian):** the official convenience script installs Docker Engine and its plugins:

```bash
curl -fsSL https://get.docker.com | sh
```

Then let your user run Docker without `sudo` (log out and back in afterwards):

```bash
sudo usermod -aG docker $USER
```

**Windows / macOS:** download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop/),
install it, and start it. On Windows, make sure **"Use WSL 2 based engine"** is ticked in its settings.

## Step 2 · Check it works

```bash
docker version
```

You should see both a **Client** and a **Server** section. If the Server part shows an error, the
Docker daemon isn't running (start Docker Desktop, or run `sudo systemctl start docker` on Linux).

Now run your first container:

```bash
docker run hello-world
```

**Output (shortened):**

```text
Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
...
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

🎉 Docker downloaded an image, created a container from it, ran it, and printed this message.
[Session 6](sessions/06-docker-architecture-cli.md) explains every step of what just happened.

## Step 3 · Handy tools

- **A code editor**: VS Code with the "Docker" extension shows your images and containers.
- **curl**: to test web apps in containers (`curl localhost:8080`). It's preinstalled on most systems.

## Common problems

:::{warning}
- **`permission denied while trying to connect to the Docker daemon socket`**: your user isn't in
  the `docker` group yet. Run the `usermod` command above, then **log out and back in**.
- **`Cannot connect to the Docker daemon`**: Docker isn't running. Start Docker Desktop, or
  `sudo systemctl start docker`.
- **`port is already allocated`**: another program is using that port. Pick another one, e.g.
  `-p 8081:80` instead of `-p 8080:80`.
:::
