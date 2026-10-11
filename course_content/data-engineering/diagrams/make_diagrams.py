"""Diagrams for End-to-End Data Engineering.

Each function writes one diagrams/<name>.html file (an inline SVG <figure>) that pages include with a
```{raw} html` block. Colours come from the .dg classes in the docs CSS, so diagrams follow light and dark
mode. Edit a function, then run:  python course_content/data-engineering/diagrams/make_diagrams.py
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


# ------------------------------------------------------------------ 1 · types
@diagram
def s01_typing():
    d = D("s01-typing", 720, 220, "From raw text to a typed record",
          "Everything in a CSV line is text. Split it into fields, then convert the ones you calculate with: "
          "quantity to int, price to float, date to a date.")
    d.box(20, 30, 680, 44, ('"1002,2025-01-03,C02,Coimbatore,Mouse,…,2,450,delivered"', "code"), "box")
    d.arrow([(360, 74), (360, 98)], label='.split(",")', lx=420, ly=86)
    fields = [("'1002'", "int 1002"), ("'2025-01-03'", "date"), ("'Mouse'", "str"), ("'2'", "int 2"), ("'450'", "float 450.0")]
    for i, (raw, typed) in enumerate(fields):
        x = 20 + i * 138
        d.box(x, 100, 128, 36, (raw, "code"), "amber", rx=8)
        d.arrow([(x + 64, 136), (x + 64, 156)])
        d.box(x, 158, 128, 36, (typed, "code"), "green", rx=8)
    return d.render()


# ------------------------------------------------------------------ 2 · loop
@diagram
def s02_loop():
    d = D("s02-loop", 720, 230, "One record at a time",
          "For each line: skip it with continue (not delivered), stop everything with break (impossible value), "
          "otherwise process it. The loop's else runs only if nothing called break.")
    d.box(12, 90, 140, 50, ["next line", ("for line in f", "code")], "blue")
    d.arrow([(152, 115), (178, 115)])
    d.box(180, 85, 160, 60, ["status ==", ("'delivered'?", "code")], "amber")
    d.arrow([(260, 85), (260, 45), (82, 45), (82, 88)], "red", label="no → continue", lx=171, ly=33)
    d.arrow([(340, 115), (378, 115)], "green", label="yes", lx=359, ly=103)
    d.box(380, 85, 150, 60, ["quantity > 0?"], "amber")
    d.arrow([(455, 145), (455, 190), (378, 190)], "red")
    d.box(250, 172, 128, 36, ("break: stop", "small"), "red", rx=8)
    d.arrow([(530, 115), (568, 115)], "green", label="yes", lx=549, ly=103)
    d.box(570, 85, 130, 60, ["process", ("total += amount", "code")], "green")
    return d.render()


# ------------------------------------------------------------------ 3 · scope
@diagram
def s03_scope():
    d = D("s03-scope", 720, 280, "Where Python looks for a name: LEGB",
          "Python looks in the Local scope first, then Enclosing functions, then the module's Global names, and "
          "finally Built-ins. Assigning to a name inside a function makes it local.")
    layers = [("Built-ins", "print, len, round", "ghost"), ("Global (module)", "TAX_RATE = 0.18", "blue"),
              ("Enclosing (outer function)", "rate inside make_pricer()", "amber"), ("Local (this function)", "tax, amount", "green")]
    for i, (name, ex, k) in enumerate(layers):
        x, y, w, h = 20 + i * 30, 15 + i * 30, 680 - i * 60, 250 - i * 60
        d.rect(x, y, w, h, k, rx=12)
        d.text(x + 16, y + 18, name, "bold", "start")
        d.text(x + w - 16, y + 18, ex, "code", "end")
    d.text(360, 190, "search order: L → E → G → B", "small")
    return d.render()


# ------------------------------------------------------------------ 4 · errors
@diagram
def s04_errors():
    d = D("s04-errors", 720, 230, "Decide in advance: skip, retry or stop",
          "Bad records go to a dead-letter list and the run continues; temporary failures are retried with a "
          "growing wait; anything that breaks the pipeline's assumptions stops it loudly. All of it is logged.")
    d.box(20, 90, 120, 50, ["record or", "API call"], "box")
    d.arrow([(140, 115), (198, 115)])
    d.box(200, 85, 120, 60, ["try:", ("process it", "small")], "blue")
    outcomes = [("bad record", "skip → dead letters", "amber", 25), ("timeout / 503", "retry with backoff", "blue", 95),
                ("broken assumption", "raise → stop", "red", 165)]
    for label, action, k, y in outcomes:
        d.arrow([(320, 115), (398, y + 20)], k if k != "amber" else "", label=None)
        d.box(400, y, 300, 40, [f"{label}  →  {action}"], k, tcls="small", rx=8)
    d.text(560, 222, "every branch writes a log line", "small")
    return d.render()


# ------------------------------------------------------------------ 5 · lookup
@diagram
def s05_lookup():
    d = D("s05-lookup", 720, 230, "Join with a dict index (a hash join)",
          "Build a dict from customer_id to customer once. Each order then finds its customer in one step, "
          "instead of scanning the whole customer list for every order.")
    d.rect(20, 20, 220, 190, "blue", rx=12)
    d.text(130, 40, "orders (many)", "bold")
    for i, (o, c) in enumerate([("1001", "C01"), ("1002", "C02"), ("1004", "C01"), ("1011", "C05")]):
        d.box(35, 55 + i * 37, 190, 30, (f"order {o} · {c}", "code"), "box", rx=6)
    d.rect(480, 20, 220, 190, "green", rx=12)
    d.text(590, 40, "by_id = {id: customer}", "code")
    for i, (cid, name) in enumerate([("C01", "Arun"), ("C02", "Priya"), ("C05", "Ravi")]):
        d.box(495, 60 + i * 45, 190, 34, (f"{cid} → {name}", "code"), "box", rx=6)
    for y1, y2 in [(70, 77), (107, 122), (144, 77), (181, 167)]:
        d.arrow([(225, y1), (493, y2)], "green")
    d.text(360, 200, "by_id[order.customer_id]: one step each", "small")
    return d.render()


# ------------------------------------------------------------------ 6 · generator pipeline
@diagram
def s06_pipeline():
    d = D("s06-pipeline", 720, 190, "A lazy generator pipeline",
          "Each stage pulls one row from the stage before it, only when needed. A row travels all the way "
          "through before the next one is read, so memory stays tiny however big the file is.")
    stages = [("read_lines", "file"), ("parse", "→ dict"), ("only_delivered", "filter"), ("deduplicate", "seen set"), ("batches", "lists of 4")]
    for i, (name, sub) in enumerate(stages):
        x = 12 + i * 141
        d.box(x, 50, 132, 60, [(name, "code"), (sub, "small")], "green" if i == len(stages) - 1 else "blue")
        if i:
            d.arrow([(x - 9, 80), (x - 1, 80)])
    d.text(360, 145, "one row at a time ⟶", "small")
    d.text(360, 168, "nothing runs until the last stage is looped over", "small")
    return d.render()


# ------------------------------------------------------------------ 7 · columnar
@diagram
def s07_columnar():
    d = D("s07-columnar", 720, 230, "Row storage (CSV) vs column storage (Parquet)",
          "CSV stores whole rows one after another, so reading one column still reads everything. Parquet stores "
          "each column together, typed and compressed, so a query reads only the columns it needs.")
    d.text(180, 25, "CSV: row by row", "bold")
    rows = ["1001 · Laptop · 55000", "1002 · Mouse · 450", "1003 · Notebook · 40"]
    for i, r in enumerate(rows):
        d.box(40, 40 + i * 44, 280, 36, (r, "code"), "amber", rx=6)
    d.text(180, 185, "need prices? read every row", "small")
    d.text(540, 25, "Parquet: column by column", "bold")
    cols = [("order_id", "int64"), ("product", "string"), ("unit_price", "int64")]
    for i, (c, t) in enumerate(cols):
        kind = "green" if c == "unit_price" else "ghost"
        d.box(400 + i * 104, 40, 96, 124, [c, (t, "small")], kind, rx=8)
    d.text(560, 185, "need prices? read one column", "small")
    return d.render()


# ------------------------------------------------------------------ 8 · api
@diagram
def s08_api():
    d = D("s08-api", 720, 220, "A reliable API ingestion",
          "Send a request with a timeout and auth header, check the status, retry temporary failures, follow "
          "the pages, save the raw JSON first, then transform a copy.")
    d.box(20, 80, 130, 60, ["your code", ("Session + token", "small")], "blue")
    d.arrow([(150, 100), (258, 100)], label="GET ?_page=n", lx=204, ly=88)
    d.box(260, 70, 150, 80, ["REST API", ("200 + JSON", "small"), ("429 / 5xx", "small")], "amber")
    d.arrow([(260, 130), (152, 130)], "green", label="response", lx=206, ly=146)
    d.arrow([(335, 70), (335, 30), (85, 30), (85, 78)], "blue", dashed=True, label="retry with backoff / next page", lx=210, ly=20)
    d.arrow([(410, 110), (478, 110)])
    d.box(480, 60, 220, 44, ("raw/dt=…/users.jsonl", "code"), "green", rx=8)
    d.box(480, 120, 220, 44, ("clean table (Parquet)", "code"), "green", rx=8)
    d.arrow([(590, 104), (590, 118)])
    return d.render()


# ------------------------------------------------------------------ 9 · config
@diagram
def s09_config():
    d = D("s09-config", 720, 200, "Layered settings",
          "Defaults in code are overridden by the config file, which is overridden by environment variables. "
          "Secrets come only from the environment and never from files in Git.")
    layers = [("defaults in code", "batch_size = 100", "ghost"), ("config file (in Git)", "pipeline.toml", "blue"),
              ("environment variables", "SHOP_BATCH_SIZE=1000", "green")]
    for i, (name, ex, k) in enumerate(layers):
        x = 20 + i * 235
        d.box(x, 50, 215, 70, [name, (ex, "code")], k)
        if i:
            d.arrow([(x - 20, 85), (x - 2, 85)])
    d.text(360, 150, "weakest  ──────────────▶  strongest", "small")
    d.box(240, 162, 240, 30, ("secrets: environment only", "small"), "red", rx=8)
    return d.render()


# ------------------------------------------------------------------ 10 · broadcasting
@diagram
def s10_broadcast():
    d = D("s10-broadcast", 720, 210, "Broadcasting a (3, 1) column across a (3, 4) grid",
          "Shapes are compared from the right: 4 vs 1, then 3 vs 3. A size of 1 is stretched to match, so each "
          "city's target is subtracted from all four of its weeks without copying data.")
    for r in range(3):
        for c in range(4):
            d.box(20 + c * 62, 30 + r * 50, 56, 42, ("·", "small"), "blue", rx=6)
    d.text(144, 190, "weekly_sales (3, 4)", "code")
    d.text(290, 85, "−", "bold")
    for r in range(3):
        d.box(320, 30 + r * 50, 56, 42, ("t", "code"), "amber", rx=6)
        for c in range(1, 4):
            d.box(320 + c * 62, 30 + r * 50, 56, 42, ("t", "code"), "ghost", rx=6)
    d.text(440, 190, "city_target (3, 1) → stretched", "code")
    d.text(640, 85, "= (3, 4)", "bold")
    return d.render()


# ------------------------------------------------------------------ 11 · dataframe
@diagram
def s11_dataframe():
    d = D("s11-dataframe", 720, 220, "Anatomy of a DataFrame",
          "A DataFrame is a set of columns that share one row index. Each column is a Series with its own "
          "dtype. Select columns with df[...], rows by label with .loc and by position with .iloc.")
    d.box(20, 30, 90, 30, ("index", "small"), "ghost", rx=6)
    for i, lab in enumerate(["0", "1", "2"]):
        d.box(20, 66 + i * 36, 90, 30, (lab, "code"), "ghost", rx=6)
    cols = [("order_id", "int64"), ("city", "object"), ("unit_price", "int64"), ("order_date", "datetime64")]
    for j, (c, t) in enumerate(cols):
        x = 125 + j * 145
        d.box(x, 30, 135, 30, (c, "code"), "blue", rx=6)
        for i in range(3):
            d.box(x, 66 + i * 36, 135, 30, ("…", "small"), "box", rx=6)
        d.text(x + 67, 186, t, "small")
    d.text(360, 210, "df['city'] → a Series · df.loc[1] → a row by label · df.iloc[0] → a row by position", "small")
    return d.render()


# ------------------------------------------------------------------ 12 · groupby
@diagram
def s12_groupby():
    d = D("s12-groupby", 720, 230, "groupby: split, apply, combine",
          "Rows are split into groups by key, a calculation runs on each group, and the results are combined "
          "into one row per group.")
    rows = [("Chennai", "55000"), ("Madurai", "400"), ("Chennai", "9500"), ("Madurai", "52000"), ("Chennai", "500")]
    for i, (city, amt) in enumerate(rows):
        d.box(20, 20 + i * 38, 170, 32, (f"{city} · {amt}", "code"), "box", rx=6)
    d.text(105, 215, "rows", "small")
    d.box(250, 20, 180, 80, ["Chennai", ("55000, 9500, 500", "code")], "blue")
    d.box(250, 120, 180, 80, ["Madurai", ("400, 52000", "code")], "amber")
    d.text(340, 215, "split", "small")
    d.arrow([(190, 80), (248, 60)])
    d.arrow([(190, 120), (248, 160)])
    d.arrow([(430, 60), (488, 80)], label="sum", lx=459, ly=60)
    d.arrow([(430, 160), (488, 140)], label="sum", lx=459, ly=166)
    d.box(490, 70, 210, 80, [("Chennai   65000", "code"), ("Madurai   52400", "code")], "green")
    d.text(595, 215, "combine", "small")
    return d.render()


if __name__ == "__main__":
    for fn in ALL:
        fn()
    print(len(ALL), "diagrams written to", OUT)
