# Session 11 · Advanced retrievers

## The big idea

So far, **what we search** and **what we give the LLM** were the same chunk. Separating them helps
a lot:

- **Parent document retriever**: search **small** chunks (precise), return their **big** parent
  (complete).
- **Multi-vector retriever**: search **summaries, keywords and likely questions** about a chunk,
  return the original chunk.
- **Multi-hop retrieval**: when one search isn't enough, use the first result to search again.

**Everyday example:** a book index. You look up one word (small and precise), but you read the
whole page it points to (big and complete).

## Parent document retriever

The dilemma from Session 5: small chunks match precisely, big chunks give the LLM enough context.
Why not both?

```text
PDF pages ──► parents (3,000 chars) ──► stored in a docstore (not embedded)
                     │
                     └──► children (300 chars) ──► embedded in Chroma (searched)

question ──► nearest CHILDREN ──► look up their PARENTS ──► LLM
```

```{raw} html
:file: ../diagrams/s11-parent.html
```

From `parent_retriever.py`:

```python
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=200)
child_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)

retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,      # Chroma: holds the child vectors
    docstore=docstore,            # InMemoryStore: holds the full parents
    child_splitter=child_splitter,
    parent_splitter=parent_splitter,
)
retriever.add_documents(clean_docs)

docs = retriever.invoke("How do list comprehensions work?")   # returns parents
```

:::{note}
`ParentDocumentRetriever` and `MultiVectorRetriever` now live in the **`langchain-classic`**
package (`from langchain_classic.retrievers import ParentDocumentRetriever`). The class code used
the old `langchain.retrievers` path, which no longer exists in LangChain 1.x.
:::

The docstore here is `InMemoryStore`, so the parents are lost when the script stops, while the
child vectors stay in `./vectorstore`. In a real app, use a persistent store (Redis, a database)
for the parents too.

## Multi-vector retriever

A question is phrased differently from the text that answers it. So for each chunk, generate
several **representations** that are easier to match, and embed those instead (`multi_vector.py`):

```python
for d in clean_docs[:10]:                       # first 10 pages, to keep the demo quick
    did = str(uuid.uuid4())
    parents.append((did, d))
    summary_docs.append(Document(page_content=summarize(d.page_content),
                                 metadata={"doc_id": did, "type": "summary"}))
    keyword_docs.append(Document(page_content=keywords(d.page_content),
                                 metadata={"doc_id": did, "type": "keywords"}))
    question_docs.append(Document(page_content=questions(d.page_content),
                                  metadata={"doc_id": did, "type": "questions"}))

vectorstore.add_documents(summary_docs)         # search these …
vectorstore.add_documents(keyword_docs)
vectorstore.add_documents(question_docs)
store.mset(parents)                             # … return these
```

When a question matches *"What is a Python variable?"* (one of the generated questions), the
retriever follows the shared `doc_id` and returns the **original page**.

This costs **3 LLM calls per chunk** at ingest time, so it suits small, valuable document sets
(FAQs, policies), not millions of pages.

## Multi-hop retrieval

Some answers need a chain of facts (`data.txt`):

```text
Amazon S3 stores objects.
S3 supports Lifecycle Policies.
Lifecycle Policies automatically move old objects to Glacier.
Amazon Glacier is a low-cost archive storage.
Glacier has Flexible Retrieval and Deep Archive storage classes.
Deep Archive is the cheapest storage option.
```

*"How does S3 reduce storage cost?"* The first search finds the lifecycle sentences, but the cost
facts are about **Glacier**, which the question never mentions. That needs a second hop:

```text
hop 1: "How does S3 reduce storage cost?"   → "Lifecycle Policies … move old objects to Glacier."
hop 2: "Glacier storage cost"                → "Amazon Glacier is a low-cost archive storage." …
answer from both hops
```

```{raw} html
:file: ../diagrams/s11-multihop.html
```

`multi_hop.py` from class does **hop 1** only. Building hop 2 is the first exercise below. The usual
way is to ask the LLM: *"Given these facts, what should we search next to answer the question?"*

## Common mistakes

- **Parent chunks too big.** If parents are 10,000 characters and you retrieve 4, the prompt
  explodes. Keep `k × parent size` within your budget.
- **Mixing summaries and originals.** With multi-vector, make sure the LLM receives the
  **originals** (what the retriever returns), not the summaries.
- **Unlimited hops.** Multi-hop needs a stop rule (max 2–3 hops, or "stop when the LLM says it has
  enough").
- **Chunk size 100 on real text.** It works for the one-fact-per-line `data.txt`, but is far too
  small for a book.

## Hands-on exercises

Try each one before opening the solution.

**Exercise 1 · The second hop.** Extend `multi_hop.py`: ask Groq what to search next, retrieve again,
and answer from both hops.

<details class="solution"><summary>Solution</summary>

```python
import os
from langchain_groq import ChatGroq

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0, api_key=os.environ["GROQ_API_KEY"])

facts = "\n".join(d.page_content for d in first_docs)
next_query = llm.invoke(
    f"Question: {question}\nFacts so far:\n{facts}\n"
    "What should we search for next to answer the question? Reply with the search query only."
).content.strip()                                   # e.g. "Glacier storage cost"

second_docs = retriever.invoke(next_query)
context = "\n".join(d.page_content for d in first_docs + second_docs)
print(llm.invoke(f"Answer only from this context:\n{context}\n\nQuestion: {question}").content)
```

</details>

**Exercise 2 · Child and parent.** For one question, print the child chunk that matched and the
start of its parent.

<details class="solution"><summary>Solution</summary>

```python
child = vectorstore.similarity_search("How do list comprehensions work?", k=1)[0]
parent_id = child.metadata["doc_id"]
parent = docstore.mget([parent_id])[0]
print("CHILD :", child.page_content)
print("PARENT:", parent.page_content[:500], "…")
```

The child is ~300 characters; the parent ~3,000. That's what the LLM receives.

</details>

**Exercise 3 · Parent size.** Try parents of 1,500 and 6,000 characters.

<details class="solution"><summary>What to notice</summary>

Smaller parents give focused but sometimes incomplete answers; bigger parents give complete answers
but a much longer prompt (4 parents × 6,000 characters is ~6,000 tokens). Pick the size of a
"section" in your documents.

</details>

**Exercise 4 · Questions only.** In `multi_vector.py`, index only the generated questions.

<details class="solution"><summary>What to notice</summary>

Comment out the summary and keyword `add_documents` lines. For "how do I…" and "what is…" questions,
retrieval often gets **better**, because the indexed text has the same shape as the user's question.
For keyword-style searches ("dict methods"), the keyword representation helped more.

</details>

**Exercise 5 · Keep the parents.** Make the parent store survive a restart.

<details class="solution"><summary>Solution</summary>

```python
from langchain_classic.storage import LocalFileStore, create_kv_docstore

docstore = create_kv_docstore(LocalFileStore("./parents"))
retriever = ParentDocumentRetriever(vectorstore=vectorstore, docstore=docstore,
                                    child_splitter=child_splitter, parent_splitter=parent_splitter)
```

The parents are now saved as files in `./parents`, next to the child vectors in `./vectorstore`.
Index once, then remove `retriever.add_documents(...)` on later runs.

</details>

## Full source

<details class="source">
<summary>parent_retriever.py</summary>

```{literalinclude} ../code/11-advanced-retrievers/parent_retriever.py
:language: python
```

</details>

<details class="source">
<summary>multi_vector.py</summary>

```{literalinclude} ../code/11-advanced-retrievers/multi_vector.py
:language: python
```

</details>

<details class="source">
<summary>multi_hop.py</summary>

```{literalinclude} ../code/11-advanced-retrievers/multi_hop.py
:language: python
```

</details>

**Downloads:**
{download}`parent_retriever.py <../code/11-advanced-retrievers/parent_retriever.py>` ·
{download}`multi_vector.py <../code/11-advanced-retrievers/multi_vector.py>` ·
{download}`multi_hop.py <../code/11-advanced-retrievers/multi_hop.py>` ·
{download}`data.txt <../code/11-advanced-retrievers/data.txt>`
