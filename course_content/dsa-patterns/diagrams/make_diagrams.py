"""Diagrams for the DSA Patterns course.

Each function below writes one diagrams/<name>.html file: an inline SVG <figure> that sessions include with

    ```{raw} html
    :file: ../diagrams/<name>.html
    ```

Colours come from the .dg / figure.diagram classes in the docs CSS (courses/builder.py), so diagrams follow
light and dark mode. Edit a function, then run:  python course_content/dsa-patterns/diagrams/make_diagrams.py
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



# ------------------------------------------------------------------ helpers
def cells(d, vals, x, y, w=56, h=44, cls=None, idx=True, gap=6, text_cls="code"):
    """Draw a row of array cells. cls maps index -> box class. Returns the centre x of every cell."""
    cls = cls or {}
    xs = []
    for i, v in enumerate(vals):
        cx = x + i * (w + gap)
        d.box(cx, y, w, h, (str(v), text_cls), cls.get(i, "box"))
        if idx:
            d.text(cx + w / 2, y + h + 14, i, "small")
        xs.append(cx + w / 2)
    return xs


def pointer(d, cx, y, label, kind="blue", up=True):
    """An arrow pointing at a cell from below (up=True) with a label under it."""
    if up:
        d.arrow([(cx, y + 34), (cx, y)], kind=kind)
        d.text(cx, y + 48, label, "bold")
    else:
        d.arrow([(cx, y - 34), (cx, y)], kind=kind)
        d.text(cx, y - 46, label, "bold")


def node(d, cx, cy, label, cls="box", r=20):
    d.circle(cx, cy, r, cls)
    d.text(cx, cy, label, "code")


# ------------------------------------------------------------------ 1 Two pointers
@diagram
def two_pointers():
    d = D("two-pointers", 720, 330, "Two pointers walk towards each other",
          "Sorted array, target 10. Too small: move the left pointer right. Too big: move the right pointer left. Found: stop.")
    vals = [1, 3, 4, 6, 8, 11]
    steps = [(0, 5, "1 + 11 = 12  → too big, move R left", "red"), (0, 4, "1 + 8 = 9  → too small, move L right", "amber"), (1, 4, "3 + 8 = 11  → too big, move R left", "red"), (1, 3, "3 + 6 = 9  → too small, move L right", "amber")]
    y = 20
    for l, r, msg, k in steps:
        cells(d, vals, 60, y, w=46, h=36, cls={l: "blue", r: "green"}, idx=False)
        d.text(410, y + 18, msg, "small", anchor="start")
        y += 52
    cells(d, vals, 60, y, w=46, h=36, cls={2: "blue", 3: "green"}, idx=False)
    d.text(410, y + 18, "4 + 6 = 10  → found!", "bold", anchor="start")
    d.text(60, y + 62, "blue = left pointer (L)      green = right pointer (R)", "small", anchor="start")
    return d.render()


# ------------------------------------------------------------------ 2 Sliding window
@diagram
def sliding_window():
    d = D("sliding-window", 720, 330, "A window slides over the string",
          "Longest substring without repeats in \"abcabcbb\": grow the right edge; when a repeat appears, shrink from the left.")
    s = "abcabcbb"
    rows = [(0, 2, "green", "right = 2: \"abc\" is valid, length 3"),
            (0, 3, "amber", "right = 3 adds 'a': two a's, broken"),
            (1, 3, "green", "left moves to 1: \"bca\" is valid, length 3"),
            (1, 4, "amber", "right = 4 adds 'b': two b's, broken"),
            (2, 4, "green", "left moves to 2: \"cab\" is valid, length 3")]
    y = 18
    for l, r, k, msg in rows:
        cells(d, list(s), 40, y, w=44, h=36, cls={i: k for i in range(l, r + 1)}, idx=False)
        d.text(40 + 8 * 50 + 10, y + 18, msg, "small", anchor="start")
        y += 56
    d.text(40, y + 14, "green = valid window      amber = broken window (must shrink)", "small", anchor="start")
    return d.render()


# ------------------------------------------------------------------ 3 Fast and slow
@diagram
def fast_slow():
    d = D("fast-slow", 720, 240, "Fast and slow pointers on a cycle",
          "Slow moves 1 step, fast moves 2. Inside a loop the fast pointer laps the slow one, so they meet.")
    xs = [70, 170, 270, 370, 470]
    for i, x in enumerate(xs):
        node(d, x, 80, str(i + 1), "blue" if i < 2 else "box")
        if i:
            d.arrow([(xs[i - 1] + 21, 80), (x - 22, 80)])
    d.arrow([(xs[-1], 101), (xs[-1], 170), (xs[2], 170), (xs[2], 102)], kind="red")
    d.text(380, 190, "cycle: 5 points back to 3", "small")
    d.text(70, 130, "slow starts here", "small"); d.text(70, 148, "fast starts here", "small")
    d.text(560, 70, "slow: 1, 2, 3, 4, 5", "code", anchor="start")
    d.text(560, 95, "fast: 1, 3, 5, 4, 3", "code", anchor="start")
    d.text(560, 125, "meet at node 3", "bold", anchor="start")
    return d.render()


# ------------------------------------------------------------------ 4 Reverse linked list
@diagram
def reverse_list():
    d = D("reverse-list", 720, 360, "Reversing a linked list one link at a time",
          "Keep prev, curr and next. Save next, flip curr.next to point backwards, then step prev and curr forward.")
    xs = [250, 360, 470]
    # (label, flipped links so far, prev index, curr index); links flipped = the first `f` nodes already point backwards
    rows = [("start", 0, None, 0), ("after step 1", 1, 0, 1), ("after step 2", 2, 1, 2), ("after step 3", 3, 2, None)]
    y = 40
    for label, f, p, c in rows:
        d.text(30, y, label, "small", anchor="start")
        d.text(170, y, "null", "code")
        d.text(570, y, "null", "code")
        for i, x in enumerate(xs):
            node(d, x, y, str(i + 1), "green" if i < f else "box")
        # the link out of node i: backwards if flipped, otherwise forwards
        for i in range(3):
            if i < f:
                if i == 0:
                    d.arrow([(xs[0] - 22, y), (184, y)], kind="green")          # 1 now points to null
                else:
                    d.arrow([(xs[i] - 22, y + 8), (xs[i - 1] + 22, y + 8)], kind="green")
            else:
                nxt = xs[i + 1] - 22 if i < 2 else 548
                d.arrow([(xs[i] + 22, y), (nxt, y)])
        if p is not None:
            d.text(xs[p], y + 38, "prev", "bold")
        if c is not None:
            d.text(xs[c], y + 56 if c == p else y + 38, "curr", "bold")
        y += 90
    return d.render()


# ------------------------------------------------------------------ 5 Binary search
@diagram
def binary_search():
    d = D("binary-search", 720, 300, "Binary search halves the range",
          "Looking for 23. Each check at mid throws away half of what is left.")
    vals = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
    rows = [(0, 9, 4, "lo=0, hi=9, mid=4 → 16 < 23, go right"), (5, 9, 7, "lo=5, hi=9, mid=7 → 56 > 23, go left"), (5, 6, 5, "lo=5, hi=6, mid=5 → 23 found!")]
    y = 20
    for lo, hi, mid, msg in rows:
        cls = {i: "ghost" for i in range(10) if i < lo or i > hi}
        cls.update({i: "blue" for i in range(lo, hi + 1)})
        cls[mid] = "green"
        cells(d, vals, 20, y, w=54, h=38, cls=cls, idx=False, gap=6)
        d.text(20, y + 58, msg, "small", anchor="start")
        y += 90
    return d.render()


# ------------------------------------------------------------------ 6 Prefix sum
@diagram
def prefix_sum():
    d = D("prefix-sum", 720, 260, "Prefix sums answer range questions in O(1)",
          "prefix[i] is the sum of the first i numbers. The sum of a range is one subtraction.")
    a = [3, 1, 4, 1, 5, 9]
    pre = [0, 3, 4, 8, 9, 14, 23]
    d.text(30, 33, "a", "bold", anchor="start")
    cells(d, a, 143, 15, w=60, h=36, cls={2: "amber", 3: "amber", 4: "amber"}, idx=False)
    d.text(30, 123, "prefix", "bold", anchor="start")
    cells(d, pre, 110, 105, w=60, h=36, cls={2: "red", 5: "green"}, idx=False)
    for i in range(7):
        d.text(140 + i * 66, 157, f"[{i}]", "small")
    d.text(360, 200, "sum of a[2..4] = prefix[5] - prefix[2] = 14 - 4 = 10", "code")
    d.text(360, 228, "4 + 1 + 5 = 10  ✓", "small")
    return d.render()


# ------------------------------------------------------------------ 7 Hash map
@diagram
def hash_map():
    d = D("hash-map", 720, 270, "Hash map: remember what you have seen",
          "Two Sum with target 9: for each number ask the map whether its partner was already seen.")
    d.text(60, 20, "nums", "title", anchor="start")
    cells(d, [2, 7, 11, 15], 60, 35, w=60, h=38, cls={0: "blue", 1: "green"}, idx=False)
    d.text(60, 110, "step 1: x = 2 → need 7 → not in map → store {2: 0}", "small", anchor="start")
    d.text(60, 135, "step 2: x = 7 → need 2 → found at index 0 → answer [0, 1]", "bold", anchor="start")
    d.text(400, 20, "map (value → index)", "title", anchor="start")
    d.box(400, 35, 80, 38, ("2 → 0", "code"), "blue")
    d.box(490, 35, 80, 38, ("7 → 1", "code"), "ghost")
    d.text(60, 185, "Without a map: compare every pair → O(n²).", "small", anchor="start")
    d.text(60, 210, "With a map: one pass, one lookup each → O(n).", "small", anchor="start")
    return d.render()


# ------------------------------------------------------------------ 8 Monotonic stack
@diagram
def mono_stack():
    d = D("mono-stack", 720, 300, "Monotonic stack: next greater element",
          "Temperatures 73, 74, 75, 71. The stack keeps indexes of days still waiting for a warmer day.")
    cells(d, [73, 74, 75, 71], 40, 20, w=60, h=38, idx=True)
    stages = [("i=0 (73)", ["0:73"], "push 0"), ("i=1 (74)", ["1:74"], "74 > 73 → pop 0, answer for day 0 = 1"), ("i=2 (75)", ["2:75"], "75 > 74 → pop 1, answer for day 1 = 1"), ("i=3 (71)", ["2:75", "3:71"], "71 < 75 → just push")]
    x = 330
    d.text(x, 20, "stack after each step (top on the right)", "title", anchor="start")
    y = 40
    for name, st, msg in stages:
        d.text(x, y + 16, name, "small", anchor="start")
        for j, s in enumerate(st):
            d.box(x + 90 + j * 70, y, 64, 32, (s, "code"), "blue")
        d.text(x + 90 + 2 * 70 + 10, y + 16, "", "small")
        d.text(x, y + 46, msg, "small", anchor="start")
        y += 62
    return d.render()


# ------------------------------------------------------------------ 9 Intervals
@diagram
def intervals():
    d = D("intervals", 720, 300, "Merging overlapping intervals",
          "Sort by start. If the next interval starts before the current one ends, they overlap and merge.")
    sx = lambda t: 40 + t * 30
    d.text(30, 20, "before", "title", anchor="start")
    for y, (s, e), c in [(35, (1, 3), "blue"), (65, (2, 6), "blue"), (95, (8, 10), "amber"), (125, (15, 18), "green")]:
        d.rect(sx(s), y, sx(e) - sx(s), 20, "bar" if c == "blue" else "bar " + c)
        d.text(sx(e) + 10, y + 10, f"[{s},{e}]", "small", anchor="start")
    d.text(sx(1), 168, "[1,3] and [2,6] overlap because 2 ≤ 3", "small", anchor="start")
    d.text(30, 205, "after", "title", anchor="start")
    for y, (s, e), c in [(220, (1, 6), "blue"), (248, (8, 10), "amber"), (276, (15, 18), "green")]:
        d.rect(sx(s), y, sx(e) - sx(s), 18, "bar" if c == "blue" else "bar " + c)
        d.text(sx(e) + 10, y + 9, f"[{s},{e}]", "code", anchor="start")
    return d.render()


# ------------------------------------------------------------------ 10 Cyclic sort
@diagram
def cyclic_sort():
    d = D("cyclic-sort", 720, 290, "Cyclic sort: every number goes to its own seat",
          "Value v belongs at index v-1. Swap the number into its seat until the current seat holds the right value.")
    steps = [([3, 1, 5, 4, 2], {0: "red", 2: "red"}, "3 belongs at index 2 → swap with 5"),
             ([5, 1, 3, 4, 2], {0: "red", 4: "red"}, "5 belongs at index 4 → swap with 2"),
             ([2, 1, 3, 4, 5], {0: "red", 1: "red"}, "2 belongs at index 1 → swap with 1"),
             ([1, 2, 3, 4, 5], {i: "green" for i in range(5)}, "sorted: every index i holds i+1")]
    y = 15
    for vals, cls, msg in steps:
        cells(d, vals, 40, y, w=54, h=38, cls=cls, idx=False)
        d.text(350, y + 19, msg, "small", anchor="start")
        y += 66
    return d.render()


# ------------------------------------------------------------------ 11 Matrix
@diagram
def matrix():
    d = D("matrix", 720, 300, "Matrix: spiral order and in-place rotation",
          "Spiral: walk the outer ring, then the next ring. Rotate 90°: transpose (mirror over the diagonal), then reverse each row.")
    n = 1
    order = [[1, 2, 3, 4], [12, 13, 14, 5], [11, 16, 15, 6], [10, 9, 8, 7]]
    d.text(120, 18, "spiral order", "title")
    for r in range(4):
        for c in range(4):
            v = order[r][c]
            d.box(40 + c * 44, 35 + r * 44, 40, 40, (str(v), "code"), "blue" if v <= 4 else ("green" if v <= 7 else ("amber" if v <= 11 else "box")))
    d.text(480, 18, "rotate 90° clockwise", "title")
    g = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    t = [[1, 4, 7], [2, 5, 8], [3, 6, 9]]
    r = [[7, 4, 1], [8, 5, 2], [9, 6, 3]]
    for k, (m, lab) in enumerate([(g, "original"), (t, "transpose"), (r, "reverse rows")]):
        ox = 300 + k * 140
        d.text(ox + 55, 220, lab, "small")
        for i in range(3):
            for j in range(3):
                d.box(ox + j * 36, 40 + i * 36 + 0, 32, 32, (str(m[i][j]), "code"), "box" if k == 0 else ("blue" if k == 1 else "green"))
    return d.render()


# ------------------------------------------------------------------ 12 BFS
@diagram
def bfs():
    d = D("bfs", 720, 300, "BFS spreads out level by level",
          "From A, first visit everything 1 step away, then everything 2 steps away. The queue holds the next level.")
    pos = {"A": (100, 150), "B": (250, 70), "C": (250, 150), "D": (250, 230), "E": (420, 70), "F": (420, 190)}
    edges = [("A", "B"), ("A", "C"), ("A", "D"), ("B", "E"), ("C", "F"), ("D", "F")]
    for a, b in edges:
        d.line(pos[a][0], pos[a][1], pos[b][0], pos[b][1])
    lv = {"A": "green", "B": "blue", "C": "blue", "D": "blue", "E": "amber", "F": "amber"}
    for k, (x, y) in pos.items():
        node(d, x, y, k, lv[k], r=22)
    d.text(100, 190, "level 0", "small"); d.text(250, 270, "level 1", "small"); d.text(430, 250, "level 2", "small")
    d.text(560, 100, "queue after each pop", "title", anchor="start")
    for i, s in enumerate(["[A]", "[B, C, D]", "[C, D, E]", "[D, E, F]", "[E, F]", "[F]"]):
        d.text(560, 125 + i * 24, s, "code", anchor="start")
    return d.render()


# ------------------------------------------------------------------ 13 DFS
@diagram
def dfs():
    d = D("dfs", 720, 300, "DFS goes deep first, then backs up",
          "Numbers show the visit order. DFS follows one path to the end, returns to the last fork, and tries the next branch.")
    pos = {"A": (260, 40), "B": (140, 120), "C": (380, 120), "D": (80, 210), "E": (200, 210), "F": (380, 210)}
    for a, b in [("A", "B"), ("A", "C"), ("B", "D"), ("B", "E"), ("C", "F")]:
        d.line(pos[a][0], pos[a][1], pos[b][0], pos[b][1])
    order = {"A": 1, "B": 2, "D": 3, "E": 4, "C": 5, "F": 6}
    for k, (x, y) in pos.items():
        node(d, x, y, k, "blue", r=22)
        d.text(x + 30, y - 18, str(order[k]), "bold")
    d.text(520, 70, "call stack", "title", anchor="start")
    for i, s in enumerate(["dfs(A)", "  dfs(B)", "    dfs(D)  ← deepest", "    back to B", "    dfs(E)"]):
        d.text(520, 100 + i * 26, s, "code", anchor="start")
    return d.render()


# ------------------------------------------------------------------ 14 Trees
@diagram
def trees():
    d = D("trees", 720, 290, "Trees: ask the children, then combine",
          "Height of a node = 1 + the bigger height of its two children. Answers flow from the leaves up to the root.")
    pos = {"1": (260, 40), "2": (140, 120), "3": (380, 120), "4": (80, 200), "5": (200, 200)}
    for a, b in [("1", "2"), ("1", "3"), ("2", "4"), ("2", "5")]:
        d.line(pos[a][0], pos[a][1], pos[b][0], pos[b][1])
    h = {"1": 3, "2": 2, "3": 1, "4": 1, "5": 1}
    for k, (x, y) in pos.items():
        node(d, x, y, k, "blue" if h[k] > 1 else "green", r=22)
        d.text(x + 34, y, f"h={h[k]}", "small")
    d.text(520, 70, "base case: None → 0", "code", anchor="start")
    d.text(520, 100, "height(4) = 1 + max(0, 0) = 1", "small", anchor="start")
    d.text(520, 124, "height(2) = 1 + max(1, 1) = 2", "small", anchor="start")
    d.text(520, 148, "height(1) = 1 + max(2, 1) = 3", "small", anchor="start")
    return d.render()


# ------------------------------------------------------------------ 15 Graphs / topological
@diagram
def topo():
    d = D("topo", 720, 270, "Topological sort with in-degrees",
          "Courses with prerequisites. Start with nodes that need nothing (in-degree 0), remove them, and repeat.")
    pos = {"Maths": (80, 135), "Algo": (240, 70), "Stats": (240, 200), "ML": (420, 135)}
    for a, b in [("Maths", "Algo"), ("Maths", "Stats"), ("Algo", "ML"), ("Stats", "ML")]:
        (x1, y1), (x2, y2) = pos[a], pos[b]
        d.arrow([(x1 + 30, y1), (x2 - 30, y2)])
    for k, (x, y) in pos.items():
        d.box(x - 30, y - 18, 60, 36, (k, "code"), "blue")
    d.text(500, 70, "in-degree", "title", anchor="start")
    for i, t in enumerate(["Maths 0  ← start", "Algo  1 → 0 after Maths", "Stats 1 → 0 after Maths", "ML    2 → 0 after both"]):
        d.text(500, 100 + i * 28, t, "code", anchor="start")
    d.text(500, 230, "order: Maths, Algo, Stats, ML", "bold", anchor="start")
    return d.render()


# ------------------------------------------------------------------ 16 Backtracking
@diagram
def backtracking():
    d = D("backtracking", 720, 310, "Backtracking explores a tree of choices",
          "Subsets of [1, 2]: at each number choose to take it or skip it. Reaching a leaf records the subset; returning undoes the choice.")
    d.box(280, 15, 120, 34, ("[ ]", "code"), "blue")
    d.arrow([(310, 49), (190, 100)], label="take 1", lx=225, ly=66)
    d.arrow([(370, 49), (500, 100)], label="skip 1", lx=470, ly=66)
    d.box(130, 100, 120, 34, ("[1]", "code"), "blue"); d.box(440, 100, 120, 34, ("[ ]", "code"), "blue")
    d.arrow([(160, 134), (90, 185)], label="take 2", lx=95, ly=152); d.arrow([(220, 134), (250, 185)], label="skip 2", lx=255, ly=152)
    d.arrow([(470, 134), (400, 185)], label="take 2", lx=405, ly=152); d.arrow([(530, 134), (570, 185)], label="skip 2", lx=580, ly=152)
    for x, s in [(40, "[1, 2]"), (210, "[1]"), (350, "[2]"), (520, "[ ]")]:
        d.box(x, 185, 100, 34, (s, "code"), "green")
    d.text(360, 255, "4 leaves = 4 subsets. After each branch we pop the last choice and try the next.", "small")
    d.text(360, 285, "choose → explore → un-choose", "bold")
    return d.render()


# ------------------------------------------------------------------ 17 Greedy
@diagram
def greedy():
    d = D("greedy", 720, 280, "Greedy: pick the interval that ends earliest",
          "Activity selection. Taking the earliest finish leaves the most room for the rest.")
    sx = lambda t: 40 + t * 55
    acts = [(1, 3), (2, 5), (4, 6), (6, 9), (5, 8)]
    chosen = {(1, 3), (4, 6), (6, 9)}
    for i, (s, e) in enumerate(sorted(acts, key=lambda a: a[1])):
        y = 30 + i * 38
        d.rect(sx(s), y, sx(e) - sx(s), 22, "bar green" if (s, e) in chosen else "bar dim")
        d.text(sx(e) + 10, y + 11, f"[{s},{e}]", "small", anchor="start")
    d.text(40, 240, "Sorted by end time. Take [1,3]; skip [2,5] (clashes); take [4,6]; skip [5,8]; take [6,9].", "small", anchor="start")
    d.text(40, 262, "green = chosen (3 activities)", "small", anchor="start")
    return d.render()


# ------------------------------------------------------------------ 18 DP
@diagram
def dp_grid():
    d = D("dp-grid", 720, 290, "Dynamic programming fills a table of small answers",
          "Unique paths in a 3×4 grid: each cell = paths from above + paths from the left. The corner holds the answer.")
    g = [[1, 1, 1, 1], [1, 2, 3, 4], [1, 3, 6, 10]]
    for r in range(3):
        for c in range(4):
            d.box(60 + c * 70, 30 + r * 56, 64, 48, (str(g[r][c]), "code"), "green" if (r, c) == (2, 3) else ("blue" if r == 0 or c == 0 else "box"))
    d.text(400, 60, "dp[r][c] = dp[r-1][c] + dp[r][c-1]", "code", anchor="start")
    d.text(400, 92, "blue: first row/column = 1 (base case)", "small", anchor="start")
    d.text(400, 118, "6 + 4 = 10", "bold", anchor="start")
    d.text(400, 144, "Each cell is computed once, so", "small", anchor="start")
    d.text(400, 166, "time = rows × cols, not 2^(rows+cols).", "small", anchor="start")
    return d.render()


@diagram
def dp_fib():
    d = D("dp-fib", 720, 270, "Overlapping sub-problems",
          "Plain recursion for fib(5) recomputes fib(3) and fib(2) again and again. A cache (memo) answers each only once.")
    pos = {"5": (260, 30), "4": (160, 90), "3a": (360, 90), "3b": (100, 160), "2a": (220, 160), "2b": (330, 160), "1": (420, 160)}
    lab = {"5": "f5", "4": "f4", "3a": "f3", "3b": "f3", "2a": "f2", "2b": "f2", "1": "f1"}
    for a, b in [("5", "4"), ("5", "3a"), ("4", "3b"), ("4", "2a"), ("3a", "2b"), ("3a", "1")]:
        d.line(pos[a][0], pos[a][1] + 16, pos[b][0], pos[b][1] - 16)
    for k, (x, y) in pos.items():
        d.box(x - 24, y - 16, 48, 32, (lab[k], "code"), "red" if lab[k] in ("f3", "f2") and k not in ("3a",) else "box")
    d.text(520, 60, "red = repeated work", "small", anchor="start")
    d.text(520, 100, "with memo: f3 and f2", "small", anchor="start")
    d.text(520, 122, "are computed once and", "small", anchor="start")
    d.text(520, 144, "looked up afterwards", "small", anchor="start")
    d.text(260, 225, "Time: O(2ⁿ) → O(n)", "bold")
    return d.render()


# ------------------------------------------------------------------ 19 XOR
@diagram
def xor():
    d = D("xor", 720, 290, "XOR cancels pairs",
          "a ^ a = 0 and a ^ 0 = a. XOR every number: the pairs cancel and the single one is left.")
    d.text(40, 25, "numbers: 4, 1, 2, 1, 2", "code", anchor="start")
    rows = [("4", "100"), ("1", "001"), ("2", "010"), ("1", "001"), ("2", "010")]
    run = 0
    y = 70
    d.text(40, y - 10, "value", "title", anchor="start"); d.text(140, y - 10, "bits", "title", anchor="start"); d.text(260, y - 10, "running XOR", "title", anchor="start")
    for v, b in rows:
        run ^= int(v)
        d.text(40, y + 14, v, "code", anchor="start"); d.text(140, y + 14, b, "code", anchor="start")
        d.box(260, y, 90, 28, (format(run, "03b") + f"  ({run})", "code"), "green" if v == rows[-1][0] and run == 4 else "box")
        y += 38
    d.text(400, 150, "1 ^ 1 = 0 and 2 ^ 2 = 0 cancel out", "small", anchor="start")
    d.text(400, 180, "Only 4 survives → answer = 4", "bold", anchor="start")
    return d.render()


# ------------------------------------------------------------------ 20 Top K
@diagram
def top_k():
    d = D("top-k", 720, 270, "Top K with a min-heap of size K",
          "Keep the K biggest seen so far. The smallest of them sits at the top, ready to be kicked out by a bigger newcomer.")
    d.text(40, 25, "stream: 5, 2, 9, 1, 7, 8   K = 3", "code", anchor="start")
    steps = [("after 5, 2, 9", [2, 5, 9], "heap full"), ("1 arrives", [2, 5, 9], "1 < top 2 → ignore"), ("7 arrives", [5, 7, 9], "7 > top 2 → pop 2, push 7"), ("8 arrives", [7, 8, 9], "8 > top 5 → pop 5, push 8")]
    y = 50
    for name, h, msg in steps:
        d.text(40, y + 18, name, "small", anchor="start")
        for j, v in enumerate(h):
            d.box(190 + j * 60, y, 54, 34, (str(v), "code"), "amber" if j == 0 else "blue")
        d.text(400, y + 18, msg, "small", anchor="start")
        y += 50
    d.text(190, 255, "amber = heap top (smallest of the K)", "small", anchor="start")
    return d.render()


# ------------------------------------------------------------------ 21 K-way merge
@diagram
def kway():
    d = D("kway", 720, 290, "Merge K sorted lists with a heap",
          "The heap always holds the current front of each list. Pop the smallest, then push the next item from the same list.")
    lists = [[1, 4, 7], [2, 5, 8], [3, 6, 9]]
    for i, l in enumerate(lists):
        d.text(40, 50 + i * 56, f"list {i + 1}", "small", anchor="start")
        cells(d, l, 100, 30 + i * 56, w=46, h=34, cls={0: "amber"}, idx=False)
    d.text(330, 20, "heap (fronts)", "title", anchor="start")
    for j, v in enumerate([1, 2, 3]):
        d.box(330 + j * 56, 32, 50, 34, (str(v), "code"), "amber")
    d.text(330, 90, "pop 1 → output [1]", "small", anchor="start")
    d.text(330, 112, "push next of list 1 → 4", "small", anchor="start")
    d.text(330, 140, "heap now 2, 3, 4", "small", anchor="start")
    d.text(330, 170, "pop 2 → output [1, 2] …", "small", anchor="start")
    d.text(330, 215, "output grows sorted: 1 2 3 4 5 6 7 8 9", "bold", anchor="start")
    d.text(330, 245, "N items total, heap of size K → O(N log K)", "small", anchor="start")
    return d.render()


# ------------------------------------------------------------------ 22 Two heaps
@diagram
def two_heaps():
    d = D("two-heaps", 720, 270, "Two heaps hold the two halves",
          "Max-heap = smaller half, min-heap = larger half. The median sits at the tops.")
    d.text(180, 20, "max-heap (smaller half)", "title"); d.text(520, 20, "min-heap (larger half)", "title")
    for j, v in enumerate([3, 2, 1]):
        d.box(100 + j * 60, 35, 54, 34, (str(v), "code"), "amber" if j == 0 else "blue")
    for j, v in enumerate([4, 5, 7]):
        d.box(430 + j * 60, 35, 54, 34, (str(v), "code"), "amber" if j == 0 else "green")
    d.text(130, 90, "top = 3", "small"); d.text(460, 90, "top = 4", "small")
    d.text(360, 140, "stream 1 2 3 4 5 7 → even count → median = (3 + 4) / 2 = 3.5", "code")
    d.text(360, 180, "add x: push to max-heap, move its top to min-heap,", "small")
    d.text(360, 202, "and if min-heap is bigger, move its top back.", "small")
    d.text(360, 235, "Sizes always differ by at most 1.", "bold")
    return d.render()


# ------------------------------------------------------------------ 23 Design data structure
@diagram
def lru():
    d = D("lru", 720, 290, "LRU cache = hash map + doubly linked list",
          "The map finds a node in O(1). The list keeps the order of use: most recent at the front, least recent at the back.")
    d.text(120, 20, "hash map", "title"); d.text(480, 20, "doubly linked list (recent → old)", "title")
    for i, (k, c) in enumerate([("A", "blue"), ("B", "green"), ("C", "amber")]):
        d.box(60, 40 + i * 50, 120, 36, (f"{k} → node {k}", "code"), c)
    xs = [330, 430, 530]
    for i, (k, c) in enumerate([("C", "amber"), ("A", "blue"), ("B", "green")]):
        d.box(xs[i], 80, 70, 40, (k, "code"), c)
        if i:
            d.arrow([(xs[i - 1] + 70, 92), (xs[i], 92)]); d.arrow([(xs[i], 108), (xs[i - 1] + 70, 108)])
    d.text(365, 150, "most recent", "small"); d.text(565, 150, "evict me", "small")
    d.text(360, 200, "get(A): look up in map, move node A to the front", "small")
    d.text(360, 225, "put(D) when full: drop the back node (B), add D at the front", "small")
    d.text(360, 255, "Both operations O(1)", "bold")
    return d.render()


if __name__ == "__main__":
    for fn in ALL:
        fn()
    print(f"wrote {len(ALL)} diagrams to {OUT}")
