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

## Try it yourself

1. Run `1.fixed.py` with sizes 100, 200 and 400. How many chunks contain a cut word?
2. Change `2.overlap.py` to overlap 0, 50 and 100. Count the chunks.
3. In `6.embedding_semantic.py`, try thresholds 0.5 and 0.85. Which gives one chunk per paragraph?
4. Split your own PDF with `RecursiveCharacterTextSplitter` at `chunk_size=500` and print the
   shortest and longest chunk.
5. Write a `paragraph_chunking(text)` that splits on blank lines (`"\n\n"`). Compare it with
   `3.semantic.py`.

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
