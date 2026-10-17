# Session 12 · LCEL: Chains, Parallel Steps and Passthrough

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/KxQ14btMwIE"
  title="Episode 16: Sequential and Parallel Workflows (LCEL)?" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

## The big idea

So far we called the model one step at a time: build a prompt, call the model, pull the text out.
**LCEL** (LangChain Expression Language) lets you snap those steps together with the `|` pipe,
like stations on an assembly line, and then run the whole line with one call.

**Everyday example:** a parotta stall. One person rolls the dough, the next cooks it on the tawa,
the last one packs it. Each station takes what the previous one hands over. LCEL is the counter
that connects the stations, and it works the same whether you make one parotta, a batch of fifty,
or hand them out one by one as they come off the tawa.

:::{admonition} Under the hood
:class: hint
LCEL is a way of *composing* objects that all follow one interface, the **Runnable protocol**.
`a | b` doesn't run anything: it builds a new Runnable (a `RunnableSequence`) that, when invoked,
feeds `a`'s output into `b`. Because the result is itself a Runnable, you get `invoke`, `batch`,
`stream` and their async versions for free, on every chain you build.
:::

In this session:

1. **Everything is a Runnable**: why every piece has the same buttons
2. **The interface**: `invoke`, `batch`, `stream`, and the async versions
3. **Sequence**: steps one after another, and chains of chains
4. **Parallel**: several steps at the same time
5. **Passthrough**: carrying data forward, adding keys and picking keys

## 1. Everything is a Runnable

```{raw} html
:file: ../diagrams/s12-runnable.html
```

**In plain words:** the prompt, the model and the parser look different, but they all have the
same three buttons: *do one* (`invoke`), *do many* (`batch`) and *give it to me as it's ready*
(`stream`). Join them with `|` and the chain you get has the same buttons too.

```python
prompt = ChatPromptTemplate.from_template("Say hi to {name}")
parser = StrOutputParser()
chain = prompt | model | parser

for name, obj in [("prompt", prompt), ("model", model), ("parser", parser), ("chain", chain)]:
    print(f"{name:7} → is Runnable? {isinstance(obj, Runnable)}   type = {type(obj).__name__}")
```

```text
prompt  → is Runnable? True   type = ChatPromptTemplate
model   → is Runnable? True   type = ChatGroq
parser  → is Runnable? True   type = StrOutputParser
chain   → is Runnable? True   type = RunnableSequence
```

Press the same button on each piece and see what comes out:

```python
prompt.invoke({"name": "Jafer"})          # messages=[HumanMessage(content='Say hi to Jafer')]
model.invoke("Say hi").content            # 'Hi there! 👋 How can I help you today?'
parser.invoke("plain text stays text")    # 'plain text stays text'
chain.invoke({"name": "Jafer"})           # "Hi Jafer! 👋 Hope you're having a great day!"
```

:::{admonition} Under the hood
:class: hint
Every Runnable has an input type and an output type, and a chain only works when each step's output
fits the next step's input:

| Step | Input | Output |
|---|---|---|
| `ChatPromptTemplate` | `dict` of variables | `ChatPromptValue` (a list of messages) |
| `ChatGroq` (any chat model) | text, messages or a `PromptValue` | `AIMessage` |
| `StrOutputParser` | `AIMessage` (or text) | `str` |
| `prompt \| model \| parser` | `dict` | `str` |

The parser is why the chain returns plain text. Leave it out and you get the whole `AIMessage`,
with token counts and metadata attached.
:::

## 2. The interface: invoke, batch, stream

```{raw} html
:file: ../diagrams/s12-interface.html
```

| Button | What it does | Use it when |
|---|---|---|
| `invoke(x)` | one input, waits, one output | a single question |
| `batch([x1, x2, …])` | many inputs at the same time, a list of outputs | the same job for many items |
| `stream(x)` | yields the answer piece by piece | showing text as it's typed, like ChatGPT |
| `ainvoke`, `abatch`, `astream` | the same, with `await` | inside async code such as a web server |

```python
msg = model.invoke("What is a parotta? Answer in one line.")
print(msg.content)          # Parotta is a flaky, layered flatbread made from wheat flour, ...
print(msg.usage_metadata)   # {'input_tokens': 82, 'output_tokens': 69, 'total_tokens': 151,
                            #  'output_token_details': {'reasoning': 37}}

answers = model.batch(
    ["Capital of Tamil Nadu? One word.", "Capital of Karnataka? One word.", "Capital of Kerala? One word."],
    config={"max_concurrency": 3},
)
print([a.content for a in answers])   # ['Chennai', 'Bengaluru.', 'Thiruvananthapuram']

for chunk in model.stream("Count from 1 to 10 in words, comma separated."):
    print(chunk.content, end="", flush=True)   # one, two, three, ... appears word by word
```

The async versions look the same, with `await` ([Session 8](08-async.md)):

```python
m = await model.ainvoke("Say 'vanakkam' and its meaning in one line.")
rs = await model.abatch(["2+2? Number only.", "3+3? Number only."])   # ['4', '6']
async for chunk in model.astream("Name 3 South Indian breakfasts, comma separated."):
    print(chunk.content, end="")                                       # Idli, dosa, upma
```

:::{admonition} Under the hood
:class: hint
- **`batch`** runs the inputs on a thread pool. `config={"max_concurrency": 3}` caps how many run at
  once. Keep it low on a free API plan, or you'll hit rate limits.
- **`stream`** yields `AIMessageChunk`s. Chunks can be added together (`chunk1 + chunk2`) to rebuild
  the full message.
- **`usage_metadata`** counts tokens. This model (`gpt-oss-120b`) is a *reasoning* model: 37 of the 69
  output tokens were its hidden "thinking". Groq returns that text in
  `msg.additional_kwargs["reasoning_content"]`. You pay for those tokens too.
- `config` is a `RunnableConfig`. Besides `max_concurrency`, it carries `tags`, `metadata`, `callbacks`
  and `run_name`, and it is passed down to every step of a chain.
:::

## 3. Sequence: one step after another

```{raw} html
:file: ../diagrams/s12-sequence.html
```

**In plain words:** the pipe hands each step's result to the next step. You can even pipe one whole
chain into another, as long as what comes out of the first is what the second expects.

```python
prompt = ChatPromptTemplate.from_template("Give a 2-line recipe summary for {dish}.")

recipe_chain = prompt | model | parser                      # Way 1: the pipe (most common)
recipe_chain_explicit = RunnableSequence(prompt, model, parser)   # Way 2: exactly the same

print(type(recipe_chain).__name__)                          # RunnableSequence
print([type(s).__name__ for s in recipe_chain.steps])       # ['ChatPromptTemplate', 'ChatGroq', 'StrOutputParser']
print(recipe_chain.invoke({"dish": "Kothu Parotta"}))
# Kothu Parotta: Toss shredded parotta with sautéed onions, tomatoes, green chilies ...
```

**A chain of chains:** the recipe comes out as text, but the translate prompt wants a dict with a
`text` key. A tiny function in between reshapes it:

```python
translate_chain = ChatPromptTemplate.from_template("Translate to simple Tamil:\n{text}") | model | parser

recipe_in_tamil = (
    recipe_chain
    | (lambda text: {"text": text})      # reshape: str → {"text": str}
    | translate_chain
)
print(recipe_in_tamil.invoke({"dish": "Egg Parotta"}))
# எக் பரோட்டா: முட்டைகளை அடித்து, நறுக்கிய வெங்காயம், ...
```

And because the chain is a Runnable, `batch` just works:

```python
recipe_chain.batch([{"dish": "Idli"}, {"dish": "Pongal"}])   # two recipes, made at the same time
```

:::{admonition} Under the hood
:class: hint
- **Coercion:** inside a chain, a plain function is wrapped in a `RunnableLambda` automatically, and a
  plain `dict` becomes a `RunnableParallel` (next section). That's how `| (lambda text: …) |` works.
- **Shapes must match.** A prompt with *one* variable accepts plain text and wraps it for you
  (`{"text": "…"}`). With *two or more* variables it can't guess, and fails:
  `TypeError: Expected mapping type as input to ChatPromptTemplate. Received <class 'str'>.`
  Writing the reshape yourself, as above, works either way and is clearer to read.
- A `RunnableLambda` receives **one** argument: whatever the previous step returned.
:::

## 4. Parallel: several steps at the same time

```{raw} html
:file: ../diagrams/s12-parallel.html
```

**In plain words:** three cooks get the same order and work at the same time: one lists the pros,
one the cons, one gives a verdict. You wait only as long as the slowest cook, not for all three one
after another.

```python
p = ChatPromptTemplate.from_template
pros    = p("List 3 pros of {topic}. Short bullets only.") | model | parser
cons    = p("List 3 cons of {topic}. Short bullets only.") | model | parser
verdict = p("One-line verdict: should a beginner learn {topic}?") | model | parser

review = RunnableParallel(pros=pros, cons=cons, verdict=verdict)
out = review.invoke({"topic": "Kubernetes"})     # {'pros': '...', 'cons': '...', 'verdict': '...'}
```

```text
Parallel took 0.7s
== verdict ==
Yes—learn Docker first, then pick up Kubernetes once you're comfortable with container fundamentals.

Sequential took 1.5s
```

**The shortcut:** a plain dict at the start of a chain becomes a `RunnableParallel`, and its output
dict fills the next prompt's variables:

```python
summary_chain = (
    {"pros": pros, "cons": cons, "verdict": verdict}         # runs all three at once
    | p("Write a 4-line summary.\nPros:{pros}\nCons:{cons}\nVerdict:{verdict}")
    | model
    | parser
)
```

:::{admonition} Under the hood
:class: hint
- Every branch receives the **same input**. The output is a dict with **one key per branch**.
- `invoke` runs the branches on a thread pool; `ainvoke` runs them with `asyncio.gather`. Either way,
  total time ≈ the slowest branch (here 0.7 s, against 1.5 s one after another).
- A dict alone is just a dict. It becomes a `RunnableParallel` only when it's piped next to a Runnable
  (`{…} | prompt`), because the Runnable's `|` handles the conversion.
- Three branches means three API calls at once. Use `config={"max_concurrency": …}` if you hit rate limits.
:::

## 5. Passthrough: carry data forward, add keys, pick keys

Often a later step needs the **original input** as well as a new result. RAG is the classic case:
the final prompt needs both the retrieved *context* and the user's *question*.

```python
docs = {
    "timing": "Parottasalna is open 7 AM to 11 PM daily.",
    "location": "Parottasalna is near Anna Nagar bus depot, Chennai.",
}

def retrieve(question: str) -> str:      # a pretend retriever
    return docs["timing"] if "open" in question.lower() else docs["location"]

rag_prompt = ChatPromptTemplate.from_template(
    "Answer only from the context.\nContext: {context}\nQuestion: {question}")
```

**(a) `RunnablePassthrough()`: let the input through unchanged**

```python
rag_chain = (
    {"context": retrieve, "question": RunnablePassthrough()}   # both get the same question
    | rag_prompt | model | parser
)
rag_chain.invoke("What time do you open?")      # 'We open at 7 AM.'
```

**(b) `.assign()`: keep what you have, add more** and **(c) `.pick()`: keep only what you need**

```{raw} html
:file: ../diagrams/s12-passthrough.html
```

```python
step_by_step = (
    RunnablePassthrough.assign(context=lambda x: retrieve(x["question"]))
    | RunnablePassthrough.assign(answer=rag_prompt | model | parser)
)
result = step_by_step.invoke({"question": "Where are you located?"})
list(result.keys())   # ['question', 'context', 'answer']: nothing was lost on the way

step_by_step.pick("answer").invoke({"question": "What time do you open?"})
# 'We open at 7 AM.'
step_by_step.pick(["answer", "context"]).invoke({"question": "Where are you?"})
# {'answer': "I'm in Parottasalna, ... near the Anna Nagar bus depot in Chennai.",
#  'context': 'Parottasalna is near Anna Nagar bus depot, Chennai.'}
```

**(d) Start from plain text:** `.assign()` needs a dict, so first turn the text into one:

```python
both = RunnableParallel(question=RunnablePassthrough()).assign(
    context=lambda x: retrieve(x["question"]))
both.invoke("Are you open on Sunday?")
# {'question': 'Are you open on Sunday?', 'context': 'Parottasalna is open 7 AM to 11 PM daily.'}
```

:::{admonition} Under the hood
:class: hint
- `RunnablePassthrough()` is the identity function: output = input.
- `RunnablePassthrough.assign(k=r)` runs `r` on the **whole input dict** and returns the input plus a
  new key `k`. That's why the lambdas read `x["question"]`. Several keys in one `.assign()` run in parallel.
- `.assign()` on anything that isn't a dict fails with
  `ValueError: The input to RunnablePassthrough.assign() must be a dict.` Hence the trick in (d).
- `.pick()` works on the *output*: it keeps only the named keys (one key gives the value itself, a list
  gives a smaller dict). Return what the caller needs while keeping the extra keys for debugging.
:::

## Common mistakes

- **Forgetting the parser.** The chain returns an `AIMessage`, not text, and `.upper()` or JSON parsing fails.
  End with `| StrOutputParser()` (or a structured parser, [Session 9](09-data-validation.md)).
- **Text where a dict is expected.** A prompt with two or more variables needs a dict. Reshape with a lambda,
  or use `RunnablePassthrough` / `.assign()`.
- **A lambda with two parameters.** A step gets exactly one input. Take the dict and read keys from it.
- **Thinking `|` runs something.** It only *builds* the chain. Nothing happens until `invoke`, `batch` or `stream`.
- **Parallel without limits.** Ten branches means ten API calls at once. Free plans have rate limits, so set
  `max_concurrency`.
- **Expecting a lambda to stream.** A plain function step waits for its whole input before it runs, so
  streaming pauses there. Put lambdas before the model, not after it, if you want word-by-word output.

## Try it yourself

1. Build the chain from section 1 **without** the parser (`prompt | model`) and print `type()` of the result. What is it?
2. Extend `review` in section 4 with a fourth branch, `alternatives`, that suggests 2 simpler tools than
   Kubernetes. Did the total time change much?
3. Make `recipe_in_tamil` return **both** the English and the Tamil recipe, using `.assign()`.
4. Stream `summary_chain` from section 4. When do the first words appear: right away, or only after the
   three parallel branches finish? Why?

<details class="source"><summary>Answers</summary>

1. `AIMessage`. The text is in `.content`, the token counts in `.usage_metadata`.
2. Add `alternatives=p("Suggest 2 simpler alternatives to {topic}.") | model | parser` to `RunnableParallel(...)`.
   The time barely changes: it's still about the slowest branch.
3. ```python
   both = (RunnablePassthrough.assign(english=recipe_chain)
           | RunnablePassthrough.assign(tamil=lambda x: translate_chain.invoke({"text": x["english"]})))
   both.pick(["english", "tamil"]).invoke({"dish": "Egg Parotta"})
   ```
4. Only after the branches finish. The final prompt needs all three results (`{pros}`, `{cons}`, `{verdict}`),
   so the summary model can't start earlier. After that, its words stream one by one.

</details>

## Full source

<details class="source"><summary>model.py</summary>

```{literalinclude} ../code/12-lcel/model.py
:language: python
```

</details>

<details class="source"><summary>00_everything_is_runnable.py</summary>

```{literalinclude} ../code/12-lcel/00_everything_is_runnable.py
:language: python
```

</details>

<details class="source"><summary>03_interface.py</summary>

```{literalinclude} ../code/12-lcel/03_interface.py
:language: python
```

</details>

<details class="source"><summary>04_sequence.py</summary>

```{literalinclude} ../code/12-lcel/04_sequence.py
:language: python
```

</details>

<details class="source"><summary>05_parallel.py</summary>

```{literalinclude} ../code/12-lcel/05_parallel.py
:language: python
```

</details>

<details class="source"><summary>06_passthrough.py</summary>

```{literalinclude} ../code/12-lcel/06_passthrough.py
:language: python
```

</details>
