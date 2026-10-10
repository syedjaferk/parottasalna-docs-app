# Session 9 · Semantic caching

## The big idea

Users ask the same thing in different words: *"What is a list in Python?"*, *"explain python
lists"*, *"what's a Python list?"*. Each one costs an LLM call (time and money) for the same answer.
A **semantic cache** stores answers by the **meaning** of the question. When a new question is
close enough to one we've answered, we return the saved answer instantly.

**Everyday example:** a help-desk FAQ. The agent doesn't research "how do I reset my password?"
from scratch each time; they recognise the question, even reworded, and give the known answer.

| Normal cache | Semantic cache |
|---|---|
| key = the exact text | key = the question's embedding |
| `"What is a list?"` ≠ `"what's a list"` | both match (similarity ≥ 0.90) |

## How it fits into RAG

```text
question ─► embed ─► similar question in cache?
                 ├─ yes (≥ 0.90) ─► return saved answer           (milliseconds, free)
                 └─ no ─► retrieve ─► LLM ─► save in cache ─► answer   (seconds, costs tokens)
```

From `augmentation.py`:

```python
cached_answer = search_cache(user_query)
if cached_answer:
    print(cached_answer)
    return

context = retrieval(user_query)
answer = call_groq([{"role": "user", "content": PROMPT.format(context=context, query=user_query)}])
store_cache(user_query, answer)
```

## The cache, in Redis

`semantic_cache.py` stores each entry as JSON in Redis, with the question's embedding:

```python
def store_cache(question, answer):
    value = {"question": question, "embedding": get_embedding(question), "answer": answer}
    redis_client.set(CACHE_PREFIX + str(abs(hash(question))), json.dumps(value))

def search_cache(question):
    query_embedding = get_embedding(question)
    for key in redis_client.scan_iter(f"{CACHE_PREFIX}*"):
        data = json.loads(redis_client.get(key))
        similarity = cosine_similarity(query_embedding, data["embedding"])
        if similarity >= SIMILARITY_THRESHOLD:     # 0.90
            return data["answer"]
    return None
```

Start Redis first (`docker run -d --name redis -p 6379:6379 redis:7`), run `ingest.py` once, then
`augmentation.py`. Ask a question, then ask it again in other words, and watch for **CACHE HIT**.

## Choosing the threshold

| Threshold | What happens |
|---|---|
| too low (0.75) | *"How do I **add** to a list?"* can return the cached answer for *"How do I **remove** from a list?"*. Wrong answers! |
| too high (0.98) | almost never hits; you pay for every call |
| 0.88–0.93 | a sensible start; test with your real questions |

## What to improve before production

The class version is perfect for learning, but has four weaknesses worth knowing:

1. **It checks every entry one by one** (`scan_iter`). Fine for 100 entries, slow for 100,000. Real
   systems use a vector index: Redis Stack's vector search, or the `redisvl` library's
   `SemanticCache`, which does exactly this job.
2. **Entries never expire.** `config.py` defines `CACHE_TTL` (7 days) but nothing uses it. Use
   `redis_client.set(key, value, ex=CACHE_TTL)` so stale answers disappear when your documents
   change.
3. **`hash()` changes every time Python starts.** Python randomises string hashes per process, so
   the same question gets a different key after a restart and is stored twice. Use a stable hash:
   `hashlib.sha256(question.encode()).hexdigest()`.
4. **Errors get cached.** If Groq fails, `call_groq` returns `"Request failed: …"`, and that text
   is saved as the answer. Only cache real answers.

:::{warning}
**Never share one cache across users for personal questions.** "What's my leave balance?" must not
return someone else's cached answer. Add the user id to the key, or only cache general questions.
:::

## Common mistakes

- **Caching answers whose context changes.** When the documents are updated, old cached answers
  are wrong. Use a TTL, or clear the cache on every ingest.
- **Embedding the answer instead of the question.** The cache key is the *question's* meaning.
- **Forgetting Redis is running in Docker.** `ConnectionError: Error 111 connecting to localhost:6379`
  means it isn't started.

## Try it yourself

1. Ask 5 questions, then 5 rewordings of them. How many hits do you get at 0.90? At 0.85?
2. Find a pair of questions that are *different* but still hit at 0.85. That's why the threshold
   matters.
3. Add the TTL: `redis_client.set(key, value, ex=CACHE_TTL)`. Check it with `redis-cli TTL <key>`.
4. Replace `abs(hash(question))` with a SHA-256 of the question, restart the script and confirm the
   same question doesn't create a second key (`redis-cli KEYS 'semantic:*'`).
5. Don't cache answers that start with `"Request failed"`.

## Full source

<details class="source">
<summary>semantic_cache.py</summary>

```{literalinclude} ../code/09-semantic-cache/semantic_cache.py
:language: python
```

</details>

<details class="source">
<summary>augmentation.py</summary>

```{literalinclude} ../code/09-semantic-cache/augmentation.py
:language: python
```

</details>

<details class="source">
<summary>config.py</summary>

```{literalinclude} ../code/09-semantic-cache/config.py
:language: python
```

</details>

**Downloads:**
{download}`config.py <../code/09-semantic-cache/config.py>` ·
{download}`embeddings.py <../code/09-semantic-cache/embeddings.py>` ·
{download}`ingest.py <../code/09-semantic-cache/ingest.py>` ·
{download}`retrieval.py <../code/09-semantic-cache/retrieval.py>` ·
{download}`semantic_cache.py <../code/09-semantic-cache/semantic_cache.py>` ·
{download}`augmentation.py <../code/09-semantic-cache/augmentation.py>`
