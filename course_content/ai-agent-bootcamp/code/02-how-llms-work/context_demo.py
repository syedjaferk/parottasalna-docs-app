# context_demo.py - the model only knows what you send it, every single time
from llm import chat

# 1. Tell it a fact, WITHOUT keeping the history.
chat([{"role": "user", "content": "My name is Asha and I love filter coffee."}], max_tokens=40)

reply, _ = chat([{"role": "user", "content": "What is my name?"}], max_tokens=40)
print("Without history :", reply.strip())

# 2. Now send the whole conversation again, like a chat app does.
history = [
    {"role": "user", "content": "My name is Asha and I love filter coffee."},
    {"role": "assistant", "content": "Nice to meet you, Asha!"},
    {"role": "user", "content": "What is my name?"},
]
reply, usage = chat(history, max_tokens=40)
print("With history    :", reply.strip())
print("Tokens sent this time:", usage.get("prompt_tokens"))
