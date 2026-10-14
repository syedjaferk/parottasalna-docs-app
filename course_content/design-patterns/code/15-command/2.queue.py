"""Commands in a queue: the same idea behind job queues like Celery or RabbitMQ workers."""
from queue import Queue


class SendEmail:
    def __init__(self, to): self.to = to
    def execute(self): print(f"emailing {self.to}")


class ResizeImage:
    def __init__(self, path): self.path = path
    def execute(self): print(f"resizing {self.path}")


jobs = Queue()
jobs.put(SendEmail("kavya@example.com"))
jobs.put(ResizeImage("photo.jpg"))

while not jobs.empty():
    jobs.get().execute()          # a worker runs them one by one
