"""Diagrams for the 40 Days of Agentic AI course.

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


# ------------------------------------------------------------------ Session 1
@diagram
def s01_variables():
    d = D("s01-variables", 720, 250, "Variables are labels pointing at values",
          "A variable is a name tag tied to a value. Re-assigning moves the tag; the old value is left behind.")
    d.text(120, 18, "NAME (label)", "title"); d.text(450, 18, "VALUE", "title"); d.text(640, 18, "TYPE", "title")
    d.box(40, 35, 160, 44, ("name", "code"), "blue")
    d.box(340, 35, 220, 44, ('"Syed Jafer K"', "code")); d.text(640, 57, "str", "small")
    d.arrow([(200, 57), (338, 57)])
    d.box(40, 110, 160, 44, ("age", "code"), "blue")
    d.box(340, 92, 220, 36, ("28", "code"), "ghost"); d.text(640, 110, "int  (before)", "small")
    d.box(340, 140, 220, 36, ('"Twenty Eight"', "code")); d.text(640, 158, "str  (after)", "small")
    d.arrow([(200, 125), (338, 110)], dashed=True)
    d.arrow([(200, 140), (338, 158)], kind="blue", label="age = \"Twenty Eight\"", lx=270, ly=175)
    d.box(40, 195, 160, 44, ("is_machine_on", "code"), "blue")
    d.box(340, 195, 220, 44, ("False", "code")); d.text(640, 217, "bool", "small")
    d.arrow([(200, 217), (338, 217)])
    return d.render()


@diagram
def s01_fizzbuzz():
    d = D("s01-fizzbuzz", 720, 372, "FizzBuzz decision order",
          "Python checks each condition from top to bottom and stops at the first one that is true. "
          "So the most specific check (divisible by 3 AND 5) must come first.")
    d.box(40, 15, 260, 40, "Take the next number n", "box")
    qs = [("Divisible by 3 AND 5?", "FizzBuzz"), ("Divisible by 3?", "Fizz"), ("Divisible by 5?", "Buzz")]
    y = 80
    d.arrow([(170, 55), (170, y - 2)])
    for i, (q, a) in enumerate(qs):
        d.box(40, y, 260, 44, q, "amber")
        d.box(440, y + 2, 160, 40, (a, "bold"), "green")
        d.arrow([(300, y + 22), (438, y + 22)], kind="green", label="yes", lx=370, ly=y + 10)
        if i < 2:
            d.arrow([(170, y + 44), (170, y + 78)], label="no", lx=190, ly=y + 62)
        y += 80
    d.arrow([(170, y - 36), (170, y - 2)], label="no", lx=190, ly=y - 18)
    d.box(40, y, 260, 40, ("print(n)", "code"), "box")
    return d.render()


# ------------------------------------------------------------------ Session 2
@diagram
def s02_list_indexes():
    d = D("s02-list", 720, 170, "List indexes",
          "Every item has a position. Count from 0 at the start, or from -1 at the end.")
    vals = [1, 10, 23, 2, 4, -9, 10]
    x0, w, g = 50, 82, 6
    for i, v in enumerate(vals):
        x = x0 + i * (w + g)
        d.text(x + w / 2, 30, i, "bold")
        d.box(x, 50, w, 56, (str(v), "code"), "blue" if i == 0 else "box")
        d.text(x + w / 2, 128, i - len(vals), "small")
    d.text(360, 155, "nums[0] → 1        nums[-3] → 4        len(nums) → 7", "code")
    return d.render()


@diagram
def s02_dict_tree():
    d = D("s02-dict", 720, 325, "A nested dictionary",
          "A dictionary maps keys to values. A value can itself be a dictionary, so you chain keys to go deeper.")
    d.box(30, 105, 130, 46, ("profile", "code"), "blue")
    for k, v, y in [('"name"', '"Syed Jafer K"', 20), ('"age"', "28", 85)]:
        d.arrow([(160, 128), (228, y + 20)])
        d.box(230, y, 120, 40, (k, "code"))
        d.arrow([(350, y + 20), (408, y + 20)]); d.box(410, y, 170, 40, (v, "code"))
    d.arrow([(160, 128), (228, 215)])
    d.box(230, 195, 120, 40, ('"marks"', "code"))
    for k, v, cy in [('"tamil"', "95", 170), ('"maths"', "45", 215), ('"biology"', "75", 260)]:
        hl = k == '"tamil"'
        kind = "green" if hl else ""
        d.arrow([(350, 215), (418, cy)], kind=kind)
        d.box(420, cy - 18, 120, 36, (k, "code"), "green" if hl else "box")
        d.arrow([(540, cy), (588, cy)], kind=kind)
        d.box(590, cy - 18, 90, 36, (v, "code"), "green" if hl else "box")
    d.text(360, 308, 'profile["marks"]["tamil"]  →  95', "code")
    return d.render()


@diagram
def s02_sets_venn():
    d = D("s02-venn", 720, 280, "Two sets compared",
          "intersection = in both · union = everything once · symmetric_difference = in exactly one")
    d.circle(275, 135, 120, "circle-a"); d.circle(445, 135, 120, "circle-b")
    d.text(200, 20, "Vandalur zoo", "bold"); d.text(520, 20, "Bannerghatta zoo", "bold")
    d.text(215, 115, "Elephant"); d.text(215, 155, "Kangaroo")
    d.text(360, 115, "Lion", "bold"); d.text(360, 155, "Giraffe", "bold")
    d.text(505, 115, "Gorilla"); d.text(505, 155, "Butterfly")
    d.text(360, 270, "intersection → {Lion, Giraffe}", "code")
    return d.render()


# ------------------------------------------------------------------ Session 3
@diagram
def s03_game_flow():
    d = D("s03-flow", 720, 380, "Number guessing game flow",
          "The game in boxes. Each box is one small function in the code.")
    d.box(20, 20, 150, 44, "Start: greet", "blue")
    d.box(200, 20, 150, 44, "Choose mode", "box")
    d.box(380, 20, 150, 44, "Pick secret", "box")
    d.arrow([(170, 42), (198, 42)]); d.arrow([(350, 42), (378, 42)])
    d.box(380, 110, 150, 44, "Ask for a guess", "box")
    d.arrow([(455, 64), (455, 108)])
    d.box(380, 195, 150, 44, "Correct?", "amber")
    d.arrow([(455, 154), (455, 193)])
    d.box(570, 195, 135, 44, ("You win! 🎉", "bold"), "green")
    d.arrow([(530, 217), (568, 217)], kind="green", label="yes", lx=549, ly=203)
    d.box(200, 195, 150, 44, ["Say higher /", "lower, attempts-1"], "box")
    d.arrow([(380, 217), (352, 217)], label="no", lx=366, ly=205)
    d.box(200, 285, 150, 44, "Attempts left?", "amber")
    d.arrow([(275, 239), (275, 283)])
    d.arrow([(200, 307), (150, 307), (150, 132), (378, 132)], kind="blue", label="yes: try again", lx=88, ly=220)
    d.box(380, 285, 150, 44, ("You lose", "bold"), "red")
    d.arrow([(350, 307), (378, 307)], label="no", lx=364, ly=295)
    d.box(570, 285, 135, 44, ["Save to", "leaderboard"], "box")
    d.arrow([(637, 239), (637, 283)])
    d.text(637, 355, "→ Play again?", "small")
    return d.render()


# ------------------------------------------------------------------ Session 4
def bars(d, x, y, items, maxw=300, h=26, gap=10, cls_for=None):
    for i, (label, p) in enumerate(items):
        yy = y + i * (h + gap)
        d.text(x - 12, yy + h / 2, label, "code", "end")
        cls = cls_for(i) if cls_for else "bar"
        d.rect(x, yy, max(4, maxw * p), h, cls)
        d.text(x + max(4, maxw * p) + 10, yy + h / 2, f"{round(p * 100)}%", "small", "start")


@diagram
def s04_next_word():
    d = D("s04-next-word", 720, 250, "An LLM predicts the next word",
          "The model gives every possible next word a probability, then picks one. Repeat, word after word.")
    d.box(20, 95, 250, 60, ['"The capital of', 'France is ..."'], "blue", "code")
    d.arrow([(270, 125), (318, 125)])
    d.text(470, 25, "Next-word probabilities", "title")
    bars(d, 420, 50, [("Paris", .92), ("a", .03), ("located", .02), ("Lyon", .01), ("…", .02)], maxw=230,
         cls_for=lambda i: "bar" if i == 0 else "bar dim")
    return d.render()


@diagram
def s04_temperature():
    d = D("s04-temperature", 720, 260, "Temperature changes how adventurous the model is",
          "Low temperature: the top choice almost always wins. High temperature: other choices get a real chance.")
    names = ["Bean & Brew", "Coffee Corner", "Roast Manifesto", "Grounds Rebellion"]
    d.text(180, 20, "temperature = 0.2  (safe)", "bold")
    bars(d, 170, 45, list(zip(names, [.85, .12, .02, .01])), maxw=150, cls_for=lambda i: "bar" if i == 0 else "bar dim")
    d.text(540, 20, "temperature = 1.0  (creative)", "bold")
    bars(d, 530, 45, list(zip(["", "", "", ""], [.35, .28, .2, .17])), maxw=150, cls_for=lambda i: "bar amber")
    d.text(360, 220, "Use low for facts, code and JSON. Use high for brainstorming.", "small")
    return d.render()


@diagram
def s04_topk_topp():
    d = D("s04-topk-topp", 720, 300, "Top-k and top-p cut-offs",
          "Top-k keeps a fixed number of words. Top-p keeps as many words as it takes to reach a total probability.")
    words = [("pizza", .45), ("pasta", .25), ("mangoes", .12), ("biryani", .08), ("rice", .05), ("cake", .03), ("cardboard", .02)]
    bars(d, 140, 30, words, maxw=360, h=24, gap=8, cls_for=lambda i: "bar" if i < 3 else "bar dim")
    d.line(110, 125, 640, 125, "line cut"); d.text(640, 113, "top-k = 3: keep these 3", "small", "end")
    d.line(110, 157, 640, 157, "line cut"); d.text(640, 145, "top-p = 0.9: 45+25+12+8 = 90% → keep 4", "small", "end")
    d.text(360, 282, 'Predicting the word after "I love eating ..."', "small")
    return d.render()


# ------------------------------------------------------------------ Session 5
@diagram
def s05_messages():
    d = D("s05-messages", 720, 250, "What you send to a chat model",
          "A chat request is a list of messages. The model reads all of them and writes the next assistant message.")
    rows = [("system", "You are a friendly maths tutor.", "purple"),
            ("user", "What is 15% of 80?", "blue"),
            ("assistant", "15% of 80 is 12.", "green"),
            ("user", "And 20%?", "blue")]
    for i, (role, txt, k) in enumerate(rows):
        y = 25 + i * 50
        d.box(20, y, 110, 38, (role, "code"), k)
        d.box(140, y, 250, 38, txt, "box")
    d.text(205, 230, "messages = [ ... ]  (a list of dictionaries)", "small")
    d.arrow([(392, 120), (448, 120)])
    d.box(450, 90, 110, 60, ("LLM", "bold"), "amber")
    d.arrow([(560, 120), (598, 120)])
    d.box(600, 90, 110, 60, ["assistant:", "\"16\""], "green", "code")
    return d.render()


@diagram
def s05_fewshot():
    d = D("s05-fewshot", 720, 270, "Few-shot prompting",
          "Show a few solved examples first. The model copies the pattern for the new input.")
    d.text(170, 15, "EXAMPLES YOU PROVIDE", "title"); d.text(530, 15, "ANSWER FORMAT", "title")
    ex = [("Order arrived broken", "Category: Shipping Damage | ..."),
          ("Charged twice this month", "Category: Billing | ..."),
          ("App crashes on upload", "Category: Bug Report | ...")]
    for i, (a, b) in enumerate(ex):
        y = 30 + i * 50
        d.box(20, y, 300, 38, a); d.arrow([(320, y + 19), (368, y + 19)]); d.box(370, y, 330, 38, (b, "code"))
    d.line(20, 192, 700, 192)
    d.box(20, 210, 300, 44, ("Screen flickers, won't turn on", "bold"), "blue")
    d.arrow([(320, 232), (368, 232)], kind="green", label="model follows the pattern", lx=345, ly=262)
    d.box(370, 210, 330, 44, ("Category: Hardware | ...", "code"), "green")
    return d.render()


@diagram
def s05_tot():
    d = D("s05-tot", 720, 300, "Tree of thought",
          "Propose several approaches, score them, then expand only the best one.")
    d.box(235, 15, 250, 44, ("Design question", "bold"), "blue")
    xs = [40, 270, 500]
    for i, (x, lab, score, k) in enumerate(zip(xs, "ABC", ["6/10", "9/10", "5/10"], ["box", "green", "box"])):
        d.arrow([(360, 59), (x + 90, 98)])
        d.box(x, 100, 180, 44, f"Approach {lab}", k)
        d.arrow([(x + 90, 144), (x + 90, 168)])
        d.box(x + 40, 170, 100, 36, (f"score {score}", "bold" if lab == "B" else ""), "green" if lab == "B" else "ghost")
    d.arrow([(360, 206), (360, 236)], kind="green")
    d.box(210, 238, 300, 44, ("Expand approach B in detail", "bold"), "green")
    d.text(90, 230, "1 propose", "small"); d.text(90, 250, "2 evaluate", "small"); d.text(90, 270, "3 expand", "small")
    return d.render()


@diagram
def s05_react():
    d = D("s05-react", 720, 300, "The ReAct loop",
          "Think, act with a tool, observe the result, and repeat until the model can give a final answer.")
    d.box(270, 30, 200, 50, ["Thought", ("I need the weather", "small")], "blue")
    d.box(500, 125, 200, 50, ["Action", ("get_weather[Chennai]", "code")], "amber")
    d.box(270, 225, 200, 50, ["Observation", ("32°C and Sunny", "small")], "green")
    d.arrow([(470, 55), (600, 55), (600, 123)])
    d.arrow([(600, 175), (600, 250), (472, 250)])
    d.arrow([(270, 250), (225, 250), (225, 55), (268, 55)], kind="blue")
    d.text(258, 150, "repeat", "small", "start")
    d.box(20, 125, 160, 50, ["Final Answer", ("It's 32°C in Chennai", "small")], "green")
    d.arrow([(330, 30), (330, 12), (100, 12), (100, 123)], kind="green", dashed=True)
    d.text(215, 24, "enough info → stop", "small")


# ------------------------------------------------------------------ Session 6
    return d.render()

@diagram
def s06_sequence():
    d = D("s06-sequence", 720, 345, "Tool calling step by step",
          "The model only asks for a tool. Your code runs it and sends the result back for the final answer.")
    lanes = [(110, "Your code", "blue"), (370, "LLM", "amber"), (620, "Tool (function)", "green")]
    for x, lab, k in lanes:
        d.box(x - 80, 10, 160, 38, (lab, "bold"), k)
        d.line(x, 48, x, 335)
    steps = [(110, 370, "① question + list of tools", ""),
             (370, 110, '② "please call get_weather(city=\'Paris\')"', ""),
             (110, 620, "③ your code runs get_weather('Paris')", "green"),
             (620, 110, "④ result: 'sunny, 25°C'", "green"),
             (110, 370, "⑤ question + request + result", ""),
             (370, 110, "⑥ \"Paris is sunny and 25°C.\"", "blue")]
    for i, (a, b, lab, k) in enumerate(steps):
        y = 85 + i * 45
        end = b - 4 if b > a else b + 4
        d.arrow([(a, y), (end, y)], kind=k)
        d.text((a + b) / 2, y - 12, lab, "small")
    return d.render()


# ------------------------------------------------------------------ Session 7
@diagram
def s07_pipeline():
    d = D("s07-pipeline", 720, 290, "The two halves of RAG",
          "Indexing prepares your documents once. Querying runs for every question and reuses the stored vectors.")
    d.text(20, 18, "1 · INDEXING (once)", "title", "start")
    row1 = ["PDF", "Load", "Clean", "Split", "Embed", "Chroma"]
    for i, lab in enumerate(row1):
        x = 20 + i * 117
        d.box(x, 35, 100, 44, (lab, "bold" if i in (0, 5) else ""), "purple" if i == 5 else ("blue" if i == 0 else "box"))
        if i:
            d.arrow([(x - 17, 57), (x - 2, 57)])
    d.text(20, 140, "2 · QUERYING (every question)", "title", "start")
    row2 = ["Question", "Embed", "Search", "Top 4", "Prompt", "LLM", "Answer"]
    for i, lab in enumerate(row2):
        x = 20 + i * 100
        k = "blue" if i == 0 else ("green" if i == 6 else ("amber" if i == 5 else "box"))
        d.box(x, 160, 86, 44, (lab, "bold" if i in (0, 6) else ""), k)
        if i:
            d.arrow([(x - 14, 182), (x - 2, 182)])
    d.arrow([(263, 158), (640, 80)], kind="blue", dashed=True, label="find the nearest chunks", lx=470, ly=105)
    d.text(360, 245, "Only the 4 most relevant chunks go into the prompt, not the whole book.", "small")
    return d.render()


@diagram
def s07_embeddings():
    d = D("s07-embeddings", 720, 300, "Embeddings put similar meanings close together",
          "Each chunk becomes a point. A question lands near the chunks that mean the same thing, even with different words.")
    d.rect(20, 15, 680, 270, "ghost", rx=12)
    groups = [("Loops", [(150, 80, "for loop over a list"), (120, 125, "while loop"), (230, 150, "iterate items")], "circle-a"),
              ("Dictionaries", [(480, 70, "dict keys & values"), (560, 110, "nested dictionary")], "circle-b"),
              ("Files", [(470, 225, "open a file"), (580, 245, "read text lines")], "circle-b")]
    for name, pts, cls in groups:
        for x, y, lab in pts:
            d.circle(x, y, 7, cls)
            d.text(x + 14, y, lab, "small", "start")
    d.circle(185, 200, 9, "amber")
    d.text(205, 200, '"How do I go through every item?"', "bold", "start")
    d.circle(175, 150, 70, "ghost")
    d.text(90, 270, "nearest = most similar meaning", "small", "start")
    return d.render()


@diagram
def s07_chunks():
    d = D("s07-chunks", 720, 190, "Chunks with overlap",
          "Neighbouring chunks share a little text, so a sentence cut at a boundary still appears whole in one chunk.")
    d.rect(20, 20, 680, 30, "box", rx=6)
    d.text(360, 35, "the whole page of text ............................................................", "small")
    d.box(20, 80, 260, 44, "chunk 1  (1000 chars)", "blue")
    d.box(230, 135, 260, 44, "chunk 2", "blue")
    d.box(440, 80, 260, 44, "chunk 3", "blue")
    d.rect(230, 80, 50, 44, "amber", rx=6); d.rect(440, 135, 50, 44, "amber", rx=6)
    d.text(255, 70, "overlap", "small")
    d.text(600, 160, "overlap = 150 chars", "small")
    return d.render()


# ------------------------------------------------------------------ Session 8
def timeline(d, x0, y, label, segs, scale, color):
    d.text(x0 - 12, y + 14, label, "", "end")
    for start, end, txt in segs:
        d.rect(x0 + start * scale, y, (end - start) * scale - 4, 28, color, rx=6)
        d.text(x0 + (start + end) / 2 * scale - 2, y + 14, txt, "small")


@diagram
def s08_kitchen():
    d = D("s08-kitchen", 720, 300, "Synchronous vs asynchronous",
          "Sync waits for each job before starting the next. Async starts both and waits once.")
    x0, sc = 170, 85
    d.text(20, 18, "SYNC  (time.sleep)", "title", "start")
    timeline(d, x0, 35, "make_toast", [(0, 3, "toasting 3s")], sc, "amber")
    timeline(d, x0, 72, "make_tea", [(3, 6, "boiling 3s")], sc, "amber")
    d.text(x0 + 6 * sc + 10, 72 + 14, "6 s", "bold", "start")
    d.text(20, 135, "ASYNC  (await asyncio.sleep + gather)", "title", "start")
    timeline(d, x0, 152, "make_toast", [(0, 2, "toasting 2s")], sc, "green")
    timeline(d, x0, 189, "make_tea", [(0, 3, "boiling 3s")], sc, "green")
    d.text(x0 + 3 * sc + 10, 189 + 14, "3 s", "bold", "start")
    d.line(x0, 240, x0 + 6 * sc, 240)
    for t in range(7):
        d.line(x0 + t * sc, 236, x0 + t * sc, 244)
        d.text(x0 + t * sc, 258, f"{t}s", "small")
    d.text(360, 285, "While one job waits, the other one runs.", "small")
    return d.render()


@diagram
def s08_gather():
    d = D("s08-gather", 720, 245, "Awaiting one by one vs gather",
          "await in a row is still sequential. asyncio.gather() starts all tasks together.")
    x0, sc = 230, 70
    d.text(20, 18, "await task1; await task2; await task3", "code", "start")
    timeline(d, x0, 32, "", [(0, 2, "Task 1"), (2, 4, "Task 2"), (4, 6, "Task 3")], sc, "amber")
    d.text(x0 + 6 * sc + 10, 46, "6 s", "bold", "start")
    d.text(20, 100, "await asyncio.gather(task1, task2, task3)", "code", "start")
    for i in range(3):
        timeline(d, x0, 115 + i * 34, "", [(0, 2, f"Task {i + 1}")], sc, "green")
    d.text(x0 + 2 * sc + 10, 166, "2 s", "bold", "start")
    return d.render()


# ------------------------------------------------------------------ Session 9
@diagram
def s09_gate():
    d = D("s09-gate", 720, 230, "Pydantic as a gate",
          "Data must pass the model's rules to get in. Bad data is stopped with a clear list of what's wrong.")
    d.box(20, 25, 230, 50, ['{"name": "Kavya",', '"age": 21}'], "box", "code")
    d.box(20, 140, 230, 50, ['{"name": "Kavya",', '"age": -9}'], "box", "code")
    d.box(300, 60, 140, 100, ["class User", ("name: str", "code"), ("age: int > 0", "code")], "blue")
    d.arrow([(250, 50), (298, 90)]); d.arrow([(250, 165), (298, 135)])
    d.box(490, 25, 210, 50, ["✓ User(name='Kavya',", "age=21)"], "green", "code")
    d.box(490, 140, 210, 50, ["✗ ValidationError", ("age: must be > 0", "small")], "red")
    d.arrow([(440, 90), (488, 50)], kind="green"); d.arrow([(440, 135), (488, 165)], kind="red")
    return d.render()


@diagram
def s09_nested():
    d = D("s09-nested", 720, 240, "Nested models",
          "Models can contain other models and lists of models. One call validates the whole tree.")
    d.box(20, 95, 120, 46, ("Order", "bold"), "blue")
    d.box(190, 40, 130, 44, "customer", "box"); d.box(190, 150, 130, 44, "items: list", "box")
    d.arrow([(140, 118), (188, 62)]); d.arrow([(140, 118), (188, 172)])
    d.box(370, 40, 130, 44, ("Customer", "bold"), "blue"); d.arrow([(320, 62), (368, 62)])
    d.box(590, 40, 110, 44, ("Address", "bold"), "blue"); d.arrow([(500, 62), (588, 62)])
    d.text(545, 48, "address", "small")
    d.box(370, 130, 130, 40, ("OrderItem", "bold"), "blue"); d.box(370, 180, 130, 40, ("OrderItem", "bold"), "blue")
    d.arrow([(320, 172), (368, 150)]); d.arrow([(320, 172), (368, 200)])
    d.text(610, 150, "order.customer", "code"); d.text(610, 172, ".address.city", "code"); d.text(610, 195, "→ 'Coimbatore'", "code")
    return d.render()

@diagram
def s09_structured():
    d = D("s09-structured", 720, 200, "Structured output from an LLM",
          "with_structured_output() sends your schema, then turns the model's JSON into a validated Python object.")
    d.box(10, 20, 150, 44, "Your question", "box")
    d.box(10, 110, 150, 54, ["MovieReview", ("schema", "small")], "blue")
    d.arrow([(160, 42), (198, 80)]); d.arrow([(160, 137), (198, 100)])
    d.box(200, 65, 80, 50, ("LLM", "bold"), "amber")
    d.arrow([(280, 90), (303, 90)])
    d.box(305, 55, 215, 70, ['{"name": "Interstellar",', '"rating": 9, ...}'], "box", "code")
    d.arrow([(520, 90), (548, 90)])
    d.text(534, 140, "validate", "small")
    d.box(550, 55, 160, 70, ["MovieReview", ("result.rating → 9", "code")], "green")


# ------------------------------------------------------------------ Session 10
    return d.render()

@diagram
def s10_stateless():
    d = D("s10-stateless", 720, 260, "The app resends the history every turn",
          "The model remembers nothing between calls. 'Memory' means sending earlier messages again, so the list keeps growing.")
    turns = [("Turn 1", ["You: I'm Jafer"]),
             ("Turn 2", ["You: I'm Jafer", "AI: Hi Jafer!", "You: I'm from Coimbatore"]),
             ("Turn 3", ["You: I'm Jafer", "AI: Hi Jafer!", "You: I'm from Coimbatore", "AI: Nice city!", "You: Where am I from?"])]
    for i, (t, msgs) in enumerate(turns):
        x = 20 + i * 235
        d.text(x + 105, 18, t + f"  ({len(msgs)} sent)", "bold")
        for j, m in enumerate(msgs):
            k = "blue" if m.startswith("You") else "green"
            d.box(x, 35 + j * 42, 210, 34, (m, "small"), k)
    return d.render()


@diagram
def s10_trim():
    d = D("s10-trim", 720, 345, "Three ways to keep history small",
          "Window keeps the first and last few messages. Token budget keeps the newest that fit. Summary compresses the old part.")
    for name, x in [("WINDOW", 20), ("TOKEN BUDGET", 260), ("SUMMARY", 500)]:
        d.text(x + 100, 15, name, "title")
    for j in range(7):
        y = 35 + j * 38
        keep = j == 0 or j >= 3
        d.box(20, y, 200, 30, (f"message {j + 1}", "small"), "blue" if keep else "ghost")
        if not keep:
            d.line(30, y + 15, 210, y + 15, "line cut")
        d.box(260, y, 200, 30, (f"message {j + 1}", "small"), "blue" if j >= 4 else "ghost")
    d.line(255, 186, 465, 186, "line cut")
    d.text(360, 307, "dashed line = 1024-token budget", "small")
    d.box(500, 35, 200, 104, ["Summary of", "messages 1–3", ("(written by the LLM)", "small")], "amber")
    for j in range(4):
        d.box(500, 149 + j * 38, 200, 30, (f"message {j + 4}", "small"), "blue")
    d.text(360, 330, "blue = sent to the model · dashed = dropped", "small")
    return d.render()

@diagram
def s10_threads_store():
    d = D("s10-threads-store", 720, 280, "Checkpointer vs Store",
          "A checkpointer remembers one conversation (thread). A Store remembers facts about a user across all their conversations.")
    d.text(170, 15, "CHECKPOINTER (per thread)", "title")
    d.box(20, 45, 140, 120, ["thread", ("session-1", "code"), ("chat history", "small")], "blue")
    d.box(180, 45, 140, 120, ["thread", ("session-2", "code"), ("chat history", "small")], "blue")
    d.text(170, 185, "separate — session-2 can't see session-1", "small")
    d.text(540, 15, "STORE (per user, all threads)", "title")
    d.box(400, 45, 300, 120, ["(\"memories\", \"Jafer\")", ("• plays chess, badminton", "small"), ("• likes cricket", "small")], "green")
    d.arrow([(90, 45), (90, 32), (370, 32), (370, 70), (398, 70)], kind="green", dashed=True)
    d.arrow([(320, 120), (398, 120)], kind="green", dashed=True)
    d.text(550, 185, "both threads read the same facts", "small")
    d.box(400, 210, 300, 50, ["(\"memories\", \"priya\")", ("empty — can't see Jafer's facts", "small")], "ghost")


# ------------------------------------------------------------------ Session 11
    return d.render()

@diagram
def s11_agent_loop():
    d = D("s11-agent-loop", 720, 260, "The agent loop",
          "Call the model, run any tools it asks for, send the results back, and repeat until it stops asking.")
    d.box(20, 105, 130, 50, ("Question", "bold"), "blue")
    d.arrow([(150, 130), (208, 130)])
    d.box(210, 105, 130, 50, ("LLM", "bold"), "amber")
    d.arrow([(340, 130), (398, 130)])
    d.box(400, 100, 140, 60, ["Asked for", "tools?"], "amber")
    d.box(590, 20, 110, 60, ["Run tools", ("(your code)", "small")], "box")
    d.arrow([(470, 100), (470, 50), (588, 50)], label="yes", lx=495, ly=38)
    d.arrow([(645, 80), (645, 215), (275, 215), (275, 157)], kind="blue", label="add results to messages, call again", lx=460, ly=232)
    d.box(590, 105, 110, 50, ("Answer", "bold"), "green")
    d.arrow([(540, 130), (588, 130)], kind="green", label="no", lx=562, ly=118)
    return d.render()


@diagram
def s11_db_layers():
    d = D("s11-db-layers", 720, 260, "Three safety layers for SQL tools",
          "Each layer stops a different kind of mistake. The read-only connection is the one that truly protects the data.")
    d.box(10, 25, 170, 50, ["Agent's SQL", ("SELECT ... JOIN", "code")], "blue")
    layers = [("① SELECT only", "check"), ("② read-only", "connection"), ("③ max 50 rows", "returned")]
    for i, (a, b) in enumerate(layers):
        x = 205 + i * 135
        d.box(x, 25, 125, 50, [(a, "bold"), (b, "small")], "amber")
        d.arrow([(x - 25, 50), (x - 2, 50)])
    d.arrow([(600, 50), (618, 50)])
    d.box(620, 25, 85, 50, ("shop.db", "code"), "green")
    d.box(10, 130, 170, 50, ["DROP TABLE orders", ("(or UPDATE ...)", "small")], "red", "code")
    d.arrow([(180, 155), (267, 155), (267, 77)], kind="red")
    d.text(300, 165, "✗ blocked", "small", "start")
    d.box(10, 200, 170, 44, ("SELECT * FROM orders", "code"), "box")
    d.arrow([(180, 222), (537, 222), (537, 77)])
    d.text(380, 236, "only 50 rows come back", "small")
    return d.render()

@diagram
def s11_mcp():
    d = D("s11-mcp", 720, 260, "Model Context Protocol",
          "One MCP server can serve many apps. Each app discovers the server's tools at runtime and calls them.")
    clients = ["Your LangChain agent", "Claude Desktop", "An IDE assistant"]
    for i, c in enumerate(clients):
        y = 25 + i * 75
        d.box(20, y, 200, 50, (c, "bold" if i == 0 else ""), "blue" if i == 0 else "box")
        d.arrow([(220, y + 25), (418, 130)], kind="blue" if i == 0 else "")
    d.text(320, 40, "MCP (stdio or HTTP)", "small")
    d.box(420, 70, 280, 120, ["MCP server \"utils\"", ("tool: add(a, b)", "code"), ("tool: reverse_text(text)", "code")], "green")
    d.text(560, 225, "get_tools() → ['add', 'reverse_text']", "code")
    return d.render()


# ------------------------------------------------------------------ Course map
@diagram
def map_agent():
    d = D("map-agent", 720, 345, "The building blocks of an agent",
          "Every session adds one building block. Together they make an agent: a model that can think, act, look things up and remember.")
    d.box(270, 130, 180, 70, ["AI Agent", ("Sessions 1–11", "small")], "blue")
    parts = [(30, 20, "The model", "Sessions 4–5", "amber"), (270, 20, "Tools", "Sessions 6, 11", "green"),
             (510, 20, "Knowledge (RAG)", "Session 7", "purple"), (30, 245, "Memory", "Session 10", "green"),
             (270, 245, "Typed output", "Session 9", "amber"), (510, 245, "Speed (async)", "Session 8", "purple")]
    for x, y, a, b, k in parts:
        d.box(x, y, 180, 60, [(a, "bold"), (b, "small")], k)
        cx, cy = x + 90, (y + 60 if y < 130 else y)
        tx = 360 + (cx - 360) * 0.45
        ty = 130 if y < 130 else 200
        d.line(cx, cy, tx, ty)
    d.text(360, 330, "Python foundations (Sessions 1–3) hold it all together", "small")
    return d.render()


if __name__ == "__main__":
    for fn in ALL:
        fn()
    print(len(ALL), "diagrams written to", OUT)
