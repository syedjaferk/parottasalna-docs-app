# Session 7 · Retrieval-Augmented Generation (RAG)

## The big idea

An AI model only knows what it read during training. It has never seen **your** PDF, your company
handbook or your notes, and if you ask about them it may confidently make things up.

**RAG** fixes this in three words: **find, then answer**. First **find** the few paragraphs in your
documents that relate to the question, then give them to the model and say *"answer using only
this"*.

**Everyday example:** an open-book exam. You don't memorise the whole textbook. You look up the
right page, read the relevant paragraph, and answer from it. RAG does the same for the AI.

| Option | Problem |
|---|---|
| Just ask the model | it hasn't read your document, so it may invent answers |
| Paste the whole book into the prompt | too long, slow and expensive (the model's input has a size limit) |
| Re-train the model on your book | expensive, slow, has to be redone for every change |
| **RAG: send only the relevant paragraphs** | short, cheap, always up to date ✅ |

## The two halves of RAG

```{raw} html
:file: ../diagrams/s07-pipeline.html
```

- **Indexing (once):** prepare the book so it can be searched quickly.
- **Querying (every question):** find the best paragraphs and answer from them.

The demo answers questions about a Python book (`python.pdf`). Each step is one small function in
`simple_rag.py`.

## Step 1 · Load the PDF

```python
from langchain_community.document_loaders import PyPDFLoader

documents = PyPDFLoader("python.pdf").load()     # one "Document" per page
documents[0].page_content    # the text of page 1
documents[0].metadata        # {'source': 'python.pdf', 'page': 0}
```

## Step 2 · Clean the text

Text from PDFs is messy: double spaces, strange line breaks, invisible characters. Clean it first,
because messy text gives messy search results.

```python
text = re.sub(r"\s+", " ", text)     # many spaces or new lines → one space
text = re.sub(r"\x00", "", text)     # remove invisible "null" characters
text = text.strip()                  # trim the ends
```

**Before:** `"Python   is\n\n a  language\x00"` → **After:** `"Python is a language"`

## Step 3 · Cut into chunks

A whole page is too big to send, and a single sentence is too small to make sense. So we cut the
text into **chunks** of about 1,000 characters (roughly a long paragraph).

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
chunks = splitter.split_documents(documents)
```

**Overlap** means each chunk repeats the last 150 characters of the one before it. If a sentence is
cut in half at the edge, it still appears whole in one of the chunks.

```{raw} html
:file: ../diagrams/s07-chunks.html
```

"Recursive" means it tries to cut at nice places first: paragraphs, then lines, then sentences,
and only cuts in the middle of a word as a last resort.

:::{tip}
Chunk size matters a lot. **Too small:** a chunk loses its meaning ("it returns a list". What
does?). **Too big:** search gets fuzzy and prompts get expensive. 500–1,000 characters is a good
start.
:::

## Step 4 · Embeddings: turning meaning into numbers

Computers can't compare *meanings* directly, but they can compare numbers. An **embedding model**
turns a piece of text into a long list of numbers, like **map coordinates for meaning**. Texts that
mean similar things get coordinates **close together**, even if they use different words.

```{raw} html
:file: ../diagrams/s07-embeddings.html
```

We create embeddings **on your own computer** with Ollama, so the book never leaves it:

```python
from langchain_ollama import OllamaEmbeddings

embeddings = OllamaEmbeddings(model="nomic-embed-text")
embeddings.embed_query("for loop")    # [0.012, -0.034, 0.051, ...] ← 768 numbers
```

## Step 5 · Store them in a vector database

A **vector database** stores every chunk with its numbers and can quickly find the chunks closest
to a question. We use **Chroma**, which saves to a folder on disk:

```python
from langchain_chroma import Chroma

if os.path.exists("./chromadb"):       # already built? just open it (fast)
    vectorstore = Chroma(collection_name="pdf_rag_collection",
                         persist_directory="./chromadb", embedding_function=embeddings)
else:                                  # first time: embed every chunk and save (slow)
    vectorstore = Chroma.from_documents(documents=chunks, embedding=embeddings,
                                        collection_name="pdf_rag_collection",
                                        persist_directory="./chromadb")
```

## Step 6 · Find the best chunks for a question

```python
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})    # k = how many chunks
docs = retriever.invoke(f"search_query: {question}")
context = "\n\n".join(doc.page_content for doc in docs)          # glue them together
```

(`search_query:` is a small label this particular embedding model expects in front of questions.)

## Step 7 · Ask the model, using only those chunks

```python
prompt = f"""
Answer the question using ONLY the context below. If the answer is not in the
context, say you don't know.
Context: {context}
Question: {question}
Answer:
"""
answer = ChatGroq(model="openai/gpt-oss-120b", temperature=0).invoke(prompt).content
```

The two key instructions are **"ONLY the context"** (don't use outside knowledge) and **"say you
don't know"** (permission not to guess).

**Example:**

```text
Ask a question: How do I remove duplicates from a list?
The book suggests converting the list to a set: list(set(my_list)). Note that this does not keep
the original order.
```

## Common mistakes in the class version

:::{warning}
- **The PDF is re-read on every run.** The code loads and chunks the PDF *before* checking whether
  `./chromadb` already exists. Check first, and only load the PDF when you need to build the database.
- **Changing the PDF doesn't update the database.** Delete the `chromadb/` folder to rebuild it.
- **Missing label on the chunks.** `nomic-embed-text` expects `search_document:` in front of each
  chunk, to match `search_query:` on questions. Adding it usually improves the search.
- **No sources shown.** Every chunk knows its page number (`doc.metadata["page"]`). Show it, so
  readers can check the answer.
:::

## Try it yourself

1. Change `k` to 2 and then to 8. Ask the same three questions. When do the answers get better or worse?
2. Change `initial_setup()` so the PDF is only loaded when `./chromadb` doesn't exist.
3. Print the page numbers under each answer: `sorted({d.metadata.get("page") for d in docs})`.
4. Ask something that's **not** in the book. Does it say "I don't know"? Remove that line from the
   prompt and ask again. What happens?

## Full source

You can use any PDF. The class used a Python book saved as `python.pdf` next to the script.

<details class="source">
<summary>simple_rag.py</summary>

```{literalinclude} ../code/07-rag/simple_rag.py
:language: python
```

</details>

{download}`Download simple_rag.py <../code/07-rag/simple_rag.py>` ·
{download}`.env example <../code/07-rag/env.example>`
