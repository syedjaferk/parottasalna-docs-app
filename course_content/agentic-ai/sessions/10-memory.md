# Session 10 · Memory for Agents

## The big idea

Here's a surprise: **AI models remember nothing.** Every call starts completely fresh. A chatbot
"remembers" what you said only because the app **sends the earlier messages again** with every new
question.

**Everyday example:** a doctor who loses their memory every night. To continue your treatment, you
bring your file to every visit. The doctor reads the file, then helps you. **Memory** is all about
managing that file: how big it gets, what to keep and what to throw away.

```{raw} html
:file: ../diagrams/s10-stateless.html
```

The list keeps growing, and longer lists cost more money and eventually hit the model's size limit.
This session shows six ways to manage it:

| # | Type | In simple words | Downside |
|---|---|---|---|
| 1 | **Buffer** | keep every message | grows forever |
| 2 | **Window** | keep the first message + the last few | forgets the middle |
| 3 | **Token budget** | keep the newest messages that fit a size limit | still forgets old things |
| 4 | **Summary** | replace old messages with a short summary | costs an extra AI call |
| 5 | **Long-term** | save important facts in a separate store | the agent must decide what to save |
| 6 | **Semantic** | long-term facts, searched by meaning | needs an embedding model |

All examples share one model, from `model.py`:

```python
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)
```

## 1. Buffer memory: keep everything

```python
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(
    model=llm,
    tools=[],
    system_prompt="You are a helpful assistant.",
    checkpointer=InMemorySaver(),        # ← this is the "patient file" cabinet
)

config = {"configurable": {"thread_id": "user-1"}}    # ← which file to use

agent.invoke({"messages": [{"role": "user", "content": "Hi, I'm Jafer from Coimbatore."}]}, config)
result = agent.invoke({"messages": [{"role": "user", "content": "Where am I from?"}]}, config)
print(result["messages"][-1].content)
```

**Output:**

```text
You're from Coimbatore.
```

- A **checkpointer** saves the conversation after every turn.
- A **thread_id** is the name of one conversation, like a file number. Same thread_id = same
  conversation. A new thread_id = a brand-new, empty conversation:

```python
agent.invoke({"messages": [{"role": "user", "content": "Where am I from?"}]},
             {"configurable": {"thread_id": "user-2"}})
# → "I don't know where you're from. Could you tell me?"
```

**Remembering after a restart:** `InMemorySaver` forgets everything when the program stops. Swap
in `SqliteSaver` (saves to a file) and memory survives restarts:

```python
from langgraph.checkpoint.sqlite import SqliteSaver   # pip install langgraph-checkpoint-sqlite

with SqliteSaver.from_conn_string("memory.db") as checkpointer:
    app = create_agent(model=llm, tools=[], checkpointer=checkpointer)
```

## Trimming the history

Types 2–4 use **middleware**: a small function that runs **right before every AI call** and can
edit the message list. Think of a receptionist who tidies the patient file before handing it to the
doctor.

```{raw} html
:file: ../diagrams/s10-trim.html
```

## 2. Window memory: first message + the last 4

```python
from langchain.agents.middleware import before_model
from langchain.messages import RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES

@before_model                                  # run this before every AI call
def keep_last_messages(state, runtime):
    messages = state["messages"]
    if len(messages) <= 4:
        return None                            # short enough: change nothing
    first = messages[0]                        # always keep the first message
    recent = messages[-4:]                     # and the last 4
    return {"messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES), first, *recent]}
```

`RemoveMessage(id=REMOVE_ALL_MESSAGES)` means "empty the file", and the messages after it are put
back in.

**Example conversation:**

```text
You: My name is Jafer.                ← first message, always kept
You: I live in Coimbatore.            ← falls out of the window later
You: I make backend and AI videos.
You: My favourite drink is Inji Tea.
You: What is my name?                 → "Your name is Jafer." ✅
You: Where do I live?                 → "I don't know." ❌ (that message was dropped)
```

## 3. Token budget: keep what fits

Counting messages is rough: one message might be 5 words, another 500. What really matters, for
cost and for the model's limit, is **tokens** (pieces of words, roughly ¾ of a word each).

```python
from langchain_core.messages.utils import count_tokens_approximately, trim_messages

@before_model
def trim_to_budget(state, runtime):
    trimmed = trim_messages(
        state["messages"],
        strategy="last",                            # keep the newest
        token_counter=count_tokens_approximately,
        max_tokens=1024,                            # the budget
        start_on="human",                           # never start in the middle of an exchange
    )
    return {"messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES), *trimmed]}
```

## 4. Summary memory: shrink, don't delete

Window and token memory **forget**. Summary memory **compresses** old messages into a short note,
so the facts survive:

```python
from langchain.agents.middleware import SummarizationMiddleware

agent = create_agent(
    model=llm,
    tools=[],
    middleware=[SummarizationMiddleware(
        model=llm,
        trigger=("tokens", 200),     # when history gets bigger than this, summarise (use 1,500+ in real apps)
        keep=("messages", 4),        # keep the last 4 messages word for word
    )],
    checkpointer=InMemorySaver(),
)
```

**Example:** in a long chat planning a Kerala trip, the early message *"Budget is ₹40,000 for 5
days"* gets folded into a summary like *"User is planning a 5-day Kerala trip in December with two
friends, budget ₹40,000, likes backwaters, dislikes crowded beaches."* Later, *"What was my budget?"*
still gets **₹40,000**. ✅

:::{tip}
Summarising is an easy job. Use a smaller, cheaper model for it than for the main agent.
:::

## 5. Long-term memory: facts that last forever

A checkpointer remembers **one conversation**. But a personal assistant should remember that you
like chess **next week, in a new chat**. That needs a **Store**: a separate place for facts about the
user, shared by all their conversations.

```{raw} html
:file: ../diagrams/s10-threads-store.html
```

We give the agent two tools and let it decide when to use them:

```python
@tool
def save_memory(fact: str, runtime: ToolRuntime[Context]) -> str:
    """Save a lasting fact about the user (preferences, name, goals)."""
    folder = ("memories", runtime.context.user_id)          # one folder per user
    runtime.store.put(folder, str(uuid.uuid4()), {"fact": fact})
    return f"Saved: {fact}"

@tool
def list_memories(runtime: ToolRuntime[Context]) -> str:
    """Retrieve everything known about the user."""
    items = runtime.store.search(("memories", runtime.context.user_id))
    return "\n".join(i.value["fact"] for i in items) or "No memories yet."
```

**What happens:**

```text
Chat 1 (Jafer):  "I like chess, badminton, cricket and football."
                  → agent calls save_memory(...)   ✅ saved

Chat 2 (Jafer, brand-new chat): "Suggest a game to play."
                  → agent calls list_memories → "How about a quick game of chess?" ✅

Chat 3 (Priya):  "Suggest a game to play."
                  → her folder is empty → a general suggestion
```

:::{note}
`user_id` comes from your app (`context=Context(user_id="Jafer")`), **not** from the AI. So the AI
can't be tricked into reading another user's memories.
:::

## 6. Semantic memory: search by meaning

With hundreds of saved facts, listing all of them is wasteful. **Semantic memory** finds only the
facts that **mean** something related to the question, using embeddings (the "meaning map" from
[Session 7](07-rag.md)):

```python
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
store = InMemoryStore(index={"embed": embeddings, "dims": 384})   # 384 = this model's size

hits = store.search(("memories", "arun"), query="what food should I avoid?", limit=3)
```

**Example:**

```text
Saved facts:  "I'm allergic to peanuts." · "I love hiking in the Western Ghats." ·
              "I play cricket on weekends." · "My favourite colour is teal."

Question:     "Any snack ideas for my trek?"
Found:        "I'm allergic to peanuts."   ← no shared words, but related meaning!
Answer:       "Try banana chips, dates or roasted chana. Avoid peanut bars because of your allergy."
```

## Which memory should I use?

| Situation | Use |
|---|---|
| short chats | buffer, saved with a persistent checkpointer |
| long chats | token budget or summary |
| "remember me next week" | long-term memory |
| lots of facts about the user | semantic memory |

Real apps often combine them, for example summary memory inside a chat plus semantic memory across chats.

## Try it yourself

1. Turn on `persistent_demo()` in `1.buffer_memory.py`. Run it twice. Does the second run remember Bruno?
2. In window memory, change `messages[-4:]` to `messages[-2:]`. Which questions stop working?
3. Add a `delete_memory` tool so a user can say "forget that".
4. Save ten different facts in semantic memory and test which ones different questions find.

## Full source

<details class="source"><summary>model.py</summary>

```{literalinclude} ../code/10-memory/model.py
:language: python
```

</details>

<details class="source"><summary>1.buffer_memory.py</summary>

```{literalinclude} ../code/10-memory/1.buffer_memory.py
:language: python
```

</details>

<details class="source"><summary>2.window_memory.py</summary>

```{literalinclude} ../code/10-memory/2.window_memory.py
:language: python
```

</details>

<details class="source"><summary>3.token_memory.py</summary>

```{literalinclude} ../code/10-memory/3.token_memory.py
:language: python
```

</details>

<details class="source"><summary>4.summary_memory.py</summary>

```{literalinclude} ../code/10-memory/4.summary_memory.py
:language: python
```

</details>

<details class="source"><summary>5.long_term.py</summary>

```{literalinclude} ../code/10-memory/5.long_term.py
:language: python
```

</details>

<details class="source"><summary>6.semantic_memory.py</summary>

```{literalinclude} ../code/10-memory/6.semantic_memory.py
:language: python
```

</details>

{download}`Whiteboard: LangChain memory types (open at excalidraw.com) <../code/10-memory/memory-types-whiteboard.excalidraw>`
