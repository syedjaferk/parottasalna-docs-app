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

## Try it yourself

1. Run `faiss/query.py` and ask three questions. Are the 3 chunks relevant? Try `k=1` and `k=8`.
2. In `langchain/retrieval.py`, also print each chunk's `doc.metadata["page"]`. Add the page
   numbers to the final answer as sources.
3. Change `augmentation.py` so it says *"I couldn't find that in the book"* when the answer isn't in
   the context. Test it with a question about cooking.
4. Make `ingest.py` safe to run twice: give chunks ids like `f"page{page}-chunk{i}"` and pass
   `ids=` to `Chroma.from_documents`.
5. Swap `IndexFlatL2` for `IndexFlatIP` with normalised embeddings (`normalize_embeddings=True` in
   `encode`). Do the results change?

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
