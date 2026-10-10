# Session 15 · Agent memory

## The big idea

An LLM remembers **nothing** between calls. Every call starts from zero; "memory" is just the
earlier messages that **your code** sends again. The question is *what* to send: everything gets
slow and expensive, nothing makes the agent forgetful. This session covers six strategies, from
simple to smart.

**Everyday example:** a doctor's visit. **Short-term memory** is today's conversation. **Long-term
memory** is your file: allergies, history. A good doctor doesn't re-read every old visit, just the
summary and the relevant notes.

| # | Strategy | Keeps | Lives in |
|---|---|---|---|
| 1 | Buffer | the whole conversation | a checkpointer, per `thread_id` |
| 2 | Window | the first + last N messages | " |
| 3 | Token | the newest messages that fit a token budget | " |
| 4 | Summary | an LLM summary of old messages + recent ones word for word | " |
| 5 | Long-term | facts saved by the agent, across conversations | a Store, per user |
| 6 | Semantic | the same, found by meaning | a Store with embeddings |

All scripts share `model.py` (Groq via `ChatGroq`) and use LangChain 1.x's `create_agent`.

## 1 · Buffer memory: a checkpointer

```python
agent = create_agent(model=llm, tools=[], system_prompt="You are a helpful assistant.",
                     checkpointer=InMemorySaver())
config = {"configurable": {"thread_id": "user-1"}}

agent.invoke({"messages": [{"role": "user", "content": "Hi, I'm Jafer from Coimbatore."}]}, config)
agent.invoke({"messages": [{"role": "user", "content": "Where am I from?"}]}, config)      # Coimbatore
agent.invoke({"messages": [{"role": "user", "content": "Where am I from?"}]},
             {"configurable": {"thread_id": "user-2"}})                                    # no idea
```

The **checkpointer** saves each thread's messages. Same `thread_id` = same conversation. Swap
`InMemorySaver` for `SqliteSaver` (`pip install langgraph-checkpoint-sqlite`) and it survives a
restart (see `persistent_demo()` in `1.buffer_memory.py`).

## 2 · Window memory

A **middleware** runs before every model call and rewrites the history: keep the first message and
the last 4 (`2.window_memory.py`):

```python
@before_model
def keep_last_messages(state: AgentState, runtime: Runtime) -> dict | None:
    messages = state["messages"]
    if len(messages) <= 4:
        return None
    return {"messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES), messages[0], *messages[-4:]]}
```

After six turns, *"What is my name?"* still works (the first message is pinned), but *"Where do I
live?"* doesn't: that message fell out of the window.

## 3 · Token memory

Same idea, but the limit is **tokens**, which is what the model's context window and your bill are
measured in (`3.token_memory.py`):

```python
trimmed = trim_messages(state["messages"], strategy="last", max_tokens=1024,
                        token_counter=count_tokens_approximately,
                        start_on="human", end_on=("human", "tool"))
```

`start_on="human"` makes sure the kept history never starts halfway through an exchange. The
script floods the chat with filler until *"my favourite language is Go"* is trimmed away.

## 4 · Summary memory

Instead of deleting old messages, **summarise** them (`4.summary_memory.py`):

```python
SummarizationMiddleware(
    model=ChatGroq(model="openai/gpt-oss-120b", temperature=0),
    trigger=("tokens", 200),       # summarise once history passes this (use ~1500+ in real apps)
    keep=("messages", 4),          # the last 4 messages stay word for word
)
```

After planning a Kerala trip over 6 turns, *"What did I say my budget was?"* is still answered
(₹40,000), from the summary.

## 5 · Long-term memory: a Store

A checkpointer only remembers within one thread. A **Store** is a key-value database shared by
**all** threads. The agent gets tools to write and read it (`5.long_term.py`):

```python
@tool
def save_memory(fact: str, runtime: ToolRuntime[Context]) -> str:
    """Save a lasting fact about the user (preferences, name, goals)."""
    runtime.store.put(("memories", runtime.context.user_id), str(uuid.uuid4()), {"fact": fact})
    return f"Saved: {fact}"
```

The namespace `("memories", user_id)` is like a folder per user. In a **new** thread, the agent can
still call `list_memories` and suggest a game based on the hobbies it saved earlier, while a
different `user_id` sees nothing.

## 6 · Semantic memory

Give the Store an embedding index, and search by **meaning** (`6.semantic_memory.py`):

```python
store = InMemoryStore(index={"embed": embeddings, "dims": 384})
hits = store.search(("memories", "arun"), query="what food should I avoid?", limit=3)
```

*"Any snack ideas for my trek?"* finds *"I'm allergic to peanuts"*, although they share no words.

## Common mistakes

- **Forgetting the `thread_id`.** With a checkpointer, every call needs `config`; without it you
  get an error or a new, empty conversation.
- **`InMemorySaver` / `InMemoryStore` in production.** Everything is gone on restart. Use SQLite,
  Postgres or Redis versions.
- **One namespace for all users.** Long-term memory must be keyed by user, or users read each
  other's facts.
- **`dims` that don't match the embedding model** (MiniLM = 384, nomic = 768).
- **Saving everything.** Tell the agent (in the system prompt) to save only *lasting* facts, not
  every sentence.

## Try it yourself

1. Run `persistent_demo()` in `1.buffer_memory.py`, then open `memory.db` with `sqlite3` and look at
   the tables.
2. In `2.window_memory.py`, keep the last 6 instead of 4. Which questions can it answer now?
3. Print the summary message in `4.summary_memory.py`. Is the budget in it word for word?
4. Add a `delete_memory(fact)` tool to `5.long_term.py`, and ask the agent to forget a hobby.
5. In `6.semantic_memory.py`, add *"I'm vegetarian"* and ask for dinner ideas. Does it find both
   food facts?

## Full source

<details class="source">
<summary>model.py</summary>

```{literalinclude} ../code/15-memory/model.py
:language: python
```

</details>

<details class="source">
<summary>1.buffer_memory.py</summary>

```{literalinclude} ../code/15-memory/1.buffer_memory.py
:language: python
```

</details>

<details class="source">
<summary>2.window_memory.py</summary>

```{literalinclude} ../code/15-memory/2.window_memory.py
:language: python
```

</details>

<details class="source">
<summary>4.summary_memory.py</summary>

```{literalinclude} ../code/15-memory/4.summary_memory.py
:language: python
```

</details>

<details class="source">
<summary>5.long_term.py</summary>

```{literalinclude} ../code/15-memory/5.long_term.py
:language: python
```

</details>

<details class="source">
<summary>6.semantic_memory.py</summary>

```{literalinclude} ../code/15-memory/6.semantic_memory.py
:language: python
```

</details>

**Downloads:**
{download}`model.py <../code/15-memory/model.py>` ·
{download}`1.buffer_memory.py <../code/15-memory/1.buffer_memory.py>` ·
{download}`2.window_memory.py <../code/15-memory/2.window_memory.py>` ·
{download}`3.token_memory.py <../code/15-memory/3.token_memory.py>` ·
{download}`4.summary_memory.py <../code/15-memory/4.summary_memory.py>` ·
{download}`5.long_term.py <../code/15-memory/5.long_term.py>` ·
{download}`6.semantic_memory.py <../code/15-memory/6.semantic_memory.py>`
