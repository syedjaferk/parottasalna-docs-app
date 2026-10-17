"""Diagrams for the Docker Mastery course. Run:  python course_content/docker-mastery/diagrams/make_diagrams.py"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "docs"))
from diagram_kit import D  # noqa: E402


def new(name, w, h, title, caption):
    return D(name, w, h, title, caption, HERE)


def vm_vs_container():
    d = new("vm-vs-container", 760, 300, "Virtual machines versus containers",
            "Each virtual machine carries its own operating system. Containers share the host's kernel, so they are smaller and start faster.")
    d.box(20, 15, 340, 34, ("Virtual machines", "bold"), "amber")
    d.box(20, 60, 100, 60, [("App A", "bold"), ("+ libs", "small")], "blue")
    d.box(130, 60, 100, 60, [("App B", "bold"), ("+ libs", "small")], "blue")
    d.box(240, 60, 100, 60, [("App C", "bold"), ("+ libs", "small")], "blue")
    for i, x in enumerate((20, 130, 240)):
        d.box(x, 126, 100, 34, ("Guest OS", "small"), "red")
    d.box(20, 166, 320, 34, ("Hypervisor", "bold"), "box")
    d.box(20, 206, 320, 34, ("Host OS + hardware", "bold"), "ghost")
    d.box(400, 15, 340, 34, ("Containers", "bold"), "green")
    for i, x in enumerate((400, 510, 620)):
        d.box(x, 60, 100, 60, [("App " + "ABC"[i], "bold"), ("+ libs", "small")], "blue")
    d.box(400, 126, 320, 34, ("Docker Engine", "bold"), "green")
    d.box(400, 166, 320, 34, ("Host OS (one shared kernel)", "bold"), "box")
    d.box(400, 206, 320, 34, ("Hardware", "bold"), "ghost")
    d.text(190, 275, "heavy: gigabytes, minutes to boot", "small")
    d.text(560, 275, "light: megabytes, about a second to start", "small")
    return d.render()


def architecture():
    d = new("docker-architecture", 760, 270, "Docker client, daemon and registry",
            "The docker command is only a client. It sends requests to the daemon, and the daemon pulls images from a registry and runs containers.")
    d.box(20, 90, 150, 80, [("docker CLI", "bold"), ("the client", "small")], "blue")
    d.box(280, 60, 200, 140, [("Docker daemon", "bold"), ("dockerd", "code"), ("images · containers", "small"), ("networks · volumes", "small")], "amber")
    d.box(590, 90, 150, 80, [("Registry", "bold"), ("Docker Hub", "small")], "green")
    d.arrow([(172, 130), (278, 130)], kind="blue", label="docker run", lx=225, ly=112)
    d.arrow([(482, 130), (588, 130)], kind="green", label="pull / push", lx=535, ly=112)
    d.text(380, 235, "client and daemon talk over /var/run/docker.sock (or the network)", "small")
    return d.render()


def image_container():
    d = new("image-container", 760, 270, "One image, many containers",
            "An image is a read-only template. Each container made from it gets its own writable layer, and changes there never touch the image.")
    d.box(20, 90, 200, 90, [("Image", "bold"), ("alpine (read-only)", "code")], "green")
    for i, y in enumerate((20, 100, 180)):
        d.box(400, y, 200, 60, [(f"Container dm-{'abc'[i]}", "bold"), ("writable layer", "small")], "blue")
        d.arrow([(222, 135), (398, y + 30)], kind="blue")
    d.text(620, 130, "docker run", "code", anchor="start")
    d.text(380, 255, "delete the container and its writable layer goes too", "small")
    return d.render()


def run_lifecycle():
    d = new("run-lifecycle", 760, 230, "Life of a container",
            "docker run creates and starts a container. It runs as long as its main process runs. Stopped containers stay until you remove them.")
    items = [("created", "docker create", "box"), ("running", "docker start / run", "green"), ("stopped", "main process exits", "amber"), ("removed", "docker rm", "red")]
    for i, (a, b, k) in enumerate(items):
        x = 20 + i * 185
        d.box(x, 50, 150, 70, [(a, "bold"), (b, "small")], k)
        if i:
            d.arrow([(x - 33, 85), (x - 2, 85)], kind="blue")
    d.text(380, 175, "docker run = create + start (+ attach).  --rm removes it as soon as it stops.", "small")
    return d.render()


def port_map():
    d = new("port-map", 760, 230, "Publishing a port",
            "-p 8088:80 sends traffic arriving at port 8088 on your machine to port 80 inside the container.")
    d.box(20, 70, 160, 80, [("Browser / curl", "bold"), ("localhost:8088", "code")], "blue")
    d.box(280, 50, 460, 120, [("Host", "bold")], "ghost")
    d.box(320, 90, 130, 60, [("host port", "small"), ("8088", "code")], "amber")
    d.box(540, 90, 160, 60, [("container", "small"), ("nginx on 80", "code")], "green")
    d.arrow([(182, 110), (318, 120)], kind="blue")
    d.arrow([(452, 120), (538, 120)], kind="green", label="-p 8088:80", lx=495, ly=102)
    return d.render()


def dockerfile_layers():
    d = new("dockerfile-layers", 760, 290, "A Dockerfile builds an image layer by layer",
            "Each instruction adds a layer. Unchanged layers are reused from the cache, so put things that change often at the bottom.")
    rows = [("FROM python:3.12-slim", "base image", "green"), ("WORKDIR /app", "set folder", "box"), ("COPY app.py .", "your code", "amber"),
            ("ENV GREETING=Hello", "settings", "box"), ("CMD [\"python\", \"app.py\"]", "start command", "blue")]
    for i, (a, b, k) in enumerate(rows):
        y = 15 + i * 52
        d.box(20, y, 360, 44, (a, "code"), k)
        d.text(400, y + 22, b, "small", anchor="start")
    d.box(520, 15, 220, 240, [("Image", "bold"), ("layers stacked", "small"), ("read-only", "small")], "ghost")
    d.text(380, 275, "change app.py: COPY and every line after it rebuilds; FROM and WORKDIR stay cached", "small")
    return d.render()


def volumes():
    d = new("volumes", 760, 260, "Where data lives",
            "Data in a container's writable layer disappears with the container. A named volume or a bind mount lives outside it.")
    d.box(20, 20, 330, 190, [("Without a volume", "bold")], "red")
    d.box(50, 70, 270, 50, ("container + its data", "code"), "box")
    d.text(185, 150, "docker rm  →  data gone", "small")
    d.box(410, 20, 330, 190, [("With a volume", "bold")], "green")
    d.box(430, 70, 130, 50, ("container", "code"), "box")
    d.box(590, 70, 130, 50, ("volume dm-data", "code"), "amber")
    d.arrow([(562, 95), (588, 95)], kind="green")
    d.text(575, 150, "docker rm  →  volume stays", "small")
    d.text(575, 175, "next container mounts it again", "small")
    return d.render()


def course_flow():
    d = new("course-flow", 760, 200, "From a Dockerfile to a running container",
            "You write a Dockerfile, build an image, optionally push it to a registry, and run containers from it.")
    items = [("Dockerfile", "recipe", "box"), ("Image", "docker build", "green"), ("Registry", "docker push / pull", "amber"), ("Container", "docker run", "blue")]
    for i, (a, b, k) in enumerate(items):
        x = 20 + i * 185
        d.box(x, 60, 150, 70, [(a, "bold"), (b, "small")], k)
        if i:
            d.arrow([(x - 33, 95), (x - 2, 95)], kind="blue")
    return d.render()


if __name__ == "__main__":
    fns = [vm_vs_container, architecture, image_container, run_lifecycle, port_map, dockerfile_layers, volumes, course_flow]
    for fn in fns:
        fn()
    print(len(fns), "diagrams written")
