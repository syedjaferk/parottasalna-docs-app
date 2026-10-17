"""Diagrams for the System Design course.

Each function writes one diagrams/<name>.html file (an inline SVG figure) that chapters include with

    ```{raw} html
    :file: ../diagrams/<name>.html
    ```

Colours come from the .dg classes in the docs CSS, so diagrams follow light and dark mode.
Edit a function, then run:  python course_content/system-design/diagrams/make_diagrams.py
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "docs"))
from diagram_kit import D as _Kit  # noqa: E402

REGISTRY = []


def diagram(fn):
    REGISTRY.append(fn)
    return fn


def new(name, w, h, title, caption):
    return _Kit(name, w, h, title, caption, out=HERE)


def row(d, items, x, y, w, h, gap, kinds=None, arrows=True, akind=""):
    """Boxes left to right with arrows between. Returns list of (x, y, w, h)."""
    out = []
    for i, label in enumerate(items):
        bx = x + i * (w + gap)
        d.box(bx, y, w, h, label, (kinds[i] if kinds else "box"))
        out.append((bx, y, w, h))
        if arrows and i:
            d.arrow([(bx - gap, y + h / 2), (bx, y + h / 2)], kind=akind)
    return out


# ---------------------------------------------------------------- core concepts
@diagram
def availability():
    d = new("availability", 760, 250, "Availability over a year",
            "Availability is the share of time the system works. Each extra nine allows ten times less downtime.")
    d.text(380, 24, "Downtime allowed per year", "title")
    rows = [("99%", "3.65 days", 300), ("99.9%", "8.8 hours", 120), ("99.99%", "53 minutes", 30), ("99.999%", "5 minutes", 4)]
    for i, (a, t, wd) in enumerate(rows):
        y = 50 + i * 44
        d.text(70, y + 14, a, "bold", anchor="end")
        d.rect(90, y, wd * 1.8, 28, "bar" + (" amber" if i == 0 else (" green" if i > 1 else "")), rx=5)
        d.text(100 + wd * 1.8, y + 14, t, "small", anchor="start")
    d.text(380, 232, "Each added nine is roughly 10x harder and more expensive.", "small")
    d.render()


@diagram
def reliability():
    d = new("reliability", 760, 250, "Available is not the same as reliable",
            "A system can be up but wrong. Reliability means correct results, durable data and recovery from faults.")
    d.box(40, 40, 320, 80, [("Available but unreliable", "bold"), ("answers, but loses writes or returns wrong data", "small")], "amber")
    d.box(400, 40, 320, 80, [("Reliable but unavailable", "bold"), ("always correct, but down for maintenance", "small")], "blue")
    d.box(220, 150, 320, 70, [("Both: the goal", "bold"), ("up, correct, durable, self-healing", "small")], "green")
    d.arrow([(200, 120), (330, 150)])
    d.arrow([(560, 120), (430, 150)])
    d.render()


@diagram
def spof():
    d = new("spof", 780, 270, "Hunting single points of failure",
            "Red boxes are single points of failure: if any one dies, users lose the service. Green layers are duplicated.")
    d.box(10, 110, 90, 50, "Users", "blue")
    d.box(150, 110, 120, 50, ["Load", "balancer"], "red")
    d.box(330, 40, 110, 44, "App 1", "green"); d.box(330, 110, 110, 44, "App 2", "green"); d.box(330, 180, 110, 44, "App 3", "green")
    d.box(520, 110, 120, 50, "Database", "red")
    d.box(670, 110, 100, 50, "DNS", "red")
    d.arrow([(100, 135), (150, 135)])
    for y in (62, 132, 202):
        d.arrow([(270, 135), (330, y)])
        d.arrow([(440, y), (520, 135)])
    d.text(210, 190, "SPOF", "bold"); d.text(580, 190, "SPOF", "bold"); d.text(720, 190, "SPOF", "bold")
    d.text(390, 250, "Fix: pair the balancer, add replicas to the database, use two DNS providers.", "small")
    d.render()


@diagram
def failover():
    d = new("failover", 780, 270, "Failover: detect, decide, redirect",
            "The standby takes over the floating IP when the primary stops sending heartbeats.")
    d.box(20, 100, 90, 50, "Clients", "blue")
    d.box(180, 100, 130, 50, ["Floating IP", "10.0.0.100"], "purple")
    d.box(430, 40, 160, 50, ["Primary", "(serving)"], "red")
    d.box(430, 170, 160, 50, ["Standby", "(replicating)"], "amber")
    d.arrow([(110, 125), (180, 125)])
    d.arrow([(310, 115), (430, 65)], label="normal", lx=345, ly=78)
    d.arrow([(310, 140), (430, 195)], dashed=True, label="after failover", lx=345, ly=190)
    d.arrow([(510, 90), (510, 170)], dashed=True, label="replicate + heartbeat", lx=630, ly=130)
    d.text(390, 255, "Detect (3 missed heartbeats), decide (promote the standby), redirect (move the IP).", "small")
    d.render()


@diagram
def fault_tolerance():
    d = new("fault-tolerance", 780, 250, "Fault tolerance keeps users unaware",
            "A fault in one copy is masked by the others, so the user sees a normal answer.")
    d.box(20, 95, 90, 50, "Request", "blue")
    d.box(180, 95, 120, 50, ["Voter /", "balancer"], "purple")
    d.box(380, 30, 120, 44, "Replica A", "green"); d.box(380, 100, 120, 44, "Replica B", "red"); d.box(380, 170, 120, 44, "Replica C", "green")
    d.box(580, 95, 170, 50, ["Correct answer", "(2 of 3 agree)"], "green")
    d.arrow([(110, 120), (180, 120)])
    for y in (52, 122, 192):
        d.arrow([(300, 120), (380, y)])
    d.arrow([(500, 52), (580, 110)]); d.arrow([(500, 192), (580, 130)])
    d.arrow([(500, 122), (580, 120)], dashed=True)
    d.text(440, 236, "Replica B is faulty; the user never notices.", "small")
    d.render()


@diagram
def scaling_journey():
    d = new("scaling-journey", 800, 300, "The scaling journey",
            "Add one idea at a time, in order, only when the numbers demand it.")
    steps = [("1", "One server", "app + DB"), ("2", "Split DB", "own machine"), ("3", "Load balancer", "stateless apps"),
             ("4", "Cache", "Redis"), ("5", "Read replicas", "copies"), ("6", "CDN", "static files"),
             ("7", "Queue", "slow work"), ("8", "Shard", "split data")]
    for i, (n, t, s) in enumerate(steps):
        x = 20 + (i % 4) * 190
        y = 30 + (i // 4) * 130
        d.box(x, y, 170, 80, [(f"{n}. {t}", "bold"), (s, "small")], ["box", "blue", "blue", "amber", "amber", "green", "green", "red"][i])
        if i % 4:
            d.arrow([(x - 20, y + 40), (x, y + 40)])
    d.arrow([(675, 110), (675, 135), (105, 135), (105, 160)], dashed=True)
    d.text(400, 270, "Never jump to step 8: shard only when one primary cannot take the writes or hold the data.", "small")
    d.render()


@diagram
def latency_throughput_bandwidth():
    d = new("latency-throughput-bandwidth", 780, 260, "A pipe: width, length and flow",
            "Bandwidth is the width, latency is the time one drop takes, throughput is what actually arrives per second.")
    d.rect(60, 80, 520, 70, "ghost", rx=35)
    d.text(320, 52, "Bandwidth = pipe width (max capacity)", "bold")
    for i in range(7):
        d.circle(100 + i * 70, 115, 12, "circle-a")
    d.arrow([(60, 175), (580, 175)], kind="blue", label="Latency = time for one drop to travel the length", lx=320, ly=195)
    d.box(610, 70, 150, 90, [("Throughput", "bold"), ("drops arriving", "small"), ("per second", "small")], "green")
    d.text(390, 238, "Little's law: in flight = throughput x latency", "small")
    d.render()


@diagram
def hash_ring():
    d = new("hash-ring", 780, 360, "The consistent hashing ring",
            "Servers and keys sit on a ring. A key belongs to the first server clockwise from it.")
    cx, cy, r = 280, 175, 120
    d.circle(cx, cy, r, "ghost")
    servers = {"A": 20, "B": 110, "C": 200, "D": 290}
    def pt(deg, rr=r):
        a = math.radians(deg - 90)
        return cx + rr * math.cos(a), cy + rr * math.sin(a)
    for name, deg in servers.items():
        x, y = pt(deg)
        d.box(x - 22, y - 16, 44, 32, (f"S{name}", "bold"), "blue")
    for label, deg in (("k1", 50), ("k2", 160), ("k3", 250), ("k4", 330)):
        x, y = pt(deg)
        d.box(x - 14, y - 11, 28, 22, (label, "small"), "amber", rx=11)
    d.text(280, 175, "ring 0 .. 2^32", "small")
    d.box(480, 50, 270, 60, [("Lookup", "bold"), ("hash(key), then go clockwise", "small"), ("to the next server", "small")], "box")
    d.box(480, 130, 270, 70, [("Add server E", "bold"), ("takes keys only from its", "small"), ("neighbour; others unmoved", "small")], "green")
    d.box(480, 220, 270, 70, [("Virtual nodes", "bold"), ("each server owns many", "small"), ("small slices: even load", "small")], "purple")
    d.render()


@diagram
def cap_theorem():
    d = new("cap-theorem", 780, 290, "CAP during a network partition",
            "When the link between nodes is cut you must choose: refuse requests (consistent) or answer with possibly old data (available).")
    d.text(390, 24, "Withdraw 500 at A. Then read the balance at B.", "title")
    d.box(60, 70, 200, 70, [("Node A", "bold"), ("balance = 500", "small")], "blue")
    d.box(520, 70, 200, 70, [("Node B", "bold"), ("balance = 1000 (stale)", "small")], "blue")
    d.line(260, 105, 520, 105, "line cut")
    d.text(390, 88, "partition", "bold")
    d.box(60, 190, 290, 70, [("CP choice", "bold"), ("B refuses: consistent, not available", "small")], "red")
    d.box(430, 190, 290, 70, [("AP choice", "bold"), ("B answers 1000: available, inconsistent", "small")], "amber")
    d.arrow([(160, 140), (160, 190)], dashed=True)
    d.arrow([(620, 140), (620, 190)], dashed=True)
    d.render()


# ---------------------------------------------------------------- networking
@diagram
def osi_layers():
    d = new("osi-layers", 780, 330, "The seven OSI layers",
            "Each layer wraps the data from the layer above with its own header on the way down, and unwraps it on the way up.")
    layers = [("7  Application", "HTTP, DNS, SMTP", "blue"), ("6  Presentation", "TLS, JSON, gzip", "blue"), ("5  Session", "sessions, RPC", "blue"),
              ("4  Transport", "TCP, UDP: ports", "green"), ("3  Network", "IP: addresses, routing", "amber"),
              ("2  Data link", "Ethernet, Wi-Fi: MAC", "red"), ("1  Physical", "cable, fibre, radio", "red")]
    for i, (a, b, k) in enumerate(layers):
        y = 20 + i * 42
        d.box(40, y, 250, 36, (a, "bold"), k)
        d.text(310, y + 18, b, "small", anchor="start")
    d.box(560, 20, 190, 36, "Your program", "box")
    d.box(560, 62 + 3 * 42 - 42 + 42, 190, 36, "TCP header + data", "green")
    d.box(560, 62 + 4 * 42 - 42 + 42, 190, 36, "IP header + TCP + data", "amber")
    d.box(560, 62 + 5 * 42 - 42 + 42, 190, 36, "Ethernet frame (all of it)", "red")
    d.arrow([(655, 56), (655, 146)], label="wrap", lx=690, ly=100)
    d.render()


@diagram
def ip_addresses():
    d = new("ip-addresses", 780, 250, "Anatomy of an IPv4 address",
            "In 10.0.1.77/24 the first 24 bits name the network and the last 8 bits name the host.")
    octets = ["10", "0", "1", "77"]
    for i, o in enumerate(octets):
        d.box(60 + i * 120, 60, 100, 50, (o, "bold"), "blue" if i < 3 else "green")
        if i < 3:
            d.text(170 + i * 120, 85, ".", "bold")
    d.text(30, 85, "IP", "small")
    d.rect(60, 128, 340, 8, "bar"); d.rect(420, 128, 100, 8, "bar green")
    d.text(230, 152, "network: first 24 bits (/24)", "small"); d.text(470, 152, "host: 8 bits", "small")
    d.box(560, 50, 190, 80, [("/24 = 256 addresses", "bold"), ("/16 = 65,536", "small"), ("/28 = 16", "small")], "box")
    d.box(60, 185, 320, 45, "Private: 10.x, 172.16-31.x, 192.168.x", "amber")
    d.box(400, 185, 350, 45, "Router: longest matching prefix wins", "purple")
    d.render()


@diagram
def tcp_vs_udp():
    d = new("tcp-vs-udp", 780, 330, "TCP handshake and acknowledgements vs UDP datagrams",
            "TCP sets up a connection and retransmits lost data. UDP sends datagrams and forgets them.")
    d.text(200, 22, "TCP", "title"); d.text(590, 22, "UDP", "title")
    d.line(100, 40, 100, 310); d.line(300, 40, 300, 310)
    d.text(100, 34, "Client", "small"); d.text(300, 34, "Server", "small")
    d.arrow([(100, 70), (300, 90)], kind="blue", label="SYN", lx=200, ly=68)
    d.arrow([(300, 110), (100, 130)], kind="green", label="SYN-ACK", lx=200, ly=108)
    d.arrow([(100, 150), (300, 170)], kind="blue", label="ACK", lx=200, ly=148)
    d.arrow([(100, 195), (300, 215)], label="data #1", lx=200, ly=193)
    d.arrow([(300, 235), (100, 255)], kind="green", label="ack #1", lx=200, ly=233)
    d.arrow([(100, 275), (200, 285)], kind="red", label="data #2 lost: resend", lx=150, ly=300, head=True)
    d.line(490, 40, 490, 310); d.line(690, 40, 690, 310)
    d.text(490, 34, "Sender", "small"); d.text(690, 34, "Receiver", "small")
    d.arrow([(490, 90), (690, 110)], label="datagram 1", lx=590, ly=88)
    d.arrow([(490, 150), (690, 170)], label="datagram 2", lx=590, ly=148)
    d.arrow([(490, 210), (600, 222)], kind="red", label="datagram 3 lost: nobody resends", lx=590, ly=240)
    d.text(590, 290, "No handshake. No acks. No order.", "small")
    d.render()


@diagram
def checksums():
    d = new("checksums", 800, 250, "A checksum detects corruption",
            "The receiver recomputes the checksum. If it differs from the one sent, the data was damaged in transit.")
    d.box(20, 90, 140, 60, [("Data", "bold"), ("transfer 5000", "small")], "blue")
    d.box(190, 90, 110, 60, ["checksum", "= 0x9A3F"], "purple")
    d.arrow([(160, 120), (190, 120)])
    d.arrow([(300, 120), (470, 120)], label="send data + checksum", lx=385, ly=100)
    d.box(470, 90, 140, 60, [("Data", "bold"), ("transfer 9000", "small")], "red")
    d.box(660, 90, 120, 60, ["recomputed", "= 0x41C2"], "purple")
    d.arrow([(610, 120), (660, 120)])
    d.text(540, 70, "one digit flipped on the wire", "small")
    d.box(330, 180, 450, 44, ("0x41C2 != 0x9A3F: corrupted, discard or repair", "bold"), "red")
    d.render()


@diagram
def dns_lookup():
    d = new("dns-lookup", 800, 330, "How a DNS lookup works",
            "The resolver walks root, TLD and authoritative servers and caches the answer for its TTL.")
    d.box(20, 130, 110, 60, ["Browser", "+ OS cache"], "blue")
    d.box(200, 130, 130, 60, ["Recursive", "resolver"], "purple")
    d.box(430, 20, 150, 50, ["Root server", "who has .com?"], "amber")
    d.box(430, 130, 170, 50, ["TLD server (.com)", "who has example.com?"], "amber")
    d.box(430, 240, 170, 50, ["Authoritative", "A record: 203.0.113.7"], "green")
    d.arrow([(130, 150), (200, 150)], label="1 asks", lx=165, ly=132)
    d.arrow([(200, 178), (130, 178)], kind="green", label="6 answer", lx=165, ly=200)
    d.arrow([(330, 145), (430, 50)], label="2", lx=375, ly=88)
    d.arrow([(330, 160), (430, 155)], label="3", lx=380, ly=140)
    d.arrow([(330, 175), (430, 265)], label="4", lx=375, ly=232)
    d.box(650, 130, 130, 60, [("Answer cached", "bold"), ("for the TTL", "small")], "box")
    d.arrow([(600, 265), (700, 190)], kind="green", dashed=True, label="5", lx=665, ly=232)
    d.render()


@diagram
def proxy_types():
    d = new("proxy-types", 800, 330, "Forward proxy vs reverse proxy",
            "A forward proxy acts for the clients. A reverse proxy acts for the servers. Clients never see the servers behind it.")
    d.text(190, 20, "Forward proxy (for clients)", "title"); d.text(600, 20, "Reverse proxy (for servers)", "title")
    for i, y in enumerate((50, 110, 170)):
        d.box(10, y, 70, 40, f"Client {i + 1}", "blue")
        d.arrow([(80, y + 20), (150, 125 + i * 0)])
    d.box(150, 100, 110, 50, ["Forward", "proxy"], "purple")
    d.arrow([(260, 125), (320, 125)])
    d.box(320, 100, 100, 50, "Internet", "box")
    d.box(480, 110, 70, 50, "Clients", "blue")
    d.arrow([(550, 135), (600, 135)])
    d.box(600, 110, 100, 50, ["Reverse", "proxy"], "purple")
    for i, y in enumerate((40, 110, 180)):
        d.box(730, y, 60, 40, f"App {i + 1}", "green")
        d.arrow([(700, 135), (730, y + 20)])
    d.text(190, 205, "hides the clients; filters and caches", "small"); d.text(620, 245, "hides the servers; TLS, balancing, caching", "small")
    d.render()


@diagram
def tls_handshake():
    d = new("tls-handshake", 780, 330, "TLS 1.3 handshake",
            "One round trip agrees on a secret key without ever sending it. After that everything is encrypted.")
    d.text(130, 20, "Browser", "title"); d.text(650, 20, "Server", "title")
    d.line(130, 36, 130, 300); d.line(650, 36, 650, 300)
    d.arrow([(130, 70), (650, 90)], kind="blue", label="ClientHello: versions, ciphers, key share", lx=390, ly=68)
    d.arrow([(650, 120), (130, 140)], kind="green", label="ServerHello + certificate + key share", lx=390, ly=118)
    d.box(150, 160, 380, 40, "Browser verifies certificate chain, name, expiry", "amber")
    d.box(290, 215, 400, 40, "Both derive the same session key (never sent)", "purple")
    d.arrow([(130, 285), (650, 285)], kind="blue", label="Encrypted HTTP requests and responses", lx=390, ly=270)
    d.render()


@diagram
def load_balancer_algorithms():
    d = new("load-balancing", 780, 300, "A load balancer in front of three servers",
            "The balancer chooses a server per request and stops using any server that fails its health check.")
    d.box(10, 110, 90, 50, "Clients", "blue")
    d.box(170, 100, 150, 70, [("Load balancer", "bold"), ("algorithm + health", "small")], "purple")
    for i, (y, k, t) in enumerate(((30, "green", "Server 1  (3 conns)"), (115, "green", "Server 2  (1 conn)"), (200, "red", "Server 3  (down)"))):
        d.box(470, y, 200, 50, t, k)
        d.arrow([(320, 135), (470, y + 25)], dashed=(k == "red"), kind=("red" if k == "red" else ""))
    d.arrow([(100, 135), (170, 135)])
    d.text(570, 270, "least connections sends the next request to Server 2", "small")
    d.render()


# ---------------------------------------------------------------- APIs
@diagram
def apis():
    d = new("apis", 780, 250, "An API is a contract",
            "The client depends only on requests, responses and status codes, not on how the server is built.")
    d.box(20, 80, 130, 70, [("Client", "bold"), ("mobile / web", "small")], "blue")
    d.box(250, 70, 190, 90, [("API (the contract)", "bold"), ("GET /orders/42", "code"), ("POST /orders", "code")], "purple")
    d.box(540, 20, 200, 60, [("Server code", "bold"), ("can change freely", "small")], "green")
    d.box(540, 100, 200, 60, [("Database", "bold"), ("can change freely", "small")], "green")
    d.arrow([(150, 105), (250, 105)], kind="blue", label="request", lx=200, ly=88)
    d.arrow([(250, 130), (150, 130)], kind="green", label="200 + JSON", lx=200, ly=150)
    d.arrow([(440, 100), (540, 50)]); d.arrow([(440, 130), (540, 130)])
    d.text(390, 215, "Change the inside as much as you like. Keep the contract stable.", "small")
    d.render()


@diagram
def rest_vs_graphql():
    d = new("rest-vs-graphql", 800, 330, "REST: three round trips. GraphQL: one.",
            "GraphQL lets the client ask for exactly the fields it needs in a single request.")
    d.text(200, 20, "REST", "title"); d.text(610, 20, "GraphQL", "title")
    d.box(10, 130, 80, 50, "Client", "blue")
    for i, (y, t) in enumerate(((50, "GET /books/42"), (130, "GET /authors/7"), (210, "GET /books/42/reviews"))):
        d.box(190, y, 200, 44, (t, "code"), "green")
        d.arrow([(90, 155), (190, y + 22)])
    d.text(290, 285, "3 requests, extra fields returned", "small")
    d.box(430, 130, 80, 50, "Client", "blue")
    d.box(590, 90, 190, 130, [("POST /graphql", "code"), "{ book(id:42) {", "title author{name}", "reviews(limit:2){text} } }"], "purple")
    d.arrow([(510, 155), (590, 155)], kind="blue")
    d.text(690, 245, "1 request, exactly those fields", "small")
    d.render()


@diagram
def api_gateway():
    d = new("api-gateway", 800, 300, "The API gateway",
            "One front door: authentication, rate limits and routing happen once, before the request reaches a service.")
    d.box(10, 70, 90, 40, "Web", "blue"); d.box(10, 130, 90, 40, "Mobile", "blue"); d.box(10, 190, 90, 40, "Partners", "blue")
    d.box(170, 60, 210, 180, [("API gateway", "bold"), "1 TLS termination", "2 authenticate token", "3 rate limit / quota", "4 route + transform", "5 log + trace id"], "purple")
    for y in (90, 150, 210):
        d.arrow([(100, y), (170, 150)])
    for i, (y, t) in enumerate(((40, "Order service"), (120, "User service"), (200, "Payment service"))):
        d.box(520, y, 180, 50, t, "green")
        d.arrow([(380, 150), (520, y + 25)])
    d.text(610, 275, "services trust the gateway's verdict", "small")
    d.render()


@diagram
def api_design():
    d = new("api-design", 780, 260, "Anatomy of a well-designed endpoint",
            "Noun URL, correct method, versioned path, paging, consistent errors and an idempotency key for unsafe writes.")
    d.box(20, 30, 740, 50, [("POST /v1/orders", "code")], "blue")
    items = [("Noun, plural", "not /createOrder"), ("Versioned", "/v1 never breaks"), ("Idempotency-Key", "safe retries"), ("201 + Location", "correct status")]
    for i, (a, b) in enumerate(items):
        d.box(20 + i * 190, 110, 175, 60, [(a, "bold"), (b, "small")], ["green", "amber", "purple", "green"][i])
        d.arrow([(107 + i * 190, 80), (107 + i * 190, 110)])
    d.box(20, 195, 740, 45, "Errors: {error: {code, message, request_id}}   Lists: ?limit=20&cursor=abc   Auth: Bearer token", "box")
    d.render()


@diagram
def websockets():
    d = new("websockets", 800, 330, "HTTP polling vs a WebSocket",
            "A WebSocket upgrades one HTTP connection into a two-way channel that stays open.")
    d.text(200, 20, "HTTP polling", "title"); d.text(610, 20, "WebSocket", "title")
    d.line(100, 36, 100, 310); d.line(300, 36, 300, 310)
    for i, y in enumerate((60, 140, 220)):
        d.arrow([(100, y), (300, y + 12)], label="any news?", lx=200, ly=y - 8)
        d.arrow([(300, y + 32), (100, y + 44)], kind="red", label="no", lx=200, ly=y + 60)
    d.line(510, 36, 510, 310); d.line(710, 36, 710, 310)
    d.arrow([(510, 60), (710, 72)], kind="blue", label="GET /chat  Upgrade: websocket", lx=610, ly=50)
    d.arrow([(710, 92), (510, 104)], kind="green", label="101 Switching Protocols", lx=610, ly=118)
    d.arrow([(710, 150), (510, 162)], kind="green", label="server pushes message", lx=610, ly=145)
    d.arrow([(510, 190), (710, 202)], kind="blue", label="client sends message", lx=610, ly=180)
    d.arrow([(710, 235), (510, 247)], kind="green", label="server pushes message", lx=610, ly=228)
    d.render()


@diagram
def websocket_scaling():
    d = new("websocket-scaling", 800, 300, "Scaling WebSockets across servers",
            "Each connection lives on one server, so servers share messages through pub/sub.")
    d.box(10, 40, 90, 40, "Asha", "blue"); d.box(10, 210, 90, 40, "Ravi", "blue")
    d.box(170, 30, 150, 60, [("WS server 1", "bold"), ("holds Asha's socket", "small")], "green")
    d.box(170, 200, 150, 60, [("WS server 4", "bold"), ("holds Ravi's socket", "small")], "green")
    d.box(430, 115, 150, 60, [("Pub/sub", "bold"), ("Redis / Kafka", "small")], "purple")
    d.arrow([(100, 60), (170, 60)]); d.arrow([(170, 230), (100, 230)], kind="green")
    d.arrow([(320, 60), (430, 135)], kind="blue", label="1 publish", lx=400, ly=78)
    d.arrow([(430, 160), (320, 230)], kind="green", label="2 deliver", lx=400, ly=215)
    d.box(630, 40, 150, 90, [("Load balancer", "bold"), ("least connections", "small"), ("sticky per socket", "small")], "box")
    d.text(400, 285, "On reconnect the client sends the last message id it saw; the server replays what it missed.", "small")
    d.render()


@diagram
def webhooks():
    d = new("webhooks", 800, 300, "Webhook flow",
            "The provider calls your endpoint when an event happens. You verify, store, reply fast and process later.")
    d.box(10, 130, 130, 60, [("Payment", "bold"), ("provider", "small")], "blue")
    d.box(260, 130, 150, 60, [("Your endpoint", "bold"), ("POST /hooks/pay", "code")], "purple")
    d.box(500, 40, 130, 50, ["Verify HMAC", "signature"], "amber")
    d.box(500, 130, 130, 50, ["Store event", "(unique id)"], "green")
    d.box(660, 130, 120, 50, ["Queue + worker", "process later"], "green")
    d.arrow([(140, 150), (260, 150)], kind="blue", label="event + signature", lx=200, ly=132)
    d.arrow([(410, 140), (500, 70)]); d.arrow([(410, 155), (500, 155)]); d.arrow([(630, 155), (660, 155)])
    d.arrow([(260, 175), (140, 175)], kind="green", label="200 OK (fast)", lx=200, ly=196)
    d.arrow([(75, 130), (75, 70), (335, 70), (335, 130)], dashed=True, kind="red")
    d.text(205, 56, "no 2xx: provider retries with backoff", "small")
    d.text(400, 260, "Duplicates will arrive: dedupe by event id.", "small")
    d.render()


@diagram
def idempotency():
    d = new("idempotency", 800, 340, "Idempotency key: retries are safe",
            "The server stores the result under the key and replays it instead of charging twice.")
    d.text(130, 20, "Client", "title"); d.text(400, 20, "Server", "title"); d.text(670, 20, "Key store", "title")
    for x in (130, 400, 670):
        d.line(x, 34, x, 320)
    d.arrow([(130, 70), (400, 80)], kind="blue", label="charge 500, key K1", lx=265, ly=58)
    d.arrow([(400, 95), (670, 105)], label="K1 new? yes: process", lx=535, ly=83)
    d.arrow([(400, 130), (130, 140)], kind="red", dashed=True, label="response lost on the way", lx=265, ly=152)
    d.arrow([(130, 200), (400, 210)], kind="blue", label="retry: charge 500, key K1", lx=265, ly=188)
    d.arrow([(400, 225), (670, 235)], label="K1 seen: return stored result", lx=535, ly=213)
    d.arrow([(400, 275), (130, 285)], kind="green", label="same result, no second charge", lx=265, ly=300)
    d.render()


@diagram
def rate_limiting():
    d = new("rate-limiting", 800, 280, "Rate limiting at the edge",
            "Requests over the limit are rejected with 429 and a Retry-After header instead of overloading the service.")
    d.box(10, 90, 100, 50, "Clients", "blue")
    d.box(180, 70, 190, 90, [("Rate limiter", "bold"), ("key: user + IP + route", "small"), ("counters in Redis", "small")], "purple")
    d.box(480, 40, 150, 50, ["Within limit", "forward to service"], "green")
    d.box(480, 130, 150, 50, ["Over limit", "429 Retry-After"], "red")
    d.box(670, 40, 110, 50, "Service", "green")
    d.arrow([(110, 115), (180, 115)]); d.arrow([(370, 100), (480, 65)]); d.arrow([(370, 135), (480, 155)])
    d.arrow([(630, 65), (670, 65)])
    d.text(400, 235, "Fail open for general traffic, fail closed for login endpoints, if the limiter store is down.", "small")
    d.render()


@diagram
def token_bucket():
    d = new("token-bucket", 780, 280, "Token bucket",
            "Tokens refill at a steady rate up to the bucket size. Each request spends one. No tokens means rejected.")
    d.box(40, 60, 150, 70, [("Refill", "bold"), ("R tokens / second", "small")], "green")
    d.arrow([(190, 95), (260, 95)], kind="green")
    d.rect(260, 40, 150, 160, "ghost", rx=12)
    for i in range(5):
        d.circle(310 + (i % 2) * 50, 170 - (i // 2) * 40, 16, "circle-b")
    d.text(335, 22, "Bucket: capacity B", "bold")
    d.box(520, 40, 230, 60, [("Request arrives", "bold"), ("take a token: allow", "small")], "blue")
    d.box(520, 130, 230, 60, [("Bucket empty", "bold"), ("reject with 429", "small")], "red")
    d.arrow([(410, 90), (520, 70)]); d.arrow([(410, 150), (520, 160)])
    d.text(390, 250, "Allows short bursts up to B, while enforcing an average rate of R.", "small")
    d.render()


# ---------------------------------------------------------------- databases
@diagram
def acid():
    d = new("acid", 800, 280, "A transfer as one atomic transaction",
            "Both updates commit together or both roll back. The log makes the commit durable.")
    d.box(10, 100, 100, 50, ["BEGIN"], "blue")
    d.box(170, 40, 190, 50, ["Asha: balance - 500"], "amber")
    d.box(170, 160, 190, 50, ["Ravi: balance + 500"], "amber")
    d.arrow([(110, 115), (170, 65)]); d.arrow([(110, 135), (170, 185)])
    d.box(430, 100, 120, 50, ["Any error?"], "purple")
    d.arrow([(360, 65), (430, 115)]); d.arrow([(360, 185), (430, 135)])
    d.box(620, 30, 160, 60, [("COMMIT", "bold"), ("both changes visible", "small")], "green")
    d.box(620, 120, 160, 60, [("ROLLBACK", "bold"), ("neither change", "small")], "red")
    d.arrow([(550, 110), (620, 60)], label="no", lx=585, ly=70); d.arrow([(550, 140), (620, 150)], label="yes", lx=585, ly=158)
    d.box(170, 235, 380, 36, "Write-ahead log is flushed before COMMIT returns: durability", "box")
    d.render()


@diagram
def sql_vs_nosql():
    d = new("sql-vs-nosql", 800, 320, "The same order in SQL and in a document store",
            "SQL stores each fact once and joins on read. A document stores the whole order together.")
    d.text(200, 20, "SQL: three tables, joined", "title"); d.text(610, 20, "Document: one record", "title")
    d.box(20, 40, 120, 70, [("customers", "bold"), "id | name", "1 | Asha"], "blue")
    d.box(20, 140, 120, 70, [("orders", "bold"), "id | cust", "100 | 1"], "blue")
    d.box(210, 140, 170, 70, [("items", "bold"), "order | sku | qty", "100 | TEA | 2"], "blue")
    d.arrow([(80, 110), (80, 140)], dashed=True); d.arrow([(140, 175), (210, 175)], dashed=True)
    d.text(200, 245, "JOIN to rebuild the order", "small")
    d.box(450, 40, 320, 180, [("order 100", "bold"), "customer: { id: 1, name: 'Asha' }", "items: [", "  { sku: 'TEA', qty: 2 },", "  { sku: 'CUP', qty: 1 } ]", ("one read gets everything", "small")], "green", tcls="code")
    d.text(400, 295, "SQL: no duplication, flexible queries.  Document: fast single reads, copies of shared data.", "small")
    d.render()


@diagram
def database_indexes():
    d = new("database-indexes", 800, 300, "A B-tree index",
            "Each level narrows the search. Three or four page reads find one row among hundreds of millions.")
    d.box(330, 20, 140, 40, ("root: 400 | 800", "code"), "purple")
    for i, (x, t) in enumerate(((120, "100 | 200 | 300"), (330, "500 | 600 | 700"), (540, "900 | 1000"))):
        d.box(x, 100, 140, 40, (t, "code"), "blue")
        d.arrow([(400, 60), (x + 70, 100)])
    for i, x in enumerate((60, 180, 300, 420)):
        d.box(x, 190, 100, 40, ("rows ...", "small"), "green")
    d.arrow([(190, 140), (110, 190)]); d.arrow([(190, 140), (230, 190)]); d.arrow([(400, 140), (350, 190)]); d.arrow([(400, 140), (470, 190)])
    d.box(600, 180, 190, 90, [("Without an index", "bold"), ("scan all rows", "small"), ("10M rows read", "small")], "red")
    d.text(300, 265, "With the index: about 4 page reads", "small")
    d.render()


@diagram
def sharding():
    d = new("sharding", 800, 300, "Sharding by user id",
            "A router hashes the shard key and sends each request to the one shard that owns that user.")
    d.box(10, 110, 100, 50, "App", "blue")
    d.box(170, 90, 160, 90, [("Router", "bold"), ("shard = hash(user_id)", "small"), ("% 4", "small")], "purple")
    for i, (y, t) in enumerate(((20, "Shard 0: users A"), (90, "Shard 1: users B"), (160, "Shard 2: users C"), (230, "Shard 3: users D"))):
        d.box(480, y, 200, 50, t, "green")
        d.arrow([(330, 135), (480, y + 25)])
    d.arrow([(110, 135), (170, 135)])
    d.box(700, 100, 90, 70, [("each shard", "small"), ("has replicas", "small")], "box")
    d.render()


@diagram
def replication_diagram():
    d = new("replication", 800, 270, "Primary and replicas",
            "Writes go to the primary. It ships changes to replicas, which serve reads and stand ready for failover.")
    d.box(10, 100, 110, 60, ["App servers"], "blue")
    d.box(250, 30, 170, 60, [("Primary", "bold"), ("accepts writes", "small")], "red")
    d.box(250, 170, 170, 60, [("Replica A", "bold"), ("serves reads", "small")], "amber")
    d.box(540, 170, 170, 60, [("Replica B", "bold"), ("other region", "small")], "amber")
    d.arrow([(120, 115), (250, 60)], kind="red", label="writes", lx=170, ly=72)
    d.arrow([(120, 150), (250, 195)], label="reads", lx=170, ly=190)
    d.arrow([(335, 90), (335, 170)], dashed=True, label="change log", lx=392, ly=130)
    d.arrow([(420, 70), (600, 170)], dashed=True)
    d.text(560, 100, "async: replicas lag slightly", "small")
    d.render()


@diagram
def database_scaling():
    d = new("database-scaling", 800, 300, "The database scaling ladder",
            "Try the cheapest rung first. Move up only when the numbers say the current rung is not enough.")
    rungs = [("1. Indexes + queries", "green"), ("2. Connection pool", "green"), ("3. Cache", "green"), ("4. Bigger machine", "amber"),
             ("5. Read replicas", "amber"), ("6. Partition + archive", "amber"), ("7. Split by feature", "red"), ("8. Shard", "red")]
    for i, (t, k) in enumerate(rungs):
        x = 20 + (i % 4) * 190
        y = 40 + (i // 4) * 110
        d.box(x, y, 170, 70, (t, "bold"), k)
        if i % 4:
            d.arrow([(x - 20, y + 35), (x, y + 35)])
    d.arrow([(765, 75), (765, 100), (105, 100), (105, 150)], dashed=True)
    d.text(400, 24, "cheap and simple  ->  powerful and complex", "small")
    d.text(400, 270, "Rungs 1 to 3 are free or cheap. Sharding (8) is the most powerful and the most expensive.", "small")
    d.render()


@diagram
def database_types():
    d = new("database-types", 800, 330, "Database families and what they are for",
            "Pick the family by the shape of the data and the access pattern.")
    cards = [("Relational", "orders, payments", "blue"), ("Key-value", "cache, sessions", "amber"), ("Document", "catalogue, profiles", "green"),
             ("Wide-column", "events, time-ordered", "purple"), ("Column store", "analytics", "blue"), ("Graph", "friends of friends", "green"),
             ("Time-series", "metrics, sensors", "amber"), ("Search", "full-text", "purple")]
    for i, (a, b, k) in enumerate(cards):
        x = 20 + (i % 4) * 190
        y = 30 + (i // 4) * 130
        d.box(x, y, 175, 100, [(a, "bold"), (b, "small")], k)
    d.text(400, 300, "Real systems combine several (polyglot persistence).", "small")
    d.render()


@diagram
def bloom_filter():
    d = new("bloom-filter", 800, 300, "Bloom filter: add and query",
            "An item sets k bits. A query that finds any 0 bit means definitely not present. All 1s means maybe present.")
    for i in range(16):
        d.rect(60 + i * 42, 120, 38, 38, "bar" + ("" if i in (2, 6, 11, 13) else " dim"), rx=3)
        d.text(79 + i * 42, 175, str(i), "small")
    d.box(30, 20, 150, 44, ["add 'asha'"], "blue")
    for bit in (2, 6, 11):
        d.arrow([(105, 64), (79 + bit * 42, 120)], kind="blue")
    d.box(430, 20, 150, 44, ["query 'zed'"], "amber")
    d.arrow([(505, 64), (79 + 2 * 42, 120)], dashed=True); d.arrow([(505, 64), (79 + 8 * 42, 120)], dashed=True)
    d.box(620, 20, 160, 44, ["bit 8 is 0: NO"], "green")
    d.text(400, 230, "No false negatives. A small chance of a false positive when bits were set by other items.", "small")
    d.text(400, 260, "About 10 bits per item gives about 1% false positives.", "small")
    d.render()


@diagram
def database_architectures():
    d = new("database-architectures", 800, 330, "Common database deployments",
            "From one node to active-active regions: more availability and lower latency cost more complexity.")
    d.box(10, 30, 240, 90, [("Primary + replicas", "bold"), ("one region, writes to one node", "small")], "blue")
    d.box(280, 30, 240, 90, [("Multi-AZ standby", "bold"), ("sync copy in another zone", "small")], "green")
    d.box(550, 30, 240, 90, [("Cross-region replica", "bold"), ("async copy for DR + reads", "small")], "amber")
    d.box(10, 150, 380, 120, [("Active-active, multi-region", "bold"), ("Mumbai, Frankfurt and Virginia all accept writes", "small"), ("conflicts avoided by home region per record", "small")], "purple")
    d.box(420, 150, 370, 120, [("Disaster-recovery strategies", "bold"), ("backup/restore: hours", "small"), ("pilot light: tens of minutes", "small"), ("warm standby: minutes", "small")], "red")
    d.render()


# ---------------------------------------------------------------- caching
@diagram
def caching_101():
    d = new("caching-101", 800, 270, "A cache in front of a database",
            "A hit is answered in about a millisecond. A miss pays the slow database trip and fills the cache.")
    d.box(10, 100, 100, 50, "App", "blue")
    d.box(250, 100, 160, 60, [("Cache", "bold"), ("Redis, ~1 ms", "small")], "amber")
    d.box(560, 100, 200, 60, [("Database", "bold"), ("5-50 ms", "small")], "red")
    d.arrow([(110, 125), (250, 125)], label="1 get(key)", lx=180, ly=108)
    d.arrow([(250, 145), (110, 145)], kind="green", label="2a hit", lx=180, ly=165)
    d.arrow([(410, 125), (560, 125)], dashed=True, label="2b miss", lx=485, ly=108)
    d.arrow([(560, 150), (410, 150)], dashed=True, label="3 store copy", lx=485, ly=172)
    d.text(400, 235, "average = hit rate x 1 ms + (1 - hit rate) x 20 ms", "small")
    d.render()


@diagram
def caching_strategies():
    d = new("caching-strategies", 800, 330, "Where the cache sits for reads and writes",
            "Cache-aside: the app manages it. Read/write-through: the cache talks to the database. Write-behind: the database is updated later.")
    for i, (t, sub) in enumerate((("Cache-aside", "app loads on miss"), ("Read-through", "cache loads on miss"),
                                  ("Write-through", "cache + DB together"), ("Write-behind", "DB updated later"))):
        x = 20 + i * 195
        d.box(x, 20, 180, 60, [(t, "bold"), (sub, "small")], ["blue", "green", "amber", "red"][i])
        d.box(x + 40, 120, 100, 44, "Cache", "amber")
        d.box(x + 40, 210, 100, 44, "Database", "red")
        d.arrow([(x + 90, 80), (x + 90, 120)])
        d.arrow([(x + 90, 164), (x + 90, 210)], dashed=(i == 3), label=("async" if i == 3 else None), lx=x + 125, ly=190)
    d.text(400, 295, "In cache-aside the app also talks to the database itself. In the others it talks only to the cache.", "small")
    d.render()


@diagram
def eviction_policies():
    d = new("eviction-policies", 800, 270, "LRU eviction",
            "The cache holds three items. Using A moves it to the front; adding D evicts the least recently used item, B.")
    d.text(150, 20, "Order of use (front = most recent)", "small")
    for i, (t, k) in enumerate((("C", "green"), ("A", "green"), ("B", "red"))):
        d.box(60 + i * 90, 40, 70, 44, (t, "bold"), k)
    d.text(165, 105, "A was just used, B is oldest", "small")
    d.arrow([(340, 62), (430, 62)], label="put D", lx=385, ly=45)
    for i, (t, k) in enumerate((("D", "blue"), ("C", "green"), ("A", "green"))):
        d.box(450 + i * 90, 40, 70, 44, (t, "bold"), k)
    d.text(580, 105, "B evicted", "small")
    d.box(60, 150, 200, 80, [("LRU", "bold"), ("recent use predicts reuse", "small")], "blue")
    d.box(300, 150, 200, 80, [("LFU", "bold"), ("keep the most popular", "small")], "green")
    d.box(540, 150, 200, 80, [("FIFO / Random", "bold"), ("cheap, ignores use", "small")], "amber")
    d.render()


@diagram
def distributed_caching():
    d = new("distributed-caching", 800, 300, "A sharded, replicated cache cluster",
            "The client library hashes the key to a node. Each shard has a replica for failover.")
    d.box(10, 110, 130, 60, [("App servers", "bold"), ("+ cache client", "small")], "blue")
    d.box(210, 20, 130, 44, "Hash ring", "purple")
    d.arrow([(140, 125), (210, 45)], dashed=True)
    for i, y in enumerate((100, 160, 220)):
        d.box(290, y, 120, 44, f"Cache node {i + 1}", "amber")
        d.arrow([(140, 140), (290, y + 22)])
        d.box(470, y, 120, 44, "Replica", "box")
        d.arrow([(410, y + 22), (470, y + 22)], dashed=True)
    d.box(650, 140, 130, 60, [("Database", "bold"), ("on a miss", "small")], "red")
    d.arrow([(590, 182), (650, 175)], dashed=True)
    d.render()


# ---------------------------------------------------------------- async
@diagram
def pub_sub():
    d = new("pub-sub", 800, 330, "Publish/subscribe",
            "The publisher sends one event to a topic. Every subscriber receives its own copy through its own queue.")
    d.box(10, 120, 120, 60, [("Order service", "bold"), ("publisher", "small")], "blue")
    d.box(230, 120, 130, 60, [("Topic", "bold"), ("order.placed", "code")], "purple")
    d.arrow([(130, 150), (230, 150)], kind="blue", label="1 event", lx=180, ly=132)
    for i, (y, t) in enumerate(((20, "Billing"), (100, "Inventory"), (180, "Email"), (250, "Analytics"))):
        d.box(560, y, 200, 44, t, "green")
        d.arrow([(360, 150), (560, y + 22)])
    d.text(400, 315, "adding a subscriber needs no change to the publisher", "small")
    d.render()


@diagram
def cdc():
    d = new("cdc", 800, 300, "Change data capture",
            "The connector reads the database transaction log and publishes every change, in order, to a stream.")
    d.box(10, 70, 100, 60, ["App"], "blue")
    d.box(170, 60, 150, 80, [("Database", "bold"), ("tables +", "small"), ("transaction log", "small")], "red")
    d.box(400, 70, 140, 60, [("CDC connector", "bold"), ("(Debezium)", "small")], "purple")
    d.box(620, 70, 160, 60, [("Stream", "bold"), ("Kafka topic", "small")], "amber")
    d.arrow([(110, 100), (170, 100)]); d.arrow([(320, 100), (400, 100)], dashed=True, label="reads log", lx=360, ly=82)
    d.arrow([(540, 100), (620, 100)])
    d.box(170, 200, 190, 56, ["Warehouse / other services"], "green")
    d.box(420, 200, 160, 56, ["Search index"], "green")
    d.box(620, 200, 160, 56, ["Cache invalidation"], "green")
    d.arrow([(700, 130), (700, 200)]); d.arrow([(660, 130), (520, 200)]); d.arrow([(640, 130), (300, 200)], dashed=True)
    d.text(400, 285, "One change event feeds every downstream system, in commit order, including deletes.", "small")
    d.render()


# ---------------------------------------------------------------- distributed systems
@diagram
def heartbeats():
    d = new("heartbeats", 800, 280, "Heartbeats and failure detection",
            "Beats arrive every second. After three missed beats the monitor suspects the node and reacts.")
    d.box(10, 90, 110, 50, "Node", "green")
    d.box(600, 90, 170, 50, [("Monitor / peers", "bold")], "purple")
    d.line(150, 115, 580, 115)
    for i, x in enumerate((170, 240, 310, 380)):
        d.circle(x, 115, 9, "circle-b")
    for x in (450, 520, 570):
        d.circle(x, 115, 9, "ghost")
    d.text(275, 150, "beats arrive", "small"); d.text(520, 150, "3 missed beats", "small")
    d.box(250, 175, 520, 44, ("Suspect the node is dead: remove it from the LB, elect a new leader", "bold"), "red")
    d.text(400, 255, "Too short a timeout means false alarms; too long means slow detection.", "small")
    d.render()


@diagram
def service_discovery():
    d = new("service-discovery", 800, 310, "Service discovery with a registry",
            "Instances register and send heartbeats. Clients ask the registry for healthy instances instead of hard-coding addresses.")
    d.box(10, 90, 130, 60, [("Order service", "bold"), ("(client)", "small")], "blue")
    d.box(280, 80, 180, 80, [("Service registry", "bold"), ("payments: .11 .12 .14", "small"), ("health-checked", "small")], "purple")
    d.arrow([(140, 105), (280, 105)], label="1 where is payments?", lx=210, ly=88)
    d.arrow([(280, 135), (140, 135)], kind="green", label="2 .11 .12 .14", lx=210, ly=156)
    for i, (y, t) in enumerate(((20, "payments .11"), (90, "payments .12"), (160, "payments .14"))):
        d.box(590, y, 190, 44, t, "green")
        d.arrow([(590, y + 22), (460, 120)], dashed=True)
    d.text(525, 12, "register + heartbeat", "small")
    d.arrow([(75, 150), (75, 255), (685, 255), (685, 204)], kind="blue", dashed=True)
    d.text(380, 275, "3 the client calls a chosen healthy instance directly", "small")
    d.render()


@diagram
def consensus():
    d = new("consensus", 800, 320, "Majority agreement (Raft)",
            "The leader replicates a command. With 3 of 5 nodes holding it, it is committed and survives any minority failure.")
    d.box(10, 120, 100, 50, "Client", "blue")
    d.box(170, 110, 130, 70, [("Leader", "bold"), ("term 3", "small")], "purple")
    d.arrow([(110, 145), (170, 145)], label="set x=5", lx=140, ly=128)
    for i, (y, t, k) in enumerate(((10, "F1  ack", "green"), (70, "F2  ack", "green"), (190, "F3  slow", "amber"), (250, "F4  down", "red"))):
        d.box(470, y, 140, 38, t, k)
        d.arrow([(300, 145), (470, y + 19)], dashed=(k != "green"))
    d.box(650, 110, 140, 70, [("Committed", "bold"), ("3 of 5 = majority", "small")], "green")
    d.arrow([(610, 90), (700, 110)], kind="green")
    d.text(400, 305, "2 nodes may fail. 3 failures: no majority, no leader: safe but stopped.", "small")
    d.render()


@diagram
def distributed_locking():
    d = new("distributed-locking", 800, 340, "Lease + fencing token",
            "A paused client wakes up with an expired lease. The storage rejects its write because the token is stale.")
    d.text(110, 20, "Client A", "title"); d.text(330, 20, "Lock service", "title"); d.text(540, 20, "Client B", "title"); d.text(720, 20, "Storage", "title")
    for x in (110, 330, 540, 720):
        d.line(x, 34, x, 310)
    d.arrow([(110, 60), (330, 70)], kind="blue", label="acquire", lx=220, ly=50)
    d.arrow([(330, 85), (110, 95)], kind="green", label="token 33, lease 10s", lx=220, ly=108)
    d.box(10, 125, 200, 40, ("A pauses (GC): lease expires", "small"), "amber")
    d.arrow([(540, 150), (330, 160)], kind="blue", label="acquire", lx=435, ly=140)
    d.arrow([(330, 175), (540, 185)], kind="green", label="token 34", lx=435, ly=198)
    d.arrow([(540, 215), (720, 225)], kind="green", label="write, token 34: ok", lx=630, ly=205)
    d.arrow([(110, 255), (720, 267)], kind="red", label="late write, token 33", lx=415, ly=245)
    d.box(480, 290, 290, 40, ("REJECTED: 33 < 34", "bold"), "red")
    d.render()


@diagram
def gossip():
    d = new("gossip", 800, 300, "Gossip spreads like a rumour",
            "Each round every informed node tells a few random peers, so the informed count roughly doubles.")
    xs = [100, 340, 580]
    labels = ["Round 0: 1 knows", "Round 1: 3 know", "Round 2: 9 know"]
    counts = [1, 3, 9]
    for r in range(3):
        d.text(xs[r] + 60, 25, labels[r], "bold")
        for i in range(9):
            cx, cy = xs[r] + 25 + (i % 3) * 45, 70 + (i // 3) * 55
            d.circle(cx, cy, 16, "circle-b" if i < counts[r] else "ghost")
    d.arrow([(260, 130), (320, 130)]); d.arrow([(500, 130), (560, 130)])
    d.text(400, 260, "10,000 nodes need only about log2(10,000) = 14 rounds. No central coordinator.", "small")
    d.render()


@diagram
def circuit_breaker():
    d = new("circuit-breaker", 800, 280, "Circuit breaker states",
            "Closed passes calls through. After too many failures it opens and fails fast. After a cool-down it lets a trial call through.")
    d.box(30, 100, 150, 70, [("CLOSED", "bold"), ("calls pass through", "small")], "green")
    d.box(330, 20, 150, 70, [("OPEN", "bold"), ("fail fast / fallback", "small")], "red")
    d.box(620, 100, 150, 70, [("HALF-OPEN", "bold"), ("a few trial calls", "small")], "amber")
    d.arrow([(180, 115), (330, 55)], label="failures > threshold", lx=205, ly=72)
    d.arrow([(480, 55), (620, 115)], label="cool-down over", lx=590, ly=72)
    d.arrow([(620, 150), (180, 150)], kind="green", label="trial succeeds: close", lx=400, ly=172)
    d.arrow([(695, 100), (480, 40)], kind="red", dashed=True, label="trial fails: open again", lx=620, ly=22)
    d.text(400, 240, "Pair with timeouts, retries with backoff, bulkheads and fallbacks.", "small")
    d.render()


@diagram
def disaster_recovery():
    d = new("disaster-recovery", 800, 290, "RPO and RTO",
            "RPO is how much data you may lose. RTO is how long you may be down.")
    d.line(40, 120, 760, 120, "line")
    d.circle(220, 120, 10, "circle-b"); d.text(220, 150, "last good backup", "small")
    d.circle(420, 120, 10, "circle-a"); d.text(420, 150, "disaster", "bold")
    d.circle(640, 120, 10, "circle-b"); d.text(640, 150, "service restored", "small")
    d.arrow([(220, 95), (420, 95)], kind="red", label="data lost (RPO)", lx=320, ly=75)
    d.arrow([(420, 95), (640, 95)], kind="blue", label="downtime (RTO)", lx=530, ly=75)
    d.box(40, 190, 170, 70, [("Backup + restore", "bold"), ("hours", "small")], "red")
    d.box(230, 190, 170, 70, [("Pilot light", "bold"), ("tens of minutes", "small")], "amber")
    d.box(420, 190, 170, 70, [("Warm standby", "bold"), ("minutes", "small")], "blue")
    d.box(610, 190, 150, 70, [("Active-active", "bold"), ("about zero", "small")], "green")
    d.render()


@diagram
def distributed_tracing():
    d = new("distributed-tracing", 800, 320, "A trace is a tree of spans",
            "Every service records a span with the same trace id. The waterfall shows where the time went.")
    rows = [("gateway", 0, 100, "blue", 0), ("cart-service", 3, 18, "green", 1), ("pricing-service", 18, 90, "amber", 1),
            ("pricing-db query", 20, 85, "red", 2), ("payment-service", 90, 98, "green", 1), ("bank API", 92, 98, "purple", 2)]
    for i, (n, a, b, k, depth) in enumerate(rows):
        y = 34 + i * 40
        d.text(30 + depth * 20, y + 14, n, "small", anchor="start")
        d.rect(300 + a * 4.6, y, (b - a) * 4.6, 26, "bar" + (" amber" if k == "amber" else (" green" if k == "green" else "")), rx=4)
    d.text(540, 18, "time  ->", "small")
    d.text(400, 295, "One slow database query is most of the request: obvious in the waterfall, invisible in separate logs.", "small")
    d.render()


# ---------------------------------------------------------------- architecture patterns
@diagram
def client_server():
    d = new("client-server", 800, 280, "Three-tier client-server",
            "Presentation, application logic and data are separate tiers. Clients are untrusted; the server enforces the rules.")
    d.box(10, 100, 130, 70, [("Clients", "bold"), ("browser, app", "small")], "blue")
    d.box(230, 100, 150, 70, [("Web / app tier", "bold"), ("business rules", "small")], "green")
    d.box(470, 100, 130, 70, [("Data tier", "bold"), ("database", "small")], "red")
    d.box(660, 100, 120, 70, [("Cache,", "small"), ("queue,", "small"), ("search", "small")], "amber")
    d.arrow([(140, 125), (230, 125)], kind="blue", label="request", lx=185, ly=108)
    d.arrow([(230, 150), (140, 150)], kind="green", label="response", lx=185, ly=172)
    d.arrow([(380, 135), (470, 135)]); d.arrow([(600, 135), (660, 135)], dashed=True)
    d.text(400, 235, "The client starts the conversation. Never trust the client: validate on the server.", "small")
    d.render()


@diagram
def microservices():
    d = new("microservices", 800, 380, "Microservices, each with its own data",
            "Small services own one capability and one database. They talk over APIs and events, and deploy independently.")
    d.box(10, 130, 100, 50, "Clients", "blue")
    d.box(160, 120, 120, 70, [("API gateway", "bold")], "purple")
    d.arrow([(110, 155), (160, 155)])
    for i, (y, t) in enumerate(((20, "Orders"), (100, "Payments"), (180, "Catalogue"), (260, "Shipping"))):
        d.box(380, y, 150, 50, t, "green")
        d.box(600, y, 150, 50, "own database", "red")
        d.arrow([(280, 155), (380, y + 25)])
        d.arrow([(530, y + 25), (600, y + 25)])
    d.box(380, 335, 370, 36, ("Event bus: services publish and subscribe", "small"), "amber")
    d.text(200, 355, "no shared database", "small")
    d.render()


@diagram
def serverless():
    d = new("serverless", 800, 290, "Serverless: events trigger functions",
            "The platform runs a function per event and scales to zero when idle. You pay only for execution time.")
    d.box(10, 30, 130, 44, "HTTP request", "blue"); d.box(10, 100, 130, 44, "File uploaded", "blue"); d.box(10, 170, 130, 44, "Queue message", "blue"); d.box(10, 240, 130, 40, "Schedule", "blue")
    d.box(250, 90, 170, 90, [("Function platform", "bold"), ("start, run, scale,", "small"), ("stop", "small")], "purple")
    for y in (52, 122, 192, 260):
        d.arrow([(140, y), (250, 135)])
    for i, (y, t) in enumerate(((50, "Function copy 1"), (120, "Function copy 2"), (190, "Function copy 3"))):
        d.box(520, y, 140, 44, t, "green")
        d.arrow([(420, 135), (520, y + 22)])
    d.box(690, 100, 100, 70, [("DB, S3,", "small"), ("queue", "small")], "red")
    d.arrow([(660, 140), (690, 135)])
    d.render()


@diagram
def event_driven():
    d = new("event-driven", 800, 300, "Event-driven choreography",
            "Services react to events and emit new ones. No service calls another directly.")
    d.box(10, 120, 120, 55, [("Order service", "bold")], "blue")
    d.box(200, 115, 130, 60, [("Event bus", "bold"), ("OrderPlaced", "code")], "purple")
    d.arrow([(130, 147), (200, 147)], kind="blue")
    d.box(430, 30, 150, 50, "Inventory", "green"); d.box(430, 110, 150, 50, "Billing", "green"); d.box(430, 190, 150, 50, "Email", "green"); d.box(430, 260, 150, 36, "Analytics", "green")
    for y in (55, 135, 215, 278):
        d.arrow([(330, 147), (430, y)])
    d.box(640, 30, 140, 50, ["StockReserved"], "amber"); d.arrow([(580, 55), (640, 55)], dashed=True)
    d.box(640, 110, 140, 50, ["PaymentTaken"], "amber"); d.arrow([(580, 135), (640, 135)], dashed=True)
    d.render()


@diagram
def p2p():
    d = new("p2p", 800, 300, "Client-server vs peer-to-peer",
            "In P2P every node is both client and server. Capacity grows with the number of peers and there is no central point of failure.")
    d.text(200, 20, "Client-server", "title"); d.text(600, 20, "Peer-to-peer", "title")
    clients = ((30, 40), (30, 140), (30, 230), (330, 40), (330, 140), (330, 230))
    for i, (x, y) in enumerate(clients):
        d.arrow([(x + 35, y + 18), (200, 140)], head=False)
    ps = [(480, 60), (640, 60), (540, 150), (700, 150), (480, 235), (640, 235)]
    for a, b in ((0, 1), (0, 2), (1, 3), (2, 3), (2, 4), (2, 5), (4, 5), (1, 2), (3, 5)):
        (x1, y1), (x2, y2) = ps[a], ps[b]
        d.arrow([(x1 + 35, y1 + 20), (x2 + 35, y2 + 20)], head=False)
    d.box(150, 110, 100, 60, "Server", "red")
    for i, (x, y) in enumerate(clients):
        d.box(x, y, 70, 36, f"C{i + 1}", "blue")
    for i, (x, y) in enumerate(ps):
        d.box(x, y, 70, 40, f"P{i + 1}", "green")
    d.render()


# ---------------------------------------------------------------- trade-offs
@diagram
def tradeoffs():
    d = new("tradeoffs", 800, 320, "Every choice buys something and costs something",
            "Name the trade-off, tie it to the requirement and the numbers, and say what would change your mind.")
    pairs = [("Consistency", "Availability"), ("Latency", "Throughput"), ("Cost", "Performance"), ("Simplicity", "Scale"),
             ("Freshness", "Speed"), ("Durability", "Write speed")]
    for i, (a, b) in enumerate(pairs):
        x = 20 + (i % 3) * 260
        y = 30 + (i // 3) * 140
        d.box(x, y, 100, 60, (a, "bold"), "blue")
        d.box(x + 130, y, 100, 60, (b, "bold"), "amber")
        d.arrow([(x + 100, y + 30), (x + 130, y + 30)], head=True)
        d.arrow([(x + 130, y + 30), (x + 100, y + 30)], head=True)
    d.text(400, 300, "There is no best design, only the right design for the requirement.", "small")
    d.render()


@diagram
def vertical_vs_horizontal():
    d = new("vertical-vs-horizontal", 800, 300, "Scale up vs scale out",
            "Vertical: one bigger machine, with a ceiling and a single point of failure. Horizontal: many machines behind a balancer.")
    d.text(200, 20, "Vertical (scale up)", "title"); d.text(600, 20, "Horizontal (scale out)", "title")
    d.box(40, 150, 70, 90, ["4 CPU", "8 GB"], "blue")
    d.arrow([(110, 195), (160, 160)]); d.box(150, 100, 100, 140, ["16 CPU", "64 GB"], "blue")
    d.arrow([(250, 170), (300, 130)]); d.box(290, 60, 120, 180, ["64 CPU", "512 GB", "(the ceiling)"], "red")
    d.box(450, 120, 100, 50, "Balancer", "purple")
    for i, y in enumerate((50, 120, 190)):
        d.box(640, y, 120, 50, f"Server {i + 1}", "green")
        d.arrow([(550, 145), (640, y + 25)])
    d.box(450, 210, 100, 40, ("add more...", "small"), "ghost")
    d.render()


@diagram
def concurrency_parallelism():
    d = new("concurrency-parallelism", 800, 300, "Concurrency vs parallelism",
            "Concurrency: one worker interleaves tasks. Parallelism: several workers run tasks at the same instant.")
    d.text(200, 20, "Concurrency: 1 core, 3 tasks taking turns", "title"); d.text(600, 20, "Parallelism: 3 cores, 3 tasks at once", "title")
    seq = ["A", "B", "C", "A", "B", "C"]
    for i, t in enumerate(seq):
        d.box(20 + i * 62, 60, 56, 40, (t, "bold"), ["blue", "green", "amber"][i % 3])
    d.text(200, 125, "one at a time, switching during waits", "small")
    for r, (t, k) in enumerate((("A", "blue"), ("B", "green"), ("C", "amber"))):
        d.box(430, 50 + r * 55, 330, 40, (f"core {r + 1}: task {t}", "bold"), k)
    d.box(40, 180, 340, 80, [("Good for I/O-bound work", "bold"), ("web servers, async, waiting on the network", "small")], "box")
    d.box(430, 220, 330, 60, [("Good for CPU-bound work", "bold"), ("maths, encoding, compression", "small")], "box")
    d.render()


@diagram
def long_polling_vs_websockets():
    d = new("long-polling-vs-websockets", 800, 320, "Long polling vs WebSocket",
            "Long polling holds each request until news arrives, then re-asks. A WebSocket stays open and either side sends at any time.")
    d.text(200, 20, "Long polling", "title"); d.text(610, 20, "WebSocket", "title")
    d.line(100, 36, 100, 290); d.line(300, 36, 300, 290)
    d.arrow([(100, 60), (300, 70)], kind="blue", label="GET /events?after=41", lx=200, ly=48)
    d.box(130, 90, 140, 36, ("server holds ... 12 s", "small"), "amber")
    d.arrow([(300, 150), (100, 160)], kind="green", label="event 42", lx=200, ly=140)
    d.arrow([(100, 190), (300, 200)], kind="blue", label="GET /events?after=42", lx=200, ly=178)
    d.box(130, 220, 140, 36, ("held again ...", "small"), "amber")
    d.line(510, 36, 510, 290); d.line(710, 36, 710, 290)
    d.arrow([(510, 60), (710, 70)], kind="blue", label="upgrade (once)", lx=610, ly=48)
    d.arrow([(710, 110), (510, 120)], kind="green", label="event 42", lx=610, ly=100)
    d.arrow([(710, 160), (510, 170)], kind="green", label="event 43", lx=610, ly=150)
    d.arrow([(510, 210), (710, 220)], kind="blue", label="client message", lx=610, ly=200)
    d.render()


@diagram
def batch_vs_stream():
    d = new("batch-vs-stream", 800, 300, "Batch vs stream",
            "Batch collects data and processes it on a schedule. Stream processes each event as it arrives.")
    d.text(200, 20, "Batch", "title"); d.text(610, 20, "Stream", "title")
    d.box(10, 100, 100, 60, ["Data piles", "up all day"], "blue")
    d.arrow([(110, 130), (170, 130)]); d.box(170, 90, 90, 80, [("Job at", "small"), ("2 am", "small")], "purple")
    d.arrow([(260, 130), (310, 130)]); d.box(310, 100, 90, 60, ["Report", "next morning"], "green")
    for i, y in enumerate((60, 110, 160)):
        d.circle(450, y + 20, 10, "circle-a")
    d.arrow([(470, 130), (540, 130)]); d.box(540, 90, 110, 80, [("Stream", "bold"), ("processor", "small")], "purple")
    d.arrow([(650, 130), (690, 130)]); d.box(690, 100, 90, 60, ["Live", "result"], "green")
    d.text(200, 220, "high throughput, hours of latency", "small"); d.text(610, 220, "seconds of latency, harder to build", "small")
    d.render()


@diagram
def stateful_vs_stateless():
    d = new("stateful-vs-stateless", 800, 320, "Where the state lives",
            "Stateful servers hold the cart in memory so the user must return to the same one. Stateless servers share one store, so any server works.")
    d.text(200, 20, "Stateful", "title"); d.text(610, 20, "Stateless", "title")
    d.box(10, 130, 70, 40, "User", "blue")
    d.box(140, 60, 170, 50, [("Server A", "bold"), ("cart in memory", "small")], "amber")
    d.box(140, 190, 170, 50, [("Server B", "bold"), ("empty!", "small")], "red")
    d.arrow([(80, 145), (140, 85)]); d.arrow([(80, 155), (140, 215)], dashed=True, kind="red")
    d.box(430, 130, 70, 40, "User", "blue")
    d.box(550, 40, 130, 44, "Server A", "green"); d.box(550, 130, 130, 44, "Server B", "green"); d.box(550, 220, 130, 44, "Server C", "green")
    for y in (62, 152, 242):
        d.arrow([(500, 150), (550, y)])
    d.box(710, 110, 80, 80, [("Redis", "bold"), ("DB", "small")], "purple")
    for y in (62, 152, 242):
        d.arrow([(680, y), (710, 150)], dashed=True)
    d.render()


@diagram
def strong_vs_eventual():
    d = new("strong-vs-eventual", 800, 320, "What a reader sees after a write",
            "Strong consistency waits for all copies. Eventual consistency answers fast and lets copies catch up.")
    d.text(200, 20, "Strong", "title"); d.text(610, 20, "Eventual", "title")
    d.box(40, 120, 90, 50, ["Write x=2"], "blue")
    for i, y in enumerate((50, 130, 210)):
        d.box(250, y, 120, 40, "copy: x=2", "green")
        d.arrow([(130, 145), (250, y + 20)])
    d.text(210, 270, "ack only after all copies update: slower, never stale", "small")
    d.box(440, 120, 90, 50, ["Write x=2"], "blue")
    d.box(660, 50, 120, 40, "copy: x=2", "green"); d.box(660, 130, 120, 40, "copy: x=1", "amber"); d.box(660, 210, 120, 40, "copy: x=1", "amber")
    d.arrow([(530, 145), (660, 70)]); d.arrow([(530, 145), (660, 150)], dashed=True); d.arrow([(530, 145), (660, 230)], dashed=True)
    d.text(610, 270, "ack at once: fast, may read stale for a moment", "small")
    d.render()


@diagram
def read_write_through():
    d = new("read-write-through", 800, 300, "Read-through and write-through",
            "The app talks only to the cache. On a read miss the cache loads from the database. On a write it updates both together.")
    d.box(10, 110, 100, 60, "App", "blue")
    d.box(260, 100, 160, 80, [("Cache layer", "bold"), ("loader + writer", "small")], "amber")
    d.box(580, 110, 160, 60, "Database", "red")
    d.arrow([(110, 130), (260, 130)], label="get / put", lx=185, ly=112)
    d.arrow([(420, 125), (580, 125)], kind="blue", dashed=True, label="read miss: load", lx=500, ly=107)
    d.arrow([(420, 160), (580, 160)], kind="red", label="write: sync both", lx=500, ly=182)
    d.text(400, 250, "Read-through helps reads. Write-through keeps the cache fresh at the cost of slower writes.", "small")
    d.render()


@diagram
def push_vs_pull():
    d = new("push-vs-pull", 800, 300, "Push vs pull",
            "Push: the producer sends as soon as data exists. Pull: the consumer asks when it is ready.")
    d.text(200, 20, "Push", "title"); d.text(610, 20, "Pull", "title")
    d.box(20, 110, 100, 50, "Producer", "blue"); d.box(280, 110, 100, 50, "Consumer", "green")
    d.arrow([(120, 135), (280, 135)], kind="blue", label="data, immediately", lx=200, ly=118)
    d.text(200, 200, "can overwhelm a slow consumer", "small")
    d.box(430, 110, 100, 50, "Producer", "blue"); d.box(690, 110, 100, 50, "Consumer", "green")
    d.arrow([(690, 125), (530, 125)], kind="green", label="any new data?", lx=610, ly=108)
    d.arrow([(530, 150), (690, 150)], kind="blue", label="here is a batch", lx=610, ly=172)
    d.text(610, 200, "consumer controls the pace", "small")
    d.text(400, 260, "Feeds: push for normal users, pull for celebrity accounts (a hybrid).", "small")
    d.render()


@diagram
def rest_vs_rpc():
    d = new("rest-vs-rpc", 800, 300, "REST resources vs RPC functions",
            "REST names things and uses the same few verbs. RPC names actions as functions on a service.")
    d.text(200, 20, "REST: nouns", "title"); d.text(610, 20, "RPC: verbs", "title")
    for i, t in enumerate(("GET    /orders/42", "PATCH  /orders/42", "DELETE /orders/42", "POST   /orders/42/cancel")):
        d.box(20, 45 + i * 52, 360, 40, (t, "code"), "green")
    for i, t in enumerate(("OrderService.GetOrder(42)", "OrderService.CancelOrder(42)", "OrderService.WatchOrders()", "binary Protobuf over HTTP/2")):
        d.box(430, 45 + i * 52, 350, 40, (t, "code"), "blue" if i < 3 else "purple")
    d.text(200, 275, "cacheable, universal, browser-friendly", "small"); d.text(610, 275, "fast, typed, streaming, internal", "small")
    d.render()


@diagram
def sync_vs_async():
    d = new("sync-vs-async", 800, 340, "Synchronous vs asynchronous",
            "In sync the caller waits through every call. In async the caller returns early and slow work finishes later via a queue.")
    d.text(200, 14, "Synchronous", "title"); d.text(610, 14, "Asynchronous", "title")
    for x in (80, 200, 320, 480, 600, 720):
        d.line(x, 60, x, 320)
    d.text(80, 46, "User", "small"); d.text(200, 46, "API", "small"); d.text(320, 46, "Email svc", "small")
    d.arrow([(80, 90), (200, 98)]); d.arrow([(200, 120), (320, 128)], label="send email", lx=262, ly=112)
    d.box(210, 145, 180, 30, ("user waits 800 ms...", "small"), "amber")
    d.arrow([(320, 195), (200, 203)], kind="green"); d.arrow([(200, 220), (80, 228)], kind="green", label="reply", lx=140, ly=247)
    d.text(480, 46, "User", "small"); d.text(600, 46, "API + queue", "small"); d.text(720, 46, "Worker", "small")
    d.arrow([(480, 90), (600, 98)]); d.arrow([(600, 120), (480, 128)], kind="green", label="reply at once", lx=540, ly=146)
    d.arrow([(600, 175), (720, 183)], dashed=True, label="later", lx=660, ly=167)
    d.box(630, 200, 150, 30, ("worker sends email", "small"), "green")
    d.render()


# ---------------------------------------------------------------- case-study and earlier diagrams in the same style
@diagram
def cdn():
    d = new("cdn", 800, 300, "CDN edge and origin",
            "Users are routed to the nearest edge. A hit is answered there. A miss goes through a shield cache to the origin.")
    d.box(10, 130, 110, 60, ["Users", "(Chennai)"], "blue")
    d.box(10, 30, 150, 44, "DNS / anycast", "purple")
    d.arrow([(65, 130), (65, 74)], label="1 which edge?", lx=150, ly=102)
    d.box(280, 120, 150, 60, [("Edge: Chennai", "bold")], "amber")
    d.box(280, 215, 150, 50, "Edge: Frankfurt", "amber")
    d.box(520, 120, 130, 60, [("Origin shield", "bold")], "green")
    d.box(690, 120, 100, 60, [("Origin", "bold")], "red")
    d.arrow([(120, 150), (280, 150)], label="2 GET", lx=200, ly=134)
    d.arrow([(280, 170), (120, 170)], kind="green", dashed=True, label="hit: answered here", lx=200, ly=190)
    d.arrow([(430, 150), (520, 150)], dashed=True, label="3 miss", lx=475, ly=134)
    d.arrow([(650, 150), (690, 150)], dashed=True)
    d.text(400, 288, "A 97% hit rate means the origin sees only 3% of the traffic.", "small")
    d.render()


@diagram
def queue():
    d = new("queue", 800, 270, "A message queue between services",
            "The producer returns at once. Workers drain the queue at their own pace and can be added when it grows.")
    d.box(10, 100, 130, 60, [("Producer", "bold"), ("API server", "small")], "blue")
    d.box(250, 110, 270, 50, ("Queue   [ m1 | m2 | m3 | m4 ]", "code"), "amber")
    d.arrow([(140, 130), (250, 130)], label="publish", lx=195, ly=112)
    for i, y in enumerate((30, 105, 180)):
        d.box(620, y, 150, 44, f"Worker {i + 1}", "green")
        d.arrow([(520, 135), (620, y + 22)])
    d.box(250, 195, 270, 44, [("Dead-letter queue", "small"), ("messages that keep failing", "small")], "red")
    d.arrow([(385, 160), (385, 195)], dashed=True)
    d.text(400, 255, "Watch queue depth and age of the oldest message.", "small")
    d.render()


@diagram
def load_balancer():
    d = new("load-balancer", 800, 300, "Inside a load balancer",
            "A redundant pair fronts the servers. A health checker removes failed servers from the pool.")
    d.box(10, 110, 90, 50, "Clients", "blue")
    d.box(160, 30, 150, 50, ["LB (active)"], "purple")
    d.box(160, 190, 150, 50, ["LB (standby)"], "purple")
    d.arrow([(100, 125), (160, 55)]); d.arrow([(100, 150), (160, 215)], dashed=True)
    d.arrow([(235, 80), (235, 190)], dashed=True, label="heartbeat", lx=290, ly=135)
    for i, (y, k, t) in enumerate(((20, "green", "Server 1"), (95, "green", "Server 2"), (170, "red", "Server 3 (down)"))):
        d.box(470, y, 170, 50, t, k)
        d.arrow([(310, 55), (470, y + 25)], dashed=(k == "red"))
    d.box(670, 95, 120, 50, ["Health", "checker"], "amber")
    d.arrow([(670, 120), (640, 120)], dashed=True, label="ping", lx=655, ly=100)
    d.render()


@diagram
def request_path():
    d = new("request-path", 800, 270, "The path of a request",
            "Each hop can answer early: browser cache, DNS cache, CDN, application cache. Otherwise the request travels on.")
    row(d, ["Browser", "DNS", "CDN", "Load balancer", "App servers"], 10, 100, 130, 60, 30, ["blue", "amber", "amber", "purple", "green"])
    d.box(520, 200, 110, 44, "Cache", "amber"); d.box(660, 200, 120, 44, "Database", "red")
    d.arrow([(720, 160), (590, 200)]); d.arrow([(720, 160), (720, 200)])
    d.render()


# ---------------------------------------------------------------- case-study diagrams
@diagram
def shortener():
    d = new("shortener", 800, 300, "URL shortener at a glance",
            "Clients reach stateless app servers through a load balancer. Reads check a cache, then a sharded store. An ID service hands out code ranges.")
    d.box(10, 110, 90, 50, "Client", "blue")
    d.box(150, 110, 120, 50, ["Load", "balancer"], "purple")
    d.box(320, 100, 130, 70, [("App servers", "bold"), ("stateless", "small")], "green")
    d.box(320, 220, 130, 50, [("ID service", "bold"), ("code ranges", "small")], "amber")
    d.box(540, 20, 150, 50, [("Cache", "bold"), ("Redis, LRU", "small")], "amber")
    d.box(540, 110, 150, 60, [("Sharded store", "bold"), ("hash(code)", "small")], "red")
    d.box(540, 220, 150, 50, [("Replicas", "bold"), ("3 zones", "small")], "red")
    d.arrow([(100, 135), (150, 135)]); d.arrow([(270, 135), (320, 135)])
    d.arrow([(450, 115), (540, 50)], label="1 hit?", lx=470, ly=70)
    d.arrow([(450, 140), (540, 140)], dashed=True, label="2 miss", lx=495, ly=124)
    d.arrow([(385, 170), (385, 220)]); d.arrow([(615, 170), (615, 220)], dashed=True)
    d.render()


@diagram
def autocomplete():
    d = new("autocomplete", 800, 300, "Autocomplete: serving path and data pipeline",
            "The serving path (top) is read-only and fast. The pipeline (bottom) rebuilds the trie offline and swaps it in.")
    d.text(400, 18, "Serving path", "title")
    d.box(10, 40, 100, 50, "Browser", "blue")
    d.box(160, 40, 140, 50, [("CDN", "bold"), ("hot prefixes", "small")], "purple")
    d.box(350, 40, 150, 50, [("Suggestion", "bold"), ("service", "small")], "green")
    d.box(550, 20, 110, 40, "Prefix cache", "amber")
    d.box(550, 75, 110, 40, ["Trie in memory"], "red")
    d.box(690, 45, 100, 60, ["top-k per", "node"], "box")
    d.arrow([(110, 65), (160, 65)], label="'ho'", lx=135, ly=48)
    d.arrow([(300, 65), (350, 65)])
    d.arrow([(500, 55), (550, 40)]); d.arrow([(500, 80), (550, 95)], dashed=True)
    d.arrow([(660, 95), (690, 85)], head=False)
    d.text(400, 150, "Data pipeline (offline)", "title")
    d.box(10, 175, 120, 50, ["Search logs", "(stream)"], "blue")
    d.box(180, 175, 140, 50, [("Aggregator", "bold"), ("counts + decay", "small")], "green")
    d.box(370, 175, 140, 50, [("Trie builder", "bold"), ("validate", "small")], "green")
    d.box(560, 175, 120, 50, ["Snapshot", "(object store)"], "amber")
    d.arrow([(130, 200), (180, 200)]); d.arrow([(320, 200), (370, 200)]); d.arrow([(510, 200), (560, 200)])
    d.arrow([(620, 175), (605, 115)], dashed=True, label="load + atomic swap", lx=700, ly=150)
    d.text(400, 270, "Never update the live trie in place: build a new one, validate it, then swap.", "small")
    d.render()


@diagram
def parking_garage():
    d = new("parking-garage", 800, 300, "Parking garage classes",
            "Each class owns its own rules: a Spot knows what fits, a PricingPolicy knows the price, the lot coordinates.")
    d.box(20, 30, 150, 70, [("ParkingLot", "bold"), ("park() / unpark()", "small")], "green")
    d.box(230, 30, 130, 70, [("Floor", "bold"), ("find + reserve", "small")], "green")
    d.box(430, 30, 140, 70, [("Spot", "bold"), ("size, can_fit()", "small")], "amber")
    d.box(630, 30, 150, 70, [("Vehicle", "bold"), ("required size", "small")], "blue")
    d.arrow([(170, 65), (230, 65)], label="has", lx=200, ly=48)
    d.arrow([(360, 65), (430, 65)], label="many", lx=395, ly=48)
    d.arrow([(630, 65), (570, 65)], label="fits", lx=600, ly=48)
    d.box(20, 170, 150, 70, [("Ticket", "bold"), ("vehicle, spot, time", "small")], "red")
    d.box(230, 170, 190, 70, [("PricingPolicy", "bold"), ("Hourly, Flat (Strategy)", "small")], "purple")
    d.box(480, 170, 130, 70, [("Payment", "bold"), ("must succeed", "small")], "red")
    d.box(660, 170, 120, 70, [("Display", "bold"), ("free per floor", "small")], "box")
    d.arrow([(95, 100), (95, 170)], label="issues", lx=130, ly=135)
    d.arrow([(170, 205), (230, 205)], label="fee", lx=200, ly=188)
    d.arrow([(420, 205), (480, 205)])
    d.arrow([(295, 100), (720, 170)], dashed=True)
    d.text(400, 275, "Subclasses of Vehicle: Motorcycle, Car, Truck. Spot assignment is atomic (a lock or a conditional update).", "small")
    d.render()


@diagram
def vending_machine():
    d = new("vending-machine", 800, 290, "Vending machine state machine",
            "Each arrow is an event. Anything not drawn, such as selecting with no money, is rejected in that state.")
    d.box(20, 110, 130, 60, [("Idle", "bold"), ("no money", "small")], "blue")
    d.box(230, 110, 150, 60, [("HasMoney", "bold"), ("balance > 0", "small")], "amber")
    d.box(460, 110, 150, 60, [("Dispensing", "bold"), ("motor running", "small")], "green")
    d.box(660, 110, 120, 60, [("Idle", "bold"), ("change returned", "small")], "blue")
    d.arrow([(150, 140), (230, 140)], label="insert coin", lx=190, ly=122)
    d.arrow([(380, 140), (460, 140)], label="select (valid)", lx=420, ly=122)
    d.arrow([(610, 140), (660, 140)], label="done", lx=635, ly=122)
    d.arrow([(305, 110), (305, 60), (85, 60), (85, 110)], label="cancel: refund", lx=195, ly=45)
    d.arrow([(305, 170), (305, 230)], dashed=True, kind="red")
    d.box(180, 230, 250, 40, ("sold out / no change: reject, stay in HasMoney", "small"), "red")
    d.box(470, 220, 300, 55, [("OutOfService", "bold"), ("jam, power loss: refund and flag", "small")], "red")
    d.arrow([(535, 170), (535, 220)], dashed=True, kind="red")
    d.render()


@diagram
def key_value_store():
    d = new("key-value-store", 800, 320, "Distributed key-value store",
            "A coordinator sends each write to the 3 replicas on the ring and waits for a quorum. Down nodes are covered by hints and repair.")
    d.box(10, 130, 90, 50, "Client", "blue")
    d.box(150, 120, 140, 70, [("Coordinator", "bold"), ("any node", "small")], "green")
    d.arrow([(100, 155), (150, 155)], label="put(k, v)", lx=125, ly=138)
    d.box(380, 20, 180, 50, [("Replica 1", "bold"), ("ack", "small")], "red")
    d.box(380, 130, 180, 50, [("Replica 2", "bold"), ("ack", "small")], "red")
    d.box(380, 240, 180, 50, [("Replica 3", "bold"), ("down: hint stored", "small")], "box")
    d.arrow([(290, 135), (380, 45)]); d.arrow([(290, 155), (380, 155)]); d.arrow([(290, 175), (380, 265)], dashed=True)
    d.box(620, 20, 170, 60, [("Hash ring", "bold"), ("virtual nodes", "small")], "purple")
    d.box(620, 110, 170, 80, [("Repair", "bold"), ("hinted handoff", "small"), ("read repair, Merkle", "small")], "amber")
    d.box(620, 220, 170, 70, [("Membership", "bold"), ("gossip + heartbeats", "small")], "amber")
    d.text(200, 230, "N=3, W=2, R=2: R + W > N", "bold"); d.text(200, 255, "so reads overlap the latest write", "small")
    d.render()


@diagram
def distributed_cache():
    d = new("distributed-cache", 800, 340, "A sharded and replicated cache cluster",
            "The client library hashes the key to a shard. Each shard has a replica. On a miss the app reads the database and fills the cache.")
    d.box(10, 120, 150, 70, [("App servers", "bold"), ("+ cache client", "small")], "green")
    d.box(230, 20, 190, 40, "Consistent hash ring", "purple")
    d.arrow([(160, 130), (300, 60)], dashed=True)
    for i, y in enumerate((90, 160, 230)):
        d.box(270, y, 130, 50, [(f"Shard {i + 1}", "bold"), ("LRU + TTL", "small")], "amber")
        d.arrow([(160, 155), (270, y + 25)])
        d.box(470, y, 110, 50, "Replica", "box")
        d.arrow([(400, y + 25), (470, y + 25)], dashed=True, label=("async" if i == 0 else None), lx=435, ly=y + 10)
    d.box(650, 135, 140, 70, [("Database", "bold"), ("source of truth", "small")], "red")
    d.arrow([(580, 185), (650, 175)], dashed=True, label="miss", lx=612, ly=160)
    d.box(10, 240, 200, 50, [("Local cache", "bold"), ("tiny, for hot keys", "small")], "blue")
    d.arrow([(85, 190), (85, 240)], dashed=True)
    d.text(400, 318, "Defend against stampede, penetration, avalanche and hot keys.", "small")
    d.render()


@diagram
def authentication():
    d = new("authentication", 800, 330, "Authentication: login once, verify everywhere",
            "The auth service verifies the password and issues short-lived tokens. The gateway verifies tokens locally on every request.")
    d.box(10, 130, 100, 60, ["User", "browser / app"], "blue")
    d.box(180, 20, 150, 50, [("Rate limiter", "bold")], "amber")
    d.box(180, 130, 150, 60, [("Auth service", "bold"), ("verify hash + MFA", "small")], "green")
    d.arrow([(110, 150), (180, 150)], label="1 login", lx=145, ly=132)
    d.arrow([(255, 70), (255, 130)], dashed=True)
    d.box(400, 40, 170, 60, [("User DB", "bold"), ("salted slow hashes", "small")], "red")
    d.box(400, 130, 170, 60, [("Token store", "bold"), ("refresh tokens, sessions", "small")], "red")
    d.box(400, 220, 170, 50, [("Audit log", "bold")], "box")
    d.arrow([(330, 140), (400, 75)]); d.arrow([(330, 160), (400, 160)]); d.arrow([(330, 175), (400, 245)], dashed=True)
    d.box(620, 130, 170, 60, [("API gateway", "bold"), ("verifies token locally", "small")], "purple")
    d.box(620, 230, 170, 50, [("Services", "bold")], "green")
    d.arrow([(110, 175), (180, 300), (620, 300), (700, 280)], dashed=True, kind="blue")
    d.text(400, 312, "2 every API call carries the access token", "small")
    d.arrow([(705, 190), (705, 230)])
    d.render()


@diagram
def upi():
    d = new("upi", 820, 320, "UPI payment flow",
            "The switch coordinates a debit at the payer bank and a credit at the payee bank, records everything and notifies both apps.")
    d.box(10, 120, 100, 60, ["Payer app"], "blue")
    d.box(160, 120, 120, 60, [("PSP bank", "bold"), ("app backend", "small")], "green")
    d.box(340, 110, 130, 80, [("UPI switch", "bold"), ("route + record", "small")], "purple")
    d.box(340, 20, 130, 50, [("VPA directory", "bold")], "box")
    d.box(340, 240, 130, 60, [("Ledger", "bold"), ("append-only", "small")], "amber")
    d.box(570, 20, 150, 60, [("Payer bank", "bold"), ("debit", "small")], "red")
    d.box(570, 220, 150, 60, [("Payee bank", "bold"), ("credit", "small")], "red")
    d.box(730, 120, 80, 60, ["Payee", "app"], "blue")
    d.arrow([(110, 150), (160, 150)], label="1 pay", lx=135, ly=132)
    d.arrow([(280, 150), (340, 150)], label="txn id", lx=310, ly=132)
    d.arrow([(405, 110), (405, 70)], dashed=True, label="resolve VPA", lx=465, ly=92)
    d.arrow([(470, 125), (570, 55)], label="2 debit", lx=505, ly=80)
    d.arrow([(470, 175), (570, 245)], label="3 credit", lx=510, ly=222)
    d.arrow([(405, 190), (405, 240)])
    d.arrow([(720, 250), (770, 180)], dashed=True, label="4 notify", lx=775, ly=222)
    d.text(130, 250, "timeout = unknown: reconcile", "small"); d.text(130, 272, "with the same transaction id", "small")
    d.render()


@diagram
def estimation():
    d = new("estimation", 800, 270, "The estimation recipe",
            "Turn events per day into requests per second, then into storage, memory and bandwidth. Finish every step with: so this means...")
    steps = [("Users or events / day", "100M links / month"), ("Divide by 86,400", "= per second"), ("Peak x 2-3", "plan for the spike"),
             ("Split read : write", "100 : 1"), ("x bytes per record", "storage per year"), ("Hot share of a day", "cache size")]
    for i, (a, b) in enumerate(steps):
        x = 15 + (i % 3) * 260
        y = 25 + (i // 3) * 100
        d.box(x, y, 240, 70, [(a, "bold"), (b, "small")], ["blue", "blue", "amber", "amber", "green", "green"][i])
        if i % 3:
            d.arrow([(x - 20, y + 35), (x, y + 35)])
    d.arrow([(255, 75), (255, 95), (135, 95), (135, 125)], head=False)
    d.text(400, 235, "Round aggressively: 86,400 is about 100,000. Being within 2 to 3 times is good enough.", "small")
    d.render()


@diagram
def snowflake():
    d = new("snowflake", 800, 230, "A Snowflake-style 64-bit ID",
            "Time in the high bits makes IDs roughly sortable. Machine id and a per-millisecond sequence make them unique with no coordination.")
    d.box(20, 60, 60, 50, ["0", "sign"], "box")
    d.box(90, 60, 440, 50, [("41 bits: milliseconds since a custom epoch", "bold"), ("about 69 years", "small")], "blue")
    d.box(540, 60, 110, 50, [("10 bits", "bold"), ("machine id", "small")], "green")
    d.box(660, 60, 120, 50, [("12 bits", "bold"), ("sequence", "small")], "amber")
    d.text(400, 150, "4,096 ids per millisecond per machine, 1,024 machines, sortable by creation time", "small")
    d.text(400, 185, "Needs: unique machine ids, and a clock that never goes backwards.", "small")
    d.render()


if __name__ == "__main__":
    for fn in REGISTRY:
        fn()
    print(f"wrote {len(REGISTRY)} diagrams to {HERE}")
