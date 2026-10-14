"""Abstract Factory: one factory per family, so every object it makes belongs together."""
from abc import ABC, abstractmethod


class Storage(ABC):
    @abstractmethod
    def save(self, name: str, data: str): ...


class Queue(ABC):
    @abstractmethod
    def push(self, msg: str): ...


# Family 1: local development
class FileStorage(Storage):
    def save(self, name, data): print(f"[file] saved {name}")


class MemoryQueue(Queue):
    def push(self, msg): print(f"[memory] queued {msg}")


# Family 2: AWS
class S3Storage(Storage):
    def save(self, name, data): print(f"[s3] uploaded {name}")


class SQSQueue(Queue):
    def push(self, msg): print(f"[sqs] sent {msg}")


# The factories
class InfraFactory(ABC):
    @abstractmethod
    def create_storage(self) -> Storage: ...

    @abstractmethod
    def create_queue(self) -> Queue: ...


class LocalFactory(InfraFactory):
    def create_storage(self): return FileStorage()
    def create_queue(self): return MemoryQueue()


class AWSFactory(InfraFactory):
    def create_storage(self): return S3Storage()
    def create_queue(self): return SQSQueue()


def run_app(factory: InfraFactory):
    storage = factory.create_storage()
    queue = factory.create_queue()
    storage.save("report.pdf", "...")
    queue.push("report ready")


run_app(LocalFactory())
run_app(AWSFactory())
