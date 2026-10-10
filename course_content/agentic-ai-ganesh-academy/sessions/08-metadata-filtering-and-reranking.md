# Session 8 · Metadata filtering and reranking

## The big idea

Two ways to make retrieval **more precise**:

- **Metadata filtering**: only search the chunks that match some facts, such as *category =
  Database*, *year ≥ 2024* or *department = HR*. It works like a `WHERE` clause before the
  similarity search.
- **Reranking**: fetch a generous list (say 15–20 chunks), then let a slower but smarter model
  **re-order** them and keep only the best 3–4.

**Everyday example:** shopping online. Filters ("size M, under ₹1,000") cut the list down; "sort
by relevance" then puts the best match first.

## Metadata filtering

Each chunk is stored with a dictionary of facts (`metadata_filtering.py`):

```python
documents = [
    "Python decorators extend the functionality of existing functions without modifying their source code.",
    # ... 31 more
]
metadatas = [
    {"category": "Programming", "topic": "Decorators", "author": "Luciano Ramalho",
     "level": "Advanced", "year": 2022},
    # ... one dictionary per document
]

db = Chroma.from_texts(texts=documents, embedding=embeddings, metadatas=metadatas, ids=ids,
                       persist_directory="./chroma_db")
```

Search with a filter:

```python
db.similarity_search(query="How do I organise code?", k=5, filter={"category": "Programming"})
```

Only Programming chunks can come back, however similar a Database chunk might be.

### Two or more conditions need `$and`

Chroma accepts **one** condition per filter. This fails:

```python
filter={"category": "Programming", "level": "Advanced"}      # ✗ error
```

Combine conditions explicitly:

```python
filter={"$and": [{"category": "Programming"}, {"level": "Advanced"}]}
```

The class script asked for category, author and level, and broke when you filled in more than one.
The version below builds the `$and` for you:

```python
if len(filters) > 1:
    metadata_filter = {"$and": [{key: value} for key, value in filters.items()]}
else:
    metadata_filter = filters or None
```

Other operators: `{"year": {"$gte": 2024}}`, `{"level": {"$in": ["Beginner", "Intermediate"]}}`,
`{"$or": [...]}`.

## Reranking with a cross-encoder

The embedding search from Session 3 uses a **bi-encoder**: the question and each chunk are embedded
*separately*, then compared. That's fast, but rough.

A **cross-encoder** reads the question and a chunk **together** and outputs one relevance score.
Much more accurate, but too slow to run over a whole database. So: bi-encoder to shortlist,
cross-encoder to pick the winners.

```text
question ─► vector search (fast) ─► top 15 ─► cross-encoder (accurate) ─► top 4 ─► LLM
```

```{raw} html
:file: ../diagrams/s08-rerank.html
```

From `rerank.py`:

```python
reranker = CrossEncoder("BAAI/bge-reranker-base")

results = collection.query(query_embeddings=[query_embedding], n_results=5)
retrieved_documents = results["documents"][0]

pairs = [[query, doc] for doc in retrieved_documents]
scores = reranker.predict(pairs)
reranked = sorted(zip(retrieved_documents, scores), key=lambda x: x[1], reverse=True)
top_documents = [doc for doc, score in reranked[:3]]
```

For *"How do MongoDB transactions work?"*, the 5 nearest sentences include anything about
MongoDB or transactions: replica sets, PostgreSQL's ACID transactions and so on. The script prints
the list before and after reranking. The cross-encoder should lift the two sentences that actually
describe **MongoDB transactions** to the top.

## A PDF chatbot with reranking

`pdf-chatbot/app.py` puts it into a LangChain chain: retrieve **15** chunks, rerank, keep **4**,
answer with Groq.

```python
def retrieve_and_rerank(query):
    docs = retriever.invoke(query)                # k=15
    docs = rerank_documents(query, docs, top_k=4)
    return "\n\n".join(doc.page_content for doc in docs)

chain = (
    {"context": RunnableLambda(retrieve_and_rerank), "question": RunnablePassthrough()}
    | prompt
    | custom_llm
)
```

`RunnableLambda` turns any Python function into a chain step, and `RunnablePassthrough` passes the
question through unchanged. The `|` pipes each step's output into the next.

## Common mistakes

- **Reranking only 3–4 results.** If the right chunk isn't in the shortlist, reranking can't save
  it. Fetch more (10–20) than you'll keep.
- **Metadata typos.** `"Programing"` or `"programming"` match nothing, silently. Use fixed values
  (dropdowns, enums), not free text.
- **Filtering on a field you never stored.** Chroma returns nothing, not an error.
- **Reranking on every keystroke.** A cross-encoder is slow on CPU. Rerank once, on the final
  query.

## Hands-on exercises

Try each one before opening the solution.

**Exercise 1 · Filters beat similarity.** Search *"what is a container?"* with no filter, then with
category *Database*.

<details class="solution"><summary>What to notice</summary>

Without a filter, Docker and Kubernetes sentences win. With `{"category": "Database"}` only database
sentences can come back, even though none is really about containers. The filter is applied
**before** similarity, so it can force poor matches: use filters for hard rules (department, user,
date), not for topic guessing.

</details>

**Exercise 2 · Combine conditions.** Find all **Advanced** chunks from **2024 or later**.

<details class="solution"><summary>Solution</summary>

```python
search("best practices", k=10, metadata_filter={
    "$and": [{"level": "Advanced"}, {"year": {"$gte": 2024}}]
})
```

Expect six: Transactions, Helm, Neural Networks, LLM, RAG and OAuth (with the default `k=5` you'd
only see five of them).

</details>

**Exercise 3 · Before vs after.** In `rerank.py`, print each document's vector rank next to its
reranked rank.

<details class="solution"><summary>Solution</summary>

```python
before = {doc: i for i, doc in enumerate(retrieved_documents, start=1)}
for after, (doc, score) in enumerate(reranked_results, start=1):
    print(f"{before[doc]} → {after}   {score:7.3f}   {doc[:60]}")
```

</details>

**Exercise 4 · Shortlist size.** In `pdf-chatbot/app.py`, retrieve `k=5` instead of 15 (still keeping
4). Ask the same three questions.

<details class="solution"><summary>What to notice</summary>

With 5 candidates the reranker has almost nothing to choose from, so it barely changes the result.
Reranking pays off when the shortlist is clearly bigger than what you keep: 15–25 → 3–5 is typical.

</details>

**Exercise 5 · A smaller reranker.** Try `cross-encoder/ms-marco-MiniLM-L-6-v2`. Faster? Same order?

<details class="solution"><summary>Solution</summary>

```python
import time
for name in ["BAAI/bge-reranker-base", "cross-encoder/ms-marco-MiniLM-L-6-v2"]:
    model = CrossEncoder(name)
    start = time.perf_counter()
    scores = model.predict(pairs)
    print(name, f"{time.perf_counter() - start:.2f}s", scores.argsort()[::-1])
```

The MiniLM model is several times smaller and faster on CPU; the top result is usually the same, with
small differences lower down. Its scores are on a different scale, so don't reuse thresholds.

</details>

**Exercise 6 · Filter by user.** Add a `"user": "arun"` or `"user": "priya"` field to some
documents and make search only return the current user's documents.

<details class="solution"><summary>Solution</summary>

```python
def search_for_user(user, query, k=5):
    return db.similarity_search(query, k=k, filter={"user": user})
```

This is how multi-user RAG keeps people's private documents apart. Always add the user filter on the
**server**, never trust the client to send it.

</details>

## Full source

<details class="source">
<summary>metadata_filtering.py</summary>

```{literalinclude} ../code/08-filter-rerank/metadata_filtering.py
:language: python
:lines: 275-
```

The first 274 lines are the sample documents and their metadata. Download the file to see them all.

</details>

<details class="source">
<summary>rerank.py</summary>

```{literalinclude} ../code/08-filter-rerank/rerank.py
:language: python
```

</details>

<details class="source">
<summary>pdf-chatbot/app.py</summary>

```{literalinclude} ../code/08-filter-rerank/pdf-chatbot/app.py
:language: python
```

</details>

<details class="source">
<summary>pdf-chatbot/groq_client.py</summary>

```{literalinclude} ../code/08-filter-rerank/pdf-chatbot/groq_client.py
:language: python
```

</details>

**Downloads:**
{download}`metadata_filtering.py <../code/08-filter-rerank/metadata_filtering.py>` ·
{download}`rerank.py <../code/08-filter-rerank/rerank.py>` ·
{download}`pdf-chatbot/app.py <../code/08-filter-rerank/pdf-chatbot/app.py>` ·
{download}`pdf-chatbot/groq_client.py <../code/08-filter-rerank/pdf-chatbot/groq_client.py>` ·
{download}`pdf-chatbot/movie_search.py <../code/08-filter-rerank/pdf-chatbot/movie_search.py>` ·
{download}`movies_sample.csv <../code/08-filter-rerank/pdf-chatbot/movies_sample.csv>`
