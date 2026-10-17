"""Diagrams for the Go course.

Each function below writes one diagrams/<name>.html file: an inline SVG <figure> that sessions include with

    ```{raw} html
    :file: ../diagrams/<name>.html
    ```

Colours come from the .dg / figure.diagram classes in the docs CSS (courses/builder.py), so diagrams follow
light and dark mode. Edit a function, then run:  python course_content/go-lang/diagrams/make_diagrams.py
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
def flow(d, y, items, x=30, w=140, h=56, gap=40, labels=None):
    """A left-to-right row of boxes joined by arrows. items = [(lines, kind)]. Returns box centres."""
    xs = []
    for i, (lines, kind) in enumerate(items):
        bx = x + i * (w + gap)
        d.box(bx, y, w, h, lines, kind)
        xs.append(bx + w / 2)
        if i:
            d.arrow([(bx - gap + 2, y + h / 2), (bx - 2, y + h / 2)], label=(labels or {}).get(i), ly=y + h / 2 - 14)
    return xs


def cells(d, vals, x, y, w=56, h=44, cls=None, idx=True, gap=6):
    cls = cls or {}
    for i, v in enumerate(vals):
        cx = x + i * (w + gap)
        d.box(cx, y, w, h, (str(v), "code"), cls.get(i, "box"))
        if idx:
            d.text(cx + w / 2, y + h + 14, i, "small")


# ------------------------------------------------------------------ 0 course map
@diagram
def course_map():
    d = D("course-map", 760, 345, "The 18 sessions in four phases",
          "Foundations, then files and command-line tools, then web APIs and databases, then concurrency and testing.")
    cols = [("1 · Foundations", "blue", ["Hello & basics", "Functions", "Arrays & slices", "Maps", "Structs & JSON", "Pointers", "Errors"]),
            ("2 · Files & CLI", "green", ["Files", "Args & flags", "Logging & config"]),
            ("3 · Web & data", "amber", ["HTTP", "Todo API", "Database"]),
            ("4 · Concurrency", "red", ["Goroutines", "WaitGroup", "Mutex", "Channels", "Testing"])]
    x = 15
    widths = [190, 170, 170, 180]
    for (title, kind, items), w in zip(cols, widths):
        d.box(x, 15, w, 38, (title, "bold"), kind)
        for i, it in enumerate(items):
            d.box(x + 10, 68 + i * 36, w - 20, 30, (it, "small"), "box", rx=8)
        x += w + 10
    return d.render()


# ------------------------------------------------------------------ 1 basics
@diagram
def run_pipeline():
    d = D("run-pipeline", 760, 250, "From hello.go to output",
          "go run compiles your source into a native program, runs it, and throws the program away; go build keeps it.")
    xs = flow(d, 30, [(["hello.go", ("source code", "small")], "box"), (["compiler", ("checks types", "small")], "blue"),
                      (["hello", ("one native file", "small")], "green"), (["Hello, Go!", ("printed", "small")], "amber")],
              x=30, w=140, gap=55, labels={1: "go build", 2: "run", 3: "output"})
    d.box(30, 125, 700, 100, ["package main  ·  import \"fmt\"  ·  func main() { … }", ("Every program: a package main and a func main as the starting point", "small"),
                              ("go run = build + run + delete  ·  go build = build and keep", "small")], "ghost", tcls="code")
    return d.render()


# ------------------------------------------------------------------ 2 defer
@diagram
def defer_stack():
    d = D("defer-stack", 760, 300, "defer runs last-in, first-out",
          "Each defer is pushed on a stack as it is reached. When the function returns, they pop in reverse order.")
    d.text(130, 20, "while the function runs", "title"); d.text(560, 20, "when it returns", "title")
    for i, (txt, k) in enumerate([("defer Println(\"cleanup 1\")", "blue"), ("defer Println(\"cleanup 2\")", "green"), ("defer Println(\"cleanup 3\")", "amber")]):
        d.box(30, 40 + i * 56, 230, 44, (txt, "code"), k)
        d.text(280, 62 + i * 56, f"pushed {i + 1}st", "small", anchor="start") if i == 0 else None
    d.arrow([(380, 125), (440, 125)], label="return", ly=108)
    for i, (txt, k) in enumerate([("cleanup 3  → runs 1st", "amber"), ("cleanup 2  → runs 2nd", "green"), ("cleanup 1  → runs 3rd", "blue")]):
        d.box(460, 40 + i * 56, 240, 44, (txt, "code"), k)
    d.text(380, 240, "Typical use: defer file.Close() right after a successful Open,", "small")
    d.text(380, 262, "so the file is closed on every path out of the function.", "small")
    return d.render()


# ------------------------------------------------------------------ 3 slices
@diagram
def slice_header():
    d = D("slice-header", 760, 330, "A slice is a small header pointing at an array",
          "Two slices can look at the same array: s covers all of it, window covers a part, so writing through one changes the other.")
    d.box(20, 20, 150, 110, [("slice s", "bold"), ("ptr  →", "code"), ("len = 5", "code"), ("cap = 6", "code")], "blue")
    d.box(20, 170, 150, 110, [("window := s[1:3]", "bold"), ("ptr  →", "code"), ("len = 2", "code"), ("cap = 5", "code")], "green")
    cells(d, [1, 99, 3, 4, 5, "·"], 260, 80, w=70, h=50, cls={1: "green", 2: "green", 5: "ghost"}, gap=6)
    d.text(440, 40, "underlying array (cap 6)", "title")
    d.arrow([(170, 70), (258, 100)], kind="blue")
    d.arrow([(170, 220), (336, 140)], kind="green")
    d.text(500, 220, "window[0] = 99 writes into the shared array,", "small"); d.text(500, 242, "so s[1] is 99 too.", "small")
    d.text(500, 280, "append beyond cap → Go allocates a bigger array", "small"); d.text(500, 302, "and the old slices stop sharing.", "small")
    return d.render()


# ------------------------------------------------------------------ 4 maps
@diagram
def map_lookup():
    d = D("map-lookup", 760, 300, "A map finds a value by its key",
          "ages[\"Jafer\"] hashes the key to find its slot. A missing key gives the zero value, and the second result says whether it existed.")
    keys = [("\"Vignesh\"", "26"), ("\"Jafer\"", "28"), ("\"Aron\"", "24")]
    for i, (k, v) in enumerate(keys):
        y = 40 + i * 62
        d.box(30, y, 140, 44, (k, "code"), "blue" if i == 1 else "box")
        d.arrow([(172, y + 22), (298, y + 22)], kind="blue" if i == 1 else "")
        d.box(300, y, 90, 44, (v, "code"), "green" if i == 1 else "box")
    d.text(100, 24, "keys", "title"); d.text(345, 24, "values", "title"); d.text(235, 24, "hash", "title")
    d.box(450, 40, 280, 100, [("age, ok := ages[\"Nobody\"]", "code"), ("age = 0   ok = false", "code"), ("missing → zero value, never an error", "small")], "amber")
    d.box(450, 160, 280, 90, [("ages2 := ages", "code"), ("both names, ONE map", "bold"), ("copy it with maps.Clone", "small")], "red")
    return d.render()


# ------------------------------------------------------------------ 5 structs
@diagram
def struct_json():
    d = D("struct-json", 760, 300, "A struct and its JSON",
          "Field tags decide the JSON names. Lowercase (unexported) fields are invisible to the json package.")
    d.box(15, 15, 400, 255, [], "box")
    d.text(215, 38, "type User struct", "bold")
    rows = [("ID    int", "`json:\"id\"`"), ("Name  string", "`json:\"name\"`"), ("Email string", "`json:\"email,omitempty\"`"), ("token string", "(private: skipped)")]
    for i, (a, b) in enumerate(rows):
        y = 58 + i * 48
        d.box(30, y, 370, 40, [], "ghost" if i == 3 else "blue")
        d.text(44, y + 20, a, "code", anchor="start")
        d.text(388, y + 20, b, "small", anchor="end")
    d.arrow([(425, 120), (490, 120)], label="Marshal", ly=102)
    d.arrow([(490, 170), (425, 170)], label="Unmarshal", ly=190)
    d.box(500, 55, 245, 170, [('{', "code"), ('  "id": 1,', "code"), ('  "name": "Syed",', "code"), ('  "email": "s@go.dev"', "code"), ('}', "code")], "green")
    d.text(622, 250, "omitempty drops Email when empty", "small")
    return d.render()


# ------------------------------------------------------------------ 6 pointers
@diagram
def pointer_copy():
    d = D("pointer-copy", 760, 310, "Pass a copy, or pass the address",
          "By value the function changes its own copy. With a pointer it follows the address and changes the original.")
    d.text(190, 20, "double(n)  – by value", "title"); d.text(570, 20, "double(&n)  – by pointer", "title")
    d.box(30, 50, 120, 50, [("n  (main)", "small"), ("5", "code")], "blue")
    d.box(230, 50, 120, 50, [("n  (copy)", "small"), ("10", "code")], "amber")
    d.arrow([(152, 75), (228, 75)], label="copied", ly=58)
    d.text(190, 130, "main still sees 5", "bold")
    d.box(410, 50, 120, 50, [("n  (main)", "small"), ("10", "code")], "green")
    d.box(610, 50, 120, 50, [("p  (pointer)", "small"), ("→ &n", "code")], "amber")
    d.arrow([(610, 75), (532, 75)], kind="green", label="*p = *p * 2", ly=56)
    d.text(570, 130, "main now sees 10", "bold")
    d.box(30, 175, 700, 110, [("x := 10  ·  p := &x  ·  *p = 20  // x is now 20", "code"), ("&x = “the address of x”  ·  *p = “the value p points at”", "small"),
                              ("A pointer you never set is nil – dereferencing nil panics", "small")], "ghost")
    return d.render()


# ------------------------------------------------------------------ 7 errors
@diagram
def error_chain():
    d = D("error-chain", 760, 290, "Errors wrap like layers of an onion",
          "Each layer adds context with %w. errors.Is and errors.As look through the layers to find the original cause.")
    d.box(20, 30, 720, 220, [], "ghost")
    d.box(60, 55, 640, 170, [], "blue")
    d.box(100, 80, 560, 120, [], "amber")
    d.box(140, 105, 480, 70, [("strconv.Atoi: parsing \"abc\": invalid syntax", "code")], "red")
    d.text(380, 66, "main:  failed to read order: …", "small")
    d.text(380, 91, "parsePositive \"abc\": …", "small")
    d.text(380, 188, "errors.Is(err, target) → true if any layer matches", "small")
    d.text(380, 270, "if err != nil { return fmt.Errorf(\"what I was doing: %w\", err) }", "code")
    return d.render()


# ------------------------------------------------------------------ 8 files
@diagram
def file_modes():
    d = D("file-modes", 760, 300, "Four ways to open a file",
          "Pick the entry point by what you need: whole file at once, line by line, create or truncate, or append at the end.")
    items = [("os.ReadFile", "whole file → []byte", "green"), ("os.Open + Scanner", "line by line", "green"),
             ("os.WriteFile", "new or truncated", "amber"), ("OpenFile+O_APPEND", "add to the end", "blue")]
    for i, (a, b, k) in enumerate(items):
        x = 20 + i * 185
        d.box(x, 30, 170, 70, [(a, "code"), (b, "small")], k)
        d.arrow([(x + 85, 100), (x + 85, 150)])
    d.box(20, 150, 720, 60, [("file on disk:  line one ⏎ line two ⏎", "code")], "box")
    d.text(380, 240, "Always check the error, and defer file.Close() right after a successful open.", "small")
    d.text(380, 266, "Missing file?  errors.Is(err, os.ErrNotExist)  or  os.IsNotExist(err)", "small")
    return d.render()


# ------------------------------------------------------------------ 9 cli
@diagram
def cli_parts():
    d = D("cli-parts", 760, 270, "What the program receives",
          "The shell splits the command into words. os.Args holds them all; flag.Parse picks the -name=value ones out.")
    words = [("finder", "Args[0]", "box", 90), ("-dir=src", "flag", "blue", 120), ("-ext=.go", "flag", "blue", 120), ("-verbose", "flag", "blue", 120), ("notes.txt", "flag.Args()", "green", 130)]
    x = 20
    for w, lab, k, wd in words:
        d.box(x, 40, wd, 44, (w, "code"), k)
        d.text(x + wd / 2, 104, lab, "small")
        x += wd + 20
    d.text(380, 20, "$ finder -dir=src -ext=.go -verbose notes.txt", "code")
    d.box(20, 150, 340, 90, [("flag.StringVar(&dir, \"dir\", \"\", usage)", "code"), ("flag.BoolVar(&verbose, \"verbose\", …)", "code"), ("flag.Parse()  // fills the variables", "code")], "ghost")
    d.box(390, 150, 350, 90, [("Validate early:", "bold"), ("empty dir? → print usage, os.Exit(1)", "small"), ("not a directory? → clear error, exit 1", "small")], "amber")
    return d.render()


# ------------------------------------------------------------------ 10 logging
@diagram
def log_levels():
    d = D("log-levels", 760, 300, "Log levels act as a filter",
          "A logger drops everything below its level. At Info, Debug lines disappear and Info, Warn and Error get through.")
    lv = [("Debug", "box"), ("Info", "blue"), ("Warn", "amber"), ("Error", "red")]
    for i, (n, k) in enumerate(lv):
        d.box(30 + i * 130, 40, 110, 50, (n, "bold"), k)
    d.line(30 + 130 - 10, 20, 30 + 130 - 10, 110, "line cut")
    d.text(150, 125, "threshold = Info", "small")
    d.text(85, 20, "dropped", "small"); d.text(330, 20, "kept", "small")
    d.box(570, 30, 170, 70, [("config.yaml", "code"), ("logging: level: info", "small")], "green")
    d.arrow([(570, 65), (500, 65)], kind="green", dashed=True)
    d.box(30, 160, 330, 100, [("slog.Info(\"login\", \"user\", \"Syed\")", "code"), ("level=INFO msg=login user=Syed", "small"), ("{\"level\":\"INFO\",\"msg\":\"login\",\"user\":\"Syed\"}", "small")], "ghost")
    d.box(390, 160, 350, 100, [("Config as a struct", "bold"), ("YAML file → yaml.Unmarshal → Config{…}", "small"), ("change behaviour without recompiling", "small")], "box")
    return d.render()


# ------------------------------------------------------------------ 11 http
@diagram
def http_flow():
    d = D("http-flow", 760, 300, "One request through a Go server",
          "The mux matches the path, calls the handler, and the handler writes the response through http.ResponseWriter.")
    flow(d, 40, [(["Client", ("curl / browser", "small")], "box"), (["Mux", ("matches the path", "small")], "blue"),
                 (["Handler", ("func(w, r)", "small")], "green"), (["Response", ("status + body", "small")], "amber")],
         x=30, w=140, gap=55, labels={1: "GET /users", 2: "route", 3: "write"})
    d.box(30, 140, 340, 130, [("Inside the handler", "bold"), ("switch r.Method { GET / POST / default }", "code"), ("json.NewDecoder(r.Body).Decode(&u)", "code"), ("http.Error(w, \"Invalid JSON\", 400)", "code")], "ghost")
    d.box(400, 140, 330, 130, [("Status codes you will use", "bold"), ("200 OK · 201 Created", "code"), ("400 Bad Request · 404 Not Found", "code"), ("405 Wrong Method · 500 Server Error", "code")], "box")
    return d.render()


# ------------------------------------------------------------------ 12 todo api
@diagram
def todo_layers():
    d = D("todo-layers", 760, 320, "The Todo API in layers",
          "main wires routes to handlers; handlers decode JSON and call the store; the store owns the data behind a lock.")
    d.box(280, 15, 200, 44, ["main.go", ("routes + ListenAndServe", "small")], "blue")
    d.box(280, 90, 200, 44, ["handlers.go", ("decode · call · encode", "small")], "green")
    d.box(280, 165, 200, 44, ["storage.go", ("[]Todo + mutex", "small")], "amber")
    d.box(30, 90, 200, 44, ["models.go", ("Todo, CreateTodoRequest", "small")], "box")
    d.arrow([(380, 59), (380, 90)]); d.arrow([(380, 134), (380, 165)])
    d.arrow([(232, 112), (278, 112)], dashed=True)
    d.box(530, 70, 210, 90, [("POST /todos", "code"), ("{\"title\":\"Learn Go\"}", "code"), ("→ 201 {\"id\":1,…}", "code")], "ghost")
    d.arrow([(530, 112), (482, 112)], kind="green")
    d.text(380, 255, "Keep each file about one job: easy to read, and the store can later be swapped", "small")
    d.text(380, 277, "for a database without touching the handlers.", "small")
    return d.render()


# ------------------------------------------------------------------ 13 database
@diagram
def sql_flow():
    d = D("sql-flow", 760, 300, "Go talks to a database through database/sql",
          "Your code uses one API. A driver, imported with a blank import, translates it for Postgres, SQLite or MySQL.")
    flow(d, 30, [(["Your code", ("db.Query(…)", "small")], "box"), (["database/sql", ("pool + API", "small")], "blue"),
                 (["driver", ("lib/pq · sqlite", "small")], "amber"), (["Database", ("tables", "small")], "green")],
         x=30, w=140, gap=55)
    d.box(30, 130, 340, 140, [("Reading rows", "bold"), ("rows, err := db.Query(sql, args…)", "code"), ("defer rows.Close()", "code"), ("for rows.Next() { rows.Scan(&a, &b) }", "code"), ("QueryRow(…).Scan(&x)  → one row", "code")], "ghost")
    d.box(400, 130, 330, 140, [("Placeholders, always", "bold"), ("\"... WHERE id = ?\", id", "code"), ("(Postgres writes $1, $2)", "small"), ("never build SQL with string +", "small"), ("→ stops SQL injection", "small")], "red")
    return d.render()


# ------------------------------------------------------------------ 14 goroutines
@diagram
def timeline():
    d = D("timeline", 760, 290, "Sequential vs concurrent",
          "Two 600ms tasks take 1200ms one after another, but about 600ms when they run as goroutines at the same time.")
    d.text(30, 20, "sequential", "title", anchor="start")
    d.rect(30, 35, 300, 30, "blue"); d.text(180, 50, "Task 1  (600 ms)", "small")
    d.rect(330, 35, 300, 30, "green"); d.text(480, 50, "Task 2  (600 ms)", "small")
    d.text(640, 50, "= 1200 ms", "bold", anchor="start")
    d.text(30, 110, "go task1()  ·  go task2()", "title", anchor="start")
    d.rect(30, 125, 300, 30, "blue"); d.text(180, 140, "Task 1", "small")
    d.rect(30, 165, 300, 30, "green"); d.text(180, 180, "Task 2", "small")
    d.text(345, 160, "= 600 ms", "bold", anchor="start")
    d.text(30, 240, "Concurrent ≠ parallel: Go interleaves goroutines and also spreads them across CPU cores.", "small", anchor="start")
    d.text(30, 262, "If main returns, every goroutine is stopped, finished or not.", "small", anchor="start")
    return d.render()


# ------------------------------------------------------------------ 15 waitgroup
@diagram
def waitgroup_counter():
    d = D("waitgroup-counter", 760, 300, "WaitGroup is a counter main waits on",
          "Add raises the counter before each goroutine starts, Done lowers it when one finishes, Wait blocks until it is zero.")
    d.box(20, 30, 150, 60, [("main", "bold"), ("wg.Add(3)", "code")], "blue")
    for i, n in enumerate(["worker 1", "worker 2", "worker 3"]):
        d.box(250, 20 + i * 60, 150, 44, [(n, "code")], "green")
        d.arrow([(172, 60), (248, 42 + i * 60)])
        d.arrow([(402, 42 + i * 60), (478, 100)], label=None)
    d.text(440, 30 + 0, "defer wg.Done()", "small")
    d.box(480, 70, 130, 60, [("counter", "small"), ("3 → 2 → 1 → 0", "code")], "amber")
    d.box(630, 70, 110, 60, [("wg.Wait()", "code"), ("returns", "small")], "blue")
    d.arrow([(612, 100), (628, 100)])
    d.text(380, 230, "Pass *sync.WaitGroup (a pointer): copying it would count on a copy.", "small")
    d.text(380, 255, "Call Add before `go`, never inside the goroutine.", "small")
    return d.render()


# ------------------------------------------------------------------ 16 mutex
@diagram
def race_vs_lock():
    d = D("race-vs-lock", 760, 320, "Why counter++ needs a lock",
          "counter++ is read, add, write. Two goroutines can read the same value, so one update is lost. A mutex lets one in at a time.")
    d.text(190, 20, "without a lock", "title"); d.text(570, 20, "with a mutex", "title")
    d.box(20, 40, 340, 40, [("A reads 7", "code")], "blue"); d.box(20, 86, 340, 40, [("B reads 7", "code")], "green")
    d.box(20, 132, 340, 40, [("A writes 8", "code")], "blue"); d.box(20, 178, 340, 40, [("B writes 8", "code")], "red")
    d.text(190, 245, "two increments, counter grew by 1", "bold")
    d.box(400, 40, 340, 40, [("A Lock → read 7 → write 8 → Unlock", "code")], "blue")
    d.box(400, 86, 340, 40, [("B waits…", "small")], "ghost")
    d.box(400, 132, 340, 40, [("B Lock → read 8 → write 9 → Unlock", "code")], "green")
    d.text(570, 200, "two increments, counter grew by 2", "bold")
    d.text(380, 290, "Find races with: go run -race file.go  ·  Lock, then defer Unlock()", "small")
    return d.render()


# ------------------------------------------------------------------ 17 channels
@diagram
def channel_pool():
    d = D("channel-pool", 760, 310, "Channels carry values between goroutines",
          "A worker pool: main sends jobs into one channel, three workers take from it, and results come back on another.")
    d.box(20, 110, 110, 60, [("main", "bold"), ("jobs <- 1..6", "small")], "blue")
    d.box(190, 120, 110, 40, [("jobs chan", "code")], "amber")
    d.arrow([(132, 140), (188, 140)])
    for i in range(3):
        d.box(380, 40 + i * 80, 120, 50, [(f"worker {i + 1}", "code")], "green")
        d.arrow([(302, 140), (378, 65 + i * 80)])
        d.arrow([(502, 65 + i * 80), (578, 140)])
    d.box(580, 120, 140, 40, [("results chan", "code")], "amber")
    d.text(380, 270, "ch <- v  send (waits for a receiver)  ·  v := <-ch  receive", "code")
    d.text(380, 295, "close(jobs) tells workers 'no more'; select picks whichever channel is ready first", "small")
    return d.render()


# ------------------------------------------------------------------ 18 testing
@diagram
def table_test():
    d = D("table-test", 760, 300, "A table-driven test",
          "List the cases once, loop over them, and run each as a named subtest so a failure tells you exactly which case broke.")
    d.box(20, 20, 330, 160, [("tests := []struct{name; input; want}{", "code"), ("  {\"simple\",  \"level\",  true},", "code"), ("  {\"spaces\",  \"Never Odd Or Even\", true},", "code"), ("  {\"not one\",  \"golang\", false},", "code"), ("}", "code")], "blue")
    d.arrow([(352, 100), (418, 100)], label="for each", ly=82)
    d.box(420, 60, 150, 80, [("t.Run(name, …)", "code"), ("IsPalindrome(in)", "small")], "green")
    d.arrow([(572, 100), (618, 100)])
    d.box(620, 60, 120, 80, [("got == want?", "code"), ("t.Errorf if not", "small")], "amber")
    d.box(20, 200, 720, 80, [("go test  ·  go test -v  ·  go test -cover  ·  go test -bench=.  ·  go test -race ./...", "code"), ("Test files end in _test.go, functions start with Test, Benchmark and take *testing.T / *testing.B", "small")], "ghost")
    return d.render()


if __name__ == "__main__":
    for fn in ALL:
        fn()
    print(f"wrote {len(ALL)} diagrams to {OUT}")
