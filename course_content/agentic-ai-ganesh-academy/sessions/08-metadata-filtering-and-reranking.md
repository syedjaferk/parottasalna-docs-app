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

## Try it yourself

1. In `metadata_filtering.py`, search *"what is a container?"* with no filter, then with category
   *Database*. What comes back?
2. Find all **Advanced** chunks from **2024 or later** (`$and` with `$gte`).
3. In `rerank.py`, print the vector rank and the reranked rank side by side for each document.
4. In `pdf-chatbot/app.py`, change retrieval to `k=5`, rerank to `top_k=4`. Ask the same 3
   questions as with `k=15`. Any difference?
5. Try the smaller reranker `cross-encoder/ms-marco-MiniLM-L-6-v2`. Is it faster? Same order?

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
