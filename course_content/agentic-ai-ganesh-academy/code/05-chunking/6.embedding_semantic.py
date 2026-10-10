import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("all-MiniLM-L6-v2")


text = """
Redis is an in-memory data structure store that is commonly used as a database, cache, and message broker. 
It supports various data structures such as strings, lists, sets, sorted sets, hashes, bitmaps, and streams. 
Because Redis stores data in memory, it is extremely fast and is often used in scenarios requiring low latency.

Redis also provides persistence mechanisms like RDB (snapshotting) and AOF (append-only file) to ensure data durability. 
These persistence strategies allow Redis to recover data after restarts, making it reliable for production use cases.

In addition to persistence, Redis supports replication, allowing data to be copied across multiple nodes for high availability. 
It also provides clustering capabilities, enabling horizontal scaling across multiple machines.

Redis is widely used in real-time analytics, caching layers, session storage, and pub/sub messaging systems. 
Its simplicity and performance make it a popular choice among developers building scalable applications.
"""


def semantic_embedding_chunking(sentences, threshold=0.7):
    if not sentences:
        return []

    embeddings = model.encode(sentences)
    
    chunks = []
    current_chunk_sentences = [sentences[0]]
    
    for i in range(1, len(sentences)):

        sim = cosine_similarity([embeddings[i-1]], [embeddings[i]])[0][0]

        print("Current Sentence ", sentences[i])
        print("Previos Sentence ", sentences[i-1])
        print("How related these 2 ", sim, threshold)
        print("\n\n")

        if sim > threshold:
            current_chunk_sentences.append(sentences[i])
        else:
            chunks.append(" ".join(current_chunk_sentences))
            current_chunk_sentences = [sentences[i]]

        print("Chunks ", current_chunk_sentences)
        input("Enter To Proceed")

    if current_chunk_sentences:
        chunks.append(" ".join(current_chunk_sentences))

    return chunks

sentences = text.split("\n")
chunks = semantic_embedding_chunking(sentences)
for chunk in chunks:
    print(chunk)
