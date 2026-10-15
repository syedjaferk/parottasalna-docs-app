# Session 5 · Build an Agent from Scratch

**Day 1 · ⏱ about 120 minutes · 🧰 you need: [Session 4](04-structured-output-and-tools.md) done (you understand tool calling)**

## The big idea

In Session 4 the AI asked for one tool, you ran it, and it answered. That is **one** round. A real job often
needs **several** rounds: *"Find the weather in Chennai, convert it to Fahrenheit, and save a note if it's above 30."*
The AI must look at each result and **decide what to do next**.

An **agent** is simply a **loop**:

```{raw} html
:file: ../diagrams/s05-agent-loop.html
```

> **Think → Act → Observe → repeat**, until the AI decides it has enough to answer.

**Everyday example:** a taxi driver with a map app. He *thinks* (where am I?), *acts* (turns left), *observes* (a road
is blocked), and *thinks again* (take another route). He keeps going until you arrive. He doesn't plan the whole trip
at the start. He reacts to what he sees.

**By the end** you'll have built a working agent with **tools, short-term memory, summary memory and safety limits**
in about 150 lines. You will then know exactly what agent frameworks (including Hermes in Session 6) do *under the hood*.

## Before you start (checklist)

- [ ] You ran `tool_demo.py` from Session 4 and saw the AI call tools.
- [ ] Create a **new folder** `session5` inside `ai-agent-bootcamp` (or just reuse the main folder), and put the files below in it.
- [ ] Download these four files, and keep them together: {download}`llm.py <../code/05-build-an-agent/llm.py>`, {download}`tools.py <../code/05-build-an-agent/tools.py>`, {download}`agent.py <../code/05-build-an-agent/agent.py>`

**🐧 Linux**

```bash
cd ~/ai-agent-bootcamp
mkdir -p session5 && cd session5
cp ../.env .          # the agent reads .env from the folder you run it in
```

**🪟 Windows (PowerShell)**

```powershell
cd ~\ai-agent-bootcamp
mkdir session5 -Force; cd session5
copy ..\.env .
```

## 1. Chatbot vs workflow vs agent

```{raw} html
:file: ../diagrams/s05-three-kinds.html
```

| | **Chatbot** | **Workflow** | **Agent** |
|---|---|---|---|
| Who decides the steps? | nobody, it just replies | **you**, in code (`if/else`) | **the AI**, while running |
| Can it use tools? | no | yes, fixed order | yes, any order, any number of times |
| Predictable? | very | very | less. This needs guard rails |
| Example | "Explain recursion" | "Every morning: fetch news → summarise → email" | "Plan my trip, check the weather, and book" |

**Tip for real life:** if you *can* write the steps down in advance, use a plain workflow; it's cheaper and more
reliable. Use an agent only when the path is **unknown** beforehand.

## 2. The four parts of every agent

```{raw} html
:file: ../diagrams/s05-parts.html
```

| Part | What it is | In our code |
|---|---|---|
| 🧠 **Brain** | the LLM that decides | `call_api(...)` |
| 🛠️ **Tools** | functions it can call | `tools.py` |
| 💾 **Memory** | what it remembers | `self.messages` + `self.summary` |
| 🔁 **Loop + limits** | keeps going, and knows when to stop | the `for step in range(...)` loop |

## 3. Memory: short-term and summary

An agent that forgets is useless, but an agent that remembers **everything** overflows the context window (Session 2)
and gets expensive. We use two kinds:

```{raw} html
:file: ../diagrams/s05-memory.html
```

| Memory | How it works | Good for | Weak at |
|---|---|---|---|
| **Short-term** | keep the last N messages as they are | the current task, exact wording | forgets when it's cut off |
| **Summary** | when the history gets long, ask the AI to write a **short summary** of the old part and keep only that | long chats: names, preferences | loses fine detail |
| **Notes (long-term)** | a tool writes to a file (`save_note`) | facts that must survive after you close the program | the agent must *choose* to save |

Our agent uses **all three**.

## 4. Stopping conditions: how an agent avoids running forever

An agent in a loop can go wrong in two ways: **loop forever** (costing money) or **repeat the same useless action**.
We add three safety rules:

```{raw} html
:file: ../diagrams/s05-stops.html
```

1. **Finish:** the AI answers without asking for a tool, so that's the normal end.
2. **`max_steps`:** after 6 steps, stop and apologise, no matter what.
3. **No repeats:** if it asks for the *exact same* tool call twice, tell it so instead of running it again.

## 5. Lab: build and run your agent

### Step 1 · The tools

Your `tools.py` now has **five** tools. `calculator`, `get_weather` and `get_time` are from Session 4, plus two new ones: **`save_note`** and
**`read_notes`**, which write and read a file `notes.txt`. This is the agent's *long-term* memory.

```{literalinclude} ../code/05-build-an-agent/tools.py
:language: python
:lines: 50-66
```

`open(NOTES_FILE, "a")` uses mode **`"a"` = append**: add to the end of the file without erasing it.

### Step 2 · The agent

```{literalinclude} ../code/05-build-an-agent/agent.py
:language: python
```

### Step 3 · Run it

```bash
python agent.py
```

**Try this conversation.** The `[step ...]` lines are the agent's thinking, printed for you to learn from:

```text
You: What is the weather in Chennai, and what is that temperature in Fahrenheit?

[step 1] THINK: asking the AI what to do next...
[step 1] ACT    : get_weather({"city": "chennai"})
[step 1] OBSERVE: Chennai: 29.4 °C, wind 11.2 km/h

[step 2] THINK: asking the AI what to do next...
[step 2] ACT    : calculator({"expression": "29.4 * 9 / 5 + 32"})
[step 2] OBSERVE: 84.92

[step 3] THINK: asking the AI what to do next...
[step 3] DONE: final answer ready.

Jarvis: It's 29.4 °C (about 84.9 °F) in Chennai right now, with a light breeze.
```

Look at what happened: the AI **needed the weather first**, and only *after seeing* `29.4` could it ask for the
calculation. It could not have asked for both at once, because it didn't know the temperature yet. **That's why a loop is needed.**

Now try these and watch the steps:

```text
You: Remember that my favourite city is Madurai.
You: What time is it?
You: What do you remember about me?
You: /quit
```

Run it again and ask `What is my favourite city?`. It reads `notes.txt`, so it still knows. That is long-term memory.

### Step 4 · Understand the code, part by part

**`__init__`**: the agent's settings and its two memories.

| Code | Meaning |
|---|---|
| `max_steps=6` | safety limit (stopping condition 2) |
| `max_messages=12` | when the history is longer, summarise the old part |
| `self.messages = []` | short-term memory |
| `self.summary = ""` | summary memory |

**`system_message()`**: rebuilds the system prompt each time and **adds the summary** to it, so the AI "remembers" the older chat.

**`run_tool()`**: *the safety net.* It **always returns text** and never crashes:

| Situation | What the tool returns |
|---|---|
| AI asks for a tool that doesn't exist | `Error: there is no tool called 'hack'. Available: ...` |
| arguments are broken JSON | `Error: the arguments were not valid JSON.` |
| wrong argument names | `Error: bad arguments for calculator: ...` |
| a bug inside the tool | `Error: calculator failed: ...` |

The AI **reads the error as the tool's result and can try again**. This is called *self-correction*.

**`ask()`**: the loop. Follow it with your finger:

1. Append the user message to memory.
2. `for step in range(1, max_steps + 1)`: repeat up to 6 times.
3. Call the AI with `system + messages + tools`.
4. Save its reply. If there are **no `tool_calls`** → it's the final answer → **return**.
5. Otherwise, for each requested tool: run it (or refuse a repeat), then append a `tool` message with the result.
6. Loop again.
7. If the loop ends without a final answer, return an apology (stopping condition 2).

**`compress_memory()`**: if the history is longer than `max_messages`, it **cuts at a `user` message** (so a tool request is never separated from its result,
which would make the API reject the history), asks the AI to summarise the old part in under 80 words, and keeps only the recent messages.

### Step 5 · Watch the safety limits work

Temporarily set `max_steps=2` in `main()` (`agent = Agent(max_steps=2)`) and ask the weather-and-Fahrenheit question again:

```text
Jarvis: Sorry, I stopped after 2 steps without finishing. Try a simpler request.
```

The agent needs three steps, so it was stopped. **This is the guard rail working.** Change it back to `6`.

## 6. What the frameworks do

You have now built, by hand, what *every* agent framework (LangChain, CrewAI, Hermes...) is made of:

| In your code | In a framework |
|---|---|
| `TOOL_SPECS` + `TOOL_FUNCTIONS` | "tools" or "skills" |
| the `for` loop in `ask()` | the "agent executor" / "agent loop" |
| `messages` + `summary` | "memory" |
| `max_steps` | "max iterations" |
| `run_tool` error handling | "tool error handling" |

Frameworks add **convenience** (more tools, scheduling, messaging, logging) but not magic. Because you understand the
loop, you can debug any of them.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| The agent loops until `max_steps` | tool results are unclear, or the system prompt doesn't say when to stop | return clear tool text; keep "reply in 1-3 sentences when you have enough" |
| `400 Bad Request ... tool` after a long chat | a `tool` message lost its matching request (bad trimming) | cut history only at `user` messages (we do this) |
| It guesses the weather instead of calling the tool | system prompt is weak, or the model is too small | "never guess ... use tools"; try a bigger model |
| It repeats the same call | the tool returned an error the AI didn't understand | make errors explicit and helpful |
| `notes.txt` appears in the wrong folder | files are saved relative to **where you run Python** | `cd` to the same folder every time |
| The agent costs too much | long history, many steps | smaller `max_steps`, `max_messages`, `max_tokens` |
| 🪟 `notes.txt` shows weird characters | not saved as UTF-8 | we already use `encoding="utf-8"`; open it in VS Code |
| The agent runs a tool you didn't expect | the description is too broad | narrow the descriptions; restrict arguments |

## Tasks

**Task 1 · Warm-up (15 min).** Ask the agent: *"What is 15% of 840, and what time is it?"* Count the steps. Then set
`max_steps=1` and ask again. What do you notice?

<details class="solution">
<summary>Answer</summary>

With the normal limit, the AI usually asks for **both tools in step 1** (they don't depend on each other), then answers in step 2.
With `max_steps=1`, the agent runs the tools but **never gets to write the answer**, so you see the "stopped after 1 steps" message.
Lesson: the *final answer* also needs a step.

</details>

**Task 2 · Build (30 min).** Add a tool `convert_currency(amount, from_currency, to_currency)` using **fixed** rates
(`USD=1, INR=83, EUR=0.92`). Register it in the three places (function, `TOOL_SPECS`, `TOOL_FUNCTIONS`) and ask:
*"How many rupees is 25 dollars?"*

<details class="solution">
<summary>Answer</summary>

```python
RATES = {"USD": 1.0, "INR": 83.0, "EUR": 0.92}      # how many of each per 1 US dollar

def convert_currency(amount, from_currency, to_currency):
    """Convert money using fixed rates (a demo, not live prices)."""
    f, t = from_currency.upper(), to_currency.upper()
    if f not in RATES or t not in RATES:
        return f"Error: I know these currencies: {', '.join(RATES)}"
    return f"{amount} {f} = {round(amount / RATES[f] * RATES[t], 2)} {t}"
```

```python
# TOOL_SPECS
    {"type": "function", "function": {
        "name": "convert_currency",
        "description": "Convert money between USD, INR and EUR using fixed demo rates.",
        "parameters": {"type": "object",
                       "properties": {"amount": {"type": "number"},
                                      "from_currency": {"type": "string", "description": "USD, INR or EUR"},
                                      "to_currency": {"type": "string", "description": "USD, INR or EUR"}},
                       "required": ["amount", "from_currency", "to_currency"]}}},
```

```python
# TOOL_FUNCTIONS
    "convert_currency": convert_currency,
```

`25 USD → INR` prints `25 USD = 2075.0 INR`.

</details>

**Task 3 · Challenge (45 min).** Add **human approval**: before `save_note` runs, the agent should ask you
`Allow saving: '<text>'? (y/n)` and only save if you type `y`. If you say `n`, the tool result should be `"The user said no."`
(This idea, *human in the loop*, is a key safety technique.)

<details class="solution">
<summary>Answer</summary>

In `agent.py`, inside `run_tool`, just after the `function is None` check, add:

```python
        NEEDS_APPROVAL = {"save_note"}
        if name in NEEDS_APPROVAL:
            try:
                shown = json.loads(raw_arguments or "{}")
            except json.JSONDecodeError:
                shown = {}
            answer = input(f"\n  ⚠ Allow {name} with {shown}? (y/n) ").strip().lower()
            if answer != "y":
                return "The user said no."
```

Now the agent can *ask* to save, but **you** stay in control. Use the same trick for any tool that changes something real
(sending email, deleting files, paying money).

</details>

## Quiz

Take **"Session 5 · Quiz"** from the portal's **Quizzes** page (agent loop, memory types, stopping conditions, error handling).

## Recap

- ✅ An **agent** = **Think → Act → Observe**, in a loop, until it can answer.
- ✅ The four parts: **brain** (LLM), **tools**, **memory**, **loop + limits**.
- ✅ **Memory**: short-term (recent messages), summary (compressed old chat), notes (file).
- ✅ **Safety**: `max_steps`, no repeats, and `run_tool` that never crashes and returns errors as text.
- ✅ Frameworks add convenience, not magic, and you now understand what's inside them.

**Next:** [Session 6 · Meet Hermes Agent](06-meet-hermes.md). We install a production-grade agent and compare it with the one you just built.

## Session materials

- {download}`llm.py <../code/05-build-an-agent/llm.py>`
- {download}`tools.py <../code/05-build-an-agent/tools.py>`
- {download}`agent.py <../code/05-build-an-agent/agent.py>`

:::{tip}
**Day 1 homework** (in Session 6): install Hermes, and download the Laya files, so Day 2 starts smoothly.
:::
