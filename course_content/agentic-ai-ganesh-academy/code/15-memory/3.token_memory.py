"""
3. TOKEN MEMORY (trim history to a token budget)

Like window memory, but the limit is measured in tokens instead of message
count, which is closer to what you actually pay for and what the context
window actually limits. trim_messages keeps the newest messages that fit
in max_tokens.
"""

from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import before_model
from langchain.messages import RemoveMessage
from langchain_core.messages.utils import count_tokens_approximately, trim_messages
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.runtime import Runtime
from model import llm

MAX_TOKENS = 1024


@before_model
def trim_to_budget(state: AgentState, runtime: Runtime) -> dict | None:
    trimmed = trim_messages(
        state["messages"],
        strategy="last",  # keep the most recent
        token_counter=count_tokens_approximately,  # no tokenizer dependency
        max_tokens=MAX_TOKENS,
        start_on="human",  # never start mid-exchange
        end_on=("human", "tool"),
    )
    return {"messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES), *trimmed]}


agent = create_agent(
    model=llm,
    tools=[],
    middleware=[trim_to_budget],
    checkpointer=InMemorySaver(),
)

config = {"configurable": {"thread_id": "token-demo"}}

# ~230 approximate tokens of filler per message (keep each message < MAX_TOKENS)
NOISE = "This is some filler text about my day that is not important. " * 15


def say(text: str) -> str:
    out = agent.invoke({"messages": [{"role": "user", "content": text}]}, config)
    stored = agent.get_state(config).values["messages"]
    tokens = count_tokens_approximately(stored)
    print(f"[state: {len(stored):>2} msgs, ~{tokens:>4} tokens] {text[:45]!r}")
    return out["messages"][-1].content


# 1) A fact we want to see survive (or not)
say("Remember this: my favourite programming language is Go. Reply only 'ok'.")

# 2) Flood the history so the budget is exceeded and old messages get trimmed
for i in range(1, 6):
    say(f"Note {i}. Reply only 'ok'. {NOISE}")

# 3) The Go message is now outside the 1024-token window
print("\nUser : What is my favourite programming language?")
print("Agent:", say("What is my favourite programming language?"))
