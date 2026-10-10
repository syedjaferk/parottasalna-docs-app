"""
4. SUMMARY MEMORY (compress old history instead of deleting it)

SummarizationMiddleware watches the history. Once it passes the trigger, the
older messages are replaced by one LLM-written summary, and only the most
recent messages are kept word-for-word. Facts survive in compressed form.

NOTE: the original trigger (1500 tokens) is never reached by a 4-message chat,
so the summary would never fire. Here the trigger is lowered so you can see it.
"""

from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver
from model import llm

TRIGGER_TOKENS = 200  # use ~1500+ in real apps
KEEP_MESSAGES = 4  # last N messages kept verbatim

agent = create_agent(
    model=llm,
    tools=[],
    middleware=[
        SummarizationMiddleware(
            # Same model as the agent here; swap in a smaller/cheaper Groq
            # model to cut cost, since summarizing is an easy task.
            model=ChatGroq(model="openai/gpt-oss-120b", temperature=0),
            trigger=("tokens", TRIGGER_TOKENS),  # summarize once history exceeds this
            keep=("messages", KEEP_MESSAGES),  # always keep the last messages verbatim
        )
    ],
    checkpointer=InMemorySaver(),
)

config = {"configurable": {"thread_id": "long-chat"}}

conversation = [
    "I'm planning a trip to Kerala in December. ",
    "Budget is ₹40,000 for 5 days.",  # will end up inside the summary
    "I like backwaters and hate crowded beaches.",
    "I'm travelling with two friends.",
    "Suggest a rough 5-day itinerary.",  # long reply pushes us over the trigger
    "What did I say my budget was?",
]

for msg in conversation:
    out = agent.invoke(
        {"messages": [{"role": "user", "content": msg + " . Give resposne in 1 line"}]},
        config,
    )
    print(f"\nUser : {msg}")
    print(f"Agent: {out['messages'][-1].content[:300]}")

# See what the history looks like now: a summary message + the recent tail
print("\n" + "=" * 60)
print("Messages currently stored in the thread:")
for m in agent.get_state(config).values["messages"]:
    text = str(m.content).replace("\n", " ")
    print(f"  {m.type:>5} | {text}")
