"""
6. SEMANTIC MEMORY (long-term memory searched by meaning)

Same idea as 5_long_term.py, but the Store has an embedding index. Every saved
fact is turned into a vector, and search_memories(query) returns the facts
closest in MEANING to the query, not just keyword matches. So "snack ideas for
my trek" can find "allergic to peanuts" even though they share no words.

Setup: pip install langchain-huggingface sentence-transformers
(the first run downloads the all-MiniLM-L6-v2 model, ~90 MB)
"""

import uuid
from dataclasses import dataclass

from langchain.agents import create_agent
from langchain.tools import ToolRuntime, tool
from langchain_huggingface import HuggingFaceEmbeddings
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from model import llm

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# dims must match the embedding model's output size (MiniLM = 384)
store = InMemoryStore(index={"embed": embeddings, "dims": 384})


@dataclass
class Context:
    user_id: str


@tool
def save_memory(fact: str, runtime: ToolRuntime[Context]) -> str:
    """Save a lasting fact about the user."""
    ns = ("memories", runtime.context.user_id)
    runtime.store.put(ns, str(uuid.uuid4()), {"fact": fact})  # auto-embedded
    return "Saved."


@tool
def search_memories(query: str, runtime: ToolRuntime[Context]) -> str:
    """Find stored facts relevant to the query."""
    hits = runtime.store.search(
        ("memories", runtime.context.user_id), query=query, limit=3
    )
    return "\n".join(h.value["fact"] for h in hits) or "Nothing relevant found."


agent = create_agent(
    model=llm,
    tools=[save_memory, search_memories],
    system_prompt="Save durable user facts. Before recommending anything, search_memories.",
    store=store,
    context_schema=Context,
    checkpointer=InMemorySaver(),
)

ctx = Context(user_id="arun")


def cfg(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}}


# Thread "a": the agent saves facts as the user mentions them
agent.invoke(
    {"messages": [{"role": "user", "content": "I'm allergic to peanuts."}]},
    cfg("a"),
    context=ctx,
)
agent.invoke(
    {"messages": [{"role": "user", "content": "I love hiking in the Western Ghats."}]},
    cfg("a"),
    context=ctx,
)

# Seed a few unrelated facts directly so the ranking below is meaningful
for fact in [
    "I play cricket on weekends.",
    "My favourite colour is teal.",
    "I work as a backend engineer.",
]:
    store.put(("memories", "arun"), str(uuid.uuid4()), {"fact": fact})

# Peek at semantic search directly (no LLM): higher score = closer in meaning
for q in ["what food should I avoid?", "outdoor activities"]:
    print(f"\nQuery: {q!r}")
    for hit in store.search(("memories", "arun"), query=q, limit=3):
        print(f"  {hit.score:.3f} | {hit.value['fact']}")

# Thread "b": a brand-new conversation; the agent must search memory by meaning
out = agent.invoke(
    {"messages": [{"role": "user", "content": "Any snack ideas for my trek?"}]},
    cfg("b"),
    context=ctx,
)
print(
    "\nAgent:", out["messages"][-1].content
)  # retrieves the allergy memory by meaning
