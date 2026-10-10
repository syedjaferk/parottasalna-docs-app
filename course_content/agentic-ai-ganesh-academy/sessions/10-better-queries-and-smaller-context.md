# Session 10 · Better queries, smaller context

## The big idea

Two problems sit on either side of retrieval:

- **Before** retrieval, the user's question is often a poor search query: *"How do I deploy it?"*
  (deploy *what*?). **Query transformation** rewrites it; **query expansion** asks it several ways.
- **After** retrieval, the chunks contain a lot of text that doesn't help. **Context compression**
  keeps only the useful sentences, so the prompt is shorter, cheaper and more focused.

**Everyday example:** a librarian first asks what you *really* mean ("deploy… your FastAPI app?"),
looks in a few sections, and then hands you just the relevant pages, not the whole shelf.

## Query transformation and expansion

`query_transformation.py` does three LLM calls.

**1 · Rewrite into a standalone question**, using the conversation so far:

```python
history = """
User: Explain FastAPI.
Assistant: FastAPI is a modern Python web framework.
"""
user_query = "How do I deploy it?"

rewrite_prompt = f"""
You are an expert search query optimizer.
Conversation
{history}
Current Query
{user_query}
Rewrite the query into a standalone search query.
Return only the rewritten query.
"""
```

Typical result: `How to deploy a FastAPI application`.

**2 · Expand into 5 variations** (with a little randomness, `temperature=0.3`). A typical result,
with the rewritten query added on top:

```text
How to deploy a FastAPI application
FastAPI deployment with Docker
Deploy FastAPI on AWS
Running FastAPI in production with Uvicorn and Gunicorn
FastAPI hosting options
```

**3 · Search with every variation, merge, and answer.** A dictionary drops duplicates while keeping
the order:

```python
retrieved_documents = {}
for query in expanded_queries:
    result = collection.query(query_embeddings=[embedding_model.encode(query).tolist()], n_results=3)
    for doc in result["documents"][0]:
        retrieved_documents[doc] = True
documents = list(retrieved_documents.keys())
```

Different wordings hit different chunks, so together they find more of the relevant ones.

:::{note}
In class this script used a Chroma collection that was already filled. The version here adds six
short documents about deploying FastAPI the first time it runs, so it works on its own.
:::

## Context compression: three ways

All three scripts read the same Chroma database (run `ingest.py` first) and print the context
**before** and **after** compressing.

### Keyword compression: cheap and fast

Keep sentences that contain a word from the question (`keyword_compression.py`):

```python
words = re.findall(r"\w+", question.lower())
keywords = [word for word in words if word not in STOPWORDS]      # "what is a dictionary" → ["dictionary"]

for sentence in re.split(r"(?<=[.!?])\s+", context):
    if any(keyword in sentence.lower() for keyword in keywords):
        compressed.append(sentence.strip())
```

It misses sentences that say the same thing in other words ("a dict maps keys to values").

### Embedding compression: by meaning

Score every sentence against the question and keep the top 10 (`embedding_compression.py`):

```python
question_embedding = embedding_model.embed_query(question)
sentence_embeddings = embedding_model.embed_documents(sentences)
scores = cosine_similarity([question_embedding], sentence_embeddings)[0]
ranked = sorted(zip(sentences, scores), key=lambda x: x[1], reverse=True)[:TOP_SENTENCES]
```

### LLM compression: the smartest, and the most expensive

Ask an LLM to remove what's unrelated, **not** to answer (`llm_compression.py`):

```text
Your task is NOT to answer the user's question.
Instead:
1. Read the user's question.
2. Read the retrieved context.
3. Remove every sentence that is unrelated.
4. Keep only information useful for answering.
5. Preserve important technical details.
6. Do not summarize unless necessary.
7. Return ONLY the compressed context.
```

| Method | Speed | Cost | Quality |
|---|---|---|---|
| keyword | instant | free | misses synonyms |
| embedding | fast | free (local model) | good |
| LLM | slow (an extra call) | tokens | best: understands the question |

:::{note}
**A fix compared to the class code.** `ingest.py` turns all whitespace, newlines included, into
single spaces. So splitting the context on `"\n"` gave back whole chunks, not sentences, and nothing
was really compressed. The scripts here split on sentence endings (`. ! ?`) instead.
:::

## Common mistakes

- **Rewriting without the history.** "How do I deploy it?" can't be fixed if the rewriter never
  sees that "it" is FastAPI.
- **Expanding too much.** 5 queries × k=3 = up to 15 chunks. Expansion increases recall; follow it
  with reranking (Session 8) or compression to keep the prompt small.
- **LLM compression on every request without measuring.** It adds a full LLM call. Use it when
  chunks are long and noisy.
- **Answering the rewritten question instead of the user's.** Search with the rewrite, but answer
  the user's own words (the class code does this correctly).

## Try it yourself

1. Change `history` and `user_query` in `query_transformation.py` to a two-turn chat about Redis.
   Does the rewrite pick up the subject?
2. Print how many documents each expanded query found and how many were unique overall.
3. In `embedding_compression.py`, change `TOP_SENTENCES` to 3. Is the answer still complete?
4. Compare the length (characters) of the original and compressed context for the same question
   with all three methods.
5. Add a minimum score to `embedding_compression.py`: drop sentences below 0.3 even if they're in
   the top 10.

## Full source

<details class="source">
<summary>query_transformation.py</summary>

```{literalinclude} ../code/10-queries-and-context/query_transformation.py
:language: python
```

</details>

<details class="source">
<summary>keyword_compression.py</summary>

```{literalinclude} ../code/10-queries-and-context/keyword_compression.py
:language: python
```

</details>

<details class="source">
<summary>embedding_compression.py</summary>

```{literalinclude} ../code/10-queries-and-context/embedding_compression.py
:language: python
```

</details>

<details class="source">
<summary>llm_compression.py</summary>

```{literalinclude} ../code/10-queries-and-context/llm_compression.py
:language: python
```

</details>

**Downloads:**
{download}`query_transformation.py <../code/10-queries-and-context/query_transformation.py>` ·
{download}`ingest.py <../code/10-queries-and-context/ingest.py>` ·
{download}`keyword_compression.py <../code/10-queries-and-context/keyword_compression.py>` ·
{download}`embedding_compression.py <../code/10-queries-and-context/embedding_compression.py>` ·
{download}`llm_compression.py <../code/10-queries-and-context/llm_compression.py>`
