# Session 1 · Talking to an LLM

## The big idea

A large language model (LLM) is a program that **continues text**. You send it a conversation; it
writes the next message. **How you ask** decides how good the answer is, and that skill is called
*prompt engineering*.

**Everyday example:** asking a new colleague "can you look at this?" gets a shrug. "Can you check
this SQL query for slow joins? It runs on 5 million rows on PostgreSQL 14" gets real help.

In class we asked the same question every time, *"Find the sum of all even numbers between 1 and
50"* (the answer is **650**), and changed only the prompt.

## Step 0 · Calling any web API

Before AI, a plain API call (`0.basics.py`): send a request, get JSON back.

```python
response = requests.get("https://jsonplaceholder.typicode.com/todos")
data = response.json()
print(len(data))      # 200
print(data[0])        # {'userId': 1, 'id': 1, 'title': 'delectus aut autem', 'completed': False}
```

Talking to an LLM is exactly the same idea, just a `POST` with your conversation inside.

## Step 1 · A chat request to Groq

From `1.general_prompting.py`:

```python
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "openai/gpt-oss-120b"

headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
payload = {"model": MODEL, "messages": messages, "temperature": temperature}
response = requests.post(GROQ_URL, headers=headers, json=payload)
answer = response.json()["choices"][0]["message"]["content"]
```

The **messages** list is the conversation. Each message has a **role**:

| Role | Written by | Used for |
|---|---|---|
| `system` | you, the developer | the rules: who the model is, how to answer |
| `user` | the person asking | the question |
| `assistant` | the model | its earlier replies (or examples *you* write for it) |

**Temperature** controls randomness: `0` gives nearly the same answer every time (good for maths,
code, JSON); `0.7`–`1` gives more variety (good for ideas and writing).

## The six techniques from class

| Technique | What you add | Use it when |
|---|---|---|
| **Zero-shot** | nothing, just the question | simple, common tasks |
| **One-shot** | one worked example | you want a particular format |
| **Few-shot** | two or more examples | the format or method must be exact |
| **System prompt** | rules in the `system` message | you need strict output (e.g. JSON only) |
| **Role prompt** | "You are a …" | you want an expert's style or depth |
| **Contextual prompt** | facts the model should use | it needs information it doesn't have |

### Zero-shot

```python
messages = [
    {"role": "system", "content": "You are a helpful AI assistant."},
    {"role": "user", "content": "Give me sum of all even numbers between 1 and 50."},
]
```

You get a correct answer, but the length and format change from run to run.

### One-shot and few-shot: teach by example

You write a fake earlier conversation. The model copies its style (`3.few_shot_prompting.py`):

```python
messages = [
    {"role": "system", "content": "You are a mathematical assistant. Use the pairing method to find sums."},
    {"role": "user", "content": "Sum of even numbers 1-6?"},
    {"role": "assistant", "content": "Evens: 2, 4, 6. Calculation: 2+4+6 = 12."},
    {"role": "user", "content": "Sum of even numbers 1-12?"},
    {"role": "assistant", "content": "Evens: 2, 4, 6, 8, 10, 12. Pairs: (2+12)+(4+10)+(6+8) = 14*3 = 42."},
    {"role": "user", "content": query},   # the real question
]
```

Typical answer: *"Pairs: (2+50)+(4+48)+… = 52 × 12 + 26 = 650."* It used the pairing method
because the examples did.

### System prompt: strict rules

```python
{"role": "system", "content": "You are a logic engine. You only respond in JSON format. "
                              "Do not provide conversational filler. Key: 'result', Value: the final answer."}
```

Typical answer: `{"result": 650}`. Your program can now read it with `json.loads()`.

### Role prompt

```python
{"role": "system", "content": "You are a Senior Mathematics Professor who specializes in Arithmetic "
                              "Progressions. Explain the formula used before giving the answer."}
```

The answer now explains *n(n + 1)* with n = 25 → 25 × 26 = 650.

### Contextual prompt: give it the facts

```python
context = """
Context: The user is learning about Gaussian Summation.
The formula for the sum of the first 'n' even numbers is n(n + 1).
In the range 1-50, there are exactly 25 even numbers.
"""
messages = [
    {"role": "system", "content": "Use the provided context to answer the user's question accurately."},
    {"role": "user", "content": f"{context}\n\nQuestion: {query}"},
]
```

This is the seed of **RAG** (Sessions 3–12): instead of typing the context yourself, a program
finds it in your documents.

## Common mistakes

- **Hard-coding the API key in the script.** It ends up on GitHub. Read it from the environment:
  `os.environ["GROQ_API_KEY"]` (see [Setup](../setup.md)).
- **Not checking the status code.** A `401` (bad key) or `429` (rate limit) has no `choices`, so
  `response.json()["choices"]` crashes with a confusing `KeyError`. Check `response.status_code`
  first, as `1.general_prompting.py` does.
- **High temperature for exact answers.** Use `0` when there is one right answer.
- **Examples that disagree.** In few-shot prompts, the model copies your examples. If they use
  different formats, so will the answers.

## Try it yourself

1. Run `1.general_prompting.py` three times with `temperature=1`, then three times with `0`. How
   different are the answers?
2. Change the system prompt in `4.system_prompting.py` so the JSON also has a `"method"` key. Parse
   the answer with `json.loads()` and print only the number.
3. Write a few-shot prompt that classifies sentences as *positive*, *negative* or *neutral* (see
   `prompts-from-class.txt` for the sentences we used).
4. In `6.contextual_prompting.py`, give a **wrong** fact in the context (say, "there are 20 even
   numbers"). Does the model trust you or correct you?
5. Turn `call_groq()` into a small helper module and use it from two different scripts.

## Full source

<details class="source">
<summary>0.basics.py · a plain API call</summary>

```{literalinclude} ../code/01-prompt-engineering/0.basics.py
:language: python
```

</details>

<details class="source">
<summary>1.general_prompting.py · zero-shot</summary>

```{literalinclude} ../code/01-prompt-engineering/1.general_prompting.py
:language: python
```

</details>

<details class="source">
<summary>2.one_shot_prompting.py</summary>

```{literalinclude} ../code/01-prompt-engineering/2.one_shot_prompting.py
:language: python
```

</details>

<details class="source">
<summary>3.few_shot_prompting.py</summary>

```{literalinclude} ../code/01-prompt-engineering/3.few_shot_prompting.py
:language: python
```

</details>

<details class="source">
<summary>4.system_prompting.py</summary>

```{literalinclude} ../code/01-prompt-engineering/4.system_prompting.py
:language: python
```

</details>

<details class="source">
<summary>5.role_prompting.py</summary>

```{literalinclude} ../code/01-prompt-engineering/5.role_prompting.py
:language: python
```

</details>

<details class="source">
<summary>6.contextual_prompting.py</summary>

```{literalinclude} ../code/01-prompt-engineering/6.contextual_prompting.py
:language: python
```

</details>

**Downloads:**
{download}`0.basics.py <../code/01-prompt-engineering/0.basics.py>` ·
{download}`1.general_prompting.py <../code/01-prompt-engineering/1.general_prompting.py>` ·
{download}`2.one_shot_prompting.py <../code/01-prompt-engineering/2.one_shot_prompting.py>` ·
{download}`3.few_shot_prompting.py <../code/01-prompt-engineering/3.few_shot_prompting.py>` ·
{download}`4.system_prompting.py <../code/01-prompt-engineering/4.system_prompting.py>` ·
{download}`5.role_prompting.py <../code/01-prompt-engineering/5.role_prompting.py>` ·
{download}`6.contextual_prompting.py <../code/01-prompt-engineering/6.contextual_prompting.py>` ·
{download}`Prompts from class <../code/01-prompt-engineering/prompts-from-class.txt>`
