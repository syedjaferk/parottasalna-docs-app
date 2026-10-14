"""Without Abstract Factory: the caller picks each piece, so mismatched families are easy."""


class S3Storage:
    def save(self, name, data): print(f"[s3] uploaded {name}")


class LocalQueue:
    def push(self, msg): print(f"[memory] queued {msg}")


storage = S3Storage()
queue = LocalQueue()      # oops: cloud storage with a local queue
storage.save("report.pdf", "...")
queue.push("report ready")  # works on a laptop, the cloud worker never sees the message
