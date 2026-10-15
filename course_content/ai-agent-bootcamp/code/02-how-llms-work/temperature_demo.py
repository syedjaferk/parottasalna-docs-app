# temperature_demo.py - same question, different temperatures
from llm import chat

QUESTION = "Give me a creative name for a tea shop. Reply with just the name."

for temperature in (0.0, 1.0, 1.8):
    print(f"\n--- temperature = {temperature} ---")
    for attempt in range(1, 4):                       # ask 3 times
        reply, usage = chat([{"role": "user", "content": QUESTION}], temperature=temperature, max_tokens=20)
        print(f"  try {attempt}: {reply.strip()}")
