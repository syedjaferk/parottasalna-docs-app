# Session 4 · Sparse, dense and hybrid search

## The big idea

There are two ways to find matching text:

- **Sparse (keyword) search** counts *words*. Great for exact terms: product codes, error messages,
  names like `PostgreSQL 14`.
- **Dense (embedding) search** compares *meaning* (Session 3). Great for "reduce body fat" ≈ "fat
  loss tips".

Each fails where the other shines, so real systems often use **both** at once: **hybrid search**.

**Everyday example:** finding a song. If you remember the exact title, search by name (sparse). If
you only remember "that sad song about rain", you need someone who understands meaning (dense).

## Sparse vectors, step by step

### 1. One-hot: is the word there or not?

`01.basic_sparse.py` gives each known word a slot and writes 1 if the sentence contains it:

```python
vocabulary = {"python": 0, "redis": 1, "fastapi": 2, "docker": 3, "database": 4}
sentence = "python fastapi application. fastapi is a nice framework. "
```

```text
Sparse Vector:
[1, 0, 1, 0, 0]
```

"Sparse" because, with a real vocabulary of 50,000 words, almost every slot is 0.

### 2. Term frequency (TF): how often?

```python
document = "Redis is an in-memory database database database"
```

```text
{'Redis': 0.142…, 'is': 0.142…, 'an': 0.142…, 'in-memory': 0.142…, 'database': 0.428…}
```

TF = (times the word appears) ÷ (words in the document). "database" appears 3 times out of 7.

### 3. Inverse document frequency (IDF): how rare?

A word that's in *every* document tells you nothing. `05.idf_implementation.py` uses
IDF = log(N ÷ documents containing the word), over 5 documents that all mention Python:

```text
python -> 0.0      ← in all 5 documents: useless for ranking
redis -> 0.916     ← in 2 of 5
docker -> 1.609    ← in 1 of 5: very informative
```

### 4. TF-IDF = TF × IDF

High when a word is frequent **here** but rare **elsewhere**. scikit-learn does it in two lines
(`06.tf_idf.py`):

```python
vectorizer = TfidfVectorizer()
document_vectors = vectorizer.fit_transform(documents)
```

Now search for `"db"`:

```text
Score: 0.0000    (for every document)
```

All zero! Every document says "database", but none says "db". **This is the weakness of sparse
search**: no shared word, no match.

### 5. BM25: TF-IDF, improved

BM25 is what search engines (Elasticsearch, OpenSearch) use by default. It stops rewarding a word
after it has appeared a few times, and it doesn't let long documents win just for being long
(`08.bm25.py`):

```python
bm25 = BM25Okapi(tokenized_documents)
scores = bm25.get_scores("database for caching".lower().split())
```

```text
Redis Introduction    BM25 Score: 1.5083
PostgreSQL Guide      BM25 Score: 0.3610
Vector Databases      BM25 Score: 0.2328
```

Redis wins because it's the only one that contains **both** "database" and "caching".

## Dense vs sparse, side by side

`comparison_dense_sparse.py` (in Session 3's folder) asks *"How to reduce body fat?"* against
"Tips for fat loss", "Python programming tutorial" and "Healthy diet plans".

- **TF-IDF** only matches the word "fat", so "Tips for fat loss" gets a small score and the diet
  plan gets **0**.
- **Dense** understands that diet plans are related too, and scores both health documents well
  above the Python tutorial.

## Hybrid search: use both

`10.hybrid.py` adds the two scores together:

```python
bm25_scores = bm25.get_scores(query.lower().split())
dense_scores = cosine_similarity(model.encode([query]), doc_embeddings)[0]

hybrid_scores = 0.5 * np.array(bm25_scores) + 0.5 * np.array(dense_scores)
```

:::{warning}
BM25 scores can be 0–10 or more, while cosine is −1 to 1. Adding them raw lets BM25 dominate.
**Normalise first**, for example divide each list by its maximum, or combine **ranks** instead of
scores (Reciprocal Rank Fusion: `score = Σ 1 / (60 + rank)`).
:::

## Hybrid search in OpenSearch

`11.open_search_hybrid.py` loads a movie dataset into **OpenSearch**, a real search engine that
does both kinds:

- a `knn_vector` field holds each movie's embedding (dense)
- normal `text` fields are searched with BM25 (sparse)
- a `hybrid` query runs both and merges the results

Start OpenSearch first (see [Setup](../setup.md)). The script gives you a menu: 1 sparse, 2 dense,
3 hybrid. Try *"chess girl"* in all three, then *"a smart child who wins at a board game"*.

For properly balanced hybrid scores, OpenSearch expects a **search pipeline** with a normalisation
processor. Without one, the raw scores aren't comparable (the same problem as the warning above).

:::{note}
The class used a scraped IMDb file. This page uses `movies_sample.csv`: 16 made-up movies with the
same columns, so you can share and change it freely.
:::

## Common mistakes

- **Using only dense search for codes and names.** "Error E1042" or "iPhone 15 Pro" are better
  found by keywords.
- **Fitting the TF-IDF vectorizer on the query.** `fit_transform` on your documents, then only
  `transform` the query, as `06.tf_idf.py` does.
- **Adding BM25 and cosine scores without normalising them.**
- **Not lowercasing or removing punctuation.** `"Redis,"` and `"redis"` become different words.

## Try it yourself

1. In `06.tf_idf.py`, search `"in-memory"`, then `"memory"`. Why do they score differently?
   (Look at how the default tokenizer splits `in-memory`.)
2. Add `"database"` to every document in `05.idf_implementation.py`. What happens to its IDF?
3. Change `10.hybrid.py` to normalise both score lists to 0–1 before adding them. Does the ranking
   change?
4. Try weights `0.2 / 0.8` and `0.8 / 0.2` in `10.hybrid.py`. Which queries prefer which?
5. Add three of your own movies to `movies_sample.csv` and find them with each search mode in
   `11.open_search_hybrid.py`.

## Full source

<details class="source">
<summary>05.idf_implementation.py</summary>

```{literalinclude} ../code/04-sparse-hybrid/05.idf_implementation.py
:language: python
```

</details>

<details class="source">
<summary>08.bm25.py</summary>

```{literalinclude} ../code/04-sparse-hybrid/08.bm25.py
:language: python
```

</details>

<details class="source">
<summary>10.hybrid.py</summary>

```{literalinclude} ../code/04-sparse-hybrid/10.hybrid.py
:language: python
```

</details>

<details class="source">
<summary>11.open_search_hybrid.py</summary>

```{literalinclude} ../code/04-sparse-hybrid/11.open_search_hybrid.py
:language: python
```

</details>

**Downloads:**
{download}`01.basic_sparse.py <../code/04-sparse-hybrid/01.basic_sparse.py>` ·
{download}`02.token_weights.py <../code/04-sparse-hybrid/02.token_weights.py>` ·
{download}`03.tf_implementation.py <../code/04-sparse-hybrid/03.tf_implementation.py>` ·
{download}`04.tf_with_movie_dataset.py <../code/04-sparse-hybrid/04.tf_with_movie_dataset.py>` ·
{download}`05.idf_implementation.py <../code/04-sparse-hybrid/05.idf_implementation.py>` ·
{download}`06.tf_idf.py <../code/04-sparse-hybrid/06.tf_idf.py>` ·
{download}`07.tf_idf_movie_dataset.py <../code/04-sparse-hybrid/07.tf_idf_movie_dataset.py>` ·
{download}`08.bm25.py <../code/04-sparse-hybrid/08.bm25.py>` ·
{download}`09.cosine_similarity_sparse.py <../code/04-sparse-hybrid/09.cosine_similarity_sparse.py>` ·
{download}`10.hybrid.py <../code/04-sparse-hybrid/10.hybrid.py>` ·
{download}`11.open_search_hybrid.py <../code/04-sparse-hybrid/11.open_search_hybrid.py>` ·
{download}`comparison_dense_sparse.py <../code/03-embeddings/dense/comparison_dense_sparse.py>` ·
{download}`movies_sample.csv <../code/04-sparse-hybrid/movies_sample.csv>`
