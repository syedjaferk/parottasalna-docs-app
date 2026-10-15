# tool_demo.py - the AI decides to call a tool, WE run it, then the AI answers
import json

from llm import call_api
from tools import TOOL_FUNCTIONS, TOOL_SPECS

messages = [
    {"role": "system", "content": "You are a helpful assistant. Use tools when they help."},
    {"role": "user", "content": "What is the weather in Chennai, and what is 17.5% of 2480?"},
]

# ---- Round 1: send the question + the tool descriptions
data = call_api({"messages": messages, "tools": TOOL_SPECS, "temperature": 0})
message = data["choices"][0]["message"]
print("AI wants to use tools:", [c["function"]["name"] for c in message.get("tool_calls") or []])

if not message.get("tool_calls"):
    print("Answer:", message["content"])
    raise SystemExit

# ---- Round 2: run each requested tool and send back the results
messages.append(message)                                   # keep the AI's request in the history
for call in message["tool_calls"]:
    name = call["function"]["name"]
    args = json.loads(call["function"]["arguments"])       # arguments arrive as JSON TEXT
    print(f"  running {name}({args})")
    result = TOOL_FUNCTIONS[name](**args)                  # call our real Python function
    print(f"  result: {result}")
    messages.append({"role": "tool", "tool_call_id": call["id"], "content": str(result)})

final = call_api({"messages": messages, "tools": TOOL_SPECS, "temperature": 0})
print("\nFinal answer:", final["choices"][0]["message"]["content"])
