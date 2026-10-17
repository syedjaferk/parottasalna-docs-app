# Session 6 · Port mapping and a real web server

## The big idea

A container has its own network, so a server listening on port 80 *inside* a container is invisible
from your computer unless you **publish** the port. `-p HOST:CONTAINER` connects a port on your machine to
a port in the container. Without it the service runs but nobody outside can reach it.

**Everyday example:** an office building with a reception desk. The meeting room (the container) is inside; visitors
can't walk straight in. Reception (the host) has a phone extension, 8088, that is forwarded to the
meeting room's line, 80. Dial the extension and you are connected. No forwarding, no calls.

```{raw} html
:file: ../diagrams/port-map.html
```

## nginx, reached from the host

```{literalinclude} ../code/06-ports.sh
:language: bash
```

```{literalinclude} ../code/06-ports.out
:language: text
```

What the output tells you:

- **`-p 8088:80`**: `docker port` confirms `80/tcp -> 0.0.0.0:8088` (and the same on IPv6). Anything that
  reaches port 8088 on this machine goes to nginx's port 80.
- **`curl` got HTTP 200 and the nginx welcome page title.** The container is serving real HTTP.
- **The access log recorded both requests.** The client address `172.17.0.1` is the host's side of
  Docker's private network. `docker logs` is how you debug a server.
- **A container started without `-p`** has no published ports (`docker port` prints nothing), so the host
  cannot reach it. It can still talk to other containers on the same Docker network.

## Choosing ports

- The left number must be **free** on the host. If 8088 is taken, Docker refuses to start.
- Use `-p 127.0.0.1:8088:80` to allow only your own machine, and not other computers on your network.
- `-P` (capital) publishes every port the image declares to random free host ports; `docker port NAME` shows which.
- Two containers can both listen on 80 *inside*; they just need different host ports (8088, 8089).

## Common mistakes

- **Swapping the numbers.** It is `HOST:CONTAINER`. `-p 80:8088` would try to take host port 80.
- **Starting a service that listens on `127.0.0.1` inside the container.** Publishing needs the app to
  listen on `0.0.0.0`, or the forwarded traffic never reaches it.
- **Forgetting that `EXPOSE` in a Dockerfile only documents a port.** It does not publish it; `-p` does.
- **Port already in use.** `bind: address already in use` means something on the host owns that port. Pick another.
- **Opening a database port to the world** with `-p 5432:5432`. Bind to localhost or keep it private.

## Hands-on exercises

**Exercise 1.** Run nginx on host port 9000 and fetch the page with `curl`.

<details class="solution"><summary>Solution</summary>

```bash
docker run -d --name web9000 -p 9000:80 nginx:alpine
sleep 2
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:9000/
docker rm -f web9000
```

It prints `200`.

</details>

**Exercise 2.** Run two nginx containers at once, on host ports 9001 and 9002. How many processes listen on port 80 *inside*?

<details class="solution"><summary>Solution</summary>

```bash
docker run -d --name web1 -p 9001:80 nginx:alpine
docker run -d --name web2 -p 9002:80 nginx:alpine
docker port web1; docker port web2
docker rm -f web1 web2
```

Each container has its own network, so each nginx listens on its own port 80. The host ports 9001 and 9002 are the only things that must differ.

</details>

**Exercise 3.** Make nginx reachable only from your own machine.

<details class="solution"><summary>Solution</summary>

```bash
docker run -d --name local -p 127.0.0.1:9003:80 nginx:alpine
docker port local
docker rm -f local
```

`docker port` shows `80/tcp -> 127.0.0.1:9003`, so only `localhost` can connect.

</details>

## Practice

Take the **Session 6 quiz**. The original Tomcat page is in the reference section.
