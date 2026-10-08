"""
1. BUFFER MEMORY (short-term memory via a checkpointer)

The checkpointer saves the full message history of every thread_id.
Same thread_id  -> the agent sees the whole earlier conversation.
Different id    -> a fresh, empty conversation.
"""

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from model import llm

agent = create_agent(
    model=llm,
    tools=[],
    system_prompt="You are a helpful assistant.",
    checkpointer=InMemorySaver(),  # lives in RAM, gone when the script exits
)

config = {"configurable": {"thread_id": "user-1"}}

# Turn 1: tell the agent something
agent.invoke(
    {"messages": [{"role": "user", "content": "Hi, I'm Jafer from Coimbatore."}]},
    config,
)

# Turn 2: same thread -> it remembers
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Where am I from?"}]}, config
)
print("Same thread :", result["messages"][-1].content)  # remembers Coimbatore

# Turn 3: a different thread_id = a fresh, empty conversation
other = agent.invoke(
    {"messages": [{"role": "user", "content": "Where am I from?"}]},
    {"configurable": {"thread_id": "user-2"}},
)
print("New thread  :", other["messages"][-1].content)  # has no idea

# Peek at what the checkpointer stored for thread "user-1"
stored = agent.get_state(config).values["messages"]
print(f"\nMessages stored for 'user-1': {len(stored)}")  # 2 human + 2 AI = 4
for m in stored:
    print(f"  {m.type:>5} | {str(m.content)[:80]}")


# ---------------------------------------------------------------------------
# Making it persistent: swap InMemorySaver for SqliteSaver.
# pip install langgraph-checkpoint-sqlite
# ---------------------------------------------------------------------------
def persistent_demo():
    try:
        from langgraph.checkpoint.sqlite import SqliteSaver
    except ImportError:
        print("\n(skip) pip install langgraph-checkpoint-sqlite to run the SQLite demo")
        return

    cfg = {"configurable": {"thread_id": "user-1"}}

    # "Run 1" of an app: store a fact in memory.db
    with SqliteSaver.from_conn_string("memory.db") as checkpointer:
        app = create_agent(model=llm, tools=[], checkpointer=checkpointer)
        app.invoke(
            {"messages": [{"role": "user", "content": "Remember: my dog is Bruno"}]},
            cfg,
        )

    # "Run 2" (simulated restart): brand-new agent + brand-new connection
    with SqliteSaver.from_conn_string("memory.db") as checkpointer:
        app = create_agent(model=llm, tools=[], checkpointer=checkpointer)
        out = app.invoke(
            {"messages": [{"role": "user", "content": "What is my dog's name?"}]}, cfg
        )
        print("\nAfter 'restart':", out["messages"][-1].content)  # Bruno


# persistent_demo()
