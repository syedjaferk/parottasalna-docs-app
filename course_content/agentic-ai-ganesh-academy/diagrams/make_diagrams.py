"""Diagrams for the Agentic AI course.

Each function below writes one diagrams/<name>.html file: an inline SVG <figure> that pages include with

    ```{raw} html
    :file: ../diagrams/<name>.html
    ```

Colours come from the .dg / figure.diagram classes in the docs CSS (courses/builder.py), so diagrams follow
light and dark mode. Edit a function, then run:  python course_content/agentic-ai-ganesh-academy/diagrams/make_diagrams.py
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


# ------------------------------------------------------------------ Session 1 · Talking to an LLM
@diagram
def s01_request():
    d = D("s01-request", 720, 250, "A chat request, end to end",
          "Your code sends the whole conversation (a list of messages with roles) to the API. "
          "The model writes the next message, which comes back in choices[0].message.content.")
    d.rect(20, 20, 250, 210, "blue", rx=14)
    d.text(145, 40, "messages = [ … ]", "code")
    d.box(35, 58, 220, 44, ["system", ("rules: role, tone, limits", "small")], "box")
    d.box(35, 112, 220, 44, ["user", ("the question", "small")], "box")
    d.box(35, 166, 220, 44, ["assistant", ("earlier replies / examples", "small")], "box")
    d.arrow([(270, 125), (338, 125)], "blue", label="POST", lx=304, ly=110)
    d.box(340, 75, 170, 100, ["Groq API", ("openai/gpt-oss-120b", "code"), ("temperature 0–1", "small")], "amber")
    d.arrow([(510, 125), (553, 125)], "green", label="JSON", lx=531, ly=110)
    d.box(555, 75, 150, 100, ["answer", ("choices[0]", "code"), (".message.content", "code")], "green")
    return d.render()


@diagram
def s01_shots():
    d = D("s01-shots", 720, 230, "Zero-shot, one-shot, few-shot",
          "The more worked examples you put before the real question, the more closely the model copies their method "
          "and format.")
    cols = [("Zero-shot", ["question"]), ("One-shot", ["example Q", "example A", "question"]),
            ("Few-shot", ["example Q", "example A", "example Q", "example A", "question"])]
    for i, (name, rows) in enumerate(cols):
        x = 20 + i * 235
        d.rect(x, 20, 220, 190, "ghost", rx=12)
        d.text(x + 110, 40, name, "bold")
        for j, r in enumerate(rows):
            kind = "green" if r == "question" else ("box" if "Q" in r else "blue")
            d.box(x + 20, 56 + j * 29, 180, 24, (r, "small"), kind, rx=6)
    return d.render()


# ------------------------------------------------------------------ Session 2 · Reasoning prompts
@diagram
def s02_react():
    d = D("s02-react", 720, 270, "The ReAct loop",
          "The model writes a Thought and an Action. Your code runs the tool and sends back the Observation. "
          "The loop repeats until the model writes a Final Answer (or you hit the round limit).")
    d.box(20, 105, 140, 60, ["Question", ("weather in Chennai?", "small")], "box")
    d.arrow([(160, 135), (178, 135), (178, 65), (188, 65)])
    d.box(190, 30, 260, 70, ["LLM", ("Thought: I need the weather", "small"), ("Action: get_weather[Chennai]", "code")], "blue")
    d.arrow([(450, 65), (488, 65)], "blue")
    d.text(469, 20, "parse", "small")
    d.box(490, 30, 210, 70, ["your code runs it", ("get_weather('Chennai')", "code")], "amber")
    d.arrow([(595, 100), (595, 180), (432, 180)], "green")
    d.text(595, 200, "Observation: 32°C and Sunny", "small")
    d.arrow([(320, 160), (320, 102)], "green")
    d.box(220, 160, 210, 40, ("messages += Observation", "small"), "green")
    d.arrow([(320, 200), (320, 222)])
    d.box(220, 222, 210, 38, ("Final Answer: 32°C, sunny", "small"), "green")
    return d.render()


@diagram
def s02_self_consistency():
    d = D("s02-self-consistency", 720, 230, "Self-consistency",
          "Ask the same question several times with some randomness, pull the final number out of each answer, "
          "and keep the most common one.")
    d.box(20, 85, 130, 60, ["Question", ("temperature 0.7", "small")], "box")
    answers = ["650", "650", "625", "650", "650"]
    for i, a in enumerate(answers):
        y = 20 + i * 40
        d.arrow([(150, 115), (238, y + 15)], head=True)
        d.box(240, y, 170, 30, (f"path {i + 1} → Final Answer: {a}", "small"), "red" if a != "650" else "blue", rx=6)
        d.arrow([(410, y + 15), (488, 115)], head=True)
    d.box(490, 75, 100, 80, ["vote", ("Counter", "code")], "amber")
    d.arrow([(590, 115), (618, 115)], "green")
    d.box(620, 85, 85, 60, ["650", ("4 of 5", "small")], "green")
    return d.render()


# ------------------------------------------------------------------ Session 3 · Embeddings
@diagram
def s03_space():
    d = D("s03-space", 720, 260, "Embeddings put similar meanings close together",
          "An embedding model turns each sentence into a vector. Drawn in 2-D, sentences about the same topic land "
          "near each other, and a question lands next to the sentences that answer it.")
    d.box(20, 70, 200, 120, ["sentence", ("↓ embedding model", "small"), ("[-0.07, 0.02, … ]", "code"), ("384 numbers", "small")], "blue")
    d.arrow([(220, 130), (268, 130)])
    d.rect(270, 20, 430, 220, "ghost", rx=12)
    pts = [(330, 70, "Python is a language", "blue"), (360, 110, "learn Python", "blue"),
           (560, 70, "I love pizza", "red"), (580, 110, "pasta recipe", "red"),
           (430, 205, "Redis is in-memory", "green"), (520, 228, "PostgreSQL database", "green")]
    for x, y, t, c in pts:
        d.circle(x, y, 7, c)
        d.text(x + 12, y, t, "small", "start")
    d.circle(455, 160, 9, "amber")
    d.text(470, 150, "Q: which DB is in memory?", "small", "start")
    d.arrow([(452, 168), (435, 197)], "green", dashed=True, head=False)
    return d.render()


@diagram
def s03_vdb():
    d = D("s03-vdb", 720, 230, "Store, then search",
          "Flow 1 stores each document with its vector. Flow 2 embeds the question with the SAME model and asks the "
          "vector database for the nearest documents.")
    d.text(20, 30, "FLOW 1 · store", "bold", "start")
    d.box(20, 45, 140, 50, ("documents", "small"), "box")
    d.arrow([(160, 70), (218, 70)])
    d.box(220, 45, 160, 50, ["embedding model", ("nomic / MiniLM", "small")], "blue")
    d.arrow([(380, 70), (478, 95)])
    d.box(480, 80, 220, 70, ["Vector DB", ("Chroma · FAISS · Pinecone", "small"), ("text + vector + metadata", "small")], "green")
    d.text(20, 140, "FLOW 2 · search", "bold", "start")
    d.box(20, 155, 140, 50, ("question", "small"), "box")
    d.arrow([(160, 180), (218, 180)])
    d.box(220, 155, 160, 50, ["same model", ("→ query vector", "small")], "blue")
    d.arrow([(380, 180), (478, 140)], label="nearest k", lx=440, ly=175)
    return d.render()


# ------------------------------------------------------------------ Session 4 · Sparse and hybrid
@diagram
def s04_sparse_dense():
    d = D("s04-sparse-dense", 720, 220, "Sparse vs dense vectors",
          "A sparse vector has one slot per word in the vocabulary, almost all zero. A dense vector has a few hundred "
          "numbers, all used, that capture meaning rather than exact words.")
    d.text(20, 30, "Sparse (TF-IDF / BM25)", "bold", "start")
    words = ["python", "redis", "fastapi", "docker", "db", "…", "zebra"]
    vals = ["0.6", "0", "0.8", "0", "0", "…", "0"]
    for i, (w, v) in enumerate(zip(words, vals)):
        x = 20 + i * 70
        d.box(x, 45, 64, 34, (v, "code"), "blue" if v not in ("0", "…") else "ghost", rx=6)
        d.text(x + 32, 92, w, "small")
    d.text(530, 62, "50,000 slots, mostly 0", "small", "start")
    d.text(20, 130, "Dense (embeddings)", "bold", "start")
    for i, v in enumerate(["-0.07", "0.21", "0.03", "-0.12", "0.09", "…", "0.04"]):
        d.box(20 + i * 70, 145, 64, 34, (v, "code"), "green", rx=6)
    d.text(530, 162, "384 slots, all used", "small", "start")
    d.text(20, 205, "matches exact words: codes, names, errors", "small", "start")
    d.text(420, 205, "matches meaning: synonyms, paraphrases", "small", "start")
    return d.render()


@diagram
def s04_hybrid():
    d = D("s04-hybrid", 720, 230, "Hybrid search",
          "Run keyword (BM25) and vector search for the same question, put both score lists on the same scale, "
          "then combine them into one ranking.")
    d.box(20, 85, 140, 60, ["question", ("Redis async backend", "small")], "box")
    d.arrow([(160, 100), (198, 55)])
    d.arrow([(160, 130), (198, 175)])
    d.box(200, 25, 180, 60, ["BM25", ("scores 0 … 10+", "small")], "blue")
    d.box(200, 145, 180, 60, ["Dense (cosine)", ("scores -1 … 1", "small")], "green")
    d.arrow([(380, 55), (438, 100)])
    d.arrow([(380, 175), (438, 130)])
    d.box(440, 80, 130, 70, ["normalise", ("then 0.5·a + 0.5·b", "small"), ("or rank fusion", "small")], "amber")
    d.arrow([(570, 115), (608, 115)], "green")
    d.box(610, 80, 95, 70, ["one", "ranking"], "green")
    return d.render()


# ------------------------------------------------------------------ Session 5 · Chunking
@diagram
def s05_chunking():
    d = D("s05-chunking", 720, 250, "Four ways to cut the same text",
          "Fixed size cuts anywhere, even mid-word. Overlap repeats the edges. Sentence chunking never splits a "
          "sentence. Semantic chunking starts a new chunk when the topic changes.")
    rows = [
        ("Fixed (200)", [(0, 200, "blue"), (200, 400, "blue"), (400, 600, "blue"), (600, 650, "blue")]),
        ("Overlap (200/50)", [(0, 200, "blue"), (150, 350, "green"), (300, 500, "blue"), (450, 650, "green")]),
        ("Sentences", [(0, 170, "blue"), (170, 390, "green"), (390, 520, "blue"), (520, 650, "green")]),
        ("Semantic", [(0, 300, "blue"), (300, 480, "green"), (480, 650, "amber")]),
    ]
    scale = 0.75
    for r, (label, segs) in enumerate(rows):
        y = 25 + r * 52
        d.text(150, y + 15, label, "small", "end")
        for k, (a, b, c) in enumerate(segs):
            off = 8 if label.startswith("Overlap") and k % 2 else 0
            d.rect(160 + a * scale, y + off, (b - a) * scale - 3, 26, c, rx=5)
    d.text(160, 235, "cuts “bitma|ps”", "small", "start")
    d.text(560, 235, "same topic = one chunk", "small", "start")
    return d.render()


# ------------------------------------------------------------------ Session 6 · First RAG pipeline
@diagram
def s06_pipeline():
    d = D("s06-pipeline", 720, 250, "The two halves of RAG",
          "Ingest runs once (or when documents change) and fills the vector database. Ask runs for every question: "
          "retrieve chunks, put them in the prompt, generate the answer.")
    d.text(20, 25, "INGEST", "bold", "start")
    steps = [("PDF", "box"), ("clean", "box"), ("chunks", "box"), ("embeddings", "blue")]
    for i, (t, k) in enumerate(steps):
        x = 20 + i * 125
        d.box(x, 40, 105, 44, (t, "small"), k)
        if i:
            d.arrow([(x - 20, 62), (x - 2, 62)])
    d.arrow([(505, 62), (548, 62)])
    d.box(550, 30, 150, 64, ["Vector DB", ("Chroma / FAISS", "small")], "green")
    d.text(20, 135, "ASK", "bold", "start")
    asks = [("question", "box"), ("top-k chunks", "green"), ("prompt", "amber"), ("LLM", "blue"), ("answer", "green")]
    for i, (t, k) in enumerate(asks):
        x = 20 + i * 140
        d.box(x, 150, 115, 44, (t, "small"), k)
        if i:
            d.arrow([(x - 25, 172), (x - 2, 172)])
    d.arrow([(625, 94), (625, 120), (200, 120), (200, 148)], "green", dashed=True, label="retrieve", lx=400, ly=108)
    d.text(420, 222, "“Use only provided context.” + chunks + question", "small")
    return d.render()


# ------------------------------------------------------------------ Session 7 · n8n
@diagram
def s07_n8n():
    d = D("s07-n8n", 720, 260, "The n8n RAG workflow",
          "Ingest: an uploaded file is loaded, split and embedded into Pinecone. Ask: an AI Agent uses Groq as its "
          "model and the Pinecone store as a retrieval tool, then sends the answer to Telegram.")
    d.text(20, 25, "INGEST", "bold", "start")
    d.box(20, 40, 130, 50, ["Upload File", ("form", "small")], "box")
    d.arrow([(150, 65), (198, 65)])
    d.box(200, 40, 170, 50, ["Pinecone (insert)", ("index js-book", "small")], "green")
    d.box(400, 30, 140, 30, ("Data Loader", "small"), "box", rx=6)
    d.box(400, 66, 140, 30, ("Text Splitter", "small"), "box", rx=6)
    d.box(560, 48, 140, 30, ("Ollama embeddings", "small"), "blue", rx=6)
    d.arrow([(400, 45), (372, 58)], dashed=True)
    d.arrow([(560, 63), (372, 66)], dashed=True)
    d.text(20, 140, "ASK", "bold", "start")
    d.box(20, 160, 130, 50, ["query", ("Edit Fields / chat", "small")], "box")
    d.arrow([(150, 185), (228, 185)])
    d.box(230, 155, 170, 60, ["AI Agent", ("answers from context", "small")], "amber")
    d.arrow([(400, 185), (548, 185)])
    d.box(550, 160, 150, 50, ["Telegram", ("send message", "small")], "box")
    d.box(200, 225, 110, 28, ("Groq model", "small"), "blue", rx=6)
    d.box(320, 225, 200, 28, ("Pinecone (retrieve-as-tool)", "small"), "green", rx=6)
    d.arrow([(255, 225), (285, 217)], dashed=True)
    d.arrow([(400, 225), (360, 217)], dashed=True)
    return d.render()


# ------------------------------------------------------------------ Session 8 · Filtering and reranking
@diagram
def s08_rerank():
    d = D("s08-rerank", 720, 240, "Filter, shortlist, rerank",
          "A metadata filter limits which chunks may match. Fast vector search shortlists about 15. A slower, more "
          "accurate cross-encoder re-scores each (question, chunk) pair and keeps the best few for the LLM.")
    d.box(20, 90, 120, 60, ["question", ("+ filter", "small")], "box")
    d.arrow([(140, 120), (178, 120)])
    d.box(180, 30, 160, 180, [], "blue")
    d.text(260, 50, "Vector DB", "bold")
    d.box(185, 70, 150, 36, ("filter: Database", "code"), "amber", rx=6)
    d.text(260, 125, "bi-encoder search", "small")
    d.text(260, 145, "fast, rough", "small")
    d.text(260, 180, "top 15", "bold")
    d.arrow([(340, 120), (398, 120)], label="15 chunks", lx=369, ly=106)
    d.box(400, 60, 160, 120, ["Cross-encoder", ("reads question + chunk", "small"), ("together", "small"), ("slow, accurate", "small")], "amber")
    d.arrow([(560, 120), (598, 120)], "green", label="top 4", lx=579, ly=106)
    d.box(600, 90, 100, 60, ("LLM", ""), "green")
    return d.render()


# ------------------------------------------------------------------ Session 9 · Semantic caching
@diagram
def s09_cache():
    d = D("s09-cache", 720, 250, "A semantic cache in front of RAG",
          "Embed the question and compare it with cached questions. Similar enough (≥ 0.90): return the saved answer "
          "instantly. Otherwise run the full RAG pipeline and save the new answer.")
    d.box(20, 95, 145, 60, ["question", ("“explain python lists”", "small")], "box")
    d.arrow([(165, 125), (188, 125)])
    d.box(190, 85, 150, 80, ["Redis cache", ("similar question?", "small"), ("cosine ≥ 0.90", "code")], "amber")
    d.arrow([(340, 105), (420, 45)], "green", label="HIT", lx=372, ly=62)
    d.box(422, 20, 280, 50, ["return saved answer", ("milliseconds · no LLM cost", "small")], "green")
    d.arrow([(340, 145), (420, 185)], "red", label="MISS", lx=372, ly=182)
    d.box(422, 160, 170, 60, ["retrieve + LLM", ("seconds · tokens", "small")], "blue")
    d.arrow([(592, 190), (640, 190), (640, 230), (265, 230), (265, 167)], dashed=True, label="store question + vector + answer", lx=455, ly=242)
    return d.render()


# ------------------------------------------------------------------ Session 10 · Queries and context
@diagram
def s10_query():
    d = D("s10-query", 720, 250, "Fix the question, then trim the context",
          "Rewrite the question using the chat history, expand it into several searches, merge the results without "
          "duplicates, then compress the context to the sentences that matter before asking the LLM.")
    d.box(20, 95, 110, 60, ["“How do I", "deploy it?”"], "box")
    d.arrow([(130, 125), (158, 125)])
    d.box(160, 85, 120, 80, ["rewrite", ("+ history", "small"), ("→ deploy FastAPI", "small")], "blue")
    d.arrow([(280, 125), (308, 125)])
    for i in range(5):
        d.box(310, 25 + i * 42, 120, 32, (f"query {i + 1}", "small"), "blue", rx=6)
        d.arrow([(430, 41 + i * 42), (468, 125)], head=False)
    d.box(470, 95, 90, 60, ["merge", ("dedupe", "small")], "green")
    d.arrow([(560, 125), (578, 125)])
    d.box(580, 85, 120, 80, ["compress", ("keyword / embed", "small"), ("/ LLM", "small")], "amber")
    d.text(640, 190, "→ LLM", "bold")
    return d.render()


# ------------------------------------------------------------------ Session 11 · Advanced retrievers
@diagram
def s11_parent():
    d = D("s11-parent", 720, 240, "Parent document retriever",
          "Small child chunks are embedded and searched, so matches are precise. Each child remembers its parent, and "
          "the retriever returns the big parent, so the LLM gets the full context.")
    for p in range(2):
        x = 20 + p * 250
        d.box(x, 30, 230, 90, [], "amber")
        d.text(x + 115, 48, f"parent {p + 1} (3,000 chars)", "bold")
        for c in range(4):
            d.box(x + 10 + c * 55, 70, 48, 36, (f"c{c + 1}", "small"), "green" if (p, c) == (1, 2) else "blue", rx=6)
    d.text(140, 140, "children (300 chars) → vectors in Chroma", "small")
    d.text(390, 140, "parents → docstore (no vectors)", "small")
    d.box(540, 30, 160, 60, ["question", ("“list comprehension”", "small")], "box")
    d.arrow([(540, 60), (461, 88)], "green", label="matches child c3", lx=560, ly=110)
    d.arrow([(385, 120), (385, 175), (520, 195)], "green", label="return its parent", lx=450, ly=170)
    d.box(520, 170, 180, 50, ["LLM", ("gets the whole parent", "small")], "green")
    return d.render()


@diagram
def s11_multihop():
    d = D("s11-multihop", 720, 210, "Multi-hop retrieval",
          "The first search finds a fact that points somewhere else. A second search, written from that fact, "
          "finds the rest of the answer.")
    d.box(20, 75, 150, 60, ["How does S3 reduce", "storage cost?"], "box")
    d.arrow([(170, 105), (208, 105)], label="hop 1", lx=189, ly=90)
    d.box(210, 60, 180, 90, ["Lifecycle Policies", ("move old objects", "small"), ("to Glacier", "small")], "blue")
    d.arrow([(390, 105), (428, 105)], label="hop 2", lx=409, ly=90)
    d.box(430, 60, 160, 90, ["search “Glacier”", ("low-cost archive", "small"), ("Deep Archive cheapest", "small")], "blue")
    d.arrow([(590, 105), (618, 105)], "green")
    d.box(620, 75, 85, 60, ["answer", ("both hops", "small")], "green")
    return d.render()


# ------------------------------------------------------------------ Session 12 · Production RAG
@diagram
def s12_stream():
    d = D("s12-stream", 720, 240, "Streaming RAG with Server-Sent Events",
          "The browser opens one long HTTP request. FastAPI retrieves context, then forwards each token from Groq as an "
          "SSE event the moment it arrives, ending with a done event.")
    d.box(20, 80, 140, 80, ["Browser", ("EventSource", "code"), ("textContent +=", "code")], "box")
    d.arrow([(160, 100), (238, 100)], label="GET /chat?question=", lx=199, ly=86)
    d.box(240, 60, 200, 120, ["FastAPI", ("EventSourceResponse", "code"), ("1 · retrieve (Chroma)", "small"), ("2 · stream tokens", "small")], "blue")
    d.arrow([(440, 100), (518, 100)], label="stream=True", lx=479, ly=86)
    d.box(520, 70, 180, 100, ["Groq", ("token · token · token", "small")], "amber")
    d.arrow([(518, 145), (442, 145)], "green")
    d.arrow([(238, 145), (162, 145)], "green", label="event: token", lx=200, ly=160)
    d.text(200, 210, "… event: done → close", "small")
    return d.render()


# ------------------------------------------------------------------ Session 13 · Async
@diagram
def s13_async():
    d = D("s13-async", 720, 210, "Sequential vs gather",
          "Awaiting three 2-second tasks one by one takes 6 seconds. asyncio.gather starts them together, so the "
          "total is the longest task: 2 seconds.")
    scale = 90
    x0 = 170
    d.text(x0 - 12, 50, "await × 3", "", "end")
    for i in range(3):
        d.rect(x0 + i * 2 * scale, 36, 2 * scale - 4, 28, "blue", rx=6)
        d.text(x0 + i * 2 * scale + scale, 50, f"Task {i + 1}", "small")
    d.text(x0 - 12, 120, "gather()", "", "end")
    for i in range(3):
        d.rect(x0, 95 + i * 22, 2 * scale - 4, 18, "green", rx=5)
        d.text(x0 + scale, 104 + i * 22, f"Task {i + 1}", "small")
    for s in range(7):
        d.line(x0 + s * scale, 170, x0 + s * scale, 176)
        d.text(x0 + s * scale, 190, f"{s}s", "small")
    d.line(x0, 170, x0 + 6 * scale, 170)
    return d.render()


# ------------------------------------------------------------------ Session 14 · Pydantic
@diagram
def s14_validate():
    d = D("s14-validate", 720, 220, "What Pydantic does with incoming data",
          "Data from a form, an API or an LLM goes through your model. Values that can be safely converted are "
          "converted; anything else raises a ValidationError that names the field and the problem.")
    d.box(20, 70, 170, 80, ["raw data", ('{"name": "Kavya",', "code"), ('"age": "9"}', "code")], "box")
    d.arrow([(190, 110), (238, 110)])
    d.box(240, 50, 190, 120, ["class User(BaseModel)", ("name: str", "code"), ("age: int = Field(gt=0)", "code")], "blue")
    d.arrow([(430, 85), (488, 55)], "green", label="valid", lx=455, ly=55)
    d.box(490, 25, 210, 60, ["User object", ("name='Kavya' age=9", "code")], "green")
    d.arrow([(430, 135), (488, 165)], "red", label="invalid", lx=455, ly=170)
    d.box(490, 135, 210, 60, ["ValidationError", ("age: greater than 0", "small")], "red")
    return d.render()


# ------------------------------------------------------------------ Session 15 · Memory
@diagram
def s15_memory():
    d = D("s15-memory", 720, 250, "Short-term vs long-term memory",
          "A checkpointer keeps each conversation (thread_id) separately: short-term memory. A Store is shared by all "
          "threads and organised by user: long-term memory the agent reads and writes with tools.")
    d.rect(20, 20, 400, 210, "blue", rx=14)
    d.text(220, 40, "Checkpointer · per thread_id", "bold")
    for i, (t, sub) in enumerate([("thread user-1", "Hi, I'm Jafer… / Where am I from?"), ("thread user-2", "fresh, empty")]):
        d.box(35, 60 + i * 80, 370, 64, [t, (sub, "small")], "box")
    d.rect(450, 20, 250, 210, "green", rx=14)
    d.text(575, 40, "Store · across threads", "bold")
    d.box(465, 60, 220, 64, ["(\"memories\", \"Jafer\")", ("likes chess, badminton…", "small")], "box")
    d.box(465, 140, 220, 64, ["(\"memories\", \"priya\")", ("nothing yet", "small")], "box")
    d.arrow([(405, 92), (463, 92)], "green", dashed=True, label="save_memory", lx=434, ly=78)
    return d.render()


# ------------------------------------------------------------------ Session 16 · Tools and MCP
@diagram
def s16_tool_loop():
    d = D("s16-tool-loop", 720, 250, "The tool-calling loop",
          "The model never runs code. It returns tool_calls; your code (or the agent) runs each tool and sends the "
          "result back as a ToolMessage, until the model replies with no tool calls.")
    d.box(20, 95, 120, 60, ["question", ("12 × 7, then + 5", "small")], "box")
    d.arrow([(140, 125), (198, 125)])
    d.box(200, 80, 170, 90, ["LLM + tools", ("bind_tools([add,", "code"), ("multiply])", "code")], "blue")
    d.arrow([(370, 105), (448, 70)], "blue", label="tool_calls", lx=400, ly=72)
    d.box(450, 30, 250, 70, ["your code runs it", ("multiply(a=12, b=7) → 84", "code")], "amber")
    d.arrow([(575, 100), (575, 140), (372, 140)], "green", label="ToolMessage: 84", lx=575, ly=155)
    d.arrow([(285, 170), (285, 205)], "green")
    d.box(200, 205, 170, 36, ("no tool_calls → answer 89", "small"), "green")
    return d.render()


@diagram
def s16_mcp():
    d = D("s16-mcp", 720, 210, "MCP: tools as a service",
          "An MCP server offers tools over a standard protocol. Any MCP client (a LangChain agent, Claude Desktop, an "
          "IDE) can discover and call them, so a tool is written once and used everywhere.")
    clients = ["LangChain agent", "Claude Desktop", "IDE assistant"]
    for i, c in enumerate(clients):
        d.box(20, 20 + i * 62, 180, 48, (c, ""), "blue")
        d.arrow([(200, 44 + i * 62), (318, 105)], "blue", head=True)
    d.text(260, 190, "MCP (stdio / HTTP)", "small")
    d.box(320, 55, 180, 100, ["MCP server", ("FastMCP(\"utils\")", "code"), ("list_tools · call_tool", "small")], "amber")
    d.arrow([(500, 85), (538, 60)])
    d.arrow([(500, 125), (538, 150)])
    d.box(540, 35, 160, 50, ("add(a, b)", "code"), "green")
    d.box(540, 125, 160, 50, ("reverse_text(text)", "code"), "green")
    return d.render()


if __name__ == "__main__":
    for fn in ALL:
        fn()
    print(len(ALL), "diagrams written to", OUT)
