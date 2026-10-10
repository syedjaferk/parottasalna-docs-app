# Session 5 · Chunking

## The big idea

You can't embed a whole 300-page PDF as one vector. Its meaning gets averaged into mush, and it
wouldn't fit in the model's prompt anyway. So we cut documents into **chunks**: small pieces that
each hold one idea. Retrieval then finds the few chunks that answer the question.

**Everyday example:** a textbook has chapters, sections and paragraphs. When you revise, you don't
re-read the book, you flip to the right paragraph. Chunks are those paragraphs.

**The trade-off:**

| Chunks too big | Chunks too small |
|---|---|
| one chunk mixes several topics, so its vector is vague | a chunk loses its context ("it supports this…" — what is *it*?) |
| fewer chunks fit in the prompt | the answer gets spread over many chunks |

All the chunking scripts cut the same Redis text (~1,100 characters) so you can compare them.

```{raw} html
:file: ../diagrams/s05-chunking.html
```

## 1 · Fixed size

Cut every 200 characters, no matter what (`1.fixed.py`):

```python
def fixed_chunking(text, chunk_size=200):
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]
```

```text
Chunk 1: … sorted sets, hashes, bitma
Chunk 2: ps, and streams. Because Redis stores data in memory …
```

**6 chunks.** Simple and fast, but it cuts words ("bitma" | "ps") and sentences in half.

## 2 · Fixed size with overlap

Each chunk repeats the last 50 characters of the one before (`2.overlap.py`):

```python
start += chunk_size - overlap     # move forward 150, not 200
```

**7 chunks.** A sentence cut at the end of one chunk appears whole at the start of the next, so
fewer ideas are lost at the edges. The cost: some text is stored twice.

## 3 · Sliding window

The same idea with a bigger overlap: a 200-character window moving 100 at a time (`4.sliding.py`).
**11 chunks.** Very safe at the edges, but it stores everything twice. (The last chunks are short
tails. Try to spot them in the output.)

## 4 · Sentence-based ("rule-based semantic")

Split into **sentences** first with NLTK, then pack whole sentences into chunks up to 200
characters (`3.semantic.py`):

```python
sentences = sent_tokenize(text)
for s in sentences:
    if len(current) + len(s) < max_chunk_size:
        current += " " + s
    else:
        chunks.append(current.strip())
        current = s
```

No sentence is ever cut in half.

## 5 · Token-based

Models count **tokens**, not characters (a token is roughly ¾ of a word). `5.token.py` uses
`tiktoken` to cut every 50 tokens:

```python
enc = tiktoken.get_encoding("cl100k_base")
tokens = enc.encode(text)
chunks = [enc.decode(tokens[i:i + 50]) for i in range(0, len(tokens), 50)]
```

**4 chunks.** Useful when you must stay under a model's exact token limit.

## 6 · Embedding-based semantic chunking

Start a **new chunk when the topic changes** (`6.embedding_semantic.py`). Embed each line and
compare it with the line before:

```python
sim = cosine_similarity([embeddings[i-1]], [embeddings[i]])[0][0]
if sim > threshold:                       # still the same topic
    current_chunk_sentences.append(sentences[i])
else:                                     # topic changed → close the chunk
    chunks.append(" ".join(current_chunk_sentences))
    current_chunk_sentences = [sentences[i]]
```

The script pauses after each step (`Enter To Proceed`) so you can watch the similarity scores. The
best chunks, but the slowest: every sentence needs an embedding.

## What LangChain uses: RecursiveCharacterTextSplitter

From the next session on we use LangChain's splitter. It tries to cut at **paragraphs** first, then
**lines**, then **sentences/words**, and only cuts mid-word as a last resort:

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)
chunks = splitter.split_documents(documents)
```

A good default for most projects.

## Reading PDFs

`7.pdf_reader.py` loads a PDF page by page and cleans the text:

```python
loader = PyPDFLoader("python.pdf")
documents = loader.load()               # one Document per page, with metadata {"page": 11, ...}

def clean_text(text):
    text = text.encode("utf-8", "ignore").decode("utf-8")   # drop broken characters
    text = re.sub(r'\s+', ' ', text)                        # many spaces/newlines → one space
    return text.strip()
```

PDFs often contain odd characters and hard line breaks in the middle of sentences. Cleaning them
first gives better chunks and better embeddings.

## Which one should I use?

| Situation | Start with |
|---|---|
| a quick prototype | `RecursiveCharacterTextSplitter`, size 500–1000, overlap 10–20 % |
| strict token budget | token-based |
| documents that jump between topics | embedding-based semantic |
| clean prose with good sentences | sentence-based |

## Common mistakes

- **No overlap.** Answers that sit across a chunk border get lost.
- **Huge chunks "to be safe".** The vector becomes vague and retrieval gets worse, not better.
- **Cleaning after splitting.** Clean the text first, then split. Otherwise chunk sizes are wrong.
- **`clean_text` removes all newlines.** That's fine for embeddings, but you can no longer split on
  `"\n"` afterwards (we hit this in [Session 10](10-better-queries-and-smaller-context.md)).

## Hands-on exercises

Try each one before opening the solution.

**Exercise 1 · Chunk size.** Run `1.fixed.py` with sizes 100, 200 and 400. How many chunks start or
end in the middle of a word?

<details class="solution"><summary>What to notice</summary>

Almost every border cuts a word at every size; smaller chunks simply have more borders. Fixed-size
chunking only works well with overlap, or for text where exact boundaries don't matter.

</details>

**Exercise 2 · Overlap.** Run `2.overlap.py` with overlap 0, 50 and 100 (chunk size 200).

<details class="solution"><summary>Answer</summary>

Each step moves forward `200 - overlap` characters, so the chunk count grows with overlap: roughly
`len(text) / (200 - overlap)`. On the ~1,100-character Redis text: about 6, 7 and 11 chunks.

</details>

**Exercise 3 · Semantic threshold.** In `6.embedding_semantic.py`, try thresholds 0.5 and 0.85.

<details class="solution"><summary>What to notice</summary>

A low threshold keeps adding lines to the current chunk (few, big chunks). A high one starts a new
chunk at almost every line (many tiny chunks). Find the value where each chunk is one paragraph:
persistence, replication, use cases. Remove the `input(...)` line first to run it straight through.

</details>

**Exercise 4 · Paragraph chunking.** Write `paragraph_chunking(text, max_chars=500)` that splits on
blank lines and merges short paragraphs.

<details class="solution"><summary>Solution</summary>

```python
def paragraph_chunking(text, max_chars=500):
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks, current = [], ""
    for p in paragraphs:
        if current and len(current) + len(p) + 2 > max_chars:
            chunks.append(current)
            current = p
        else:
            current = f"{current}\n\n{p}" if current else p
    if current:
        chunks.append(current)
    return chunks
```

</details>

**Exercise 5 · Your PDF.** Split your own PDF with `RecursiveCharacterTextSplitter(chunk_size=500,
chunk_overlap=50)` and print the shortest and longest chunks.

<details class="solution"><summary>Solution</summary>

```python
pages = PyPDFLoader("python.pdf").load()
chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_documents(pages)
sizes = sorted(chunks, key=lambda c: len(c.page_content))
print(len(chunks), "chunks")
print("shortest:", repr(sizes[0].page_content))
print("longest :", len(sizes[-1].page_content), "chars")
```

Very short chunks are usually page headers or footers. Filtering out chunks under ~50 characters
often improves retrieval.

</details>

**Exercise 6 · Tokens vs characters.** Count the tokens in each 200-character fixed chunk with
`tiktoken`.

<details class="solution"><summary>Solution</summary>

```python
enc = tiktoken.get_encoding("cl100k_base")
for c in fixed_chunking(text):
    print(len(c), "chars →", len(enc.encode(c)), "tokens")
```

English averages about 4 characters per token, so ~200 characters is ~45 tokens. Tamil and other
scripts use many more tokens per character, so measure in tokens when you have a budget.

</details>

## Full source

<details class="source">
<summary>2.overlap.py</summary>

```{literalinclude} ../code/05-chunking/2.overlap.py
:language: python
```

</details>

<details class="source">
<summary>3.semantic.py</summary>

```{literalinclude} ../code/05-chunking/3.semantic.py
:language: python
```

</details>

<details class="source">
<summary>6.embedding_semantic.py</summary>

```{literalinclude} ../code/05-chunking/6.embedding_semantic.py
:language: python
```

</details>

**Downloads:**
{download}`1.fixed.py <../code/05-chunking/1.fixed.py>` ·
{download}`2.overlap.py <../code/05-chunking/2.overlap.py>` ·
{download}`3.semantic.py <../code/05-chunking/3.semantic.py>` ·
{download}`4.sliding.py <../code/05-chunking/4.sliding.py>` ·
{download}`5.token.py <../code/05-chunking/5.token.py>` ·
{download}`6.embedding_semantic.py <../code/05-chunking/6.embedding_semantic.py>` ·
{download}`7.pdf_reader.py <../code/05-chunking/7.pdf_reader.py>`
