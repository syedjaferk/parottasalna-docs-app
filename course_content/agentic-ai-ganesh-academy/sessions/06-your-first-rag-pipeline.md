# Session 6 · Your first RAG pipeline

## The big idea

RAG has two halves that run at different times:

```text
INGEST (once, or when documents change)
  PDF → clean text → chunks → embeddings → vector database

ASK (every question)
  question → embedding → nearest chunks → prompt with those chunks → LLM → answer
```

**R**etrieve the right chunks, **A**ugment the prompt with them, **G**enerate the answer.

**Everyday example:** an open-book exam. Ingest is putting sticky notes in the book. Asking is
flipping to the right notes and writing the answer in your own words.

```{raw} html
:file: ../diagrams/s06-pipeline.html
```

We built it twice: once **by hand** with FAISS, so you see every step, and once with **LangChain
+ Chroma**, the way most projects do it.

## Version 1 · By hand with FAISS

### build_index.py: ingest

```python
text = extract_text("python.pdf")                    # pypdf, page by page
chunks = create_chunks(text, 500)                    # fixed 500-character chunks
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
embeddings = model.encode(chunks, batch_size=32, show_progress_bar=True)

index = faiss.IndexFlatL2(embeddings.shape[1])       # 384-dimensional, Euclidean distance
index.add(embeddings)
faiss.write_index(index, "rag.index")                # the vectors
with open("chunks.pkl", "wb") as f:
    pickle.dump(chunks, f)                           # the text, in the same order
```

FAISS stores **only vectors**. Result number 7 means "the 7th vector", so we save the chunk texts in
the same order to look them up again.

### query.py: retrieve

```python
query_embedding = model.encode([query])
distances, indices = index.search(query_embedding, k=3)
for idx in indices[0]:
    print(chunks[idx])
```

This prints the 3 most relevant chunks. There's no LLM yet: this is the **R** of RAG on its own,
and it's worth checking it finds good chunks before adding generation.

## Version 2 · LangChain + Chroma

Three small files, one per step.

### ingest.py

```python
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)
documents = PyPDFLoader("./python.pdf").load()
# … clean_text() each page …
chunks = splitter.split_documents(clean_docs)

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
db = Chroma.from_documents(chunks, embeddings, persist_directory="./chroma_db")
```

Chroma keeps the **text and metadata** (like the page number) next to each vector, so there's no
separate pickle file.

### retrieval.py

```python
db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

def retrieval(query):
    docs = db.similarity_search(query, k=3)
    return "\n".join(doc.page_content for doc in docs)
```

### augmentation.py: the prompt

```python
PROMPT = """
You are a Python Expert

Use only provided context.

Context :
    {context}

Question:
    {query}

Answer:
"""
context = retrieval(user_query)
prompt = PROMPT.format(context=context, query=user_query)
response = call_groq([{"role": "system", "content": "You are a helpful AI assistant."},
                      {"role": "user", "content": prompt}])
```

*"Use only provided context"* is the important line: it tells the model to answer from **your**
book, not its memory.

:::{note}
The class code imported `Chroma` and `HuggingFaceEmbeddings` from `langchain_community`. On this
page they come from `langchain_chroma` and `langchain_huggingface`, the current packages. They work
the same way, and Chroma now saves to `persist_directory` automatically, so `db.persist()` is gone.
:::

## When documents change

A real knowledge base changes: a policy is updated, a page is removed. The vector database must
follow, or the bot keeps quoting old text. The usual pattern:

1. Give every chunk a **stable id**, made from the source and position, for example
   `f"{file_name}:{page}:{chunk_no}"`.
2. Keep a **hash** (fingerprint) of each source file. On the next ingest, skip files whose hash
   hasn't changed.
3. For a changed file: **delete all its old chunks** (`collection.delete(where={"source": file_name})`)
   and insert the new ones. Deleting first matters: if the new version has fewer chunks, the extra
   old ones would otherwise stay behind.
4. For a deleted file: delete its chunks.

## Common mistakes

- **Rebuilding the index on every run.** Ingest once, then only query. (Running `ingest.py` twice
  stores everything twice.)
- **The chunk list and the FAISS index get out of order.** Always save and load them together.
- **No "I don't know" instruction.** Without it, the model happily answers from memory when
  retrieval finds nothing useful.
- **Judging RAG only by the final answer.** Print the retrieved chunks first. Most bad answers are
  bad retrieval.

## Hands-on exercises

Try each one before opening the solution.

**Exercise 1 · Test retrieval first.** Run `faiss/query.py`, ask three questions, and try `k=1` and
`k=8`.

<details class="solution"><summary>What to notice</summary>

With `k=1` a good answer depends on one lucky chunk. With `k=8` you see more of the topic, but also
unrelated chunks that would distract an LLM. Most pipelines start at 3–5.

</details>

**Exercise 2 · Show sources.** Print the page number of each chunk, and add the pages to the final
answer.

<details class="solution"><summary>Solution</summary>

```python
def retrieval(query):
    docs = db.similarity_search(query, k=3)
    pages = sorted({d.metadata.get("page", 0) + 1 for d in docs})   # PyPDFLoader counts from 0
    context = "\n".join(d.page_content for d in docs)
    return context, pages

context, pages = retrieval(user_query)
...
print(response)
print("Sources: pages", ", ".join(map(str, pages)))
```

</details>

**Exercise 3 · An honest bot.** Make `augmentation.py` reply *"I couldn't find that in the book"*
for off-topic questions.

<details class="solution"><summary>Solution</summary>

```python
PROMPT = """
You are a Python Expert.
Use ONLY the context. If the context does not contain the answer, reply exactly:
I couldn't find that in the book.

Context:
{context}

Question:
{query}
"""
```

Test with *"How do I make dosa?"*.

</details>

**Exercise 4 · Safe re-runs.** Make `langchain/ingest.py` safe to run twice.

<details class="solution"><summary>Solution</summary>

```python
ids = [f"python.pdf:{c.metadata.get('page')}:{i}" for i, c in enumerate(chunks)]
db = Chroma.from_documents(chunks, embeddings, ids=ids, persist_directory="./chroma_db")
```

Same ids on the next run overwrite instead of duplicating. Check with
`db._collection.count()` before and after.

</details>

**Exercise 5 · Update one document.** Write `reingest(file_name)` that removes a file's old chunks and
adds the new ones.

<details class="solution"><summary>Solution</summary>

```python
def reingest(path):
    pages = PyPDFLoader(path).load()
    chunks = splitter.split_documents(pages)       # metadata["source"] == path
    db.delete(where={"source": path})              # 1. remove every old chunk of this file
    db.add_documents(chunks)                       # 2. add the new version
```

Delete first: if the new file is shorter, its old extra chunks would otherwise stay forever.

</details>

**Exercise 6 · L2 vs inner product.** Swap `IndexFlatL2` for `IndexFlatIP` with normalised
embeddings. Do the results change?

<details class="solution"><summary>Answer</summary>

```python
embeddings = model.encode(chunks, normalize_embeddings=True)
index = faiss.IndexFlatIP(embeddings.shape[1])
...
query_embedding = model.encode([query], normalize_embeddings=True)
```

The ranking is the same. For unit-length vectors, a smaller L2 distance and a larger dot product
(= cosine similarity) mean the same thing. Only the scores change: higher is now better.

</details>

## Full source

<details class="source">
<summary>faiss/build_index.py</summary>

```{literalinclude} ../code/06-first-rag/faiss/build_index.py
:language: python
```

</details>

<details class="source">
<summary>faiss/query.py</summary>

```{literalinclude} ../code/06-first-rag/faiss/query.py
:language: python
```

</details>

<details class="source">
<summary>langchain/ingest.py</summary>

```{literalinclude} ../code/06-first-rag/langchain/ingest.py
:language: python
```

</details>

<details class="source">
<summary>langchain/retrieval.py</summary>

```{literalinclude} ../code/06-first-rag/langchain/retrieval.py
:language: python
```

</details>

<details class="source">
<summary>langchain/augmentation.py</summary>

```{literalinclude} ../code/06-first-rag/langchain/augmentation.py
:language: python
```

</details>

**Downloads:**
{download}`build_index.py <../code/06-first-rag/faiss/build_index.py>` ·
{download}`query.py <../code/06-first-rag/faiss/query.py>` ·
{download}`ingest.py <../code/06-first-rag/langchain/ingest.py>` ·
{download}`retrieval.py <../code/06-first-rag/langchain/retrieval.py>` ·
{download}`augmentation.py <../code/06-first-rag/langchain/augmentation.py>`
