# Session 3 · Calling APIs & Chatbots

**Day 1 · ⏱ about 90 minutes · 🧰 you need: [Session 2](02-how-llms-work.md) done (`llm.py` works)**

## The big idea

In Session 2 you learned that the AI has **no memory** and that a chat works because *your program
sends the whole conversation every time*. Today you build that program: **a chatbot with a personality
and a memory**, in about 70 lines of Python.

**Everyday example:** imagine a very smart friend with a **short-term memory loss**. Every time you talk,
you must first hand him a notebook with everything said so far, plus a sticky note saying how he should
behave ("be a pirate"). He reads the notebook, answers, and you add his answer to the notebook. The
notebook is the **history**. The sticky note is the **system prompt**.

**By the end** you will have your first working AI application, and you will know how to handle the
errors that real APIs throw at you (wrong key, busy server, rate limits).

## Before you start (checklist)

- [ ] `llm.py` from Session 2 is in your `ai-agent-bootcamp` folder and `python context_demo.py` works.
- [ ] Venv on: you see `(.venv)`.

## 1. The three roles

Every message in a chat has a **role**. There are only three:

```{raw} html
:file: ../diagrams/s03-roles.html
```

| Role | Who | What it's for |
|---|---|---|
| `system` | **you, the developer** | rules and personality. Set once at the start. The user never sees it. |
| `user` | the person chatting | the questions |
| `assistant` | the AI | its earlier replies (you add them to the history yourself) |

The data you send is simply **a list of dictionaries**, exactly the structure from Session 1:

```python
messages = [
    {"role": "system",    "content": "You are a friendly Python tutor."},
    {"role": "user",      "content": "What is a variable?"},
    {"role": "assistant", "content": "It's a name tag stuck on a value."},
    {"role": "user",      "content": "Give an example."},
]
```

The AI reads **all four** and writes the next `assistant` message. That is how it "remembers".

## 2. Writing a good system prompt

The **system prompt** is the most powerful line in your chatbot. Compare:

| Weak ❌ | Strong ✅ |
|---|---|
| `You are helpful.` | `You are a patient Python tutor for complete beginners. Use simple words, give one small example, and end with a short question to check understanding.` |
| `Answer short.` | `Answer in at most 3 sentences. If you don't know, say "I don't know". Never invent facts.` |

**A recipe for a good system prompt** (use it again and again):

1. **Role**: who is the AI? (*a tutor, a chai-shop owner, a support agent*)
2. **Audience**: who is it talking to? (*complete beginners*)
3. **Style**: tone and length (*simple words, under 60 words*)
4. **Rules**: what to do and what **not** to do (*never invent facts; say "I don't know"*)

:::{tip}
Be specific, and tell it what to do when it is **unsure**. Vague prompts give vague answers.
:::

## 3. The chatbot loop

```{raw} html
:file: ../diagrams/s03-chat-loop.html
```

The whole program is a loop of five steps. Memory is just step 2 and step 4: **appending** to a list.

## 4. Upgrade `llm.py`: handle errors like a pro

Real APIs fail in boring ways. Your program must **survive** them. Replace your `llm.py` with this new
version:

```{literalinclude} ../code/03-calling-apis-and-chatbots/llm.py
:language: python
```

### What the status codes mean, and what we do

```{raw} html
:file: ../diagrams/s03-errors.html
```

| Code | Meaning | Our reaction in the code |
|---|---|---|
| `200` | success | return the answer |
| `401` / `403` | your key is wrong | **stop** with a clear message (retrying won't help) |
| `404` | wrong model name or URL | stop with a clear message |
| `429` | you are sending too many requests (**rate limit**) | wait, then retry |
| `500` - `504` | the server had a problem | wait, then retry |

### Backoff: be polite when the server is busy

```{raw} html
:file: ../diagrams/s03-backoff.html
```

`wait = 2 ** attempt` gives 1, 2, 4 seconds. Each retry waits twice as long as the last (**exponential
backoff**). Hammering a busy server immediately makes things worse; waiting longer gives it time to recover.

### New ideas in this file

| Code | Meaning |
|---|---|
| `class LLMError(Exception)` | our **own kind of error** with a human-friendly message |
| `except (requests.Timeout, requests.ConnectionError)` | catch **only** network trouble, not every possible error |
| `else:` after `try/except` | runs only if the `try` worked (no network error) |
| `{"model": MODEL, **body}` | merge two dictionaries (`**` "unpacks" one into the other) |
| `call_api(body)` | the *general* function: any request body in, full JSON out. We use it in Sessions 4 and 5 for tools |
| `chat(...)` | the *simple* function from before, now built on top of `call_api` |

## 5. Lab: build the chatbot

Create `chatbot.py`:

```{literalinclude} ../code/03-calling-apis-and-chatbots/chatbot.py
:language: python
```

Run it:

```bash
python chatbot.py
```

**A sample conversation (your replies will differ):**

```text
Chatbot ready. Commands: /persona <tutor|pirate|chai>  /reset  /save  /quit
Current personality: tutor

You: What is a list?
Bot: A list is like a shopping list in Python: a row of items in order. For example:
     fruits = ["apple", "banana"]. Can you guess what fruits[0] gives?
     [118 tokens]

You: apple?
Bot: Exactly right! Position counting starts at 0, so fruits[0] is "apple". 🎉
     [171 tokens]

You: /persona pirate
(personality is now 'pirate', memory cleared)
You: what is a list?
Bot: Arr! A list be a treasure chest o' items, all lined up in order, matey!
     [64 tokens]
```

Notice that the second answer (`apple?`) only makes sense **because the bot remembered the first**.
Also notice the token count **grows** with each turn: that is the history getting longer.

### Line by line (the important new parts)

| Code | Meaning |
|---|---|
| `PERSONAS = {...}` | a dictionary: name → system prompt. Easy to add more |
| `history = [{"role": "system", ...}]` | the notebook, starting with the sticky note |
| `trim(history)` | keep the system message + only the **last 10 pairs**. Without this the history would eventually overflow the context window (Session 2!) and cost more each turn |
| `rest[-MAX_TURNS * 2:]` | "the last 20 items of the list" (negative index counts from the end) |
| `while True:` | loop forever, until we `break` on `/quit` |
| `input("You: ")` | wait for the user to type, give back the text |
| `history.append(...)` | **this one line is the memory** |
| `except LLMError` + `history.pop()` | if the call fails, remove the question so history stays clean |
| `if __name__ == "__main__":` | run `main()` only when started directly |

## 6. One code, any provider

Your code never mentions *Groq*. It only reads three lines from `.env`. To switch provider, **edit `.env` only**:

| Provider | `LLM_BASE_URL` | `LLM_MODEL` (example) |
|---|---|---|
| Groq | `https://api.groq.com/openai/v1` | `llama-3.1-8b-instant` |
| OpenRouter | `https://openrouter.ai/api/v1` | a model ending in `:free` |
| Ollama (on your laptop) | `http://localhost:11434/v1` | `llama3.2` |

Try it: change those lines (and `LLM_API_KEY`), restart `chatbot.py`, and it just works. This is why we
built our own tiny `llm.py` instead of using one company's library.

## 7. Rate limits: what to do when you hit them

Free tiers allow only so many requests per minute and tokens per day. If you see the *"server busy ... 429"*
message, that is normal.

* Our `call_api` already **waits and retries** for you.
* Avoid loops that fire many calls instantly. Add `time.sleep(1)` between calls.
* Keep `max_tokens` small and history short (`trim`) to use fewer tokens.
* If it keeps failing, switch the model (a smaller one has a bigger allowance) or provider in `.env`.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| The bot forgets everything | you didn't `append` the reply to `history` | add both the user message and the assistant reply |
| The bot behaves oddly after many turns | history too long, or a very long system prompt | `trim()` the history; keep the system prompt short |
| `KeyError: 'choices'` | the API returned an error object, not an answer | use `call_api` (it checks status first) |
| The persona is ignored | the `system` message isn't first in the list | it must be `history[0]` |
| Reply is cut mid-sentence | `max_tokens` too low | raise it to 250-500 |
| 🪟 Weird characters (`â€™`) when saving | file encoding | always `open(..., encoding="utf-8")`, as we do |
| `/persona` does nothing | typed without a name | `/persona pirate` |

## Tasks

**Task 1 · Warm-up (10 min).** Add a fourth personality called `"grandma"`: *"You are a loving grandmother who explains everything with a small story."*
Test it with `/persona grandma`.

<details class="solution">
<summary>Answer</summary>

Add one line inside the `PERSONAS` dictionary:

```python
    "grandma": "You are a loving grandmother who explains everything using a short, warm story. "
               "Keep it under 80 words.",
```

The `/persona` command already looks names up in this dictionary, so nothing else changes.

</details>

**Task 2 · Build (25 min).** Add an `/undo` command that removes the **last question and answer** from the history
(like "forget that last turn").

<details class="solution">
<summary>Answer</summary>

Add this block next to the other commands, before `history.append(...)`:

```python
        if text == "/undo":
            if len(history) >= 3:
                history.pop()      # the assistant reply
                history.pop()      # the user question
                print("(last turn removed)")
            else:
                print("(nothing to undo)")
            continue
```

`len(history) >= 3` makes sure we never remove the system message (which sits at position 0).

</details>

**Task 3 · Challenge (40 min).** Make the bot **load `chat.json` when it starts**, so it remembers you even after you
close it. Also print a warning when the total tokens of one call go above `2000`.

<details class="solution">
<summary>Answer</summary>

```python
import os

def load_history(persona):
    if os.path.exists("chat.json"):
        with open("chat.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return new_history(persona)

# in main(): replace  history = new_history(persona)  with:
history = load_history(persona)

# after printing the reply:
if usage.get("total_tokens", 0) > 2000:
    print("     ⚠ This chat is getting long. Use /reset to save tokens.")
```

Remember to type `/save` before `/quit`, or call the save code automatically when the user quits. The
warning matters because tokens (and cost) grow every turn.

</details>

## Quiz

Take **"Session 3 · Quiz"** from the portal's **Quizzes** page (roles, history, system prompts, status codes, backoff).

## Recap

- ✅ A chat = **a list of `{role, content}` dictionaries**, sent in full every time.
- ✅ **system** = rules, **user** = you, **assistant** = the AI.
- ✅ **Memory** = appending to the list; **trim** it so it never gets too long.
- ✅ Handle errors: `401` stop, `429`/`5xx` retry with **backoff**.
- ✅ One code works with Groq, OpenRouter or Ollama: only `.env` changes.
- ✅ You built **your first working AI application**.

**Next:** [Session 4 · Structured Output & Tools](04-structured-output-and-tools.md). We teach the AI to return
exact JSON and to **ask your code to run functions**. That is the step that turns a chatbot into an agent.

## Session materials

- {download}`llm.py (version 2) <../code/03-calling-apis-and-chatbots/llm.py>`
- {download}`chatbot.py <../code/03-calling-apis-and-chatbots/chatbot.py>`
