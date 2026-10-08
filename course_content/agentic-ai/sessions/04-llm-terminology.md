# Session 4 · LLMs and Key Terminology

## The big idea

When you type into ChatGPT or Claude, there's no magic and no person behind it. It's a program that
has read a huge amount of text and learned one skill extremely well: **guessing the next word**.
This session explains how that works, and the "dials" you can turn to change its answers.

**Everyday example:** your phone keyboard's word suggestions. Type "Good" and it suggests
"morning". An LLM is the same idea, but massively bigger and smarter.

## What is AI?

**AI (Artificial Intelligence)** is a program that learns patterns from examples, instead of a
person writing every rule by hand.

**Example:** your phone camera draws a box around faces. Nobody wrote "if there's a nose here and
two eyes there, it's a face". The program learned it by looking at millions of photos.

## What is an LLM?

**LLM = Large Language Model.** It's an AI that has read a gigantic amount of text: books,
websites, articles, code. From all that reading it learned how language works.

Its only job: **given some words, predict the next word.** Then the next. Then the next. That's how
it writes whole answers.

```{raw} html
:file: ../diagrams/s04-next-word.html
```

The model doesn't "look up" that Paris is the capital. It has seen this pattern so many times that
"Paris" is by far the most likely next word.

:::{note}
**Hallucination:** because the model *predicts* instead of *looking up*, it can write something
that sounds confident but is completely wrong. That's called a **hallucination**. Later sessions
show two fixes: give the model the real facts ([Session 7, RAG](07-rag.md)), and let it use real
tools ([Session 6](06-tool-calling.md)).
:::

## What is a prompt?

A **prompt** is what you send to the model: your question or instruction. Better prompts give
better answers.

| Prompt | What you get |
|---|---|
| *"Write about dogs."* | something long, generic and unfocused |
| *"Write a 3-line funny Instagram caption for a golden retriever who just had a bath and hates it."* | short, specific and usable ✅ |

[Session 5](05-prompt-engineering.md) is all about writing great prompts.

## What are parameters?

**Parameters** are the numbers inside the model that got adjusted while it learned. You can think
of them as tiny knobs in its "brain". There are **billions** of them.

| Model size | Example | In simple words |
|---|---|---|
| ~175 billion parameters | GPT-3 | a huge brain: very capable, needs big servers |
| ~7 billion ("7B") | Mistral 7B, Llama 3 8B | a small brain: runs on a laptop, less deep |

More parameters usually means smarter, but also slower and more expensive to run.

## Temperature: safe or creative?

**Temperature** controls how "adventurous" the model is when it picks the next word.

- **Low (like 0 or 0.2):** it almost always picks the most likely word. Predictable and safe.
- **High (like 1.0):** less likely words get a real chance. Creative, surprising, sometimes weird.

**Example:** *"Suggest a name for my coffee shop."*

```{raw} html
:file: ../diagrams/s04-temperature.html
```

| Use **low** temperature for | Use **high** temperature for |
|---|---|
| facts, maths, code | brainstorming names and ideas |
| answers your program will read (like JSON) | stories, poems, jokes |

**In code:** you set it when you create the model. The sessions use `temperature=0`, so answers are
the same every time you run them:

```python
from langchain_groq import ChatGroq

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)
```

## Top-k and top-p: limiting the choices

When choosing the next word, the model ranks **every** possible word. These two settings decide how
many of them it's allowed to pick from:

- **Top-k:** "only consider the top **k** words." A fixed number.
- **Top-p:** "keep adding the best words until their chances add up to **p** (like 90%)." The number
  of words changes depending on the situation.

```{raw} html
:file: ../diagrams/s04-topk-topp.html
```

**Menu example:**

- **Top-k = 5** → "only look at the first 5 dishes on the menu."
- **Top-p = 0.9** → "look at as many dishes as it takes to cover 90% of what people usually order."

:::{tip}
You'll mostly change **temperature**. If you also try top-p, change one at a time, otherwise you
won't know which one made the difference. Many hosted APIs (including Groq's) let you set
`temperature` and `top_p` but not `top_k`.
:::

## Local models: AI on your own computer

A **local model** is an LLM you download and run on your own laptop instead of calling a company's
server over the internet.

| 👍 Good | 👎 Not so good |
|---|---|
| your data never leaves your computer | needs a decent computer (RAM, ideally a GPU) |
| free to use, no subscription | smaller models aren't as smart as the big cloud ones |

**Popular local models:** Llama (Meta), Mistral, Gemma (Google), Phi (Microsoft), DeepSeek (great
at code). The easiest way to run them is **[Ollama](https://ollama.com)**:

```bash
ollama run llama3.2
```

**Example use:** a developer working on a client's private code uses a local coding model, so the
code never leaves their laptop.

## Putting it all together

You ask a local model to write a joke:

| Term | In this example |
|---|---|
| **LLM** | the model itself, e.g. Mistral 7B |
| **Prompt** | "Write a joke about Mondays." |
| **Parameters** | 7B: how big its "brain" is |
| **Temperature** | 0.9, to make the joke a bit wild |
| **Top-p** | 0.9, so it stays creative without picking nonsense words |

Turn these dials and the same model can be a serious report writer or a silly joke machine.

## Try it yourself

1. Low or high temperature? Explain why for each: summarising a legal contract; naming a startup;
   writing SQL from a question; writing a birthday poem.

   <details class="solution">
   <summary>Answer</summary>

   Low, high, low, high. Exact or checkable work needs low temperature; creative work benefits
   from high temperature.

   </details>

2. Explain top-k vs top-p to a friend in two sentences.
3. Install Ollama and run `ollama run llama3.2`. Ask the same question twice after typing
   `/set parameter temperature 0` and then `/set parameter temperature 1`. Compare the answers.
