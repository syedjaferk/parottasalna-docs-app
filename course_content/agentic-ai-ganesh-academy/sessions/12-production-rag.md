# Session 12 · RAG for real apps: conversations, async and streaming

## The big idea

Three things a real chat app needs that our scripts didn't have yet:

1. **Conversation memory**: "and what about tuples?" only makes sense if the app remembers the
   previous question.
2. **Speed through async**: run several searches **at the same time** instead of one after another.
3. **Streaming**: show the answer word by word as it's generated, instead of a blank screen for 5
   seconds.

**Everyday example:** a good waiter remembers your order (memory), the kitchen cooks several dishes
in parallel (async), and starters come out as soon as they're ready (streaming).

## 1 · Conversational RAG with Redis

`conversational/app.py` keeps the chat history in Redis under a session id and puts the **last 5
exchanges** into every prompt (shortened here):

```python
def save_chat(question, answer):
    history = json.loads(redis_client.get(SESSION_ID) or "[]")
    history.append({"user": question, "assistant": answer})
    redis_client.set(SESSION_ID, json.dumps(history))

prompt = PromptTemplate.from_template("""
You are a helpful assistant.
Conversation History
{history}
Relevant Documents
{context}
Current Question
{question}
Answer the question using the documents and conversation.
""")
```

Run `conversational/ingest.py` once, then the app:

```text
You : What is a dictionary in Python?
Assistant : A dictionary stores key–value pairs …
You : How do I loop over one?
Assistant : You can loop over a dictionary's keys, values or items …   ← "one" = a dictionary
```

:::{note}
The history fixes the *answer*, but the *search* still uses only "How do I loop over one?". Combine
this with the **query rewriting** from [Session 10](10-better-queries-and-smaller-context.md): rewrite
the question with the history first, then retrieve.
:::

Because the history lives in Redis, it survives restarts and can be shared by several app servers.
The class code uses a fixed `SESSION_ID = "user_123"`; a real app uses one id per user or chat.

## 2 · Async retrieval

`async_rag.py` runs three searches at once with `asyncio.gather`:

```python
async def retrieve(query):
    vector_docs, keyword_docs, metadata_docs = await asyncio.gather(
        vector_search(query),      # Chroma, by meaning
        keyword_search(query),     # BM25, by words
        metadata_search(query),    # Chroma with a filter
    )
    return vector_docs + keyword_docs + metadata_docs
```

Then it removes duplicates and asks the LLM with `await llm.ainvoke(prompt)`. That's also a hybrid
search (Session 4) assembled from LangChain parts.

:::{warning}
`async def` alone doesn't make code run in parallel. `metadata_search` calls the normal (blocking)
`db.similarity_search(...)` inside an `async def`, so while it runs, nothing else can. Use the async
version (`await db.asimilarity_search(...)`) or `await asyncio.to_thread(db.similarity_search, ...)`.
[Session 13](13-async-python.md) explains why.
:::

## 3 · Streaming answers with Server-Sent Events

The LLM can send its answer **token by token** (`streaming/llm.py`):

```python
completion = client.chat.completions.create(model="openai/gpt-oss-120b", stream=True,
                                            messages=[{"role": "user", "content": prompt}])
for chunk in completion:
    if chunk.choices:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
```

FastAPI passes each token to the browser as a **Server-Sent Event** (`streaming/app.py`):

```python
@app.get("/chat")
async def chat(question: str):
    async def event_generator():
        context = retrieve(question)
        for token in stream_answer(question, context):
            yield {"event": "token", "data": token}
        yield {"event": "done", "data": "END"}
    return EventSourceResponse(event_generator())
```

And the page listens with `EventSource` (`streaming/index.html`):

```javascript
source.addEventListener("token", (event) => {
    output.textContent += event.data;
});
```

Run it:

```bash
cd streaming
python ingest.py
uvicorn app:app --reload
```

Then open `index.html` in your browser and watch the answer appear.

:::{note}
**Two fixes compared to the class code.** `ingest.py` split the pages into chunks but then stored the
whole *pages*; it now stores the chunks. `index.html` added tokens with `innerHTML`, which would run
any HTML the model produced (a security hole called XSS); it now uses `textContent`.
:::

## Common mistakes

- **Unlimited history in the prompt.** Every turn adds tokens. Keep the last N turns or summarise
  older ones (more in [Session 15](15-agent-memory.md)).
- **One `SESSION_ID` for everyone.** Users would see each other's conversations.
- **Blocking calls inside async code** (see the warning above). The synchronous Groq stream in
  `stream_answer` also blocks the server while it runs; with many users, use `AsyncGroq` and
  `async for`.
- **Putting model output into the page with `innerHTML`.**

## Try it yourself

1. Give `conversational/app.py` a session id per run: ask for a name at start-up and use it as the
   Redis key. Check two users don't see each other's history.
2. Add an expiry to the history: `redis_client.set(SESSION_ID, ..., ex=3600)`.
3. In `async_rag.py`, time `retrieve()` with `time.perf_counter()`. Then fix `metadata_search` with
   `asyncio.to_thread` and time it again.
4. In `streaming/index.html`, add a text box and a button, so the question comes from the user.
5. Switch `streaming/llm.py` to `AsyncGroq` and make `stream_answer` an `async` generator.

## Full source

<details class="source">
<summary>conversational/app.py</summary>

```{literalinclude} ../code/12-production-rag/conversational/app.py
:language: python
```

</details>

<details class="source">
<summary>async_rag.py</summary>

```{literalinclude} ../code/12-production-rag/async_rag.py
:language: python
```

</details>

<details class="source">
<summary>streaming/app.py, llm.py, rag.py</summary>

```{literalinclude} ../code/12-production-rag/streaming/app.py
:language: python
```

```{literalinclude} ../code/12-production-rag/streaming/llm.py
:language: python
```

```{literalinclude} ../code/12-production-rag/streaming/rag.py
:language: python
```

</details>

<details class="source">
<summary>streaming/index.html</summary>

```{literalinclude} ../code/12-production-rag/streaming/index.html
:language: html
```

</details>

**Downloads:**
{download}`conversational/ingest.py <../code/12-production-rag/conversational/ingest.py>` ·
{download}`conversational/app.py <../code/12-production-rag/conversational/app.py>` ·
{download}`async_rag.py <../code/12-production-rag/async_rag.py>` ·
{download}`streaming/ingest.py <../code/12-production-rag/streaming/ingest.py>` ·
{download}`streaming/rag.py <../code/12-production-rag/streaming/rag.py>` ·
{download}`streaming/llm.py <../code/12-production-rag/streaming/llm.py>` ·
{download}`streaming/app.py <../code/12-production-rag/streaming/app.py>` ·
{download}`streaming/index.html <../code/12-production-rag/streaming/index.html>`
