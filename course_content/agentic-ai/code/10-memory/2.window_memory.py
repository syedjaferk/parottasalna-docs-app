"""
2. WINDOW MEMORY (sliding window by message count)

A @before_model middleware runs right before every LLM call and rewrites the
message list: keep the FIRST message + the LAST 4 messages, drop the middle.
Because it rewrites the checkpointed state, the dropped messages are deleted
for good, not just hidden from the model.
"""

from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import before_model
from langchain.messages import RemoveMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.runtime import Runtime
from model import llm


@before_model
def keep_last_messages(state: AgentState, runtime: Runtime) -> dict | None:
    messages = state["messages"]
    if len(messages) <= 4:
        return None  # nothing to trim yet
    first = messages[0]  # keep the opening message
    recent = messages[-4:]  # keep last 4
    # REMOVE_ALL_MESSAGES wipes the list, then we re-add only what we want
    return {"messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES), first, *recent]}


agent = create_agent(
    model=llm,
    tools=[],
    middleware=[keep_last_messages],
    checkpointer=InMemorySaver(),
)

config = {"configurable": {"thread_id": "window-demo"}}

turns = [
    "My name is Jafer.",  # first message -> always kept
    "I live in Coimbatore.",  # will fall out of the window
    "I make backend and AI videos.",
    "My favourite drink is Inji Tea.",
    "What is my name?",  # answerable: first message is pinned
    "Where do I live?",  # NOT answerable: that message was dropped
]

for text in turns:
    out = agent.invoke({"messages": [{"role": "user", "content": text}]}, config)
    stored = agent.get_state(config).values["messages"]
    print(f"\nUser : {text}")
    print(f"Agent: {out['messages'][-1].content}")
    print(f"[messages in state: {len(stored)}]")  # levels off at 6

print("\nWhat's left in memory:")
for m in agent.get_state(config).values["messages"]:
    print(f"  {m.type:>5} | {str(m.content)[:80]}")
