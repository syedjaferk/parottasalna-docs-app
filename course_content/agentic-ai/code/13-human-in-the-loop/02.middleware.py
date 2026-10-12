"""
Level 3 — create_agent + HumanInTheLoopMiddleware + checkpointer  (PRODUCTION PATTERN)
---------------------------------------------------------------------------------------
Head chef analogy: a big restaurant. The cook works on his own, but there's a RULE BOOK:
  • checking an order status      → no approval needed
  • refunds above ₹200            → head chef must approve (approve / edit / reject)
  • emailing a customer           → head chef must approve
  • asking the customer something → the head chef answers on the customer's behalf (respond)

When a rule is hit, the agent PAUSES. Its state is saved in the checkpointer under a
thread_id, so the head chef can answer seconds or hours later — even from another
request/process — and the agent RESUMES exactly where it stopped.

    user ─► agent ─► tool call? ─ safe ──────────────────────► run tool ─► answer
                                  └ needs approval ─► ⏸ PAUSE (saved: checkpointer + thread_id)
                                                        ─► 👨‍🍳 approve/edit/reject/respond
                                                        ─► ▶ agent.invoke(Command(resume=...))

Requires: pip install -U langchain langgraph langchain-groq python-dotenv
          langchain>=1.3.3 for the `when` option.
"""

import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware, ToolCallRequest
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

load_dotenv()  # expects GROQ_API_KEY in .env

model = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
)


# ---------- Tools ----------
@tool
def check_order_status(order_id: str) -> str:
    """Look up the delivery status of an order."""
    return f"Order {order_id}: delivered 55 minutes late, food was cold."


@tool
def issue_refund(order_id: str, amount: float) -> str:
    """Refund money (in rupees) to a customer for an order."""
    return f"Refunded ₹{amount} for order {order_id}"


@tool
def send_email(to: str, body: str) -> str:
    """Send an email to a customer."""
    return f"Email sent to {to}"


@tool
def ask_user(question: str) -> str:
    """Ask the customer a clarifying question (e.g. a missing order id)."""
    return "This tool is answered by a human."  # never actually runs — human 'responds'


# ---------- The rule book (conditional approval) ----------
def is_big_refund(request: ToolCallRequest) -> bool:
    """Only pause refunds above ₹200. Small ones run automatically."""
    return float(request.tool_call["args"].get("amount", 0)) > 200


agent = create_agent(
    model=model,
    tools=[check_order_status, issue_refund, send_email, ask_user],
    system_prompt=(
        "You are a support agent for Parottasalna restaurant. "
        "If the order id is missing, use ask_user to get it. "
        "Check the order status before refunding."
    ),
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "check_order_status": False,  # safe → never pause
                "issue_refund": {
                    "allowed_decisions": ["approve", "edit", "reject"],
                    "when": is_big_refund,  # pause only if > ₹200
                },
                "send_email": {"allowed_decisions": ["approve", "edit", "reject"]},
                "ask_user": {"allowed_decisions": ["respond"]},  # human IS the tool
            },
            description_prefix="👨‍🍳 Head chef approval needed",
        )
    ],
    checkpointer=InMemorySaver(),  # production: PostgresSaver / MongoDBSaver
)


# ---------- The head chef's decision for ONE paused action ----------
def head_chef_decides(action: dict, allowed: list[str]) -> dict:
    print("\n" + "=" * 60)
    print(action["description"])
    print("Allowed:", ", ".join(allowed))

    if allowed == ["respond"]:  # e.g. ask_user
        return {"type": "respond", "message": input("💬 Your answer: ")}

    choice = input("👨‍🍳 [a]pprove  [e]dit  [r]eject : ").strip().lower()

    if choice == "e" and "edit" in allowed:
        new_args = dict(action["args"])
        for k, v in new_args.items():
            new = input(f"   {k} [{v}]: ").strip()
            if new:
                new_args[k] = float(new) if isinstance(v, (int, float)) else new
        return {
            "type": "edit",
            "edited_action": {"name": action["name"], "args": new_args},
        }

    if choice == "r" and "reject" in allowed:
        reason = input("   Why reject? (the agent reads this): ")
        return {
            "type": "reject",
            "message": reason or "Rejected by head chef. Do not retry.",
        }

    return {"type": "approve"}


if __name__ == "__main__":
    # thread_id = which "order ticket" we are working on. Same id → resume same conversation.
    config = {"configurable": {"thread_id": "ticket-001"}}

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "My parotta came cold. Refund ₹300 and email me sorry at ravi@example.com",
                }
            ]
        },
        config=config,
        version="v2",
    )

    # The agent may pause several times — keep answering until it finishes
    while result.interrupts:
        request = result.interrupts[0].value
        allowed_by_tool = {
            rc["action_name"]: rc["allowed_decisions"]
            for rc in request["review_configs"]
        }

        # One decision per action, in the SAME ORDER as action_requests
        decisions = [
            head_chef_decides(action, allowed_by_tool[action["name"]])
            for action in request["action_requests"]
        ]

        result = agent.invoke(
            Command(resume={"decisions": decisions}),
            config=config,  # same thread_id → resume where it paused
            version="v2",
        )

    print("\n✅ FINAL ANSWER:\n" + result.value["messages"][-1].content)

    # Note: on older LangGraph versions (no version="v2"), drop version=... and read
    # interrupts from result["__interrupt__"] and messages from result["messages"].
