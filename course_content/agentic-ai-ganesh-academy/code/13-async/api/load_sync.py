import time

import requests


def send_request(msg):
    start = time.time()
    resp = requests.post("http://localhost:8000/chat", json={"message": msg})
    elapsed = time.time() - start
    print(f"[{msg}] -> {resp.json()['reply']}  ({elapsed:.2f}s)")


messages = [
    "Weather in Chennai?",
    "Weather in Mumbai?",
    "Time in Delhi?",
]

start = time.time()
for message in messages:
    send_request(message)

print(f"\nTotal time: {time.time() - start:.2f}s")
