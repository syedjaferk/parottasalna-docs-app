"""Diagrams for the Design Patterns course.

Each function below writes one diagrams/<name>.html file: an inline SVG <figure> that pages include with

    ```{raw} html
    :file: ../diagrams/<name>.html
    ```

Colours come from the .dg / figure.diagram classes in the docs CSS (courses/builder.py), so diagrams follow
light and dark mode. Edit a function, then run:  python course_content/design-patterns/diagrams/make_diagrams.py
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


# ------------------------------------------------------------------ Course map
@diagram
def map_patterns():
    d = D("map-patterns", 720, 300, "The three families of design patterns",
          "Creational patterns are about making objects, structural about fitting them together, "
          "behavioural about how they talk and share work.")
    fams = [(20, "CREATIONAL", "How objects are made", "blue",
             ["1 Singleton", "2 Factory Method", "3 Abstract Factory", "4 Builder", "5 Prototype"]),
            (260, "STRUCTURAL", "How objects fit together", "green",
             ["6 Adapter", "7 Decorator", "8 Facade", "9 Proxy", "10 Composite", "11 Bridge", "12 Flyweight"]),
            (500, "BEHAVIOURAL", "How objects work together", "amber",
             ["13 Strategy", "14 Observer", "15 Command", "16 State", "17 Template Method", "18 Chain of Resp."])]
    for x, title, sub, kind, names in fams:
        d.box(x, 15, 200, 56, [(title, "bold"), (sub, "small")], kind)
        for i, n in enumerate(names):
            d.box(x + 20, 85 + i * 29, 160, 24, (n, "small"), "box", rx=6)
    return d.render()


# ------------------------------------------------------------------ Creational
@diagram
def s01_singleton():
    d = D("s01-singleton", 720, 230, "Singleton: everyone gets the same object",
          "The first Config() call creates the object. Every later call returns that same object, so a "
          "change made through one variable is seen through all of them.")
    for i, (code, who) in enumerate([("a = Config()", "settings page"), ("b = Config()", "API handler"),
                                     ("c = Config()", "background job")]):
        y = 20 + i * 68
        d.box(20, y, 190, 50, [(code, "code"), (who, "small")], "blue")
        d.arrow([(210, y + 25), (418, 110)], kind="green" if i == 0 else "")
    d.text(300, 40, "first call: create", "small")
    d.text(330, 222, "later calls: return the same one", "small")
    d.box(420, 60, 280, 100, [("the one Config object", "bold"), ('settings = {"debug": True}', "code"),
                              ("a is b is c  →  True", "small")], "green")
    return d.render()


@diagram
def s02_factory():
    d = D("s02-factory", 720, 250, "Factory Method: one place decides which class to create",
          "Callers ask the factory by name. Only the factory knows the classes, so adding WhatsApp is one "
          "new class and one line in the factory.")
    d.box(20, 50, 170, 50, ("welcome_user()", "code"), "blue")
    d.box(20, 140, 170, 50, ("send_invoice()", "code"), "blue")
    d.box(250, 90, 190, 60, [("create_notifier(ch)", "code"), ("the only if/dict", "small")], "amber")
    d.arrow([(190, 75), (248, 110)]); d.arrow([(190, 165), (248, 130)])
    prods = [("EmailNotifier", "box"), ("SMSNotifier", "green"), ("WhatsAppNotifier", "ghost")]
    for i, (p, k) in enumerate(prods):
        y = 25 + i * 72
        d.box(510, y, 190, 48, (p, "code"), k)
        d.arrow([(440, 120), (508, y + 24)], kind="green" if k == "green" else "", dashed=k == "ghost")
    d.text(605, 225, "new type = new class + one line", "small")
    d.text(480, 138, '"sms"', "code")
    return d.render()


@diagram
def s03_abstract_factory():
    d = D("s03-abstract-factory", 720, 270, "Abstract Factory: pick a family once",
          "run_app() only talks to a factory. Each factory makes a whole matching family, so cloud storage "
          "with a local queue can't happen.")
    d.box(250, 15, 220, 46, ("run_app(factory)", "code"), "blue")
    for x, fac, kind, prods in [(30, "LocalFactory", "green", ["FileStorage", "MemoryQueue"]),
                                (390, "AWSFactory", "amber", ["S3Storage", "SQSQueue"])]:
        d.box(x, 95, 300, 46, (fac, "bold"), kind)
        d.arrow([(360, 61), (x + 150, 93)])
        for i, p in enumerate(prods):
            d.box(x + 10 + i * 150, 175, 130, 44, (p, "code"), "box")
            d.arrow([(x + 150, 141), (x + 75 + i * 150, 173)])
    d.line(240, 245, 480, 245, "line cut")
    d.text(360, 233, "S3Storage + MemoryQueue: can't be mixed", "small")
    return d.render()


@diagram
def s04_builder():
    d = D("s04-builder", 720, 220, "Builder: one named step at a time",
          "Each method sets one thing and returns the builder, so calls chain. build() checks everything "
          "once and returns the finished object.")
    steps = ["PizzaBuilder()", '.size("large")', '.crust("thin")', '.topping("corn")', ".extra_cheese()"]
    for i, s in enumerate(steps):
        x = 10 + i * 142
        d.box(x, 30, 136, 46, (s, "code"), "blue" if i else "ghost")
        if i:
            d.arrow([(x - 6, 53), (x - 1, 53)])
    d.arrow([(646, 76), (646, 110), (430, 110), (430, 128)])
    d.box(330, 130, 200, 50, [(".build()", "code"), ("validate: max 5 toppings", "small")], "amber")
    d.arrow([(330, 155), (262, 155)], kind="green")
    d.box(20, 130, 240, 50, [("Pizza(size='large', …)", "code"), ("finished and valid", "small")], "green")
    return d.render()


@diagram
def s05_prototype():
    d = D("s05-prototype", 720, 280, "Prototype: set up once, then copy",
          "deepcopy gives each clone its own inner lists. A shallow copy shares them, so changing one copy's "
          "list changes the original too.")
    d.box(20, 40, 200, 70, [("base", "bold"), ("slow setup ran once", "small")], "amber")
    for i, (n, ch) in enumerate([("support_bot", "same as base"), ("sales_bot", "temperature 0.7, + crm")]):
        y = 20 + i * 70
        d.box(330, y, 230, 50, [(n, "code"), (ch, "small")], "green")
        d.arrow([(220, 75), (328, y + 25)], kind="green", label="deepcopy" if i == 0 else None, lx=275, ly=40)
    d.text(180, 170, "SHALLOW COPY", "title"); d.text(540, 170, "DEEP COPY", "title")
    d.box(30, 190, 110, 40, ("a", "code"), "box"); d.box(170, 190, 110, 40, ("shallow", "code"), "box")
    d.box(100, 240, 110, 30, ("[tools]", "code"), "red")
    d.arrow([(85, 230), (140, 238)], kind="red"); d.arrow([(225, 230), (170, 238)], kind="red")
    d.box(400, 190, 110, 40, ("a", "code"), "box"); d.box(570, 190, 110, 40, ("deep", "code"), "box")
    d.box(400, 240, 110, 30, ("[tools]", "code"), "green"); d.box(570, 240, 110, 30, ("[tools]", "code"), "green")
    d.arrow([(455, 230), (455, 238)], kind="green"); d.arrow([(625, 230), (625, 238)], kind="green")
    return d.render()


# ------------------------------------------------------------------ Structural
@diagram
def s06_adapter():
    d = D("s06-adapter", 720, 240, "Adapter: translate one interface into another",
          "checkout() only knows pay(rupees). Each adapter translates that call into its provider's own "
          "method name and units.")
    d.box(20, 95, 140, 50, ("checkout()", "code"), "blue")
    d.box(200, 85, 150, 70, [("PaymentGateway", "bold"), ("pay(rupees)", "code")], "purple")
    d.arrow([(160, 120), (198, 120)])
    rows = [("RazorpayAdapter", "RazorpayClient", "make_payment(₹)"),
            ("StripeAdapter", "StripeClient", "charge(paise)")]
    for i, (ad, cl, m) in enumerate(rows):
        y = 25 + i * 120
        d.box(385, y, 140, 60, (ad, "bold"), "amber")
        d.box(555, y, 155, 60, [(cl, "small"), (m, "code")], "box")
        d.arrow([(350, 120), (383, y + 30)])
        d.arrow([(525, y + 30), (553, y + 30)], label="₹ → paise" if i else None, lx=540, ly=y + 80)
    return d.render()


@diagram
def s07_decorator():
    d = D("s07-decorator", 720, 240, "Decorator: wrap, keep the interface, add a little",
          "Sugar wraps Milk, which wraps Espresso. Each layer passes the call inward and adds its own part "
          "on the way out.")
    d.box(20, 20, 440, 200, [], "amber")
    d.text(40, 42, "Sugar   +5", "bold", "start")
    d.box(50, 60, 380, 145, [], "blue")
    d.text(70, 82, "Milk   +20", "bold", "start")
    d.box(80, 100, 320, 90, [("Espresso", "bold"), ("cost() = 100", "code")], "green")
    d.arrow([(470, 120), (520, 120)])
    d.box(525, 70, 180, 100, [("order.cost()", "code"), ("100 + 20 + 5", "small"), (" = 125", "bold")], "box")
    return d.render()


@diagram
def s08_facade():
    d = D("s08-facade", 720, 260, "Facade: one simple front door",
          "The caller makes one call. The facade runs the subsystems in the right order; they stay usable "
          "directly for special cases.")
    d.box(20, 105, 130, 50, ("checkout page", "bold"), "blue")
    d.box(190, 90, 180, 80, [("OrderFacade", "bold"), ("place_order(item, ₹)", "code")], "amber")
    d.arrow([(150, 130), (188, 130)])
    subs = ["① Inventory.check", "② Payment.charge", "③ Shipping.book", "④ Notifier.send"]
    for i, s in enumerate(subs):
        y = 15 + i * 60
        d.box(450, y, 250, 46, (s, "code"), "box")
        d.arrow([(370, 130), (448, y + 23)])
    return d.render()


@diagram
def s09_proxy():
    d = D("s09-proxy", 720, 250, "Proxy: a stand-in with the same interface",
          "The caller can't tell the proxy from the real object. The proxy decides whether, when and how "
          "the real object is used.")
    d.box(20, 95, 130, 50, ("caller", "bold"), "blue")
    d.box(200, 70, 200, 100, [("proxy", "bold"), ("same methods", "small"), ("lazy · cache · check · log", "small")],
          "amber")
    d.arrow([(150, 120), (198, 120)], label="show()", lx=175, ly=108)
    d.box(500, 70, 200, 100, [("real object", "bold"), ("slow / remote / costly", "small")], "green")
    d.arrow([(400, 120), (498, 120)], kind="green", label="only if needed", lx=450, ly=108)
    d.arrow([(300, 170), (300, 215), (85, 215), (85, 147)], kind="blue", dashed=True,
            label="cache hit or refused: answers itself", lx=200, ly=232)
    return d.render()


@diagram
def s10_composite():
    d = D("s10-composite", 720, 270, "Composite: a tree where groups and items look the same",
          "Folders and files both have size(). A folder asks its children and adds up the answers, so the "
          "same call works at every level.")
    d.box(280, 15, 160, 46, [("📁 project", "bold"), ("size() = 8", "code")], "amber")
    nodes = [(60, "📁 src", "6", "amber"), (300, "📁 docs", "1", "amber"), (520, "📄 LICENSE", "1", "green")]
    for x, n, s, k in nodes:
        d.box(x, 105, 150, 46, [(n, "bold"), (f"size() = {s}", "code")], k)
        d.arrow([(360, 61), (x + 75, 103)])
    leaves = [(10, "📄 main.py", "4", 135), (170, "📄 utils.py", "2", 135), (335, "📄 readme.md", "1", 375)]
    for x, n, s, px in leaves:
        d.box(x, 200, 150, 46, [(n, "bold"), (f"size() = {s}", "code")], "green")
        d.arrow([(px, 151), (x + 75, 198)])
    d.text(600, 225, "green = leaf, amber = group", "small")
    return d.render()


@diagram
def s11_bridge():
    d = D("s11-bridge", 720, 250, "Bridge: two hierarchies joined by one link",
          "WHAT the report is and HOW it is exported vary on their own. Any report works with any exporter: "
          "2 + 2 classes instead of 2 × 2.")
    d.text(160, 18, "ABSTRACTION: what", "title"); d.text(560, 18, "IMPLEMENTATION: how", "title")
    d.box(60, 35, 200, 46, ("Report", "bold"), "blue")
    d.box(460, 35, 200, 46, ("Exporter", "bold"), "green")
    d.arrow([(260, 58), (458, 58)], label="has an exporter (the bridge)",
            lx=360, ly=45)
    for i, n in enumerate(["SalesReport", "InventoryReport"]):
        d.box(20 + i * 160, 150, 145, 44, (n, "code"), "box")
        d.arrow([(160, 81), (92 + i * 160, 148)])
    for i, n in enumerate(["PDFExporter", "CSVExporter"]):
        d.box(410 + i * 155, 150, 145, 44, (n, "code"), "box")
        d.arrow([(560, 81), (482 + i * 155, 148)])
    d.text(360, 228, "SalesReport(PDFExporter())   ·   InventoryReport(CSVExporter())", "code")
    return d.render()


@diagram
def s12_flyweight():
    d = D("s12-flyweight", 720, 250, "Flyweight: share the heavy part",
          "Every tree keeps only its own position. The species and the 1 MB texture live once, in a shared "
          "TreeType: about 100 MB becomes about 1 MB.")
    for i in range(6):
        y = 10 + i * 38
        d.box(20, y, 150, 30, (f"Tree x={i} y={i * 2}", "small"), "blue", rx=6)
        d.arrow([(170, y + 15), (398, 120)])
    d.text(95, 245, "… 100 trees", "small")
    d.box(400, 70, 300, 100, [("TreeType (shared)", "bold"), ("species = Neem", "code"),
                              ("texture = 1 MB, read-only", "code")], "green")
    d.text(290, 30, "extrinsic: x, y", "small"); d.text(550, 200, "intrinsic: stored once", "small")
    return d.render()


# ------------------------------------------------------------------ Behavioural
@diagram
def s13_strategy():
    d = D("s13-strategy", 720, 250, "Strategy: plug in the way of doing the job",
          "The cart doesn't care how the discount is worked out. It calls apply(total) on whichever strategy "
          "is plugged in, and you can swap it at run time.")
    d.box(20, 90, 200, 70, [("Cart", "bold"), ("discount.apply(total)", "code")], "blue")
    strats = [("NoDiscount", "total"), ("StudentDiscount", "× 0.9"), ("PremiumDiscount", "× 0.8"),
              ("FlatOff(100)", "− 100")]
    for i, (n, f) in enumerate(strats):
        y = 15 + i * 58
        k = "green" if i == 1 else "box"
        d.box(400, y, 300, 46, [(n, "code"), (f, "small")], k)
        d.arrow([(220, 125), (398, y + 23)], kind="green" if i == 1 else "", dashed=i != 1)
    d.text(120, 185, "green = plugged in now", "small")
    return d.render()


@diagram
def s14_observer():
    d = D("s14-observer", 720, 250, "Observer: publish once, every subscriber reacts",
          "OrderService only publishes an event. The bus calls every subscribed handler. A new reaction is "
          "one subscribe() call; the publisher never changes.")
    d.box(20, 95, 160, 60, [("OrderService", "bold"), ("publish(...)", "code")], "blue")
    d.box(240, 90, 170, 70, [("EventBus", "bold"), ('"order_placed"', "code")], "amber")
    d.arrow([(180, 125), (238, 125)])
    subs = [("📧 email", "green"), ("📦 inventory", "green"), ("📊 analytics", "green"), ("+ subscribe()", "ghost")]
    for i, (s, k) in enumerate(subs):
        y = 10 + i * 58
        d.box(480, y, 220, 46, (s, "bold" if k == "green" else "small"), k)
        d.arrow([(410, 125), (478, y + 23)], kind="green" if k == "green" else "", dashed=k == "ghost")
    return d.render()


@diagram
def s15_command():
    d = D("s15-command", 720, 260, "Command: actions as objects you can keep",
          "Each action is an object with execute() and undo(). History keeps them on a stack, so undo pops "
          "the last one and reverses it; redo puts it back.")
    d.box(20, 20, 200, 60, [("AppendText(\"Hello\")", "code"), ("execute() · undo()", "small")], "blue")
    d.box(20, 100, 200, 60, [("AppendText(\" World\")", "code"), ("execute() · undo()", "small")], "blue")
    d.box(290, 40, 170, 110, [("History", "bold"), ("done: [Hello, World]", "small"), ("undone: []", "small")],
          "amber")
    d.arrow([(220, 50), (288, 80)], label="run", lx=250, ly=52); d.arrow([(220, 130), (288, 110)])
    d.box(515, 55, 195, 80, [("Editor", "bold"), ('text = "Hello World"', "code")], "green")
    d.arrow([(460, 95), (513, 95)], kind="green", label="execute", lx=487, ly=82)
    d.arrow([(375, 150), (375, 205), (618, 205), (618, 137)], kind="red", dashed=True,
            label="undo(): pop and reverse", lx=500, ly=222)
    return d.render()


@diagram
def s16_state():
    d = D("s16-state", 720, 260, "State: each state knows what happens next",
          "The order holds its current state and passes every call to it. Paying in Placed moves to Paid; "
          "cancelling after Shipped is refused.")
    d.box(20, 30, 140, 50, ("Placed", "bold"), "blue")
    d.box(290, 30, 140, 50, ("Paid", "bold"), "blue")
    d.box(560, 30, 140, 50, ("Shipped", "bold"), "green")
    d.box(290, 175, 140, 50, ("Cancelled", "bold"), "red")
    d.arrow([(160, 55), (288, 55)], kind="green", label="pay()", lx=224, ly=43)
    d.arrow([(430, 55), (558, 55)], kind="green", label="ship()", lx=494, ly=43)
    d.arrow([(90, 80), (90, 200), (288, 200)], kind="red", label="cancel()", lx=190, ly=188)
    d.arrow([(360, 80), (360, 173)], kind="red", label="cancel()", lx=400, ly=128)
    d.text(630, 110, "cancel() here:", "small"); d.text(630, 128, "“too late to cancel”", "small")
    return d.render()


@diagram
def s17_template():
    d = D("s17-template", 720, 280, "Template Method: a fixed order, a few blanks",
          "run() fixes the order of the steps. Shared steps live in the base class; subclasses fill in only "
          "the steps that differ.")
    d.text(130, 16, "run() in the base class", "title")
    steps = [("connect()", "shared", "box"), ("extract()", "subclass must write", "amber"),
             ("transform()", "default, may override", "blue"), ("load()", "shared", "box"),
             ("close()", "shared", "box")]
    for i, (s, note, k) in enumerate(steps):
        y = 30 + i * 48
        d.box(20, y, 220, 38, [(s, "code")], k)
        d.text(255, y + 19, note, "small", "start")
        if i:
            d.arrow([(130, y - 10), (130, y - 1)])
    d.box(470, 50, 230, 70, [("CSVPipeline", "bold"), ("extract(): read the file", "small")], "amber")
    d.box(470, 150, 230, 70, [("APIPipeline", "bold"), ("extract() + transform()", "small")], "amber")
    return d.render()


@diagram
def s18_chain():
    d = D("s18-chain", 720, 230, "Chain of Responsibility: pass it down the line",
          "Each handler either stops the request with an answer or passes it to the next one. Cheap checks "
          "go first, so expensive work only happens for good requests.")
    d.box(10, 60, 90, 46, ("request", "bold"), "blue")
    handlers = [("AuthCheck", "401"), ("BlockedCheck", "403"), ("RateLimit", "429"), ("SizeCheck", "413")]
    for i, (h, code) in enumerate(handlers):
        x = 130 + i * 125
        d.box(x, 60, 110, 46, (h, "code"), "amber")
        d.arrow([(x - 30 if i == 0 else x - 15, 83), (x - 2, 83)], kind="green")
        d.box(x + 15, 160, 80, 36, (code, "bold"), "red")
        d.arrow([(x + 55, 106), (x + 55, 158)], kind="red")
    d.arrow([(630, 83), (643, 83)], kind="green")
    d.box(645, 60, 65, 46, ("200", "bold"), "green")
    d.text(360, 220, "red = stop here with an error · green = pass it on", "small")
    return d.render()


if __name__ == "__main__":
    for fn in ALL:
        fn()
    print(len(ALL), "diagrams written to", OUT)
