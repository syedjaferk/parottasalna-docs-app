"""Diagrams for the Python Fundamentals course.

Each function writes one diagrams/<name>.html file (an inline SVG <figure>) that pages include with a
```{raw} html` block. Colours come from the .dg classes in the docs CSS, so diagrams follow light and dark
mode. Edit a function, then run:  python course_content/python-fundamentals/diagrams/make_diagrams.py
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


# ------------------------------------------------------------------ Session 1 · print()
@diagram
def s01_print():
    d = D("s01-print", 720, 200, "What print() does with its arguments",
          "print() turns each argument into text, puts sep between them (a space by default) and end after the last "
          "one (a newline by default).")
    parts = [("\"Hello\"", "blue"), ("sep", "amber"), ("\"world\"", "blue"), ("end", "amber")]
    x = 20
    for t, k in parts:
        w = 130 if k == "blue" else 90
        d.box(x, 30, w, 50, (t, "code"), k)
        x += w + 12
    d.text(20, 110, 'print("Hello", "world")                  →  Hello world⏎', "code", "start")
    d.text(20, 140, 'print("Hello", "world", sep="-", end="!") →  Hello-world!', "code", "start")
    d.text(20, 170, "defaults: sep=\" \"   end=\"\\n\"", "small", "start")
    return d.render()


# ------------------------------------------------------------------ Session 2 · data types
@diagram
def s02_types():
    d = D("s02-types", 720, 250, "Python's built-in data types",
          "Every value has a type. The type decides what you can do with it: add numbers, join strings, change a list, "
          "look up a key in a dictionary.")
    groups = [
        ("Numbers", ["int  42", "float  3.14", "complex  2+3j"], "blue"),
        ("Text · Bool · None", ["str  \"Idly\"", "bool  True", "NoneType  None"], "green"),
        ("Sequences", ["list  [1, 2]", "tuple  (1, 2)", "range  range(5)"], "amber"),
        ("Mapping · Sets", ["dict  {\"a\": 1}", "set  {1, 2}", "frozenset"], "purple"),
    ]
    for i, (title, items, k) in enumerate(groups):
        x = 20 + i * 172
        d.rect(x, 20, 160, 210, k, rx=12)
        d.text(x + 80, 42, title, "bold")
        for j, it in enumerate(items):
            d.box(x + 10, 62 + j * 54, 140, 42, (it, "code"), "box", rx=8)
    return d.render()


# ------------------------------------------------------------------ Session 3 · references
@diagram
def s03_refs():
    d = D("s03-refs", 720, 240, "Names point to objects",
          "a = [1, 2] creates a list object and binds the name a to it. b = a binds a second name to the SAME object, "
          "so a change through b is visible through a.")
    d.rect(20, 20, 200, 200, "ghost", rx=12)
    d.text(120, 40, "namespace (names)", "bold")
    d.box(50, 70, 140, 44, ("a", "code"), "blue")
    d.box(50, 140, 140, 44, ("b", "code"), "blue")
    d.rect(420, 20, 280, 200, "ghost", rx=12)
    d.text(560, 40, "objects in memory", "bold")
    d.box(460, 85, 200, 70, ["list object", ("[1, 2, 3]", "code"), ("id 1407…", "small")], "green")
    d.arrow([(190, 92), (458, 110)], "green")
    d.arrow([(190, 162), (458, 132)], "green")
    d.text(320, 85, "a = [1, 2]", "code")
    d.text(320, 175, "b = a", "code")
    d.text(560, 195, "b.append(3) → a sees it too", "small")
    return d.render()


# ------------------------------------------------------------------ Session 4 · conditionals
@diagram
def s04_if():
    d = D("s04-if", 720, 260, "if / elif / else",
          "Python checks the conditions from top to bottom and runs the first block whose condition is True. "
          "else runs only if none matched.")
    d.box(20, 105, 150, 50, ["number =", ("float(input())", "code")], "box")
    d.arrow([(170, 130), (208, 130)])
    conds = [("if number > 0", "positive"), ("elif number < 0", "negative"), ("else", "zero")]
    for i, (c, r) in enumerate(conds):
        y = 25 + i * 80
        d.box(210, y, 190, 50, (c, "code"), "amber")
        d.arrow([(400, y + 25), (468, y + 25)], "green", label="True" if i < 2 else None, lx=434, ly=y + 12)
        d.box(470, y, 230, 50, (f'print("… {r}.")', "code"), "green")
        if i < 2:
            d.arrow([(305, y + 50), (305, y + 78)], "red", label="False", lx=335, ly=y + 64)
    return d.render()


# ------------------------------------------------------------------ Session 5 · functions
@diagram
def s05_function():
    d = D("s05-function", 720, 230, "Anatomy of a function",
          "def gives the function a name and parameters. Calling it passes arguments in; return sends a value back to "
          "the caller.")
    d.rect(20, 20, 400, 190, "blue", rx=12)
    d.text(220, 45, "def celsius_to_fahrenheit(celsius):", "code")
    d.text(220, 75, "name                parameter", "small")
    d.box(50, 95, 340, 44, ("return (celsius * 9/5) + 32", "code"), "box")
    d.text(220, 170, "the body runs only when the function is called", "small")
    d.box(480, 30, 220, 50, ("celsius_to_fahrenheit(25)", "code"), "amber")
    d.text(590, 98, "argument 25 → celsius", "small")
    d.arrow([(480, 55), (422, 55)], "blue")
    d.arrow([(422, 117), (480, 150)], "green", label="return", lx=450, ly=122)
    d.box(480, 130, 220, 50, ("77.0", "code"), "green")
    return d.render()


# ------------------------------------------------------------------ Session 6 · indexing
@diagram
def s06_index():
    d = D("s06-index", 720, 210, "Indexes and a slice of \"HELLOWORLD\"",
          "Each character has a positive index from the left (starting at 0) and a negative index from the right "
          "(starting at -1). message[3:7] takes indexes 3, 4, 5 and 6: the stop index is not included.")
    word = "HELLOWORLD"
    for i, ch in enumerate(word):
        x = 60 + i * 60
        d.box(x, 70, 54, 50, (ch, "bold"), "green" if 3 <= i < 7 else "box", rx=6)
        d.text(x + 27, 55, str(i), "code")
        d.text(x + 27, 138, str(i - len(word)), "small")
    d.text(30, 55, "+", "small")
    d.text(30, 138, "−", "small")
    d.line(240, 160, 474, 160)
    d.line(240, 152, 240, 168)
    d.line(474, 152, 474, 168)
    d.text(357, 180, 'message[3:7] → "LOWO"', "code")
    return d.render()


# ------------------------------------------------------------------ Session 7 · lists
@diagram
def s07_list():
    d = D("s07-list", 720, 230, "Alex's truck: list methods",
          "A list is an ordered, changeable row of items. append adds at the end, insert at a position, remove deletes "
          "by value, pop removes and returns the last item.")
    items = ["Letter", "Fragile Box", "Parcel", "Special Delivery"]
    for i, it in enumerate(items):
        d.box(20 + i * 140, 40, 130, 50, [it, (f"[{i}]", "code")], "blue" if i < 3 else "green", rx=8)
    d.text(580, 25, "append() ⟶ new item at the end", "small")
    ops = [("insert(1, x)", "put x at index 1"), ("remove(\"Box\")", "delete first \"Box\""),
           ("pop()", "remove + return last"), ("sort() / reverse()", "reorder in place")]
    for i, (op, what) in enumerate(ops):
        x = 20 + i * 172
        d.box(x, 120, 162, 80, [(op, "code"), (what, "small")], "amber", rx=8)
    return d.render()


# ------------------------------------------------------------------ Session 8 · tuples
@diagram
def s08_tuple():
    d = D("s08-tuple", 720, 220, "A tuple is a sealed photo",
          "A tuple is ordered like a list but immutable: you can read, unpack, join and repeat tuples, but you can't "
          "change an item in place.")
    d.rect(20, 25, 400, 80, "blue", rx=12)
    for i, t in enumerate(["\"Ooty\"", "\"2024-07-01\"", "\"Botanical\""]):
        d.box(30 + i * 128, 45, 120, 44, (t, "code"), "box", rx=8)
    d.text(220, 120, "ooty = (place, date, note)", "code")
    d.box(460, 25, 240, 40, ("ooty[0] → \"Ooty\"   ✓ read", "small"), "green", rx=8)
    d.box(460, 75, 240, 40, ("place, date, note = ooty   ✓", "small"), "green", rx=8)
    d.box(460, 125, 240, 40, ("ooty + other, ooty * 2   ✓", "small"), "green", rx=8)
    d.box(460, 175, 240, 40, ("ooty[2] = \"…\"   ✗ TypeError", "small"), "red", rx=8)
    return d.render()


# ------------------------------------------------------------------ Session 9 · dictionaries
@diagram
def s09_dict():
    d = D("s09-dict", 720, 230, "Annachi Kadai's price list",
          "A dictionary maps keys to values. You look up a value by its key, not by position. Keys are unique; "
          "assigning to an existing key replaces its value.")
    d.rect(20, 20, 330, 190, "amber", rx=12)
    d.text(185, 42, "prices = {", "code")
    rows = [("\"rice\"", "60"), ("\"dal\"", "120"), ("\"oil\"", "180")]
    for i, (k, v) in enumerate(rows):
        y = 60 + i * 46
        d.box(40, y, 120, 36, (k, "code"), "blue", rx=6)
        d.arrow([(160, y + 18), (208, y + 18)])
        d.box(210, y, 120, 36, (v, "code"), "green", rx=6)
    d.text(185, 200, "}", "code")
    d.text(380, 50, 'prices["dal"]            → 120', "code", "start")
    d.text(380, 85, 'prices["sugar"] = 45     → add', "code", "start")
    d.text(380, 120, 'prices["dal"] = 125      → update', "code", "start")
    d.text(380, 155, 'prices.get("tea", 0)    → 0', "code", "start")
    d.text(380, 190, 'prices["tea"]            → KeyError', "code", "start")
    return d.render()


# ------------------------------------------------------------------ Session 10 · sets
@diagram
def s10_sets():
    d = D("s10-sets", 720, 260, "Rose garden and botanical garden",
          "Set operations compare two collections of unique items: union (|) is everything, intersection (&) is what's "
          "in both, difference (-) is what's only in the first.")
    d.circle(240, 145, 100, "circle-a")
    d.circle(370, 145, 100, "circle-b")
    d.text(200, 25, "rose_garden", "bold")
    d.text(420, 25, "botanical_garden", "bold")
    d.text(190, 125, "white rose", "small")
    d.text(190, 160, "pink rose", "small")
    d.text(305, 145, "red rose", "small")
    d.text(420, 125, "sunflower", "small")
    d.text(420, 160, "tulip", "small")
    ops = [("a | b", "union"), ("a & b", "intersection"), ("a - b", "difference"), ("a ^ b", "in one only")]
    for i, (o, name) in enumerate(ops):
        d.box(500, 40 + i * 50, 200, 40, [(f"{o}   {name}", "code")], "box", rx=8)
    return d.render()


# ------------------------------------------------------------------ Session 11 · generators
@diagram
def s11_lazy():
    d = D("s11-lazy", 720, 230, "Buffet (list) vs waiter (generator)",
          "A list builds every item first and keeps them all in memory. A generator produces one item each time you ask, "
          "pausing at yield in between.")
    d.rect(20, 20, 330, 190, "blue", rx=12)
    d.text(185, 42, "list: everything at once", "bold")
    for i in range(10):
        d.box(35 + (i % 5) * 61, 60 + (i // 5) * 50, 55, 40, (str(i + 1), "code"), "box", rx=6)
    d.text(185, 185, "range(1_000_000) as a list ≈ 8 MB", "small")
    d.rect(370, 20, 330, 190, "green", rx=12)
    d.text(535, 42, "generator: one at a time", "bold")
    d.box(390, 70, 120, 50, ["yield n", ("pause", "small")], "amber", rx=8)
    d.arrow([(510, 95), (568, 95)], "green", label="next()", lx=539, ly=80)
    d.box(570, 70, 110, 50, ("5", "code"), "box", rx=8)
    d.arrow([(625, 120), (625, 150), (450, 150), (450, 122)], dashed=True, label="resume where it paused", lx=537, ly=165)
    d.text(535, 195, "the generator object ≈ 100 bytes", "small")
    return d.render()


# ------------------------------------------------------------------ Session 12 · guessing game
@diagram
def s12_game():
    d = D("s12-game", 720, 260, "The guessing game loop",
          "Pick a secret number, then loop: read a valid guess, count the attempt, compare, and give a hint, until the "
          "guess is right or the attempts run out.")
    d.box(10, 105, 160, 50, ["secret =", ("randint(1, 100)", "code")], "blue")
    d.arrow([(170, 130), (188, 130)])
    d.box(190, 105, 150, 50, ["read guess", ("validated int", "small")], "box")
    d.arrow([(340, 130), (378, 130)])
    d.box(380, 100, 120, 60, ["compare", ("with secret", "small")], "amber")
    d.arrow([(500, 115), (568, 50)], "red", label="lower", lx=520, ly=70)
    d.box(570, 25, 130, 44, ("“Too low!”", "small"), "red")
    d.arrow([(500, 145), (568, 210)], "red", label="higher", lx=520, ly=195)
    d.box(570, 190, 130, 44, ("“Too high!”", "small"), "red")
    d.arrow([(500, 130), (568, 130)], "green", label="equal", lx=534, ly=118)
    d.box(570, 108, 130, 44, ("You win! 🎉", "small"), "green")
    d.arrow([(635, 25), (635, 10), (265, 10), (265, 103)], dashed=True, label="attempts left? try again", lx=450, ly=22)
    d.arrow([(635, 234), (635, 250), (265, 250), (265, 157)], dashed=True)
    return d.render()


if __name__ == "__main__":
    for fn in ALL:
        fn()
    print(len(ALL), "diagrams written to", OUT)
