# Session 2 · Prompts that make the model think

## The big idea

Some questions need **steps**, not a quick reply. These techniques make the model show its work,
check itself, explore options, or even **act** (call a tool) before it answers.

**Everyday example:** a maths teacher says "show your working". Students who write each step make
fewer mistakes, and you can see *where* a wrong answer went wrong.

| Technique | In one line | Cost |
|---|---|---|
| **Chain of thought (CoT)** | think step by step | 1 call |
| **Self-consistency** | ask several times, take the majority answer | N calls |
| **Tree of thought (ToT)** | propose options → judge them → follow the best | 3+ calls |
| **ReAct** | Thought → Action (use a tool) → Observation → repeat | 1 call per step |

## Chain of thought

Show one worked example with numbered steps, and ask for the same (`7.chain_of_thought.py`):

```python
{"role": "system", "content": "You are a logical reasoning engine. For every problem, "
                              "show your work step-by-step before providing the final answer."},
{"role": "user", "content": "Find the sum of all even numbers between 1 and 10."},
{"role": "assistant", "content": """Step 1: Identify the even numbers in the range [1, 10]. They are 2, 4, 6, 8, 10.
Step 2: Group them into pairs for easier addition: (2 + 10) = 12, (4 + 8) = 12, and the middle number 6.
Step 3: Add the pairs and the remaining number: 12 + 12 + 6 = 30.
Final Answer: 30."""},
{"role": "user", "content": query},
```

The model answers the real question with the same Step 1, 2, 3 layout and ends with
`Final Answer: 650.`

## Self-consistency: vote on the answer

One reasoning path can go wrong. Ask **5 times** with some randomness (`temperature=0.7`), pull out
each final number, and keep the most common one (`8.self_consistency.py`):

```python
match = re.search(r"Final Answer:\s*(\d+)", content)      # pull the number out
...
vote_count = Counter(results)
final_answer, count = vote_count.most_common(1)[0]
```

Typical output:

```text
Generating 5 reasoning paths...
 Sample 1: 650
 Sample 2: 650
 Sample 3: 650
 Sample 4: 650
 Sample 5: 650

Consistent Answer: 650 (Found in 5/5 paths)
```

```{raw} html
:file: ../diagrams/s02-self-consistency.html
```

If the answers disagree (say 3 × 650 and 2 × 625), the vote still picks the likely right one.

## Tree of thought: explore, judge, then solve

Three separate calls (`9.tree_of_thought.py`), on a harder question: *the sum of the cubes of 1 to
50*.

```text
1. PROPOSE   "Give 3 distinct possible first steps. Label them Step 1A, 1B, 1C."
2. EVALUATE  "Here are 3 paths … which one is most robust? Reply with the label."
3. SOLVE     "Based on this winning strategy: Step 1B … complete the calculation."
```

The script pauses with `input()` between steps so you can read each prompt. Press **Enter** to go
on. (The answer is (50 × 51 / 2)² = **1,625,625**.)

## ReAct: reason and act

The model can't check today's weather; it needs a **tool**. ReAct is a prompt format where the
model writes what it wants to do, and **your code** does it (`10.ReAct.py`):

```text
Thought: I need the current weather in Chennai.
Action: get_weather[Chennai]
```

Your loop spots `Action:`, runs the real function, and sends the result back:

```python
if "Action:" in ai_text:
    tool_call = ai_text.split("Action:")[1].strip()        # get_weather[Chennai]
    tool_name = tool_call.split("[")[0]                    # get_weather
    arg = tool_call.split("[")[1].split("]")[0]            # Chennai
    obs = get_weather(arg)                                 # "32°C and Sunny"
    messages.append({"role": "assistant", "content": ai_text})
    messages.append({"role": "user", "content": f"Observation: {obs}"})
```

```{raw} html
:file: ../diagrams/s02-react.html
```

Next round the model writes `Final Answer: It's 32°C and sunny in Chennai.` This loop of
**think → act → observe** is exactly what agents do. In [Session 16](16-tools-and-mcp.md) we let a
library run the loop with proper tool calling instead of text parsing.

## Prompt frameworks

Templates for writing a good prompt quickly. Fill in each part:

| Framework | Parts | Good for |
|---|---|---|
| **CRISP** | Context, Role, Instruction, Style, Purpose | writing: blogs, emails, designs |
| **RICE** | Role, Input, Constraints, Expectations | technical work with limits (e.g. "keep PostgreSQL 14") |
| **CoT** | "think step by step and show your reasoning" | planning, maths, trade-offs |
| **ToT** | "explore these options, compare them on …" | big decisions with several paths |
| **ReAct** | Thought / Action / Observation | research and tool use |

The full examples from class (a Redis blog, SQL tuning, a trip plan, a career switch) are in the
downloads below.

## Common mistakes

- **Using CoT for everything.** Step-by-step answers are longer, slower and cost more tokens. Use
  it when the task really has steps.
- **Self-consistency with `temperature=0`.** Every sample is the same, so the vote means nothing.
- **Trusting the parser.** In ReAct, the model might write `Action: get_weather(Chennai)` with round
  brackets and the `split("[")` crashes. Always cap the loop (the class code stops after 3 rounds)
  and handle "unknown tool" or bad formats.
- **Letting the model write the Observation.** Sometimes it invents `Observation: 30°C` itself.
  Tell it to stop after `Action:`, or use real tool calling (Session 16).

## Hands-on exercises

Try each one before opening the solution.

**Exercise 1 · CoT without the example.** Remove the worked example from `7.chain_of_thought.py` and
keep only the system prompt. Is the format the same?

<details class="solution"><summary>What to notice</summary>

The model still reasons step by step (the system prompt asks for it), but the layout varies: no
reliable "Step 1/2/3" or "Final Answer:" line. The example is what fixes the **format**, which
matters if your code reads the answer.

</details>

**Exercise 2 · A harder vote.** In `8.self_consistency.py`, set `num_samples=9` and ask *"How many
times does the digit 7 appear in the numbers from 1 to 100?"*

<details class="solution"><summary>Answer</summary>

The right answer is **20** (7, 17, …, 97 is ten; 70–79 is ten more, and 77 counts twice). Single
samples sometimes say 19; the majority vote usually lands on 20, which is exactly why
self-consistency exists.

</details>

**Exercise 3 · Self-consistency needs randomness.** Run `8.self_consistency.py` with
`temperature=0`. What happens to the vote?

<details class="solution"><summary>Answer</summary>

All samples are (nearly) identical, so you pay 5× for one answer. Self-consistency only helps when
each path can reason differently, which needs a temperature around 0.5–0.8.

</details>

**Exercise 4 · A second tool for ReAct.** Add `get_time[city]` to `10.ReAct.py` and ask *"What's the
weather and time in London?"*

<details class="solution"><summary>Solution</summary>

```python
def get_time(city):
    return {"London": "10:30 AM", "Chennai": "3:00 PM"}.get(city, "Time not found.")

TOOLS = {"get_weather": get_weather, "get_time": get_time}
```

Add `- get_time[city]: Returns the current time.` to the system prompt, then run the tool with
`obs = TOOLS[tool_name](arg) if tool_name in TOOLS else "Unknown tool."`. Raise the loop limit to 4,
because the model now needs two actions.

</details>

**Exercise 5 · A sturdier parser.** Make the ReAct parser accept both `get_weather[Chennai]` and
`get_weather(Chennai)`.

<details class="solution"><summary>Solution</summary>

```python
import re

match = re.search(r"Action:\s*(\w+)\s*[\[(]\s*([^\])]+?)\s*[\])]", ai_text)
if match:
    tool_name, arg = match.group(1), match.group(2)
```

If there's no match, send back `Observation: invalid action format, use tool[argument]` instead of
crashing.

</details>

**Exercise 6 · Write a RICE prompt.** Use RICE for a task from your work (for example: *speed up a slow
Django page*). Compare the answer with a one-line prompt.

<details class="solution"><summary>Example</summary>

```text
ROLE: You are a senior Django performance engineer.
INPUT: A list page with 200 orders takes 4 seconds. It runs 600 SQL queries.
CONSTRAINTS: Django 5, PostgreSQL 16, no schema changes, no new services.
EXPECTATIONS: 1) likely cause 2) the exact ORM fix with code 3) how to verify with numbers.
```

The structured prompt usually names the N+1 problem and `select_related`/`prefetch_related`
directly; the one-liner gives a generic checklist.

</details>

## Full source

<details class="source">
<summary>7.chain_of_thought.py</summary>

```{literalinclude} ../code/01-prompt-engineering/7.chain_of_thought.py
:language: python
```

</details>

<details class="source">
<summary>8.self_consistency.py</summary>

```{literalinclude} ../code/01-prompt-engineering/8.self_consistency.py
:language: python
```

</details>

<details class="source">
<summary>9.tree_of_thought.py</summary>

```{literalinclude} ../code/01-prompt-engineering/9.tree_of_thought.py
:language: python
```

</details>

<details class="source">
<summary>10.ReAct.py</summary>

```{literalinclude} ../code/01-prompt-engineering/10.ReAct.py
:language: python
```

</details>

**Downloads:**
{download}`7.chain_of_thought.py <../code/01-prompt-engineering/7.chain_of_thought.py>` ·
{download}`8.self_consistency.py <../code/01-prompt-engineering/8.self_consistency.py>` ·
{download}`9.tree_of_thought.py <../code/01-prompt-engineering/9.tree_of_thought.py>` ·
{download}`10.ReAct.py <../code/01-prompt-engineering/10.ReAct.py>` ·
{download}`CRISP <../code/01-prompt-engineering/frameworks/crisp.txt>` ·
{download}`RICE <../code/01-prompt-engineering/frameworks/rice.txt>` ·
{download}`Step-by-step trip plan <../code/01-prompt-engineering/frameworks/step-by-step-trip.txt>` ·
{download}`ReAct <../code/01-prompt-engineering/frameworks/react.txt>` ·
{download}`Tree of thought <../code/01-prompt-engineering/frameworks/tree-of-thought.txt>` ·
{download}`When to use which <../code/01-prompt-engineering/frameworks/when-to-use-which.txt>`
