# Session 3 · Embeddings and vector databases

## The big idea

An LLM only knows what it was trained on. To answer from **your** documents, we first need to
**find** the right paragraph. Keyword search fails when the words differ ("reduce body fat" vs
"tips for fat loss"). **Embeddings** fix that: they turn text into a list of numbers so that
**similar meanings get similar numbers**. A **vector database** stores those numbers and finds the
closest ones fast.

**Everyday example:** a library arranged by *topic*, not alphabet. Books about cooking sit
together, so you find "baking bread" right next to "making pizza dough" even though the titles
share no words.

## What an embedding looks like

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
vector = model.encode("Redis is an in-memory database")
print(len(vector))   # 384  numbers
print(vector[:5])    # e.g. [-0.07  0.02  0.01 -0.05  0.04]
```

One sentence → 384 numbers (the model decides the length: `all-MiniLM-L6-v2` gives 384,
`nomic-embed-text` gives 768). On their own the numbers mean nothing. What matters is **how close two
vectors are**.

```{raw} html
:file: ../diagrams/s03-space.html
```

## Measuring "closeness": cosine similarity

Cosine similarity compares the **direction** of two vectors: about `1` means same meaning; near `0`
means unrelated (`dense/cosine_similarity.py`):

```python
texts = ["How to learn Python?", "Best way to study Python", "I love pizza"]
embeddings = model.encode(texts)
print(cosine_similarity(embeddings))
```

The two Python questions score each other **much higher** than either scores "I love pizza",
although "learn" and "study" are different words. That's the whole trick.

## Searching by meaning

`dense/sentence_transformer.py` ranks documents against a question:

```python
documents = [
    "Redis is an in-memory database",
    "FastAPI is used for building APIs",
    "Docker helps create containers",
    "Kubernetes manages containers",
    "PostgreSQL is a relational database",
]
query = "Which database works in memory?"

scores = cosine_similarity(model.encode([query]), model.encode(documents))[0]
for index in np.argsort(scores)[::-1]:      # highest score first
    print(documents[index], round(scores[index], 4))
```

Redis comes first, PostgreSQL (also a database) second, and the container sentences last.

## Why a vector *database*?

Comparing the question with every vector works for 5 sentences. For **5 million** chunks it's too
slow, and the vectors must survive a restart. A vector database (Chroma, FAISS, Pinecone,
OpenSearch…) **stores** vectors on disk and **indexes** them for fast nearest-neighbour search.

`simple_vector_search.py` does it with **Ollama** embeddings and **Chroma**, in two flows:

```python
# FLOW 1 · store: text → embeddings → Chroma
client = chromadb.PersistentClient(path="./chroma_storage")
collection = client.get_or_create_collection("ollama_demo")
collection.add(documents=docs, embeddings=ollama_embed(docs), ids=[str(i) for i in range(len(docs))])

# FLOW 2 · search: question → embedding → nearest documents
results = collection.query(query_embeddings=ollama_embed(["tell me about vector database"]), n_results=2)
print(results["documents"])   # typically [['ChromaDB is a vector database', 'PostgreSQL is a relational Database']]
```

:::{note}
**Store and search with the same embedding model.** Vectors from different models live in
different "maps", so comparing them is meaningless.
:::

```{raw} html
:file: ../diagrams/s03-vdb.html
```

## Seeing the vectors

384 dimensions can't be drawn, so **t-SNE** squeezes them down to 2 while trying to keep close
things close (`visualization.py`, `dense/visualizer.py`). Run `dense/simple_rag.py` and you'll see
the question plotted as a big **X** next to the documents it matched.

## Retrieve, then generate: a first taste of RAG

`dense/simple_rag.py` puts it together: find the 2 nearest documents in Chroma, paste them into the
prompt, and let Groq answer.

```python
results = collection.query(query_embeddings=[query_embedding.tolist()], n_results=2)
context = "\n".join(results["documents"][0])

prompt = f"""
Answer the question using the context below.

Context:
{context}

Question:
{query}
"""
```

That's **R**etrieval-**A**ugmented **G**eneration. The next sessions make each step better.

## Common mistakes

- **Mixing embedding models** between storing and searching.
- **Running `collection.add` twice with the same ids.** Chroma keeps the old ones. Use `upsert`
  (as `simple_rag.py` does) when you re-run a script.
- **t-SNE `perplexity` too big.** It must be smaller than the number of points; with 5 documents
  use 2–4.
- **Forgetting Ollama is a separate program.** `ollama.embeddings(...)` fails until Ollama is running
  and you've done `ollama pull nomic-embed-text`.

## Hands-on exercises

Try each one before opening the solution.

**Exercise 1 · Topics separate.** Add three cooking sentences to the documents in
`dense/sentence_transformer.py` and ask *"how do I bake bread?"*

<details class="solution"><summary>What to notice</summary>

The cooking sentences take the top places and the tech sentences drop to the bottom, even if no
sentence contains the word "bake". Meaning, not words, decides the order.

</details>

**Exercise 2 · Compare two models.** Run the same query with `all-MiniLM-L6-v2` and
`BAAI/bge-small-en`. Do the rankings or the scores change?

<details class="solution"><summary>What to notice</summary>

The order of the top results is usually the same, but the **scores** are on different scales (bge
scores tend to be higher across the board). Never compare scores, or a fixed threshold, between
different embedding models.

</details>

**Exercise 3 · Distances.** In `simple_vector_search.py`, set `n_results=5` and print
`results["distances"]`.

<details class="solution"><summary>Solution</summary>

```python
results = collection.query(query_embeddings=q_emb, n_results=5, include=["documents", "distances"])
for doc, dist in zip(results["documents"][0], results["distances"][0]):
    print(f"{dist:8.2f}  {doc}")
```

Smaller distance = closer meaning. "ChromaDB is a vector database" should have the smallest.

</details>

**Exercise 4 · Say "I don't know".** Ask `simple_rag.py` *"What is Kafka?"* (not in the documents),
then make it admit it doesn't know.

<details class="solution"><summary>Solution</summary>

```python
prompt = f"""
Answer the question using ONLY the context below.
If the answer is not in the context, reply exactly: I don't know.

Context:
{context}

Question:
{query}
"""
```

Without that line the model answers from its own memory, which is not what a RAG system should do.

</details>

**Exercise 5 · Re-runs without duplicates.** Run `simple_vector_search.py` twice and count the
documents. Then fix it.

<details class="solution"><summary>Solution</summary>

`collection.add` with existing ids keeps the old entries (Chroma warns about duplicate ids), so the
script isn't safe to re-run. Use upsert:

```python
collection.upsert(documents=docs, embeddings=emb, ids=[str(i) for i in range(len(docs))])
print(collection.count())    # stays 5
```

</details>

**Exercise 6 · Your own semantic search.** Build a tiny search over 10 FAQ answers from a product you
know, and test it with 5 questions phrased differently from the answers.

<details class="solution"><summary>Solution outline</summary>

```python
model = SentenceTransformer("all-MiniLM-L6-v2")
faq = ["You can reset your password from Settings → Security.", ...]
faq_vectors = model.encode(faq)

def ask(q, k=2):
    scores = cosine_similarity(model.encode([q]), faq_vectors)[0]
    return [faq[i] for i in scores.argsort()[::-1][:k]]

print(ask("I forgot my login"))     # → the password reset answer
```

</details>

## Full source

<details class="source">
<summary>simple_vector_search.py · Ollama + Chroma</summary>

```{literalinclude} ../code/03-embeddings/simple_vector_search.py
:language: python
```

</details>

<details class="source">
<summary>vsearch.py · search + t-SNE plot</summary>

```{literalinclude} ../code/03-embeddings/vsearch.py
:language: python
```

</details>

<details class="source">
<summary>dense/sentence_transformer.py · rank documents by meaning</summary>

```{literalinclude} ../code/03-embeddings/dense/sentence_transformer.py
:language: python
```

</details>

<details class="source">
<summary>dense/simple_rag.py · retrieve + generate</summary>

```{literalinclude} ../code/03-embeddings/dense/simple_rag.py
:language: python
```

</details>

<details class="source">
<summary>dense/visualizer.py</summary>

```{literalinclude} ../code/03-embeddings/dense/visualizer.py
:language: python
```

</details>

**Downloads:**
{download}`simple_vector_search.py <../code/03-embeddings/simple_vector_search.py>` ·
{download}`visualization.py <../code/03-embeddings/visualization.py>` ·
{download}`vsearch.py <../code/03-embeddings/vsearch.py>` ·
{download}`st_example_1.py <../code/03-embeddings/dense/st_example_1.py>` ·
{download}`cosine_similarity.py <../code/03-embeddings/dense/cosine_similarity.py>` ·
{download}`sentence_transformer.py <../code/03-embeddings/dense/sentence_transformer.py>` ·
{download}`simple_rag.py <../code/03-embeddings/dense/simple_rag.py>` ·
{download}`visualizer.py <../code/03-embeddings/dense/visualizer.py>` ·
{download}`groq_ex.py <../code/03-embeddings/dense/groq_ex.py>`
