"""Diagrams for the setup page, the course home page and Sessions 1-3."""
from _dg import D, diagram


@diagram
def course_ladder():
    d = D("course-ladder", 720, 300, "From beginner to intermediate",
          "Each session adds one step. By Session 5 you build an agent by hand; by Session 11 you ship a guarded bot.")
    steps = [("Python\nbasics", "S1", "ghost"), ("How LLMs\nwork", "S2", "ghost"), ("Chat\nbot", "S3", "blue"),
             ("Tools &\nJSON", "S4", "blue"), ("Your own\nagent", "S5", "green"), ("Hermes\nagent", "S6-8", "green"),
             ("Guard &\nroute", "S9-10", "amber"), ("Capstone\nbot", "S11", "amber")]
    x = 16
    for i, (t, s, k) in enumerate(steps):
        h = 70 + i * 24
        y = 270 - h
        d.box(x, y, 80, h, [(ln, "bold") for ln in t.split("\n")], k)
        d.text(x + 40, y - 12, s, "small")
        x += 88
    d.text(60, 22, "BEGINNER", "title"); d.text(640, 22, "INTERMEDIATE", "title")
    d.arrow([(120, 30), (580, 30)], kind="blue")
    return d.render()


@diagram
def setup_overview():
    d = D("setup-overview", 720, 230, "What setup gives you",
          "Python and a virtual environment run your code; the .env file holds the secret key; the key lets your code reach an AI model on the internet.")
    d.box(20, 20, 200, 190, [("Your laptop", "bold")], "box")
    d.box(36, 55, 168, 36, ("Python 3.10+", "code"), "blue")
    d.box(36, 100, 168, 36, (".venv  (private box)", "code"), "blue")
    d.box(36, 145, 168, 36, (".env  (secret key)", "code"), "amber")
    d.box(300, 70, 150, 90, [("API request", "bold"), ("over internet", "small")], "ghost")
    d.arrow([(220, 120), (298, 120)], kind="blue")
    d.arrow([(450, 105), (520, 105)], kind="blue")
    d.box(520, 60, 180, 110, [("AI provider", "bold"), ("Groq / OpenRouter", "small"), ("(the model lives here)", "small")], "green")
    d.arrow([(520, 140), (452, 140)], kind="green", dashed=True)
    d.text(485, 190, "answer comes back", "small")
    return d.render()


@diagram
def s01_run():
    d = D("s01-run", 720, 190, "How Python runs a file",
          "Python reads the file from top to bottom, one line at a time, and does each instruction in order.")
    lines = ['name = "Asha"', "age = 21", 'print("Hello,", name)', "print(age)"]
    d.box(30, 20, 250, 150, [], "box")
    for i, l in enumerate(lines):
        d.text(50, 48 + i * 34, f"{i + 1}  {l}", "code")
        d.els[-1] = d.els[-1].replace('text-anchor="middle"', 'text-anchor="start"')
    d.arrow([(24, 40), (24, 150)], kind="blue")
    d.box(380, 30, 140, 50, [("Python", "bold"), ("(the reader)", "small")], "blue")
    d.arrow([(280, 55), (378, 55)], kind="blue", label="reads", lx=330, ly=42)
    d.box(380, 110, 300, 50, [("Hello, Asha", "code"), ("21", "code")], "green")
    d.arrow([(450, 80), (450, 108)], kind="green")
    return d.render()


@diagram
def s01_list_dict():
    d = D("s01-list-dict", 720, 250, "A list and a dictionary",
          "A list is ordered by position (starting at 0). A dictionary is looked up by a label (key).")
    d.text(130, 18, "LIST  (by position)", "title")
    for i, v in enumerate(["apple", "banana", "mango"]):
        d.text(60 + i * 90, 42, i, "bold")
        d.box(20 + i * 90, 52, 80, 44, (v, "code"), "blue" if i == 0 else "box")
    d.text(130, 120, 'fruits[0]  →  "apple"', "code")
    d.text(500, 18, "DICTIONARY  (by label)", "title")
    rows = [("name", '"Asha"'), ("age", "21"), ("city", '"Chennai"')]
    for i, (k, v) in enumerate(rows):
        y = 40 + i * 50
        d.box(400, y, 100, 40, (k, "code"), "amber")
        d.box(510, y, 160, 40, (v, "code"), "box")
        d.arrow([(500, y + 20), (508, y + 20)], head=False)
    d.text(540, 200, 'person["name"]  →  "Asha"', "code")
    d.box(120, 150, 480, 70, [("Together: a chat is a LIST of DICTIONARIES", "bold"), ('[{"role": "user", "content": "Hi"}, ...]', "code")], "green")
    d.els = [e for e in d.els]  # keep order
    return d.render()


@diagram
def s01_json_dict():
    d = D("s01-json-dict", 720, 230, "Dictionary ⇄ JSON text",
          "json.dumps turns a Python dictionary into JSON text; json.loads turns JSON text back into a dictionary.")
    d.box(30, 40, 230, 130, [("Python dict", "bold"), ('{"city": "Chennai",', "code"), (' "rain": False}', "code")], "blue")
    d.box(460, 40, 230, 130, [("JSON text (a string)", "bold"), ('{"city": "Chennai",', "code"), (' "rain": false}', "code")], "amber")
    d.arrow([(262, 80), (458, 80)], kind="blue", label="json.dumps(data)", lx=360, ly=64)
    d.arrow([(458, 130), (262, 130)], kind="green", label="json.loads(text)", lx=360, ly=150)
    d.text(360, 205, "False ↔ false     None ↔ null     'single' quotes ↔ \"double\" quotes", "small")
    return d.render()


@diagram
def s01_request():
    d = D("s01-request", 720, 230, "A web API call",
          "Your program sends a request (URL + parameters); the server sends back a response with a status code and JSON.")
    d.box(20, 50, 170, 110, [("Your Python", "bold"), ("requests.get(...)", "code")], "blue")
    d.box(530, 50, 170, 110, [("Server", "bold"), ("api.open-meteo.com", "small")], "green")
    d.arrow([(190, 85), (528, 85)], kind="blue", label="REQUEST: URL + params", lx=360, ly=68)
    d.arrow([(528, 130), (190, 130)], kind="green", label="RESPONSE: 200 + JSON", lx=360, ly=152)
    d.box(250, 180, 220, 36, ('{"temperature": 26.5, ...}', "code"), "ghost")
    return d.render()


@diagram
def s01_env():
    d = D("s01-env", 720, 190, "Where secrets live",
          "The key sits in .env, outside your code. python-dotenv loads it, and os.getenv hands it to your program.")
    d.box(20, 60, 150, 70, [(".env", "code"), ("LLM_API_KEY=gsk_...", "small")], "amber")
    d.box(270, 60, 160, 70, [("load_dotenv()", "code"), ("reads the file", "small")], "blue")
    d.box(530, 60, 170, 70, [('os.getenv("LLM_API_KEY")', "code"), ("gives your code the key", "small")], "green")
    d.arrow([(170, 95), (268, 95)], kind="blue"); d.arrow([(430, 95), (528, 95)], kind="blue")
    d.text(360, 160, "Your .py files never contain the secret → safe to share and upload", "small")
    return d.render()


@diagram
def s01_venv():
    d = D("s01-venv", 720, 220, "Virtual environment",
          "A virtual environment is a private box of packages for one project, separate from the rest of your computer.")
    d.box(20, 20, 250, 180, [("Whole computer", "bold")], "box")
    d.box(40, 60, 210, 120, [], "ghost")
    d.text(145, 75, "other projects", "small")
    d.box(330, 20, 370, 180, [("ai-agent-bootcamp/.venv", "bold")], "blue")
    for i, p in enumerate(["requests", "python-dotenv", "(later) laya"]):
        d.box(350 + i * 115, 90, 105, 44, (p, "code"), "green" if i < 2 else "ghost")
    d.text(515, 170, "pip install → goes inside the box only", "small")
    d.arrow([(272, 110), (328, 110)], kind="blue", label="activate", lx=300, ly=96)
    return d.render()


# ------------------------------------------------------------------ Session 2
@diagram
def s02_predict():
    d = D("s02-predict", 720, 230, "An LLM predicts the next word",
          "Given the words so far, the model scores every possible next token and picks one. It repeats this over and over.")
    d.box(20, 20, 330, 50, ('"The capital of India is"', "code"), "blue")
    d.arrow([(185, 70), (185, 100)], kind="blue")
    d.box(100, 100, 170, 40, ("LLM (the model)", "bold"), "amber")
    d.arrow([(270, 120), (400, 120)], kind="blue")
    d.text(560, 24, "scores for the next token", "title")
    bars = [(" New", 0.82), (" Delhi", 0.1), (" the", 0.04), (" a", 0.02)]
    for i, (t, p) in enumerate(bars):
        y = 40 + i * 42
        d.box(405, y, 70, 30, (t, "code"), "box")
        d.rect(480, y + 3, 220 * p, 24, "green" if i == 0 else "blue")
        d.text(485 + 220 * p + 4, y + 15, f"{int(p * 100)}%", "small")
        d.els[-1] = d.els[-1].replace('text-anchor="middle"', 'text-anchor="start"')
    d.text(360, 215, "It then adds the chosen token and asks again, until the answer is complete.", "small")
    return d.render()


@diagram
def s02_tokens():
    d = D("s02-tokens", 720, 200, "Text is cut into tokens",
          "A token is a small piece of text, often part of a word. Models read and charge in tokens, not words.")
    pieces = ["Learn", "ing", " Py", "thon", " is", " fun", "!"]
    x = 30
    for i, p in enumerate(pieces):
        w = 20 + len(p) * 14
        d.box(x, 40, w, 44, (p, "code"), "blue" if i % 2 == 0 else "amber")
        x += w + 6
    d.text(360, 110, "7 tokens   (about 4 letters per token in English; Tamil and other languages use more)", "small")
    d.box(60, 135, 600, 48, [("≈ 1 token ≈ ¾ of an English word   →   100 words ≈ 130 tokens", "bold")], "ghost")
    return d.render()


@diagram
def s02_context():
    d = D("s02-context", 720, 220, "The context window",
          "The model can only 'see' what fits in its context window: the system prompt, the whole chat so far, and the reply being written.")
    d.box(20, 40, 680, 70, [], "box")
    d.box(26, 46, 120, 58, [("system", "bold"), ("prompt", "small")], "amber")
    d.box(152, 46, 360, 58, [("conversation history", "bold"), ("(you + assistant, every turn)", "small")], "blue")
    d.box(518, 46, 100, 58, [("new reply", "bold")], "green")
    d.box(624, 46, 70, 58, [("FREE", "small")], "ghost")
    d.text(360, 24, "CONTEXT WINDOW  (e.g. 8,000 or 128,000 tokens)", "title")
    d.arrow([(580, 140), (580, 112)], kind="red")
    d.text(500, 165, "When it is full, the oldest messages must be cut off", "small")
    d.text(360, 200, "→ the model forgets whatever is outside the window", "bold")
    return d.render()


@diagram
def s02_temperature():
    d = D("s02-temperature", 720, 250, "Temperature",
          "Low temperature always picks the most likely word (steady). High temperature gives other words a chance (creative, riskier).")
    for col, (t, probs, k) in enumerate([("temperature 0  (steady)", [0.95, 0.03, 0.02], "blue"),
                                           ("temperature 1.5  (creative)", [0.45, 0.33, 0.22], "amber")]):
        x0 = 30 + col * 350
        d.text(x0 + 150, 20, t, "title")
        for i, p in enumerate(probs):
            y = 40 + i * 50
            d.box(x0, y, 80, 34, [(["Delhi", "Mumbai", "Chennai"][i], "code")], "box")
            d.rect(x0 + 90, y + 4, 200 * p, 26, "green" if k == "blue" else "amber")
    d.text(360, 215, "Same question → temperature 0 repeats itself; temperature 1.5 varies each time", "small")
    return d.render()


@diagram
def s02_models():
    d = D("s02-models", 720, 210, "Choosing a model",
          "Bigger models are smarter but slower and pricier; small models are fast and cheap. Pick the smallest that does the job.")
    d.box(30, 50, 200, 110, [("Small / fast", "bold"), ("8B parameters", "small"), ("cheap, quick", "small"), ("simple tasks", "small")], "green")
    d.box(260, 50, 200, 110, [("Medium", "bold"), ("70B parameters", "small"), ("balanced", "small"), ("most agent work", "small")], "blue")
    d.box(490, 50, 200, 110, [("Large / frontier", "bold"), ("paid, biggest", "small"), ("best reasoning", "small"), ("hard problems", "small")], "amber")
    d.arrow([(30, 185), (690, 185)], kind="blue")
    d.text(130, 200, "cheaper & faster", "small"); d.text(600, 200, "smarter & costlier", "small")
    return d.render()


# ------------------------------------------------------------------ Session 3
@diagram
def s03_roles():
    d = D("s03-roles", 720, 250, "The three message roles",
          "system sets the rules once, user is you, assistant is the AI. The whole list is sent every time.")
    rows = [("system", "You are a friendly Tamil-English tutor.", "amber"), ("user", "What is a variable?", "blue"),
            ("assistant", "It's a name tag stuck on a value.", "green"), ("user", "Give an example.", "blue")]
    for i, (r, t, k) in enumerate(rows):
        y = 20 + i * 54
        d.box(20, y, 120, 42, (r, "code"), k)
        d.box(150, y, 420, 42, (t, ""), "box")
    d.box(590, 20, 110, 204, [("whole list", "bold"), ("is sent", "small"), ("every time", "small")], "ghost")
    d.arrow([(570, 122), (588, 122)], kind="blue")
    return d.render()


@diagram
def s03_chat_loop():
    d = D("s03-chat-loop", 720, 240, "The chatbot loop",
          "Read your input, add it to the history, send the history to the model, add the reply to the history, print it, repeat.")
    steps = ["1 Read\nyour input", "2 Append to\nhistory", "3 Send history\nto the model", "4 Append reply\nto history", "5 Print\nreply"]
    x = 14
    for i, s in enumerate(steps):
        d.box(x, 60, 124, 66, [(ln, "bold" if j == 0 else "small") for j, ln in enumerate(s.split("\n"))], ["blue", "box", "amber", "box", "green"][i])
        if i < 4:
            d.arrow([(x + 124, 93), (x + 138, 93)], kind="blue")
        x += 140
    d.arrow([(640, 126), (640, 180), (75, 180), (75, 128)], kind="blue", dashed=True)
    d.text(360, 200, "repeat until the user types 'quit'", "small")
    return d.render()


@diagram
def s03_errors():
    d = D("s03-errors", 720, 240, "Handling API errors",
          "401 means fix your key; 429 means wait and retry; 5xx means the server had a problem so retry a few times.")
    rows = [("200", "OK", "use the answer", "green"), ("401", "bad key", "fix .env, don't retry", "red"),
            ("429", "too many requests", "wait, then retry (backoff)", "amber"), ("500+", "server problem", "retry a few times", "amber")]
    for i, (c, m, a, k) in enumerate(rows):
        y = 20 + i * 52
        d.box(20, y, 80, 40, (c, "bold"), k)
        d.box(110, y, 180, 40, (m, ""), "box")
        d.arrow([(290, y + 20), (340, y + 20)], kind="blue")
        d.box(340, y, 340, 40, (a, ""), "ghost")
    return d.render()


@diagram
def s03_backoff():
    d = D("s03-backoff", 720, 190, "Exponential backoff",
          "After each failure, wait twice as long before trying again: 1s, 2s, 4s. This is polite to a busy server.")
    x = 40
    for i, (lab, w) in enumerate([("try 1", 0), ("wait 1s", 60), ("try 2", 0), ("wait 2s", 120), ("try 3", 0), ("wait 4s", 200), ("try 4", 0)]):
        if w:
            d.box(x, 60, w, 40, (lab, "small"), "amber"); x += w + 6
        else:
            d.box(x, 60, 56, 40, (lab, "bold"), "red" if i < 6 else "green"); x += 62
    d.text(360, 140, "✗ fail   →   wait 1s   →   ✗ fail   →   wait 2s   →   ✗ fail   →   wait 4s   →   ✓ works", "small")
    return d.render()
