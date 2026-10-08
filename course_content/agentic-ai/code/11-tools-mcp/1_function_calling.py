"""
1. Function Calling - what really happens under the hood.

Key idea: the LLM NEVER runs your function.
It only returns a structured request: "please call add(a=12, b=7)".
YOUR code runs the function and sends the result back.
"""

from langchain.tools import tool
from langchain_core.messages import HumanMessage
from model import model


@tool
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b


tools = [add, multiply]
tools_by_name = {t.name: t for t in tools}

# bind_tools sends each tool's name + description + JSON schema to the model
llm_with_tools = model.bind_tools(tools)
# Force a specific tool:  model.bind_tools(tools, tool_choice="add")

# ---------------------------------------------------------------
# STEP A: see the raw tool call the model produces
# ---------------------------------------------------------------
print("=== STEP A: raw tool call ===")
ai_msg = llm_with_tools.invoke(
    "What is 12 multiplied by 7 ?. Use the provided tools if present. "
)
print("content   :", repr(ai_msg.content))  # usually empty
print(
    "tool_calls:", ai_msg.tool_calls
)  # [{'name': 'multiply', 'args': {...}, 'id': '...'}]

# ---------------------------------------------------------------
# STEP B: the manual loop (this is what agents automate for you)
# ---------------------------------------------------------------
print("\n=== STEP B: manual tool loop ===")
messages = [
    HumanMessage(
        "What is 12 multiplied by 7, then add 5 to the result?. Use the provided tools if present."
    )
]

while True:
    ai_msg = llm_with_tools.invoke(messages)
    messages.append(ai_msg)

    if not ai_msg.tool_calls:  # no more tools needed -> final answer
        break

    for call in ai_msg.tool_calls:
        print(f"-> model wants {call['name']}({call['args']})")
        tool_msg = tools_by_name[call["name"]].invoke(call)  # returns a ToolMessage
        print(f"<- result: {tool_msg.content}")
        messages.append(tool_msg)  # feed the result back to the model

print("\nFINAL ANSWER:", ai_msg.content)
