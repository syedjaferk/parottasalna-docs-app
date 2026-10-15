# Session 1 · Python for AI

**Day 1 · ⏱ about 90 minutes · 🧰 you need: [Setup](../setup.md) finished**

## The big idea

An AI agent is, at its heart, **a Python program that talks to the internet**. It sends a message to an
AI model, gets text back, and then does something with that text. So before we build agents, we need
five small Python skills. Think of them as the five tools in a cook's kitchen:

| Skill | Kitchen comparison | Where an agent uses it |
|---|---|---|
| **Functions** | a recipe you can reuse | every *tool* an agent can use is a function |
| **Lists** | a shopping list, in order | the conversation history is a list |
| **Dictionaries** | a labelled spice rack | every message is a dictionary |
| **JSON** | a standard packing box for data | AI APIs send and receive JSON |
| **requests + `.env`** | a phone that can call shops, with a locked drawer for secrets | calling the AI, keeping the API key safe |

**By the end of this session** you will have a working Python environment and a script that calls a
real web service, reads the answer and prints a clean summary.

## Before you start (checklist)

- [ ] You finished [Setup](../setup.md) and `python check_setup.py` shows `[ OK ]` on every line.
- [ ] Terminal is open in your `ai-agent-bootcamp` folder and the virtual environment is on (you see `(.venv)`).
- [ ] VS Code is open on the same folder (**File → Open Folder**).

:::{tip}
**Open a terminal inside VS Code**: press `` Ctrl + ` `` (the key above Tab). It opens already in your
project folder, and it remembers your virtual environment. 🐧 Linux and 🪟 Windows both work the same way.
:::

## 1. How does a Python program run?

You write instructions in a text file that ends in `.py`. When you type `python filename.py`, Python reads
the file **from the top to the bottom, one line at a time**, and does each instruction.

```{raw} html
:file: ../diagrams/s01-run.html
```

### Your first program

1. In VS Code, click **New File** (the page icon next to your folder name) and name it **`hello.py`**.
2. Type this:

```{literalinclude} ../code/01-python-for-ai/hello.py
:language: python
```

3. Save (`Ctrl + S`). Then run it in the terminal:

```bash
python hello.py
```

**Expected output:**

```text
Hello, Asha
Asha is 21 years old.
Learning AI? True
```

**Line by line:**

| Line | What it does |
|---|---|
| `# hello.py ...` | A **comment**. Python ignores anything after `#`. It's a note for humans. |
| `name = "Asha"` | Makes a **variable**: a name tag (`name`) stuck on a value (`"Asha"`). The text must be in quotes. |
| `age = 21` | A whole number. No quotes for numbers. |
| `is_learning = True` | A **boolean**: only `True` or `False` (capital first letter!). |
| `print("Hello,", name)` | `print` shows something on screen. Commas put a space between items. |
| `print(f"{name} is ...")` | An **f-string**: put an `f` before the quote, and `{name}` is replaced by the value. |

:::{note}
**Read `=` as "points to", not "equals".** `age = 21` means *the name `age` now points to the number 21*.
Later `age = 22` simply moves the name tag to a new value.
:::

## 2. Functions: a recipe you can reuse

A **function** is a named recipe. You write the steps once, then **call** it by name whenever you need it.
In Session 4 you'll see that *every tool an AI agent uses is just a function*, so this idea matters.

Create `functions_demo.py`:

```{literalinclude} ../code/01-python-for-ai/functions_demo.py
:language: python
```

```bash
python functions_demo.py
```

```text
5
Hello, Asha!
HELLO, ASHA!
35
```

**How to read a function:**

```python
def add(a, b):          # def = "define". 'a' and 'b' are the INPUTS (parameters)
    return a + b        # return = hand back the ANSWER
```

* **Indentation matters.** The lines *inside* the function are pushed right by 4 spaces. That's how Python knows where the function ends.
* `add(2, 3)` **calls** the function. The values `2` and `3` are the **arguments**.
* `shout=False` in `greet` is a **default value**. If you don't give it, Python uses `False`.
* `for p in prices:` is a **loop**: do the indented lines once for every item in the list.

## 3. Lists and dictionaries

```{raw} html
:file: ../diagrams/s01-list-dict.html
```

* A **list** is an ordered row of things. Count positions **from 0**. `fruits[0]` is the first item, `fruits[-1]` is the last.
* A **dictionary** (dict) is a set of **label → value** pairs. You look things up by the label, not the position.

Create `data_structures.py`:

```{literalinclude} ../code/01-python-for-ai/data_structures.py
:language: python
```

```bash
python data_structures.py
```

```text
apple
mango
4
I like apple
I like banana
I like mango
I like grape
Asha
not given
   system: You are a friendly assistant.
     user: Hi! What is Python?
assistant: Python is a programming language.
```

Look at the last part. **That list of dictionaries is exactly how you will talk to an AI.** Each message is
a dictionary with a `role` (who is speaking) and `content` (what they say), and the whole conversation is a
list of those dictionaries. Remember this picture. It comes back in Session 3.

:::{caution}
**Common mistake:** `person["phone"]` crashes with a `KeyError` if there is no `phone` key.
`person.get("phone", "not given")` is the safe version: it returns the default instead of crashing.
:::

## 4. JSON: the language of the internet

**JSON** (say "JAY-son") is just **text that is written in a special tidy way**, so that *any* programming
language can read it. It looks almost exactly like a Python dictionary.

```{raw} html
:file: ../diagrams/s01-json-dict.html
```

Two functions do all the work. Remember **s = string**:

| Function | Direction | Memory trick |
|---|---|---|
| `json.dumps(data)` | Python → JSON **text** | *dump to string* |
| `json.loads(text)` | JSON **text** → Python | *load from string* |
| `json.dump(data, file)` / `json.load(file)` | the same, but for **files** | no `s` = file |

Create `json_demo.py`:

```{literalinclude} ../code/01-python-for-ai/json_demo.py
:language: python
```

```bash
python json_demo.py
```

```text
{
  "name": "Asha",
  "age": 21,
  "skills": [
    "python",
    "sql"
  ],
  "student": true
}
<class 'str'>
Chennai 31.5
<class 'dict'>
True
```

Notice three small differences between Python and JSON: Python writes `True` but JSON writes `true`;
Python has `None` but JSON has `null`; and JSON **always** uses double quotes `"`.
You never have to convert these yourself. `json.dumps` and `json.loads` do it.

You should also see a new file `person.json` appear in your folder. Open it to see the saved JSON.

## 5. requests: calling a web API

An **API** (Application Programming Interface) is a *door on a website that programs can knock on*.
A normal website gives you a page for humans to read. An API gives you **data (JSON) for programs to read**.

```{raw} html
:file: ../diagrams/s01-request.html
```

Every AI service you'll use in this course is exactly this: your program **sends a request**, a server
**sends back a response**, usually JSON.

### The request has 3 important parts

| Part | What it is | Example |
|---|---|---|
| **URL** | the address of the door | `https://api.open-meteo.com/v1/forecast` |
| **Parameters** | the details of what you want | `latitude=13.08`, `longitude=80.27` |
| **Status code** | a number in the answer that says how it went | `200` = OK, `401` = bad key, `404` = not found, `429` = too many requests, `500` = server problem |

### Try it first in your browser

Paste this in your browser's address bar. It is a *real* request:

```text
https://api.open-meteo.com/v1/forecast?latitude=13.08&longitude=80.27&current_weather=true
```

You'll see JSON like this (your numbers will differ):

```json
{"latitude": 13.0, "longitude": 80.25, "current_weather": {"temperature": 26.5, "windspeed": 2.0, "weathercode": 51}}
```

### Now do it from Python

Create `weather_summary.py`:

```{literalinclude} ../code/01-python-for-ai/weather_summary.py
:language: python
```

```bash
python weather_summary.py
python weather_summary.py london
```

**Expected output (numbers will differ):**

```text
Weather in Chennai: 26.5 °C, wind 2.0 km/h
Weather in London: 12.3 °C, wind 14.8 km/h
```

**Line by line, the important parts:**

| Code | Meaning in simple words |
|---|---|
| `import requests` | bring in the library that makes web calls (you installed it with `pip`) |
| `CITIES = {...}` | a dictionary: city name → (latitude, longitude) |
| `requests.get(URL, params=params, timeout=15)` | knock on the door. `params` becomes the `?latitude=...` part. `timeout=15` means "give up after 15 seconds instead of waiting forever" |
| `response.raise_for_status()` | if the status is an error (4xx/5xx), **stop and raise an error** instead of pretending all is fine |
| `response.json()` | turn the JSON text in the answer into a Python dictionary |
| `["current_weather"]` | dig into the dictionary to get the part we want |
| `try: ... except requests.RequestException` | "try this; if the internet fails, don't crash. Run the `except` part instead" |
| `if __name__ == "__main__":` | "run this part only when I start this file directly". We use it so other files can `import get_weather` later |
| `sys.argv[1]` | the word you typed after the filename (`london`) |

:::{tip}
**No internet error?** If you see `Could not get the weather: ...`, check your connection. The `try/except`
did its job: it gave you a friendly message instead of a scary wall of red text.
:::

## 6. Keeping secrets safe with `.env`

In Session 2 you'll send your **API key** with every request. A key is like a password. It must **never**
be written inside your code, because code gets shared, copied and uploaded. Instead:

```{raw} html
:file: ../diagrams/s01-env.html
```

1. The key lives in the file `.env` (already created in Setup).
2. `python-dotenv` reads that file when your program starts.
3. `os.getenv("NAME")` hands the value to your code.

Create `env_demo.py`:

```{literalinclude} ../code/01-python-for-ai/env_demo.py
:language: python
```

```bash
python env_demo.py
```

```text
Key found: gsk_**********
Model: llama-3.1-8b-instant
```

If you see `No API key found`, you are probably in the wrong folder or the `.env` file is missing.
Fix: `cd ~/ai-agent-bootcamp` (🐧) or `cd ~\ai-agent-bootcamp` (🪟), then run again.

## 7. Virtual environments, one more time

```{raw} html
:file: ../diagrams/s01-venv.html
```

* `python -m venv .venv` **creates** the private box (once per project).
* `source .venv/bin/activate` (🐧) or `.\.venv\Scripts\Activate.ps1` (🪟) **turns it on** (every new terminal).
* `pip install requests` puts a package **inside the box**.
* `pip freeze > requirements.txt` saves the list of packages. Anyone (even you, on a new laptop) can rebuild
  the same box with `pip install -r requirements.txt`.
* `deactivate` turns the box off.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `IndentationError` | the lines inside a function/loop are not lined up | use 4 spaces, never mix tabs and spaces |
| `NameError: name 'x' is not defined` | typo, or the variable is made *after* you use it | check spelling; order matters |
| `ModuleNotFoundError: requests` | the venv is off | activate it, then `pip install requests` |
| `KeyError: 'city'` | the dict has no such label | use `.get("city")` or print the dict to see what's inside |
| `JSONDecodeError` | the text isn't valid JSON (maybe an HTML error page) | `print(response.text)` to look at it |
| `FileNotFoundError: .env` | you ran the script from another folder | `cd` into `ai-agent-bootcamp` |
| 🪟 `python` opens the Microsoft Store | Python isn't installed/on PATH | reinstall and tick **Add to PATH** |

## Tasks

**Task 1 · Warm-up (10 min).** In `functions_demo.py`, add a function `celsius_to_fahrenheit(c)`
(formula: `c * 9 / 5 + 32`) and print the answer for `31`.

<details class="solution">
<summary>Answer</summary>

```python
def celsius_to_fahrenheit(c):
    return c * 9 / 5 + 32

print(celsius_to_fahrenheit(31))   # 87.8
```

</details>

**Task 2 · Build (20 min).** Add a 4th city (for example `"mumbai": (19.08, 72.88)`) to `weather_summary.py`.
Then change the output so it also prints the temperature in Fahrenheit using your Task 1 function.

<details class="solution">
<summary>Answer</summary>

```python
CITIES = {
    "chennai": (13.08, 80.27),
    "delhi": (28.61, 77.21),
    "london": (51.51, -0.13),
    "mumbai": (19.08, 72.88),
}

def celsius_to_fahrenheit(c):
    return c * 9 / 5 + 32

# ...at the bottom of the file:
f = celsius_to_fahrenheit(info["temperature_c"])
print(f"Weather in {info['city'].title()}: {info['temperature_c']} °C ({f:.1f} °F), wind {info['wind_kmh']} km/h")
```

`:.1f` means "show one number after the decimal point".

</details>

**Task 3 · Challenge (30 min).** Write `top_news.py` that calls the free Hacker News API:
`https://hacker-news.firebaseio.com/v0/topstories.json` returns a list of story ids. For the first 5 ids, call
`https://hacker-news.firebaseio.com/v0/item/<id>.json` and print each story's `title`. Handle internet
errors with `try/except`.

<details class="solution">
<summary>Answer</summary>

```python
import requests

BASE = "https://hacker-news.firebaseio.com/v0"

try:
    ids = requests.get(f"{BASE}/topstories.json", timeout=15).json()
    for story_id in ids[:5]:                     # [:5] = the first five items
        story = requests.get(f"{BASE}/item/{story_id}.json", timeout=15).json()
        print("-", story["title"])
except requests.RequestException as error:
    print("Could not reach Hacker News:", error)
```

</details>

## Quiz

Take **"Session 1 · Quiz"** from the portal's **Quizzes** page. It checks functions, lists, dicts, JSON,
status codes and `.env`.

## Recap

- ✅ You can run a Python file and read its output.
- ✅ A **function** is a reusable recipe; every agent *tool* will be one.
- ✅ A **list of dictionaries** is how conversations are stored.
- ✅ **JSON** is text that converts to and from dictionaries (`dumps`/`loads`).
- ✅ **requests** calls web APIs; always use `timeout` and handle errors.
- ✅ Secrets go in `.env`, **never** in code.

**Next:** [Session 2 · How LLMs Work](02-how-llms-work.md): what is actually happening inside the AI, and your
first call to one.

## Session materials

- {download}`hello.py <../code/01-python-for-ai/hello.py>`
- {download}`functions_demo.py <../code/01-python-for-ai/functions_demo.py>`
- {download}`data_structures.py <../code/01-python-for-ai/data_structures.py>`
- {download}`json_demo.py <../code/01-python-for-ai/json_demo.py>`
- {download}`weather_summary.py <../code/01-python-for-ai/weather_summary.py>`
- {download}`env_demo.py <../code/01-python-for-ai/env_demo.py>`
- {download}`check_setup.py <../code/01-python-for-ai/check_setup.py>`
