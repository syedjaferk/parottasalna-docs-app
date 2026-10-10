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

```{raw} html
:file: ../diagrams/s09-cache.html
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

## Hands-on exercises

Try each one before opening the solution.

**Exercise 1 · Hit rate.** Ask 5 questions, then 5 rewordings. Count the hits at threshold 0.90 and
0.85.

<details class="solution"><summary>What to notice</summary>

Close rewordings ("What is a list in Python?" / "what's a python list") usually score above 0.9.
Looser ones ("explain lists to me") may only hit at 0.85. Every point you lower the threshold buys
more hits **and** more risk of wrong ones.

</details>

**Exercise 2 · A dangerous pair.** Find two *different* questions that still hit at 0.85.

<details class="solution"><summary>Example</summary>

*"How do I add an item to a list?"* and *"How do I remove an item from a list?"* differ in one word
and often score very high. The cache would return the "add" answer to the "remove" question. Test
pairs like this before choosing a threshold.

</details>

**Exercise 3 · Expiry.** Use `CACHE_TTL` so entries disappear after 7 days.

<details class="solution"><summary>Solution</summary>

```python
from config import CACHE_TTL

redis_client.set(key, json.dumps(value), ex=CACHE_TTL)
```

Check with `docker exec -it redis redis-cli TTL <key>`: it counts down from 604800.

</details>

**Exercise 4 · A stable key.** Replace `abs(hash(question))` with SHA-256, restart the script and
store the same question again.

<details class="solution"><summary>Solution</summary>

```python
import hashlib

key = CACHE_PREFIX + hashlib.sha256(question.strip().lower().encode()).hexdigest()
```

`redis-cli KEYS 'semantic:*'` now shows one key per question across restarts, instead of a new one
each time Python picks a new random hash seed.

</details>

**Exercise 5 · Don't cache failures.** Make sure `"Request failed: …"` answers are never stored.

<details class="solution"><summary>Solution</summary>

```python
answer = call_groq([...])
if answer.startswith("Request failed"):
    print(answer)
    return                       # show it, but don't cache it
store_cache(user_query, answer)
```

Better still: make `call_groq` raise on errors (Session 1, exercise 5), so a failure can never look
like an answer.

</details>

**Exercise 6 · Per-user cache.** Make cached answers private to each user.

<details class="solution"><summary>Solution</summary>

Put the user in the prefix and only scan that user's keys:

```python
def cache_prefix(user_id):
    return f"semantic:{user_id}:"

for key in redis_client.scan_iter(f"{cache_prefix(user_id)}*"):
    ...
```

Keep a shared prefix only for general questions whose answer is the same for everyone.

</details>

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
