# Session 5 · Prompt Engineering

## The big idea

The same AI model can give you a vague answer or a brilliant one. The only thing that changes is
**how you ask**. Prompt engineering is the skill of asking well.

**Everyday example:** asking a new colleague for help. "Can you look at this?" gets you a shrug.
"Can you check this SQL query for slow joins? It runs on 5 million rows and must work on
PostgreSQL 14" gets you real help. AI models are the same.

In class we tried **9 techniques**. For each one there's a **BEFORE** prompt (a lazy question) and
an **AFTER** prompt (a well-designed one), sent to a real model so you can compare the answers.

## How the demo project is organised

```text
05-prompt-engineering/
├── groq_client.py        ← the one file that talks to the AI model
├── run_examples.py       ← runs the demos from the terminal
├── techniques/           ← one file per technique (BEFORE and AFTER prompts)
└── frameworks/           ← ready-made prompt templates to copy
```

Run it after setting up your `.env` (see [Setup](../setup.md)):

```bash
python run_examples.py                          # all 9 techniques
python run_examples.py --technique few_shot     # just one
```

## How a chat request looks

Talking to a chat model means sending it a **list of messages**. Each message has a **role**:

| Role | Who writes it | What it's for |
|---|---|---|
| `system` | you, the developer | the rules: "You are a friendly maths tutor." |
| `user` | the person asking | the question |
| `assistant` | the model | its earlier replies, so it knows the conversation so far |

```{raw} html
:file: ../diagrams/s05-messages.html
```

Under the hood it's just a web request with that list inside (from `groq_client.py`):

```python
payload = {"model": model, "messages": messages, "temperature": temperature}
response = requests.post(GROQ_URL, headers=headers, json=payload)
answer = response.json()["choices"][0]["message"]["content"]
```

### Prompt templates: fill in the blanks

Instead of copy-pasting prompts, we make **templates** with `{blanks}`, like a form:

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant."),
    ("human", "{question}"),          # {question} gets filled in later
])

run_prompt(prompt, {"question": "What is RAG?"})
```

`run_prompt()` (in `groq_client.py`) fills the blanks, turns the template into the message list
above, and sends it. Every technique below is just a different template.

## The 9 techniques at a glance

| Technique | In simple words | Use it when |
|---|---|---|
| 1. Zero-shot | ask clearly, with rules, no examples | simple, common tasks |
| 2. Few-shot | show examples first | you need an exact format |
| 3. Role-based | "act as a …" | you want an expert's style |
| 4. Contextual | give it the facts to use | it needs info it doesn't have |
| 5. Instruction-based | "reply only in this JSON shape" | your program will read the answer |
| 6. Chain-of-thought | "think step by step" | maths and logic |
| 7. Self-consistency | ask several times, take the majority | you want extra confidence |
| 8. Tree-of-thought | list options, judge them, pick the best | design decisions |
| 9. ReAct | think → use a tool → look at the result → repeat | it needs live data |

## 1. Zero-shot: be specific

No examples, just a much clearer request.

**BEFORE:** *"Explain what RAG is."* → a long, generic essay.

**AFTER:**

```text
You are a technical writer for junior developers who know Python but have never used LLMs.

Explain what RAG is.
- Exactly 3 short paragraphs.
- Paragraph 1: a one-sentence definition.
- Paragraph 2: what problem it solves.
- Paragraph 3: an everyday analogy.
- Define every acronym the first time you use it.
```

→ a short, structured answer at the right level. **Tell the model who it's writing for, how long,
and in what shape.**

## 2. Few-shot: teach by example

**Everyday example:** showing a new employee three filled-in forms before they fill in their own.

```{raw} html
:file: ../diagrams/s05-fewshot.html
```

In code, the examples are a list of dictionaries, and `FewShotChatMessagePromptTemplate` turns each
one into a little question-and-answer pair:

```python
EXAMPLES = [
    {"ticket": "My order arrived broken and the box was crushed.",
     "output": "Category: Shipping Damage | Reason: physical damage reported on arrival."},
    {"ticket": "I was charged twice for the same subscription this month.",
     "output": "Category: Billing | Reason: duplicate charge on subscription."},
    {"ticket": "The app crashes every time I try to upload a photo.",
     "output": "Category: Bug Report | Reason: reproducible crash on a specific action."},
]
```

**Result for** *"The screen flickers and sometimes the laptop won't turn on"*:

```text
Category: Hardware | Reason: display flicker and intermittent power failure.
```

Exactly the same format as the examples. ✅

:::{tip}
Pick examples that are **different from each other**. Three varied examples teach more than ten
similar ones, and every example costs tokens (money) on every call.
:::

## 3. Role-based: "act as …"

**Question:** *"Is it safe to store API keys in a .env file?"*

**BEFORE:** no role → a polite, balanced essay.

**AFTER:**

```text
You are a senior application security engineer doing a code review. You are terse,
risk-focused, and always state the severity (Low/Medium/High). You give concrete fixes.
```

→ *"Medium. Fine for local development. Never commit it: add `.env` to `.gitignore`. In production,
use a secrets manager."* Short, direct, practical.

## 4. Contextual: give it the facts

**Everyday example:** an open-book exam. Give the model the textbook page and tell it to use it.

```text
System: Use the provided context to answer. If the context gives a formula, you must use it.
User:   Context: The sum of the first n even numbers is n(n + 1). Between 1 and 50 there are 25 even numbers.
        Question: Find the sum of all even numbers between 1 and 50.
```

**Answer:** *25 × 26 = **650*** (using the formula you gave it).

This is the heart of RAG in [Session 7](07-rag.md): find the right "textbook page" automatically,
then prompt exactly like this.

## 5. Instruction-based: answers your program can read

People can read messy text. Programs can't. So we ask for **only JSON** in a fixed shape, then check
it:

```python
class ProjectFacts(BaseModel):          # the shape we want (Pydantic, see Session 9)
    name: str
    category: str
    release_year: int | None = None
    primary_language: str | None = None
```

**Input text:** *"LangChain is a framework for building LLM applications, released in 2022, written
primarily in Python, with over 90k GitHub stars."*

**Output, a checked Python object:**

```json
{"name": "LangChain", "category": "LLM application framework",
 "release_year": 2022, "primary_language": "Python", "popularity_signal": "90k+ GitHub stars"}
```

The code also strips the `` ```json `` fences that models often add even when told not to.
[Session 9](09-data-validation.md) shows a much easier way: `with_structured_output()`.

## 6. Chain-of-thought: "think step by step"

**Everyday example:** a maths teacher saying "show your working".

**Problem:** *A store had 42 notebooks. It sold 17 on Monday, received 25 on Tuesday, then sold 13
on Wednesday. How many are left?*

**BEFORE** ("answer with just the number") → sometimes a wrong number.

**AFTER** ("think step by step, then write `FINAL ANSWER: <number>`"):

```text
1. Start: 42
2. After Monday: 42 - 17 = 25
3. After Tuesday: 25 + 25 = 50
4. After Wednesday: 50 - 13 = 37
FINAL ANSWER: 37
```

The fixed `FINAL ANSWER:` line lets the code pull out the number reliably:

```python
re.search(r"FINAL ANSWER:\s*(-?\d+)", text).group(1)     # '37'
```

## 7. Self-consistency: ask several times, vote

Run the same step-by-step prompt **several times** with a slightly higher temperature (0.7), so the
model takes different paths. Then take the answer that comes up most often:

```text
Sample 1: 650
Sample 2: 650
Sample 3: 625   ← one path made a mistake
Consistent Answer: 650 (found in 2/3 paths)
```

It costs 3× the calls, so use it only when a wrong answer is expensive.

## 8. Tree-of-thought: explore options, pick the best

For open questions like *"How should I add an API Gateway to my microservices?"*, one quick answer
just grabs the first idea. Tree-of-thought uses **three steps** (three separate model calls):

```{raw} html
:file: ../diagrams/s05-tot.html
```

## 9. ReAct: think, act, observe

The model can't know today's weather by itself. **ReAct** (Reason + Act) lets it ask for a
**tool**, see the result, and continue:

```{raw} html
:file: ../diagrams/s05-react.html
```

The system prompt teaches the model this format, and a Python loop does the rest. It reads the
model's text, finds `Action: get_weather[Chennai]`, runs the real function, and sends back
`Observation: 32°C and Sunny`.

:::{warning}
**Why we won't write ReAct by hand again.** This loop reads the model's text with simple string
cutting, which is fragile:

- the model might **invent** its own `Observation:` before your tool runs
- one missing bracket or extra word breaks the parsing
- the class version even throws the final answer away (it returns `"Agent finished loop."`)

[Session 6](06-tool-calling.md) uses **native tool calling** instead, where the AI service sends
back a clean, structured request. No string cutting needed.
:::

## Prompt frameworks: checklists for good prompts

A framework is a checklist so you don't forget an important part of the prompt.

**CRISP: for a clear instruction**

```text
Context:     I run a backend engineering blog for beginners.
Role:        You are a senior backend engineer and technical writer.
Instruction: Write a detailed blog on Redis Pub/Sub with Python examples.
Style:       Simple English, real-world analogies, diagrams, code examples.
Purpose:     Help beginners understand Redis Pub/Sub practically.
```

**RICE: to control the output.** Give the **R**ole ("PostgreSQL performance expert"), the
**I**nput (the slow query, its `EXPLAIN ANALYZE` output and the table structure), the
**C**onstraints ("don't change the schema much, keep PostgreSQL 14") and your **E**xpectations
("bottleneck analysis, index suggestions, an optimised query").

**Step-by-step, for real-life decisions:** *"I'm planning a 3-day trip to Sri Lanka from Chennai.
Budget ₹15,000. Think step by step about: 1. travel, 2. hotel, 3. food, 4. places, 5. final budget."*

**Tree-of-thought, for comparing options:** *"Compare Backend, DevOps, Data and AI Engineering by
learning curve, salary, demand and time to a job, then recommend one for someone from a non-CS
background."*

| Framework | Use it to |
|---|---|
| CoT | think step by step |
| ReAct | think and act repeatedly (tools) |
| ToT | explore many options before choosing |
| CRISP | give a well-structured instruction |
| RICE | tightly control the output |

All the framework prompts from class are in the downloads at the bottom of this page. Paste them
into any chat model and adapt them.

## Try it yourself

1. Write a few-shot prompt that turns a product review into
   `Sentiment: positive/negative/mixed | About: <what it's about>`. Test it on three reviews.
2. Take a prompt you used recently and rewrite it with CRISP. Compare the answers.
3. Fix the ReAct loop so it returns the model's final answer.

   <details class="solution">
   <summary>Answer</summary>

   In the `else:` branch, replace `return "\nAgent finished loop."` with:

   ```python
   return ai_text.split("Final Answer:")[-1].strip()
   ```

   </details>

4. Run `self_consistency.py` with temperature 0, then 0.9. How many different answers do you get?

## Full source

<details class="source">
<summary>groq_client.py</summary>

```{literalinclude} ../code/05-prompt-engineering/groq_client.py
:language: python
```

</details>

<details class="source">
<summary>run_examples.py</summary>

```{literalinclude} ../code/05-prompt-engineering/run_examples.py
:language: python
```

</details>

<details class="source">
<summary>techniques/zero_shot.py</summary>

```{literalinclude} ../code/05-prompt-engineering/techniques/zero_shot.py
:language: python
```

</details>

<details class="source">
<summary>techniques/few_shot.py</summary>

```{literalinclude} ../code/05-prompt-engineering/techniques/few_shot.py
:language: python
```

</details>

<details class="source">
<summary>techniques/role_based.py</summary>

```{literalinclude} ../code/05-prompt-engineering/techniques/role_based.py
:language: python
```

</details>

<details class="source">
<summary>techniques/contextual_prompting.py</summary>

```{literalinclude} ../code/05-prompt-engineering/techniques/contextual_prompting.py
:language: python
```

</details>

<details class="source">
<summary>techniques/instruction_based.py</summary>

```{literalinclude} ../code/05-prompt-engineering/techniques/instruction_based.py
:language: python
```

</details>

<details class="source">
<summary>techniques/chain_of_thought.py</summary>

```{literalinclude} ../code/05-prompt-engineering/techniques/chain_of_thought.py
:language: python
```

</details>

<details class="source">
<summary>techniques/self_consistency.py</summary>

```{literalinclude} ../code/05-prompt-engineering/techniques/self_consistency.py
:language: python
```

</details>

<details class="source">
<summary>techniques/tree_of_thought.py</summary>

```{literalinclude} ../code/05-prompt-engineering/techniques/tree_of_thought.py
:language: python
```

</details>

<details class="source">
<summary>techniques/react.py</summary>

```{literalinclude} ../code/05-prompt-engineering/techniques/react.py
:language: python
```

</details>

<details class="source">
<summary>techniques/__init__.py</summary>

```{literalinclude} ../code/05-prompt-engineering/techniques/__init__.py
:language: python
```

</details>

**Downloads:**
{download}`groq_client.py <../code/05-prompt-engineering/groq_client.py>` ·
{download}`run_examples.py <../code/05-prompt-engineering/run_examples.py>` ·
{download}`.env example <../code/05-prompt-engineering/env.example>` ·
{download}`All prompt examples from class <../code/05-prompt-engineering/examples.txt>` ·
{download}`CRISP <../code/05-prompt-engineering/frameworks/crisp.txt>` ·
{download}`RICE <../code/05-prompt-engineering/frameworks/rice.txt>` ·
{download}`Step-by-step examples <../code/05-prompt-engineering/frameworks/step-by-step-examples.txt>` ·
{download}`ReAct <../code/05-prompt-engineering/frameworks/react_prompt.txt>` ·
{download}`Tree of thought <../code/05-prompt-engineering/frameworks/tot.txt>` ·
{download}`When to use which <../code/05-prompt-engineering/frameworks/when-to-use-which.txt>`
