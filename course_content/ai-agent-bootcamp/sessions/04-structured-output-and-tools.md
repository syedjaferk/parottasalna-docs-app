# Session 4 · Structured Output & Tools

**Day 1 · ⏱ about 100 minutes · 🧰 you need: [Session 3](03-calling-apis-and-chatbots.md) done (`llm.py` version 2)**

## The big idea

So far your AI **talks**. Today it learns to **act**. Two skills make that possible:

1. **Structured output:** getting the AI to answer in **exact JSON** instead of free text, so *code* can read it.
2. **Tool calling:** letting the AI **ask your program to run a function** (like a calculator or a weather lookup) and then use the result.

**Everyday example:** a manager (the AI) can't use a calculator himself, because he only *speaks*.
So he tells his assistant (your Python code): *"Please calculate 17.5% of 2480 and tell me the result."*
The assistant runs the calculator, gives him the number, and the manager writes the final report.
**The AI never runs anything. It only asks. Your code does the work.** This is the most important sentence of the
whole bootcamp. Read it twice.

**By the end** you'll write a script where the AI uses a calculator and a weather tool by itself. This is the core mechanism that turns a chatbot into an agent.

## Before you start (checklist)

- [ ] `llm.py` **version 2** (with `call_api`) is in your folder. If not, download it below.
- [ ] You can run `python chatbot.py` without errors.
- [ ] Put the files of this session in the **same folder** as `llm.py`.

## 1. Prompt engineering in 10 minutes

**Prompt engineering** just means *writing clear instructions*. Three simple tools cover 90% of cases:

```{raw} html
:file: ../diagrams/s04-prompt-levels.html
```

| Technique | What you do | Example |
|---|---|---|
| **Instructions** | say exactly what you want | `Classify the sentiment as one word.` |
| **Constraints** | set limits and the format | `Reply with only: positive, negative or mixed.` |
| **Examples (few-shot)** | show 2-3 solved examples | `"Loved it!" -> positive` |

Create `prompt_patterns.py` and run it to *see* the difference:

```{literalinclude} ../code/04-structured-output-and-tools/prompt_patterns.py
:language: python
```

```bash
python prompt_patterns.py
```

**Typical output:**

```text
=== Weak prompt ===
The sentiment of the review is mixed. While the food and service were negative, the dessert was a highlight...

=== Instructions + constraints ===
mixed

=== Few-shot examples ===
mixed
```

The weak prompt gives a long paragraph. Your code can't easily use that. The other two give **one clean word**.
**Rule of thumb:** *the more specific you are about the output, the more reliable it is.*

## 2. Structured output: make the AI speak JSON

Code can't read paragraphs. It can read **JSON** (Session 1!). So we ask for JSON:

```{raw} html
:file: ../diagrams/s04-structured.html
```

Why does it matter?

| Free text | JSON |
|---|---|
| "I'd say it's mostly positive, maybe 7 out of 10, about food and service" | `{"sentiment": "mixed", "score": 7, "topics": ["food", "service"]}` |
| your code must *guess* with string tricks | your code reads `result["score"]` directly |

### Three levels of reliability

1. **Ask nicely in the prompt:** *"Reply ONLY with JSON in this shape ..."* (works most of the time).
2. **JSON mode:** add `"response_format": {"type": "json_object"}` to the request. The provider **forces valid JSON**.
3. **Always validate in code:** parse, then check the keys and values. *Never trust the output blindly.*

Create `json_mode.py`:

```{literalinclude} ../code/04-structured-output-and-tools/json_mode.py
:language: python
```

```bash
python json_mode.py
```

```text
Raw text from the AI:
 {"sentiment": "mixed", "score": 6, "topics": ["food", "service", "dessert"]}

Now it is a Python dictionary we can use:
Sentiment: mixed
Score    : 6
Topics   : food, service, dessert
```

**Line by line:**

| Code | Meaning |
|---|---|
| `"temperature": 0` | steady output, best for structured data (Session 2) |
| `"response_format": {"type": "json_object"}` | "the reply must be valid JSON". Needs the word *JSON* in your prompt (we have it) |
| `json.loads(text)` | convert the JSON text to a dictionary (Session 1) |
| `try/except json.JSONDecodeError` | handle the rare broken answer without crashing |
| `missing = [key for key in ... if key not in result]` | a **list comprehension**: collect every required key that the AI forgot |
| `raise SystemExit(...)` | stop the program with a message |

:::{note}
**JSON mode makes the *format* valid, not the *content* correct.** The AI can still return the wrong
sentiment. That is why we check allowed values (`in ("positive", "negative", "mixed")`).
:::

## 3. Tool calling: letting the AI ask for help

### The idea, in pictures

```{raw} html
:file: ../diagrams/s04-tool-flow.html
```

1. You send the question **plus a menu of tools** (names and descriptions).
2. The AI reads the question and decides: *"I need the weather tool."* It replies **not with an answer, but with a request**: *"call `get_weather` with `{city: chennai}`"*.
3. **Your code** runs the real function.
4. You send the **result** back to the AI.
5. The AI writes the final answer using the result.

```{raw} html
:file: ../diagrams/s04-tool-sequence.html
```

### Step A · The tools: functions + descriptions

Create `tools.py`. It has **three parts** (read the comments):

```{literalinclude} ../code/04-structured-output-and-tools/tools.py
:language: python
```

**Part 1 · the real functions.** `calculator`, `get_weather`, `get_time` are ordinary Python. Look at three details:

* **`calculator` doesn't use `eval()`.** `eval` would run *any* code the AI (or an attacker!) writes, for example `__import__("os").system("delete everything")`. Our `_eval` walks the maths expression and only allows numbers and `+ - * / ** %`. Run it with the test below to see it refuse bad input. **Never give an AI a tool that can run arbitrary code.**
* **Tools return text, even for errors** (`"Error: ..."`). The AI can read the error and fix its mistake.
* `get_weather` uses `timeout=15` and catches network errors, exactly like Session 1.

**Part 2 · `TOOL_SPECS`, the menu the AI reads.** For each tool you write:

| Field | What it is for |
|---|---|
| `name` | what the AI calls it |
| `description` | **the most important field.** The AI decides *when* to use the tool from this sentence. Be clear and specific |
| `parameters` | a **JSON Schema**: which arguments exist, their types, and which are `required` |

**Part 3 · `TOOL_FUNCTIONS`, a phone book.** It maps a name (text) to the real function. When the AI says
`"get_weather"`, we look it up here and call it: `TOOL_FUNCTIONS[name](**args)`. (`**args` unpacks a dictionary into
named arguments: `{"city": "chennai"}` becomes `get_weather(city="chennai")`.)

Test your tools **without any AI** first (always a good habit):

```bash
python -c "from tools import calculator, get_time; print(calculator('(12 + 8) * 3')); print(calculator('1/0')); print(get_time())"
```

```text
60
Error: division by zero
Thursday, 15 October 2026, 20:32
```

### Step B · The conversation with tools

Create `tool_demo.py`:

```{literalinclude} ../code/04-structured-output-and-tools/tool_demo.py
:language: python
```

```bash
python tool_demo.py
```

**Expected output:**

```text
AI wants to use tools: ['get_weather', 'calculator']
  running get_weather({'city': 'chennai'})
  result: Chennai: 29.4 °C, wind 11.2 km/h
  running calculator({'expression': '0.175 * 2480'})
  result: 434.0

Final answer: In Chennai it's currently 29.4 °C with a light wind of 11.2 km/h. And 17.5% of 2480 is 434.
```

**Line by line:**

| Code | Meaning |
|---|---|
| `"tools": TOOL_SPECS` | hand the AI the menu |
| `message.get("tool_calls")` | if the AI wants tools, this is a list of requests. If not, it just answered |
| `messages.append(message)` | **keep the AI's request in the history.** Without it the next call makes no sense |
| `json.loads(call["function"]["arguments"])` | the arguments arrive as **JSON text**, so we convert to a dict |
| `TOOL_FUNCTIONS[name](**args)` | **our code runs the real function** |
| `{"role": "tool", "tool_call_id": ..., "content": ...}` | the result goes back with the **fourth role, `tool`**, and the matching `tool_call_id` so the AI knows which request it answers |
| second `call_api` | the AI now sees the results and writes the final answer |

:::{important}
**Notice what you did NOT write:** you never wrote `if "weather" in question:`. The AI itself decided *which*
tools to use, *how many*, and *with which arguments*. It even called two tools for one question. That decision-making is what
makes it an agent. In Session 5 we wrap this in a loop so it can keep going until the job is done.
:::

## 4. Writing good tool descriptions

A tool is only as good as its description. Compare:

| Weak ❌ | Strong ✅ |
|---|---|
| `"Gets stuff"` | `"Get the current weather for a city. Known cities: chennai, delhi, london."` |
| parameter `x` | parameter `city`: `"city name in lowercase"` |
| one big tool `do_everything` | small tools that each do **one** thing |

**Checklist:** one job per tool · a clear verb in the name · say *when* to use it · list allowed values ·
return short, readable text · return errors as text.

## 5. Safety: the AI is *not* in charge

Because **your code** runs the tools, you decide what is allowed:

* Never give a tool that runs raw shell commands or `eval` unless you have sandboxed it (Session 12).
* **Check the arguments** before acting (our `get_weather` rejects unknown cities).
* Keep tools **read-only** at first. Give "delete" or "send money" tools later, with human approval.
* The AI can ask for a tool that doesn't exist. `TOOL_FUNCTIONS[name]` would then crash, so in Session 5 we add a safe lookup.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| The AI never calls the tool | the `description` is vague, or the question doesn't need the tool | rewrite the description; ask a question that clearly needs it |
| `KeyError: 'get_wheather'` | the AI used a name not in `TOOL_FUNCTIONS` | match names exactly; look names up with `.get()` |
| `TypeError: unexpected keyword argument` | the AI sent an argument your function doesn't have | make `parameters` in the spec match the function |
| `400 ... tool_call_id` | you forgot the `tool_call_id` or didn't append the AI's message first | follow the order: append `message`, then one `tool` message per call |
| `JSONDecodeError` on arguments | the AI wrote broken JSON in `arguments` | catch it, return `"Error: bad arguments"` as the tool result |
| Model says it doesn't support tools | not every free model can call tools | pick another model (Llama 3.x on Groq works) |
| JSON mode returns an error | your prompt never says "JSON" | include the word JSON in the system prompt |

## Tasks

**Task 1 · Warm-up (10 min).** Run `python -c "from tools import calculator; print(calculator('2 ** 10'))"`, then try
`calculator('__import__(\"os\")')`. What happens, and why is that *good*?

<details class="solution">
<summary>Answer</summary>

`2 ** 10` prints `1024`. The second one prints `Error: only numbers and + - * / ** % are allowed`.
That is good because our calculator only understands maths. With `eval()`, the same text would have **run Python code**.
A tool must do exactly what you intend and nothing more.

</details>

**Task 2 · Build (30 min).** Add a new tool `word_count(text)` that returns how many words are in a text. Add it to
`tools.py` (function, `TOOL_SPECS`, `TOOL_FUNCTIONS`), then ask: *"How many words are in 'the quick brown fox jumps'?"*

<details class="solution">
<summary>Answer</summary>

```python
def word_count(text):
    """Count the words in a text."""
    return str(len(text.split()))
```

```python
# in TOOL_SPECS
    {"type": "function", "function": {
        "name": "word_count",
        "description": "Count how many words are in a piece of text.",
        "parameters": {"type": "object",
                       "properties": {"text": {"type": "string", "description": "the text to count"}},
                       "required": ["text"]}}},
```

```python
# in TOOL_FUNCTIONS
    "word_count": word_count,
```

All three places must agree on the name `word_count` and the argument name `text`.

</details>

**Task 3 · Challenge (45 min).** Write `extract_contact.py`: send *"Hi, I'm Priya from Coimbatore. Call me on 98765 43210 or mail priya@example.com"* with JSON mode and a system prompt that asks for `{"name", "city", "phone", "email"}`. Validate that all four keys exist, and that `email` contains `@`. Print each field on its own line.

<details class="solution">
<summary>Answer</summary>

```python
import json
from llm import call_api

TEXT = "Hi, I'm Priya from Coimbatore. Call me on 98765 43210 or mail priya@example.com"
body = {
    "messages": [
        {"role": "system", "content": 'Extract contact details. Reply ONLY with JSON: '
                                       '{"name": "", "city": "", "phone": "", "email": ""}'},
        {"role": "user", "content": TEXT},
    ],
    "temperature": 0,
    "response_format": {"type": "json_object"},
}
text = call_api(body)["choices"][0]["message"]["content"]
data = json.loads(text)

missing = [k for k in ("name", "city", "phone", "email") if k not in data]
if missing:
    raise SystemExit(f"Missing keys: {missing}")
if "@" not in data["email"]:
    raise SystemExit("That doesn't look like an email.")

for key in ("name", "city", "phone", "email"):
    print(f"{key:>6}: {data[key]}")
```

This is a real-world use of LLMs: turning messy text into clean data.

</details>

## Quiz

Take **"Session 4 · Quiz"** from the portal's **Quizzes** page (prompting, JSON mode, tool calling, the `tool` role, safety).

## Recap

- ✅ **Prompt engineering** = instructions + constraints + examples.
- ✅ **Structured output**: ask for JSON, use JSON mode, **validate** in code.
- ✅ **Tool calling**: the AI *asks*, your code *runs*, you send the result back, the AI answers.
- ✅ A tool = a **function** + a **description** (the AI reads this) + an entry in the **phone book**.
- ✅ Good descriptions, small tools, text errors, no raw `eval`.
- ✅ This is the core mechanism that turns a chatbot into an **agent**.

**Next:** [Session 5 · Build an Agent from Scratch](05-build-an-agent.md). We put the tool call in a **loop**, add memory and
guard rails, and you'll have a real mini agent.

## Session materials

- {download}`llm.py <../code/04-structured-output-and-tools/llm.py>`
- {download}`prompt_patterns.py <../code/04-structured-output-and-tools/prompt_patterns.py>`
- {download}`json_mode.py <../code/04-structured-output-and-tools/json_mode.py>`
- {download}`tools.py <../code/04-structured-output-and-tools/tools.py>`
- {download}`tool_demo.py <../code/04-structured-output-and-tools/tool_demo.py>`
