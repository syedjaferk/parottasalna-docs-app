# run_task.py - give your Session 5 agent ONE task and measure it, so you can compare it with Hermes.
# Put this file in the same folder as agent.py, tools.py, llm.py and .env.
#
#   python run_task.py "What is the weather in Chennai, and what is that in Fahrenheit?"
import sys
import time

from agent import Agent

task = " ".join(sys.argv[1:]) or "What is the weather in Chennai, and what is that temperature in Fahrenheit?"

agent = Agent(verbose=False)
start = time.time()
answer = agent.ask(task)
seconds = time.time() - start

tool_calls = [m for m in agent.messages if m["role"] == "tool"]

print("TASK  :", task)
print("ANSWER:", answer)
print(f"\nTime       : {seconds:.1f} seconds")
print(f"Tool calls : {len(tool_calls)}")
