
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


def sliding_window_chunking(text, window_size=200, step=100):
    return [text[i:i+window_size] for i in range(0, len(text), step)]

sliding_chunks = sliding_window_chunking(text)

print("\nSliding Window Chunking")
for i, c in enumerate(sliding_chunks):
    print(f"\nChunk {i+1}:\n{c}")
