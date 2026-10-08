"""Diagrams for the Docker & Kubernetes Systems Engineering course.

Each function below writes one diagrams/<name>.html file: an inline SVG <figure> that pages include with

    ```{raw} html
    :file: ../diagrams/<name>.html
    ```

Colours come from the .dg / figure.diagram classes in the docs CSS (courses/builder.py), so diagrams follow
light and dark mode. Edit a function, then run:  python course_content/agentic-ai/diagrams/make_diagrams.py
"""
import html
from pathlib import Path

OUT = Path(__file__).resolve().parent
LINE = 20


class D:
    def __init__(self, name, w, h, title, caption):
        self.name, self.w, self.h, self.title, self.caption = name, w, h, title, caption
        self.els = []

    def box(self, x, y, w, h, lines, kind="box", tcls="", rx=10):
        self.els.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="{kind}"/>')
        if isinstance(lines, (str, tuple)):   # one line, optionally ("text", "class")
            lines = [lines]
        cy = y + h / 2 - (len(lines) - 1) * LINE / 2
        for i, ln in enumerate(lines):
            cls = tcls
            if isinstance(ln, tuple):
                ln, cls = ln
            self.text(x + w / 2, cy + i * LINE, ln, cls)

    def text(self, x, y, s, cls="", anchor="middle"):
        c = f' class="{cls}"' if cls else ""
        self.els.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" dominant-baseline="middle"{c}>'
                        f'{html.escape(str(s))}</text>')

    def arrow(self, pts, kind="", dashed=False, label=None, lx=None, ly=None, lcls="small", head=True):
        d = "M" + " L".join(f"{x},{y}" for x, y in pts)
        cls = "arrow" + (f" {kind}" if kind else "") + (" dashed" if dashed else "")
        mid = f"{self.name}-h{('-' + kind) if kind else ''}"
        m = f' marker-end="url(#{mid})"' if head else ""
        self.els.append(f'<path d="{d}" class="{cls}"{m}/>')
        if label:
            if lx is None:
                (x1, y1), (x2, y2) = pts[0], pts[-1]
                lx, ly = (x1 + x2) / 2, (y1 + y2) / 2 - 12
            self.text(lx, ly, label, lcls)

    def line(self, x1, y1, x2, y2, cls="line"):
        self.els.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="{cls}"/>')

    def rect(self, x, y, w, h, cls, rx=4):
        self.els.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="{cls}"/>')

    def circle(self, cx, cy, r, cls):
        self.els.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" class="{cls}"/>')

    def render(self):
        n = self.name
        markers = "".join(
            f'<marker id="{n}-h{("-" + k) if k else ""}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
            f'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="head{(" " + k) if k else ""}"/></marker>'
            for k in ("", "blue", "green", "red"))
        svg = (f'<figure class="diagram">\n<svg class="dg" viewBox="0 0 {self.w} {self.h}" role="img" '
               f'aria-labelledby="{n}-t {n}-d" xmlns="http://www.w3.org/2000/svg">\n'
               f'<title id="{n}-t">{html.escape(self.title)}</title>\n'
               f'<desc id="{n}-d">{html.escape(self.caption)}</desc>\n<defs>{markers}</defs>\n'
               + "\n".join(self.els) + "\n</svg>\n"
               f'<figcaption>{html.escape(self.caption)}</figcaption>\n</figure>\n')
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / f"{n}.html").write_text(svg, encoding="utf-8")
        return svg


ALL = []


def diagram(fn):
    ALL.append(fn)
    return fn




def timeline(d, x0, y, label, segs, scale, color):
    d.text(x0 - 12, y + 14, label, "", "end")
    for start, end, txt in segs:
        d.rect(x0 + start * scale, y, (end - start) * scale - 4, 28, color, rx=6)
        d.text(x0 + (start + end) / 2 * scale - 2, y + 14, txt, "small")


# ------------------------------------------------------------------ Session 1
@diagram
def s01_stack():
    d = D("s01-stack", 720, 300, "Bare metal vs virtual machines vs containers",
          "VMs each carry a full guest operating system. Containers share the host's kernel, so they are small and start in seconds.")
    cols = [("BARE METAL", 20), ("VIRTUAL MACHINES", 260), ("CONTAINERS", 500)]
    for name, x in cols:
        d.text(x + 100, 15, name, "title")
    d.box(20, 35, 200, 80, ["One app", ("(or a few, fighting", "small"), ("over libraries)", "small")], "blue")
    d.box(20, 125, 200, 50, "Operating system", "box")
    d.box(20, 185, 200, 50, ("Hardware", "bold"), "amber")
    for i in range(2):
        x = 260 + i * 102
        d.box(x, 35, 96, 34, ("App", "small"), "blue")
        d.box(x, 73, 96, 34, ("Libs", "small"), "box")
        d.box(x, 111, 96, 34, ("Guest OS", "small"), "red")
    d.box(260, 150, 198, 32, ("Hypervisor", "small"), "purple")
    d.box(260, 186, 198, 22, ("Host OS", "small"), "box")
    d.box(260, 212, 198, 23, ("Hardware", "small"), "amber")
    for i in range(3):
        x = 500 + i * 68
        d.box(x, 35, 64, 34, ("App", "small"), "blue")
        d.box(x, 73, 64, 34, ("Libs", "small"), "box")
    d.box(500, 111, 200, 34, ("Docker Engine", "small"), "green")
    d.box(500, 150, 200, 36, ("Host OS (shared kernel)", "small"), "box")
    d.box(500, 190, 200, 45, ("Hardware", "bold"), "amber")
    d.text(120, 265, "1 app per server", "small"); d.text(360, 265, "GBs each · boots in minutes", "small")
    d.text(600, 265, "MBs each · starts in seconds", "small")
    return d.render()


# ------------------------------------------------------------------ Session 2
@diagram
def s02_tree():
    d = D("s02-tree", 720, 250, "A process tree",
          "Every process has a parent (its PPID). PID 1 starts first and is the ancestor of everything else.")
    d.box(270, 15, 180, 44, ["PID 1", ("systemd", "code")], "amber")
    kids = [(60, "sshd", 312), (290, "nginx (master)", 640), (520, "dockerd", 980)]
    for x, name, pid in kids:
        d.arrow([(360, 59), (x + 70, 98)])
        d.box(x, 100, 140, 44, [f"PID {pid}", (name, "code")], "blue")
    d.arrow([(130, 144), (130, 183)]); d.box(60, 185, 140, 44, ["PID 1504", ("bash", "code")], "box")
    d.arrow([(360, 144), (360, 183)]); d.box(290, 185, 140, 44, ["PID 641", ("nginx (worker)", "code")], "box")
    d.arrow([(590, 144), (590, 183)]); d.box(520, 185, 140, 44, ["PID 2210", ("containerd", "code")], "box")
    return d.render()


@diagram
def s02_stop():
    d = D("s02-stop", 720, 200, "What docker stop does",
          "docker stop asks politely with SIGTERM, waits 10 seconds, then forces it with SIGKILL.")
    d.box(20, 70, 130, 50, ("docker stop", "code"), "blue")
    d.arrow([(150, 95), (198, 95)])
    d.box(200, 70, 150, 50, ["SIGTERM", ("\"please shut down\"", "small")], "amber")
    d.arrow([(350, 80), (420, 40)], kind="green")
    d.box(422, 15, 278, 50, ["App cleans up and exits", ("exit code 0 (or 143)", "small")], "green")
    d.arrow([(350, 110), (420, 150)], kind="red", label="ignored for 10 s", lx=360, ly=150)
    d.box(422, 125, 278, 50, ["SIGKILL: killed instantly", ("no cleanup · exit code 137", "small")], "red")
    return d.render()


# ------------------------------------------------------------------ Session 3
@diagram
def s03_namespaces():
    d = D("s03-namespaces", 720, 300, "Namespaces: what a container is allowed to see",
          "Namespaces give a process its own view of the system. Inside, your app is PID 1 with its own hostname, network and files; on the host it is just another process.")
    d.text(170, 15, "INSIDE THE CONTAINER", "title"); d.text(545, 15, "ON THE HOST", "title")
    d.rect(20, 30, 300, 255, "green", rx=14)
    rows = [("PID", "python app.py is PID 1"), ("UTS", "hostname: web-1"), ("NET", "own eth0, own IP 172.17.0.2"),
            ("MNT", "own / (the image's files)"), ("IPC", "own shared memory"), ("USER", "root here ≠ root on host")]
    for i, (ns, txt) in enumerate(rows):
        y = 42 + i * 40
        d.box(32, y, 60, 32, (ns, "bold"), "box")
        d.text(102, y + 16, txt, "small", "start")
    d.rect(380, 30, 320, 255, "box", rx=14)
    for i, (pid, cmd) in enumerate([(1, "systemd"), (980, "dockerd"), (2210, "containerd"), (4321, "python app.py ←")]):
        y = 50 + i * 48
        d.box(395, y, 290, 38, (f"PID {pid:<5} {cmd}", "code"), "blue" if pid == 4321 else "box")
    d.text(540, 250, "the same process, seen from outside", "small")
    d.arrow([(320, 66), (393, 213)], kind="green", dashed=True)
    return d.render()


# ------------------------------------------------------------------ Session 4
@diagram
def s04_cgroups():
    d = D("s04-cgroups", 720, 240, "cgroups: how much a container is allowed to use",
          "Namespaces limit what a container can see; cgroups limit how much CPU and memory it can use. Go over the memory limit and the kernel's OOM killer stops it.")
    d.box(20, 15, 200, 70, ["docker run", ("--memory=100m", "code"), ("--cpus=0.5", "code")], "blue")
    d.arrow([(220, 50), (268, 50)])
    d.box(270, 15, 180, 70, ["cgroup", ("memory.max = 100 MB", "code"), ("cpu.max = half a CPU", "code")], "purple")
    d.arrow([(450, 50), (498, 50)])
    d.box(500, 20, 200, 60, ["Container", ("its processes", "small")], "green")
    d.text(360, 115, "If the container tries to use more than 100 MB:", "small")
    d.box(110, 140, 160, 50, ["Kernel OOM killer", ("picks the process", "small")], "amber")
    d.arrow([(270, 165), (318, 165)], kind="red")
    d.box(320, 140, 140, 50, ("SIGKILL", "bold"), "red")
    d.arrow([(460, 165), (508, 165)], kind="red")
    d.box(510, 140, 190, 50, ["Exited (137)", ("OOMKilled = true", "code")], "red")
    return d.render()


# ------------------------------------------------------------------ Session 5
@diagram
def s05_runtime():
    d = D("s05-runtime", 720, 300, "Who actually runs a container",
          "Docker is a stack of programs. dockerd hands the job to containerd, which uses runc to create the container. Kubernetes talks to containerd directly through CRI.")
    d.text(130, 15, "DOCKER", "title"); d.text(590, 15, "KUBERNETES", "title")
    d.box(30, 30, 200, 40, ("docker CLI", "code"), "blue")
    d.arrow([(130, 70), (130, 93)], label="REST API", lx=180, ly=82)
    d.box(30, 95, 200, 40, ("dockerd", "code"), "blue")
    d.box(490, 30, 200, 40, ("kubelet", "code"), "purple")
    d.box(490, 95, 200, 40, ["CRI", ("(gRPC interface)", "small")], "purple")
    d.arrow([(590, 70), (590, 93)])
    d.box(250, 160, 220, 44, ["containerd", ("images · containers · snapshots", "small")], "green")
    d.arrow([(130, 135), (300, 158)], label="gRPC", lx=195, ly=140)
    d.arrow([(590, 135), (420, 158)])
    d.box(250, 225, 105, 44, ["shim", ("one per container", "small")], "box")
    d.box(365, 225, 105, 44, ["runc", ("OCI runtime", "small")], "amber")
    d.arrow([(330, 204), (310, 223)]); d.arrow([(390, 204), (410, 223)])
    d.text(600, 247, "runc sets up namespaces + cgroups,", "small")
    d.text(600, 265, "starts the process, then exits", "small")
    return d.render()


# ------------------------------------------------------------------ Session 6
@diagram
def s06_architecture():
    d = D("s06-architecture", 720, 250, "Docker client, daemon and registry",
          "You type commands in the client. The daemon does the work: it pulls images from a registry like Docker Hub and runs containers.")
    d.box(20, 30, 170, 150, ["Client", ("docker build", "code"), ("docker pull", "code"), ("docker run", "code")], "blue")
    d.arrow([(190, 105), (238, 105)], label="API", lx=214, ly=92)
    d.rect(240, 20, 260, 210, "green", rx=14)
    d.text(370, 38, "Docker host (dockerd)", "bold")
    d.box(255, 55, 110, 70, ["Images", ("nginx:alpine", "small"), ("python:3.12", "small")], "box")
    d.box(375, 55, 110, 70, ["Containers", ("web", "small"), ("db", "small")], "box")
    d.arrow([(365, 90), (373, 90)])
    d.text(370, 150, "an image is run as", "small"); d.text(370, 168, "one or more containers", "small")
    d.box(550, 55, 150, 110, ["Registry", ("Docker Hub", "small"), ("ghcr.io, ECR …", "small")], "purple")
    d.arrow([(548, 95), (487, 95)], label="pull", lx=518, ly=82)
    d.arrow([(487, 130), (548, 130)], label="push", lx=518, ly=145)
    return d.render()


@diagram
def s06_lifecycle():
    d = D("s06-lifecycle", 720, 210, "Container lifecycle",
          "A container moves between these states. Stopping keeps it (and its files); removing deletes it.")
    states = [(20, "Created", "docker create", "box"), (175, "Running", "docker start / run", "green"),
              (330, "Paused", "docker pause", "amber"), (485, "Stopped", "docker stop", "amber")]
    for x, name, cmd, k in states:
        d.box(x, 40, 135, 50, [(name, "bold"), (cmd, "small")], k)
    d.arrow([(155, 65), (173, 65)]); d.arrow([(310, 58), (328, 58)]); d.arrow([(328, 76), (310, 76)])
    d.arrow([(310, 85), (310, 120), (552, 120), (552, 92)])
    d.text(430, 133, "docker stop", "small")
    d.arrow([(552, 40), (552, 20), (242, 20), (242, 38)], kind="green")
    d.text(400, 12, "docker start (again)", "small")
    d.arrow([(620, 65), (640, 65), (640, 150), (612, 150)], kind="red")
    d.box(485, 135, 125, 40, ("Removed", "bold"), "red")
    d.text(668, 108, "docker rm", "small")
    return d.render()


# ------------------------------------------------------------------ Session 7
@diagram
def s07_layers():
    d = D("s07-layers", 720, 290, "Image layers and the container layer",
          "An image is a stack of read-only layers. Each container adds one thin writable layer on top. Images that share a base reuse the same layers on disk.")
    d.text(170, 15, "IMAGE A: my-flask-app", "title"); d.text(530, 15, "IMAGE B: my-api", "title")
    for x, top in ((40, "COPY app.py"), (420, "COPY main.py")):
        d.box(x, 35, 260, 34, ("container layer (writable)", "small"), "green")
        d.box(x, 79, 260, 32, (top, "code"), "blue")
        d.box(x, 115, 260, 32, ("RUN pip install …", "code"), "blue")
    d.rect(40, 165, 640, 32, "purple", rx=8); d.text(360, 181, "python:3.12-slim layers  (shared, stored once)", "code")
    d.rect(40, 205, 640, 32, "purple", rx=8); d.text(360, 221, "debian slim base layer  (shared, stored once)", "code")
    d.text(360, 262, "read-only layers are never changed; writes go to the container layer (copy-on-write)", "small")
    return d.render()


@diagram
def s07_id_digest():
    d = D("s07-id-digest", 720, 190, "Tags, image IDs and digests",
          "A tag is a movable name. A digest is a fingerprint of exact content and can never point to anything else.")
    d.box(20, 30, 200, 50, ["Tag", ("nginx:alpine", "code")], "amber")
    d.text(120, 100, "can move to a new image", "small"); d.text(120, 118, "next week", "small")
    d.arrow([(220, 55), (268, 55)])
    d.box(270, 30, 200, 50, ["Digest", ("sha256:df221d…", "code")], "green")
    d.text(370, 100, "hash of the manifest", "small"); d.text(370, 118, "pin this in production", "small")
    d.arrow([(470, 55), (518, 55)])
    d.box(520, 30, 180, 50, ["Image ID", ("sha256:bf8527…", "code")], "blue")
    d.text(610, 100, "hash of the image config", "small"); d.text(610, 118, "(local to your machine)", "small")
    d.text(360, 165, "docker pull nginx@sha256:df221d…  →  always the exact same bytes", "code")
    return d.render()


# ------------------------------------------------------------------ Session 8
@diagram
def s08_flow():
    d = D("s08-flow", 720, 200, "From Dockerfile to running container",
          "A Dockerfile is a recipe. docker build turns it into an image (a read-only template); docker run starts a container from that image.")
    steps = [("Dockerfile", "text recipe", "box"), ("docker build", "+ build context", "amber"),
             ("Image", "read-only", "blue"), ("docker run", "+ -e, -p, args", "amber"),
             ("Container", "PID 1 = your CMD", "green")]
    for i, (a, b, k) in enumerate(steps):
        x = 10 + i * 143
        d.box(x, 50, 128, 64, [(a, "bold"), (b, "small")], k)
        if i:
            d.arrow([(x - 15, 82), (x - 2, 82)])
    d.text(225, 140, "build time: FROM, RUN, COPY, ARG", "small")
    d.text(560, 140, "run time: CMD, ENTRYPOINT, ENV", "small")
    return d.render()


@diagram
def s08_cmd_entrypoint():
    d = D("s08-cmd-entrypoint", 720, 270, "What runs on docker run: CMD vs ENTRYPOINT",
          "CMD is a default that run arguments replace. ENTRYPOINT is fixed and run arguments are added after it.")
    d.box(260, 15, 200, 44, ("docker run img [args]", "code"), "blue")
    d.arrow([(360, 59), (360, 83)])
    d.box(270, 85, 180, 44, "ENTRYPOINT set?", "amber")
    d.arrow([(270, 107), (190, 107), (190, 150)], label="no", lx=225, ly=95)
    d.arrow([(450, 107), (530, 107), (530, 150)], label="yes", lx=490, ly=95)
    d.box(20, 152, 340, 64, ["Run your args if given,", "otherwise the CMD", ("CMD [\"python\", \"app.py\"]", "code")], "box")
    d.box(380, 152, 320, 64, ["Run ENTRYPOINT + args", "(no args: ENTRYPOINT + CMD)", ("ENTRYPOINT [\"echo\", \"Hello\"]", "code")], "green")
    d.text(190, 240, "docker run img bash  →  runs bash", "code")
    d.text(540, 240, "docker run img Docker  →  Hello Docker", "code")
    return d.render()


# ------------------------------------------------------------------ Session 9
@diagram
def s09_cache():
    d = D("s09-cache", 720, 270, "Layer caching: why order matters",
          "When a layer changes, it and every layer after it is rebuilt. Copy the files that change rarely (requirements) before the ones that change often (your code).")
    d.text(180, 15, "BAD ORDER  (you edited app.py)", "title"); d.text(540, 15, "GOOD ORDER  (you edited app.py)", "title")
    bad = [("FROM python:3.12-slim", True), ("WORKDIR /app", True), ("COPY . .", False),
           ("RUN pip install …", False), ("CMD [\"python\", \"app.py\"]", False)]
    good = [("FROM python:3.12-slim", True), ("WORKDIR /app", True), ("COPY requirements.txt .", True),
            ("RUN pip install …", True), ("COPY . .", False), ("CMD [\"python\", \"app.py\"]", False)]
    for col, rows in ((10, bad), (370, good)):
        for i, (txt, cached) in enumerate(rows):
            d.box(col, 30 + i * 36, 340, 30, (f"{txt}  [{'CACHED' if cached else 'REBUILT'}]", "code"), "green" if cached else "red")
    d.text(180, 230, "pip reinstalls everything: slow", "small"); d.text(540, 248, "pip layer reused: about a second", "small")
    return d.render()


@diagram
def s09_signals():
    d = D("s09-signals", 720, 260, "Exec form vs shell form on docker stop",
          "Measured: exec form with a SIGTERM handler stopped in 0.1 s; shell form waited the full 10 s and was killed (exit 137).")
    d.box(220, 15, 280, 40, ("docker stop → SIGTERM to PID 1", "small"), "blue")
    d.arrow([(330, 55), (190, 85)]); d.arrow([(390, 55), (530, 85)])
    d.box(20, 87, 340, 56, ["Exec form", ("CMD [\"python\", \"app.py\"]", "code")], "green")
    d.box(380, 87, 320, 56, ["Shell form", ("CMD python app.py", "code")], "red")
    d.box(20, 160, 340, 64, ["PID 1 = python", "handler runs · exits in 0.1 s", ("exit code 0", "code")], "green")
    d.box(380, 160, 320, 64, ["PID 1 = /bin/sh -c …", "SIGTERM not passed on · 10 s wait", ("SIGKILL · exit code 137", "code")], "red")
    d.arrow([(190, 143), (190, 158)], kind="green"); d.arrow([(540, 143), (540, 158)], kind="red")
    d.text(360, 246, "No signal handler in your app? Run with  docker run --init  (also stops in 0.1 s)", "small")
    return d.render()


@diagram
def s09_context():
    d = D("s09-context", 720, 200, "The build context and .dockerignore",
          "The dot in docker build . is the build context: that folder is sent to the builder. .dockerignore keeps junk and secrets out of it.")
    d.box(20, 20, 220, 100, ["your project folder", ("app.py", "code"), ("requirements.txt", "code"), ("Dockerfile", "code")], "blue")
    d.box(20, 130, 220, 48, ["ignored:", (".venv/  .git/  .env", "code")], "red")
    d.box(280, 70, 160, 60, [".dockerignore", ("filters the context", "small")], "amber")
    d.arrow([(240, 100), (278, 100)])
    d.arrow([(440, 100), (478, 100)], label="sent to builder", lx=470, ly=85)
    d.box(480, 25, 220, 150, ["Builder", ("small, fast context", "small"), ("no secrets in layers", "small"), ("COPY only sees this", "small")], "green")
    return d.render()


# ------------------------------------------------------------------ Bind mounts & permissions (EP 3)
@diagram
def bind_mount_uid():
    d = D("bind-mount-uid", 720, 250, "A bind mount shares one folder, and file owners are just numbers",
          "Both sides see the same folder. A file made by root (UID 0) in the container is owned by root on the host too; --user makes it yours.")
    d.rect(20, 20, 300, 200, "blue", rx=14); d.text(170, 40, "Your laptop (host)", "bold")
    d.box(40, 60, 260, 46, ["~/project/html", ("you are UID 1000", "small")], "box")
    d.box(40, 120, 260, 40, ("from-container.txt  owner 0 (root)", "small"), "red")
    d.box(40, 168, 260, 40, ("as-me.txt  owner 1000 (you)", "small"), "green")
    d.rect(400, 20, 300, 200, "green", rx=14); d.text(550, 40, "Container", "bold")
    d.box(420, 60, 260, 46, ["/usr/share/nginx/html", ("runs as root (UID 0) by default", "small")], "box")
    d.box(420, 120, 260, 40, ("touch from-container.txt", "code"), "box")
    d.box(420, 168, 260, 40, ("--user 1000:1000 touch as-me", "code"), "box")
    d.arrow([(302, 83), (418, 83)], "blue", label="-v", lx=360, ly=70)
    d.arrow([(418, 83), (302, 83)], "blue", head=True)
    d.text(360, 102, "same folder", "small")
    return d.render()


# ------------------------------------------------------------------ IP addressing (EP 5)
@diagram
def net_ip_address():
    d = D("net-ip-address", 720, 260, "An IPv4 address and its subnet",
          "An IPv4 address is 4 numbers (0–255), 32 bits in total. The /24 says the first 24 bits name the network and the rest name the host.")
    octets = ["192", "168", "1", "10"]
    for i, o in enumerate(octets):
        x = 60 + i * 155
        d.box(x, 30, 130, 50, (o, "bold"), "green" if i < 3 else "amber")
        d.text(x + 65, 98, f"{int(o):08b}", "code")
        if i < 3:
            d.text(x + 142, 55, ".", "bold")
    d.line(60, 120, 500, 120, "line"); d.text(280, 138, "network part (24 bits): 192.168.1", "small")
    d.line(525, 120, 655, 120, "line"); d.text(590, 138, "host part (8 bits)", "small")
    d.box(60, 165, 290, 72, ["192.168.1.0/24", ("mask 255.255.255.0", "small"), ("256 addresses, 254 usable", "small")], "blue")
    d.box(370, 165, 290, 72, ["172.17.0.0/16", ("mask 255.255.0.0", "small"), ("Docker's default bridge: 65,536", "small")], "purple")
    return d.render()


@diagram
def net_public_private():
    d = D("net-public-private", 720, 240, "Private addresses inside, one public address outside",
          "Devices at home or in Docker get private addresses. The router (or Docker's NAT) swaps them for a public address on the way out.")
    d.rect(20, 20, 380, 200, "green", rx=14); d.text(210, 40, "Private network 192.168.1.0/24", "bold")
    for i, (n, ip) in enumerate([("Laptop", "192.168.1.10"), ("Phone", "192.168.1.11"), ("TV", "192.168.1.12")]):
        d.box(40, 60 + i * 52, 160, 44, [n, (ip, "code")], "box")
        d.arrow([(200, 82 + i * 52), (268, 130)])
    d.box(270, 95, 110, 70, ["Router", ("NAT", "small")], "amber")
    d.arrow([(380, 130), (468, 130)], label="public IP", lx=424, ly=116)
    d.box(470, 85, 230, 90, ["Internet", ("sees only 49.204.x.x", "small"), ("(one public address)", "small")], "purple")
    return d.render()


# ------------------------------------------------------------------ Docker networking (EP 6)
@diagram
def net_bridge():
    d = D("net-bridge", 720, 290, "The default bridge network and port publishing",
          "Each container gets its own eth0 joined to the docker0 bridge by a veth pair. -p 8080:80 adds a NAT rule from the host's port 8080 to the container's port 80.")
    d.rect(20, 20, 680, 250, "box", rx=14); d.text(360, 40, "Docker host", "bold")
    d.box(40, 60, 170, 56, ["Host eth0", ("192.168.1.10", "code")], "blue")
    d.box(40, 140, 170, 70, ["NAT rule (iptables)", ("host:8080 →", "code"), ("172.17.0.2:80", "code")], "amber")
    d.arrow([(125, 116), (125, 138)])
    d.box(270, 120, 180, 56, ["docker0 bridge", ("172.17.0.1", "code")], "green")
    d.arrow([(210, 175), (268, 150)])
    for i, (n, ip) in enumerate([("web (nginx)", "172.17.0.2"), ("db", "172.17.0.3")]):
        y = 70 + i * 110
        d.box(520, y, 160, 60, [n, ("eth0 " + ip, "code")], "purple")
        d.arrow([(450, 148), (518, y + 30)], label="veth" if i == 0 else None, lx=478, ly=y + 40)
    d.text(125, 245, "curl localhost:8080 → web:80", "small")
    return d.render()


@diagram
def net_modes():
    d = D("net-modes", 720, 230, "bridge vs host vs none",
          "bridge: own IP behind NAT (the default). host: shares the host's network directly, no isolation. none: only loopback, no network at all.")
    cols = [("bridge (default)", "green", ["own namespace + IP", "reach it with -p", "user-defined: DNS", "by container name"]),
            ("host", "amber", ["shares host network", "no -p needed", "no port isolation", "Linux only"]),
            ("none", "red", ["only loopback (lo)", "no outside access", "batch jobs,", "max isolation"])]
    for i, (name, kind, lines) in enumerate(cols):
        x = 20 + i * 235
        d.box(x, 20, 210, 46, (name, "bold"), kind)
        d.box(x, 76, 210, 130, [(l, "small") for l in lines], "box")
    return d.render()


if __name__ == "__main__":
    for fn in ALL:
        fn()
    print(len(ALL), "diagrams written to", OUT)
