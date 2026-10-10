"""Diagrams for the AWS Solutions Architect (SAA-C03) course.

Each function below writes one diagrams/<name>.html file: an inline SVG <figure> that pages include with

    ```{raw} html
    :file: ../diagrams/<name>.html
    ```

Colours come from the .dg / figure.diagram classes in the docs CSS (courses/builder.py), so diagrams follow
light and dark mode. Edit a function, then run:  python course_content/aws-solutions-architect/diagrams/make_diagrams.py
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


# ------------------------------------------------------------------ Session 1 · Introduction
@diagram
def s01_global():
    d = D("s01-global", 720, 275, "AWS global infrastructure",
          "A Region is a geographic area with several isolated Availability Zones (each one or more data centres). "
          "Edge locations sit closer to users for CloudFront and Route 53.")
    d.rect(20, 20, 470, 240, "blue", rx=14)
    d.text(255, 40, "Region: ap-south-1 (Mumbai)", "bold")
    for i, az in enumerate(["ap-south-1a", "ap-south-1b", "ap-south-1c"]):
        x = 40 + i * 150
        d.box(x, 60, 135, 170, [], "box")
        d.text(x + 67, 80, "Availability Zone", "small")
        d.text(x + 67, 100, az, "code")
        d.box(x + 15, 120, 105, 40, ("data centre", "small"), "green")
        d.box(x + 15, 172, 105, 40, ("data centre", "small"), "green")
    d.line(175, 140, 190, 140); d.line(325, 140, 340, 140)
    d.text(255, 246, "AZs: separate power and network, joined by fast private links", "small")
    d.box(520, 60, 180, 70, ["Edge location", ("Chennai, Bengaluru…", "small")], "amber")
    d.box(520, 150, 180, 70, ["Edge location", ("close to users", "small")], "amber")
    d.text(610, 245, "CloudFront · Route 53", "small")
    return d.render()


@diagram
def s01_shared():
    d = D("s01-shared", 720, 230, "The shared responsibility model",
          "AWS secures the cloud itself. You secure everything you put in it: data, identities, OS patches and network rules.")
    d.box(20, 20, 680, 95, [], "green")
    d.text(360, 42, "YOU: security IN the cloud", "bold")
    for i, t in enumerate(["Your data", "IAM users & keys", "OS patches", "Security groups", "Encryption"]):
        d.box(35 + i * 133, 60, 125, 40, (t, "small"), "box")
    d.box(20, 125, 680, 95, [], "blue")
    d.text(360, 147, "AWS: security OF the cloud", "bold")
    for i, t in enumerate(["Data centres", "Hardware", "Network", "Hypervisor", "Regions & AZs"]):
        d.box(35 + i * 133, 165, 125, 40, (t, "small"), "box")
    return d.render()


# ------------------------------------------------------------------ Session 2 · IAM
@diagram
def s02_iam():
    d = D("s02-iam", 720, 280, "IAM building blocks",
          "Policies give permissions. Attach them to groups (for people) or roles (for services and other accounts). "
          "A role hands out temporary credentials.")
    d.box(20, 30, 150, 90, ["Users", ("arun, priya", "small"), ("long-term login", "small")], "blue")
    d.arrow([(170, 75), (238, 75)], label="member of", lx=204, ly=62)
    d.box(240, 30, 170, 90, ["Group", ("developers", "code")], "blue")
    d.arrow([(410, 75), (488, 75)], label="attached", lx=449, ly=62)
    d.box(490, 30, 210, 90, ["Policy (JSON)", ("Allow s3:GetObject", "code"), ("on arn:aws:s3:::reports/*", "small")], "green")
    d.box(20, 170, 150, 90, ["EC2 / Lambda", ("or another", "small"), ("AWS account", "small")], "amber")
    d.arrow([(170, 215), (238, 215)], label="assumes", lx=204, ly=202)
    d.box(240, 170, 170, 90, ["Role", ("app-reads-s3", "code"), ("no password", "small")], "purple")
    d.arrow([(410, 215), (488, 215)], label="via STS", lx=449, ly=202)
    d.box(490, 170, 210, 90, ["Temporary credentials", ("expire automatically", "small"), ("(minutes to hours)", "small")], "green")
    d.arrow([(595, 168), (595, 122)], dashed=True)
    return d.render()


@diagram
def s02_evaluation():
    d = D("s02-evaluation", 720, 230, "How IAM decides allow or deny",
          "Everything starts as denied. An explicit Allow grants access, but any explicit Deny anywhere always wins.")
    d.box(20, 85, 140, 60, ["Request", ("s3:DeleteObject", "small")], "box")
    d.arrow([(160, 115), (198, 115)])
    d.box(200, 80, 150, 70, ["Explicit Deny", ("in any policy?", "small")], "amber")
    d.arrow([(275, 80), (275, 40), (548, 40)], "red", label="yes", lx=410, ly=28)
    d.box(550, 15, 150, 50, ("DENY", "bold"), "red")
    d.arrow([(350, 115), (388, 115)], label="no", lx=369, ly=102)
    d.box(390, 80, 140, 70, ["Explicit Allow", ("anywhere?", "small")], "amber")
    d.arrow([(530, 115), (548, 115)], "green")
    d.box(550, 90, 150, 50, ("ALLOW", "bold"), "green")
    d.text(560, 82, "yes", "small")
    d.arrow([(460, 150), (460, 190), (548, 190)], "red", label="no", lx=500, ly=178)
    d.box(550, 165, 150, 50, ["DENY", ("(implicit)", "small")], "red")
    return d.render()


# ------------------------------------------------------------------ Sessions 4-5 · Load balancing
@diagram
def s04_haproxy():
    d = D("s04-haproxy", 720, 270, "A load balancer in front of three app servers",
          "Clients only know the load balancer's address. It spreads requests across healthy servers and skips any that fail the health check.")
    for i in range(3):
        d.box(20, 30 + i * 75, 110, 55, ("client", "small"), "box")
        d.arrow([(130, 57 + i * 75), (238, 135)])
    d.box(240, 85, 200, 100, ["HAProxy", ("frontend :80", "code"), ("roundrobin", "code")], "blue")
    names = [("app1 :5001", "green", "healthy ✓"), ("app2 :5002", "green", "healthy ✓"), ("app3 :5003", "red", "down ✗")]
    for i, (n, kind, h) in enumerate(names):
        y = 30 + i * 75
        d.box(540, y, 160, 55, [(n, "code"), (h, "small")], kind)
        if kind == "red":
            d.arrow([(440, 135), (538, y + 27)], "red", dashed=True)
        else:
            d.arrow([(440, 135), (538, y + 27)], "green")
    d.text(490, 255, "health check every 2 s: GET /health", "small")
    return d.render()


@diagram
def s05_alb():
    d = D("s05-alb", 720, 300, "An Application Load Balancer across two AZs",
          "The ALB listener on 443 checks its rules: /api goes to one target group, everything else to another. "
          "Targets live in two Availability Zones, so one AZ can fail.")
    d.box(20, 115, 110, 60, ["Users", ("HTTPS", "small")], "box")
    d.arrow([(130, 145), (178, 145)])
    d.box(180, 90, 180, 110, ["ALB", ("listener :443", "code"), ("rule: /api/* → api", "small"), ("default → web", "small")], "blue")
    d.arrow([(360, 120), (438, 70)], "green", label="/api/*", lx=395, ly=80)
    d.arrow([(360, 170), (438, 220)], "green", label="default", lx=392, ly=212)
    d.box(440, 20, 260, 110, [], "green")
    d.text(570, 38, "Target group: api", "bold")
    d.box(455, 55, 110, 55, ["EC2", ("AZ a", "small")], "box")
    d.box(575, 55, 110, 55, ["EC2", ("AZ b", "small")], "box")
    d.box(440, 165, 260, 110, [], "green")
    d.text(570, 183, "Target group: web", "bold")
    d.box(455, 200, 110, 55, ["EC2", ("AZ a", "small")], "box")
    d.box(575, 200, 110, 55, ["EC2", ("AZ b", "small")], "box")
    return d.render()


@diagram
def s05_types():
    d = D("s05-types", 720, 220, "The three Elastic Load Balancer types",
          "Pick by what you need to see in the traffic: HTTP details (ALB), raw TCP/UDP speed (NLB) or security appliances (GWLB).")
    cols = [("ALB", "Layer 7 · HTTP/HTTPS", ["path & host routing", "targets: EC2, IP, Lambda", "WAF, auth, redirects"], "blue"),
            ("NLB", "Layer 4 · TCP/UDP/TLS", ["millions of req/sec", "static IP per AZ", "lowest latency"], "green"),
            ("GWLB", "Layer 3 · IP packets", ["firewalls / IDS appliances", "GENEVE port 6081", "transparent bump-in-wire"], "purple")]
    for i, (name, layer, lines, kind) in enumerate(cols):
        x = 20 + i * 235
        d.box(x, 20, 215, 60, [(name, "bold"), (layer, "small")], kind)
        d.box(x, 90, 215, 110, [(l, "small") for l in lines], "box")
    return d.render()


# ------------------------------------------------------------------ Session 6 · EC2 storage & access
@diagram
def s06_ebs():
    d = D("s06-ebs", 720, 250, "EBS volumes and snapshots",
          "An EBS volume lives in one AZ and attaches to an instance there. A snapshot is stored in S3 (managed by AWS) "
          "and can create a new volume in any AZ, even another Region.")
    d.rect(20, 20, 300, 210, "blue", rx=14); d.text(170, 40, "AZ ap-south-1a", "bold")
    d.box(40, 60, 120, 70, ["EC2", ("/dev/xvda", "code")], "box")
    d.box(180, 60, 120, 70, ["EBS gp3", ("20 GiB", "small")], "green")
    d.line(160, 95, 180, 95)
    d.box(40, 150, 260, 60, ["EBS volume /data", ("attach · mkfs · mount", "code")], "green")
    d.arrow([(300, 180), (383, 180)], label="snapshot", lx=342, ly=166)
    d.box(385, 140, 135, 80, ["Snapshot", ("incremental", "small"), ("stored in S3", "small")], "amber")
    d.arrow([(520, 180), (583, 180)], label="restore", lx=552, ly=166)
    d.rect(585, 20, 115, 210, "purple", rx=14); d.text(642, 40, "AZ 1b", "bold")
    d.box(595, 140, 95, 80, ["new EBS", ("volume", "small")], "green")
    return d.render()


@diagram
def s06_role():
    d = D("s06-role", 720, 200, "An instance role instead of access keys",
          "The app asks the instance metadata service for temporary credentials of the attached role. "
          "Nothing is stored on disk, and the keys rotate by themselves.")
    d.box(20, 50, 200, 100, ["EC2 instance", ("app: boto3 / aws cli", "small"), ("no keys on disk", "small")], "blue")
    d.arrow([(220, 80), (298, 80)], label="1 · ask", lx=259, ly=67)
    d.box(300, 40, 180, 80, ["Metadata service", ("169.254.169.254", "code"), ("(IMDSv2)", "small")], "amber")
    d.arrow([(298, 112), (222, 118)], label="2 · temp keys", lx=259, ly=101)
    d.arrow([(220, 140), (300, 175), (520, 175)], "green", label="3 · call with temp keys", lx=400, ly=163)
    d.box(520, 40, 180, 160, ["Role", ("app-reads-s3", "code"), ("policy: s3:GetObject", "small"), ("→ Amazon S3", "bold")], "green")
    return d.render()


# ------------------------------------------------------------------ Sessions 7-8 · VPC, subnets, NAT
@diagram
def s07_vpc():
    d = D("s07-vpc", 720, 300, "A VPC with a public and a private subnet",
          "A subnet is public only because its route table sends 0.0.0.0/0 to the Internet Gateway. "
          "The private subnet has only the local route, so the internet can't reach it.")
    d.box(280, 10, 160, 40, "Internet", "box")
    d.line(360, 50, 360, 70)
    d.box(290, 70, 140, 34, ("Internet Gateway", "small"), "amber")
    d.rect(20, 115, 680, 175, "blue", rx=14); d.text(110, 133, "VPC 10.0.0.0/16", "bold")
    d.rect(40, 145, 310, 130, "green", rx=10); d.text(195, 163, "Public subnet 10.0.1.0/24", "bold")
    d.box(55, 175, 120, 50, ["web EC2", ("public IP", "small")], "box")
    d.box(180, 175, 162, 85, [("route table", "small"), ("10.0.0.0/16 → local", "code"), ("0.0.0.0/0 → igw", "code")], "box")
    d.rect(370, 145, 310, 130, "purple", rx=10); d.text(525, 163, "Private subnet 10.0.2.0/24", "bold")
    d.box(385, 175, 120, 50, ["app / db", ("private IP only", "small")], "box")
    d.box(510, 175, 162, 85, [("route table", "small"), ("10.0.0.0/16 → local", "code"), ("(no internet)", "small")], "box")
    d.line(360, 104, 360, 145, "line")
    d.arrow([(115, 225), (115, 268), (445, 268), (445, 227)], "green", label="local", lx=360, ly=256)
    return d.render()


@diagram
def s08_nat():
    d = D("s08-nat", 720, 260, "Outbound internet for a private subnet with a NAT Gateway",
          "The private instance sends internet traffic to the NAT Gateway in the public subnet. Replies come back, "
          "but nobody on the internet can start a connection to the private instance.")
    d.rect(20, 20, 520, 220, "blue", rx=14); d.text(100, 38, "VPC 10.0.0.0/16", "bold")
    d.rect(40, 55, 230, 165, "purple", rx=10); d.text(155, 73, "Private subnet", "bold")
    d.box(55, 90, 200, 60, ["app EC2 10.0.2.15", ("apt update / pip install", "small")], "box")
    d.box(55, 160, 200, 50, [("0.0.0.0/0 → nat-gw", "code")], "box")
    d.rect(290, 55, 230, 165, "green", rx=10); d.text(405, 73, "Public subnet", "bold")
    d.box(305, 90, 200, 60, ["NAT Gateway", ("Elastic IP 13.x.x.x", "small")], "amber")
    d.box(305, 160, 200, 50, [("0.0.0.0/0 → igw", "code")], "box")
    d.arrow([(255, 120), (303, 120)], "green")
    d.box(570, 95, 130, 50, ("Internet GW", "small"), "amber")
    d.arrow([(505, 120), (568, 120)], "green")
    d.text(635, 175, "internet → private:", "small"); d.text(635, 193, "blocked ✗", "small")
    return d.render()


# ------------------------------------------------------------------ Sessions 9-11 · Connecting VPCs
@diagram
def s09_peering():
    d = D("s09-peering", 720, 230, "VPC peering is not transitive",
          "A↔B and B↔C are peered, but A still can't reach C through B. Every pair that must talk needs its own peering "
          "and routes on both sides, and CIDR ranges must not overlap.")
    vpcs = [("VPC A", "10.0.0.0/16", 20), ("VPC B", "10.1.0.0/16", 270), ("VPC C", "10.2.0.0/16", 520)]
    for name, cidr, x in vpcs:
        d.box(x, 40, 180, 80, [name, (cidr, "code")], "blue")
    d.arrow([(200, 80), (268, 80)], "green", label="pcx-ab", lx=234, ly=67)
    d.arrow([(268, 80), (200, 80)], "green")
    d.arrow([(450, 80), (518, 80)], "green", label="pcx-bc", lx=484, ly=67)
    d.arrow([(518, 80), (450, 80)], "green")
    d.arrow([(110, 120), (110, 175), (610, 175), (610, 122)], "red", dashed=True, label="A → C through B: not allowed ✗", lx=360, ly=163)
    d.text(360, 210, "fix: peer A↔C directly, or use a Transit Gateway", "small")
    return d.render()


@diagram
def s10_tgw():
    d = D("s10-tgw", 720, 280, "Transit Gateway: one hub for many networks",
          "Each VPC (and the office VPN) attaches once to the Transit Gateway. The TGW route tables decide who can reach whom, "
          "and routing through the hub is transitive.")
    d.box(270, 105, 180, 70, ["Transit Gateway", ("route tables", "small")], "amber")
    spokes = [("VPC prod", 20, 20), ("VPC dev", 20, 200), ("VPC shared", 520, 20), ("Office", 520, 200)]
    for name, x, y in spokes:
        kind = "green" if name == "Office" else "blue"
        d.box(x, y, 180, 60, [name, ("VPN attachment" if name == "Office" else "VPC attachment", "small")], kind)
    d.arrow([(200, 50), (268, 120)]); d.arrow([(200, 230), (268, 160)])
    d.arrow([(520, 50), (452, 120)]); d.arrow([(520, 230), (452, 160)])
    d.text(360, 255, "4 attachments instead of 6 peering connections", "small")
    return d.render()


@diagram
def s11_endpoints():
    d = D("s11-endpoints", 720, 270, "Reaching AWS services privately with VPC endpoints",
          "A gateway endpoint (S3, DynamoDB) is a route in the route table and is free. An interface endpoint puts a private "
          "network card (ENI) in your subnet for almost any other service, using PrivateLink.")
    d.rect(20, 20, 420, 230, "blue", rx=14); d.text(120, 38, "VPC · private subnet", "bold")
    d.box(40, 60, 150, 60, ["app EC2", ("no internet", "small")], "box")
    d.box(40, 150, 180, 80, [("route table", "small"), ("pl-s3 → vpce-gw", "code"), ("(gateway endpoint)", "small")], "green")
    d.box(250, 150, 170, 80, ["Interface endpoint", ("ENI 10.0.2.40", "code"), ("private DNS", "small")], "purple")
    d.arrow([(190, 90), (558, 70)], "green", label="via gateway endpoint (free)", lx=310, ly=66)
    d.box(560, 40, 140, 60, ["Amazon S3", ("DynamoDB", "small")], "amber")
    d.arrow([(120, 120), (300, 148)])
    d.arrow([(420, 190), (558, 190)], label="PrivateLink", lx=490, ly=178)
    d.box(560, 160, 140, 60, ["SQS, SSM,", ("Secrets Mgr, ECR…", "small")], "amber")
    return d.render()


# ------------------------------------------------------------------ Sessions 12-13 · WAF, Flow Logs, DNS
@diagram
def s12_waf():
    d = D("s12-waf", 720, 250, "AWS WAF filters requests before your app sees them",
          "A Web ACL is attached to CloudFront, an ALB or API Gateway. Its rules run in priority order; the first match decides "
          "Allow or Block, and the default action handles the rest.")
    d.box(20, 40, 140, 55, ["Student", ("GET /courses", "small")], "box")
    d.box(20, 150, 140, 55, ["Attacker", ("' OR 1=1 --", "code")], "red")
    d.rect(200, 20, 280, 210, "amber", rx=14); d.text(340, 40, "Web ACL", "bold")
    rules = ["1 · IP block list", "2 · rate limit 300 / 5 min", "3 · SQL injection rules", "4 · common exploits (XSS…)", "default: Allow"]
    for i, r in enumerate(rules):
        d.box(215, 55 + i * 34, 250, 28, (r, "small"), "box")
    d.arrow([(160, 67), (198, 67)], "green")
    d.arrow([(160, 177), (198, 177)], "red")
    d.arrow([(480, 90), (548, 90)], "green", label="allowed", lx=514, ly=78)
    d.box(550, 60, 150, 60, ["ALB → app", ("only clean traffic", "small")], "green")
    d.arrow([(480, 160), (548, 170)], "red", label="blocked", lx=514, ly=182)
    d.box(550, 150, 150, 50, ("403 Forbidden", "bold"), "red")
    return d.render()


@diagram
def s13_dns():
    d = D("s13-dns", 720, 280, "How a name becomes an IP address",
          "The resolver asks the root, then the .com servers, then the domain's own (authoritative) servers, "
          "and caches the answer for the record's TTL.")
    d.box(20, 110, 130, 60, ["Browser", ("learn.example.com", "small")], "box")
    d.arrow([(150, 140), (218, 140)], label="1", lx=184, ly=128)
    d.box(220, 100, 160, 80, ["Resolver", ("ISP / 8.8.8.8 /", "small"), ("VPC .2 resolver", "small")], "blue")
    steps = [("Root server", "“ask .com”", 20), ("TLD .com", "“ask ns-1.awsdns…”", 105), ("Authoritative", "A 13.234.5.6", 190)]
    for i, (name, ans, y) in enumerate(steps):
        d.box(520, y, 180, 70, [name, (ans, "small")], "amber" if i < 2 else "green")
        d.arrow([(380, 140), (518, y + 35)], label=str(i + 2), lx=440 + i * 8, ly=y + 30 if i != 1 else 128)
    d.arrow([(220, 165), (150, 165)], "green", label="5 · IP (cached for TTL)", lx=185, ly=200)
    return d.render()


@diagram
def s13_flowlogs():
    d = D("s13-flowlogs", 720, 220, "VPC Flow Logs record who talked to whom",
          "Flow logs capture IP traffic metadata (not contents) for a VPC, subnet or network interface, "
          "and deliver it to CloudWatch Logs, S3 or Firehose.")
    d.box(20, 50, 170, 110, ["VPC / subnet /", "network interface", ("flow log on", "small")], "blue")
    d.arrow([(190, 105), (258, 105)])
    d.box(260, 30, 230, 150, [("one record:", "small"), ("10.0.1.5 → 10.0.2.9", "code"), ("port 5432 TCP", "code"),
                               ("bytes 4210", "code"), ("action REJECT", "code")], "amber")
    d.arrow([(490, 70), (548, 60)])
    d.arrow([(490, 140), (548, 150)])
    d.box(550, 30, 150, 55, ["CloudWatch Logs", ("search · alarms", "small")], "green")
    d.box(550, 125, 150, 55, ["Amazon S3", ("Athena queries", "small")], "green")
    return d.render()


# ------------------------------------------------------------------ Sessions 14-16 · Route 53, S3, API Gateway
@diagram
def s14_route53():
    d = D("s14-route53", 720, 260, "Pointing a domain to AWS with Route 53",
          "The registrar is told which name servers own the domain. Route 53's hosted zone then answers with records "
          "that point at your load balancer, bucket or server.")
    d.box(20, 30, 140, 70, ["Registrar", ("GoDaddy / R53", "small")], "box")
    d.arrow([(160, 65), (238, 65)], label="NS records", lx=199, ly=52)
    d.rect(240, 20, 260, 220, "amber", rx=14); d.text(370, 40, "Hosted zone example.com", "bold")
    recs = [("A (Alias) example.com → ALB", "green"), ("CNAME www → example.com", "box"),
            ("MX → mail provider", "box"), ("TXT → verification", "box")]
    for i, (r, k) in enumerate(recs):
        d.box(255, 55 + i * 44, 230, 36, (r, "small"), k)
    d.arrow([(485, 73), (548, 73)], "green")
    d.box(550, 40, 150, 65, ["ALB", ("→ EC2 targets", "small")], "blue")
    d.box(550, 130, 150, 90, [("routing policies:", "small"), ("simple · weighted", "small"), ("latency · failover", "small"), ("geolocation…", "small")], "box")
    return d.render()


@diagram
def s15_classes():
    d = D("s15-classes", 720, 250, "S3 storage classes: pay less for data you read less",
          "Moving right, storage gets cheaper but reading the data costs more or takes longer, and there's a minimum storage period.")
    classes = [("Standard", "hot data", "ms access"), ("Intelligent-", "Tiering", "auto moves"),
               ("Standard-IA", "monthly use", "30-day min"), ("One Zone-IA", "re-creatable", "1 AZ only"),
               ("Glacier", "Instant Retr.", "90-day min"), ("Glacier", "Flexible Retr.", "min–hours"),
               ("Glacier Deep", "Archive", "12–48 hours")]
    for i, (a, b, c) in enumerate(classes):
        x = 20 + i * 98
        d.box(x, 40, 92, 110, [(a, "small"), (b, "small"), (c, "small")], "blue" if i < 2 else ("green" if i < 4 else "purple"))
    d.arrow([(30, 185), (690, 185)], label="storage price per GB goes down →", lx=360, ly=173)
    d.arrow([(690, 220), (30, 220)], label="← cheaper and faster to read the data", lx=360, ly=208)
    return d.render()


@diagram
def s15_bucket():
    d = D("s15-bucket", 720, 200, "Buckets, objects and keys",
          "A bucket holds objects. Each object is the data plus metadata, found by its key. The “folders” you see in the console "
          "are just parts of the key.")
    d.rect(20, 20, 300, 160, "amber", rx=14); d.text(170, 40, "Bucket: parottasalna-notes", "bold")
    keys = ["2026/oct/notes.pdf", "2026/oct/diagram.png", "index.html"]
    for i, k in enumerate(keys):
        d.box(40, 55 + i * 40, 260, 32, (k, "code"), "box")
    d.arrow([(300, 71), (378, 71)])
    d.box(380, 20, 320, 160, [("object = data + metadata", "bold"), ("key: 2026/oct/notes.pdf", "code"),
                               ("size: up to 5 TB", "small"), ("version id (if versioning on)", "small"),
                               ("storage class · encryption · tags", "small")], "box")
    return d.render()


@diagram
def s16_apigw():
    d = D("s16-apigw", 720, 260, "Amazon API Gateway in front of Lambda",
          "API Gateway receives the request, checks who is calling and how often, then hands it to a Lambda function or "
          "another backend. Logs and metrics go to CloudWatch.")
    d.box(20, 95, 105, 70, ["Client", ("app / browser", "small")], "box")
    d.arrow([(125, 130), (178, 130)], label="HTTPS", lx=151, ly=117)
    d.rect(180, 30, 300, 200, "amber", rx=14); d.text(330, 50, "API Gateway · stage prod", "bold")
    for i, t in enumerate(["custom domain + TLS", "authorizer (JWT / IAM / Lambda)", "throttling · API keys", "route: GET /courses/{id}"]):
        d.box(195, 65 + i * 38, 270, 30, (t, "small"), "box")
    d.arrow([(480, 100), (538, 80)], "green", label="invoke", lx=510, ly=72)
    d.box(540, 45, 160, 70, ["Lambda", ("getCourse()", "code")], "green")
    d.arrow([(480, 170), (538, 190)])
    d.box(540, 160, 160, 60, ["CloudWatch", ("logs · latency · 4XX/5XX", "small")], "blue")
    return d.render()


if __name__ == "__main__":
    for fn in ALL:
        fn()
    print(len(ALL), "diagrams written to", OUT)
