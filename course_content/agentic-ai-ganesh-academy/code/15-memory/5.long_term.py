"""
5. LONG-TERM MEMORY (cross-thread memory with a Store)

The checkpointer only remembers within one thread_id. A Store is a separate
key-value database that lives ACROSS threads. Here the agent gets two tools:
  save_memory   -> writes a fact into the store under the user's namespace
  list_memories -> reads every fact for that user
The LLM itself decides when to call them.
"""

import uuid
from dataclasses import dataclass

from langchain.agents import create_agent
from langchain.tools import ToolRuntime, tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from model import llm


@dataclass
class Context:
    """Per-invocation info passed via agent.invoke(..., context=...)."""

    user_id: str


@tool
def save_memory(fact: str, runtime: ToolRuntime[Context]) -> str:
    """Save a lasting fact about the user (preferences, name, goals)."""
    ns = ("memories", runtime.context.user_id)  # namespace = per-user folder
    runtime.store.put(ns, str(uuid.uuid4()), {"fact": fact})
    return f"Saved: {fact}"


@tool
def list_memories(runtime: ToolRuntime[Context]) -> str:
    """Retrieve everything known about the user."""
    items = runtime.store.search(("memories", runtime.context.user_id))
    return "\n".join(i.value["fact"] for i in items) or "No memories yet."


store = InMemoryStore()  # use a Postgres-backed store in production

agent = create_agent(
    model=llm,
    tools=[save_memory, list_memories],
    system_prompt=(
        "You have long-term memory. Save important user facts with "
        "save_memory, and call list_memories when personalization helps."
    ),
    store=store,
    context_schema=Context,
    checkpointer=InMemorySaver(),
)

ctx = Context(user_id="Jafer")

# Session 1: the user states preferences; the agent should call save_memory
out = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "I like to play chess, badminton, cricket, football. These are my hobbies.",
            }
        ]
    },
    {"configurable": {"thread_id": "session-1"}},
    context=ctx,
)
print("Session 1:", out["messages"][-1].content)

# Look inside the store to verify something was actually saved
print("\nStore contents for 'Jafer':")
for item in store.search(("memories", "Jafer")):
    print("  -", item.value["fact"])

# Session 2: a brand-new thread, but the memory persists
out = agent.invoke(
    {"messages": [{"role": "user", "content": "Suggest a game to play."}]},
    {"configurable": {"thread_id": "session-2"}},
    context=ctx,
)
print("\nSession 2 (same user):", out["messages"][-1].content)

# A different user_id -> different namespace -> no access to Jafer's memories
out = agent.invoke(
    {"messages": [{"role": "user", "content": "Suggest a game to play. "}]},
    {"configurable": {"thread_id": "session-3"}},
    context=Context(user_id="priya"),
)
print("\nSession 3 (different user):", out["messages"][-1].content)
