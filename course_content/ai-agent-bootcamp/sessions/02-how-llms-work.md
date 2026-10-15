# Session 2 · How LLMs Work

**Day 1 · ⏱ about 90 minutes · 🧰 you need: [Session 1](01-python-for-ai.md) done, `.env` working**

## The big idea

An **LLM** (*Large Language Model*) is the "brain" inside ChatGPT, Gemini, Claude, Llama and every AI
agent. You do **not** need maths to use one well. You only need a good **mental model**, a picture in
your head of what it is and what it is not.

> **An LLM is a super-powered autocomplete.** On your phone, the keyboard suggests the next word after
> "Good...". An LLM does the same thing, but it has read a huge part of the internet, so it can continue
> *almost any* text in a very sensible way.

**Everyday example:** if I say *"Idli, dosa, vada and..."* you instantly think *"sambar"*. You never
looked it up. You have simply seen those words together many times. An LLM has "seen" billions of
such sentences.

**By the end of this session** you will know the five words everyone uses (token, context window,
temperature, hallucination, parameters) and you will have made your first real call to an LLM from Python.

## Before you start (checklist)

- [ ] `python check_setup.py` shows all `[ OK ]` (from [Setup](../setup.md)).
- [ ] Your terminal is in `ai-agent-bootcamp` with `(.venv)` on.
- [ ] Download the helper {download}`llm.py <../code/02-how-llms-work/llm.py>` into the same folder. We explain it in this session, and every later session uses it.

## 1. What is happening when you "ask" an AI?

```{raw} html
:file: ../diagrams/s02-predict.html
```

The model does **one thing**: *given the text so far, guess the next small piece of text.*

1. You send: `The capital of India is`
2. The model gives every possible next piece a **score** (a probability). `" New"` gets 82%.
3. It **picks one** (we'll see *how* in the temperature section).
4. It adds that piece to the text and **repeats**, one piece at a time, until the answer is finished.

That is it. A whole essay is just this loop run a few hundred times. This is why the AI "types" its
answer word by word on the screen.

:::{note}
**"Training" in one paragraph.** To build the model, engineers show it a gigantic amount of text and
ask it to guess the next word, again and again. Every time it is wrong, it nudges its internal numbers
a tiny bit. After weeks on thousands of computers, it becomes very good at guessing. The internal
numbers are called **parameters** (or "weights"). "Llama 3.1 **8B**" means about **8 billion** of them.
More parameters usually means smarter, but slower and costlier.
:::

## 2. Tokens: how the AI reads text

The model doesn't read letters or whole words. It reads **tokens**: small chunks of text.

```{raw} html
:file: ../diagrams/s02-tokens.html
```

* Short common words (`is`, `the`) are 1 token. Long or rare words are split (`Learn` + `ing`).
* In English, **1 token ≈ 4 letters ≈ ¾ of a word**. So 100 words ≈ 130 tokens.
* Tamil, Hindi and other non-English languages usually need **more tokens** for the same meaning, so they cost more and fill the memory faster.
* **You pay in tokens**, for what you send *and* for what the AI writes. Limits are also in tokens.

## 3. The context window: the model's short-term memory

The **context window** is the maximum amount of text (in tokens) the model can look at **in one go**:
the instructions, the whole chat so far, *and* the answer it is writing.

```{raw} html
:file: ../diagrams/s02-context.html
```

Two facts that surprise beginners:

1. **The model has no memory between calls.** Each time you call the API, it starts from a blank mind. A "conversation" only works because *your program sends the whole conversation again every time*. (You'll prove this in the lab below.)
2. **When the history gets too long, something must be cut.** Older messages fall out of the window and the model **forgets them**.

Typical sizes: small free models ≈ 8,000 tokens (about 6,000 words); bigger ones 128,000 or more.

## 4. Temperature: steady or creative?

When the model scores the next token, it must **choose**. **Temperature** is the dial for how adventurous that choice is.

```{raw} html
:file: ../diagrams/s02-temperature.html
```

| Temperature | Behaviour | Use it for |
|---|---|---|
| **0** | always picks the top choice, so it is **steady** and repeatable | maths, code, JSON, tools, agents |
| **0.5 - 0.8** | mostly the top choices, some variety | normal chat |
| **1.0 - 2.0** | gives unlikely words a chance, so it is **creative**, sometimes nonsense | brainstorming names, poems |

:::{tip}
**For agents, use a low temperature (0 to 0.3).** An agent must pick the right tool and write valid JSON.
You want it boring and reliable, not creative.
:::

(There is a related dial called **top_p**. Leave it at the default. Temperature is enough for now.)

## 5. Hallucination: confident and wrong

Because an LLM is *guessing a likely continuation*, it will sometimes produce something that **sounds
right but is false**: a fake book title, a made-up law, a wrong date. This is called a **hallucination**.
The model isn't lying. It doesn't know the difference between "likely" and "true".

**How to reduce it:**

* Give the model the facts in your message and say *"use only this text"*.
* Let it **use tools** (a calculator, a search, a database) instead of guessing. This is the whole reason agents exist (Session 4).
* Ask it to say **"I don't know"** when unsure.
* **Always check important answers** (money, health, legal, code that runs on a server).

## 6. Choosing a model

```{raw} html
:file: ../diagrams/s02-models.html
```

| Question | Guide |
|---|---|
| **Free or paid?** | Learn on free tiers (Groq, OpenRouter `:free`, or Ollama on your laptop). Move to paid for production. |
| **Big or small?** | Start small (8B). If answers are poor, try a bigger one (70B). Use the **smallest model that does the job**. |
| **Context size?** | Chat is fine with 8K. Reading long documents needs 32K or more. |
| **Open or closed?** | *Open* (Llama, Qwen, Mistral) can run on your own machine. *Closed* (GPT, Claude, Gemini) only through their servers. |

## 7. Lab: your first AI call, with nothing hidden

### Step 1 · The raw call

Create `first_call.py`. This uses plain `requests` so you can see **exactly** what is sent and received:

```{literalinclude} ../code/02-how-llms-work/first_call.py
:language: python
```

Run it (venv on):

```bash
python first_call.py
```

**Expected output (the wording of the answer will differ):**

```text
Status code: 200
{
  "id": "chatcmpl-...",
  "model": "llama-3.1-8b-instant",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "A variable is a named container that stores a value you can use and change in a program."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 42,
    "completion_tokens": 22,
    "total_tokens": 64
  }
}
```

**How to read the answer** (this is the shape of *every* AI API reply):

| Field | Meaning |
|---|---|
| `choices[0].message.content` | **the AI's actual reply**. This is the part we want. |
| `finish_reason` | `stop` = it finished; `length` = it ran out of `max_tokens` and was cut off |
| `usage` | tokens used: `prompt_tokens` (what you sent), `completion_tokens` (what it wrote) |

**Line by line:**

| Code | Meaning |
|---|---|
| `os.getenv("LLM_BASE_URL")` | the provider's address from `.env` |
| `+ "/chat/completions"` | the "door" for chatting. It is the same on Groq, OpenRouter and Ollama |
| `headers = {"Authorization": "Bearer <key>"}` | your secret key, like showing a library card |
| `body = {...}` | what we want: which `model`, and the list of `messages` |
| `requests.post(..., json=body)` | POST sends data *to* the server (GET only asks for data) |

### Step 2 · The helper `llm.py`

Typing all of that each time is boring, so we put it in one reusable function:

```{literalinclude} ../code/02-how-llms-work/llm.py
:language: python
```

`chat(messages, temperature, max_tokens)` returns **two things**: the reply text and the `usage`.
`raise_for_status()` makes a bad key or rate limit stop the program with a clear error.
Keep `llm.py` in your project folder. **Every later session imports it.**

### Step 3 · Temperature experiment

```{literalinclude} ../code/02-how-llms-work/temperature_demo.py
:language: python
```

```bash
python temperature_demo.py
```

**Typical output:**

```text
--- temperature = 0.0 ---
  try 1: Chai Chronicles
  try 2: Chai Chronicles
  try 3: Chai Chronicles

--- temperature = 1.0 ---
  try 1: The Brew Nook
  try 2: Steep & Sip
  try 3: Chai Chronicles

--- temperature = 1.8 ---
  try 1: Kettle Karma Dreamhouse
  try 2: Masala Moonbeam
  try 3: Tea-ffany's
```

**What you learn:** at `0.0` the answers repeat. As you raise the dial you get more variety. At
`1.8` you may even get odd or broken answers. Notice `max_tokens=20`. It tells the model to stop after
about 20 tokens, so the reply (and your bill) stays small.

### Step 4 · Counting tokens and cost

```{literalinclude} ../code/02-how-llms-work/tokens_and_cost.py
:language: python
```

```bash
python tokens_and_cost.py
```

```text
Reply: Marina Beach in Chennai is one of the longest urban beaches in the world...

Tokens you SENT     : 47
Tokens the AI WROTE : 54
Total tokens        : 101

Your message has 10 words, so we expect roughly 13 tokens.
This one call would cost about $0.00000670
```

Why is "SENT" (47) bigger than our guess (13)? The provider adds a few hidden tokens for message formatting, so
there is always a little overhead. The point: **every call has a cost you can measure.** In Session 12 we use
this to build a budget.

### Step 5 · Prove the AI has no memory

```{literalinclude} ../code/02-how-llms-work/context_demo.py
:language: python
```

```bash
python context_demo.py
```

```text
Without history : I don't have access to your name. Could you tell me?
With history    : Your name is Asha!
Tokens sent this time: 52
```

The **first** call told the AI the name, but the **second call** started from a blank mind. Only when we
sent the whole conversation again did it "remember". **Memory is something your program builds, not
something the model has.** This single idea is the foundation of Session 3 (chatbots) and Session 5 (agent memory).

## What an LLM can and cannot do

| ✅ Good at | ❌ Bad at (without tools) |
|---|---|
| Writing, summarising, translating | Exact maths with big numbers |
| Explaining and brainstorming | Knowing today's news, weather or your private data |
| Turning messy text into structured data | Remembering past chats (unless you send them) |
| Writing and fixing small code | Always telling the truth (it can hallucinate) |

The "bad at" column is *exactly* what tools and agents solve. That is where we are heading.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `401 Unauthorized` | wrong key, or extra spaces/quotes in `.env` | copy the key again |
| `404 model not found` | model name changed or typo | run `python check_setup.py`, copy a name from its list |
| `429 Too Many Requests` | free-tier limit | wait 30-60 s; make fewer calls |
| Answer stops mid-sentence | `max_tokens` too small (`finish_reason: length`) | raise `max_tokens` |
| `ConnectionError` on 🪟 or 🐧 | no internet, or `LLM_BASE_URL` has a typo | check the URL; it must end with `/v1` (Groq) |
| `TypeError: NoneType` on `os.getenv(...) + "..."` | `.env` missing or not in the current folder | `cd ai-agent-bootcamp`; check the file name is `.env` |
| `ModuleNotFoundError: llm` | `llm.py` is not in the same folder as your script | put them in one folder |

## Tasks

**Task 1 · Warm-up (10 min).** Estimate the tokens in this sentence using the "1 token ≈ 4 letters" rule, then
check with `tokens_and_cost.py` by changing the message: *"Artificial intelligence is changing how we write software."*

<details class="solution">
<summary>Answer</summary>

The sentence is 61 characters including spaces. 61 ÷ 4 ≈ **15 tokens**. The real count is usually 12-16
plus a few formatting tokens. If your estimate was within a few tokens, you have the right feel for it.

</details>

**Task 2 · Build (20 min).** Edit `temperature_demo.py` to use your own prompt (for example *"Suggest a name for a
pet parrot"*) and temperatures `0.0, 0.7, 1.5`. Write down in a note: at which temperature did the answers
start to differ?

<details class="solution">
<summary>Answer</summary>

Change two lines only:

```python
QUESTION = "Suggest a name for a pet parrot. Reply with just the name."

for temperature in (0.0, 0.7, 1.5):
```

At `0.0` the three answers are the same (or almost). Differences usually start around `0.7`. There is no
exact number; it depends on the model and the question. That is the lesson: you pick the temperature by
experimenting.

</details>

**Task 3 · Challenge (30 min).** *Catch a hallucination.* Ask the model about something that does not exist, for
example *"Summarise the 1987 Tamil novel 'The Silver Peacock of Madurai' by Kavin Raj."* Then ask again, adding at
the start of your message: *"Answer only if you are sure it exists. Otherwise say exactly: I don't know."*
Compare both answers. Which one is better and why?

<details class="solution">
<summary>Answer</summary>

```python
from llm import chat

fake = "Summarise the 1987 Tamil novel 'The Silver Peacock of Madurai' by Kavin Raj."
careful = "Answer only if you are sure it exists. Otherwise say exactly: I don't know.\n" + fake

for prompt in (fake, careful):
    reply, _ = chat([{"role": "user", "content": prompt}], temperature=0, max_tokens=120)
    print(reply.strip(), "\n---")
```

The first call often invents a plot with great confidence (a hallucination). The second often says
*"I don't know"*. Instructions that give the model an honest way out reduce hallucination, but they don't
remove it. For real facts, give it a **tool** or the **source text**.

</details>

## Quiz

Take **"Session 2 · Quiz"** from the portal's **Quizzes** page (tokens, context window, temperature, hallucination, memory).

## Recap

- ✅ An LLM is a **next-token guesser**; long answers are the guess repeated.
- ✅ **Tokens** are the unit of reading, limits and cost (≈ ¾ word in English).
- ✅ The **context window** is short-term memory; the model forgets everything between calls.
- ✅ **Temperature** low = steady (agents), high = creative.
- ✅ **Hallucinations** are confident wrong answers; tools and source text reduce them.
- ✅ You made a real API call and wrote the reusable helper `llm.py`.

**Next:** [Session 3 · Calling APIs & Chatbots](03-calling-apis-and-chatbots.md). We use what you learned to build a
chatbot with personality and memory.

## Session materials

- {download}`llm.py <../code/02-how-llms-work/llm.py>`
- {download}`first_call.py <../code/02-how-llms-work/first_call.py>`
- {download}`temperature_demo.py <../code/02-how-llms-work/temperature_demo.py>`
- {download}`tokens_and_cost.py <../code/02-how-llms-work/tokens_and_cost.py>`
- {download}`context_demo.py <../code/02-how-llms-work/context_demo.py>`
