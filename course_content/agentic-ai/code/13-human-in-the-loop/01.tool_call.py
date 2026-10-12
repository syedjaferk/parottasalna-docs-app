"""
Level 2 — Reviewing tool_calls by hand
--------------------------------------
Head chef analogy: the cook doesn't touch the cash box himself.
He writes a SLIP: "refund ₹120 for order 1234". The head chef reads
the slip and decides: approve / edit / reject.

When a model uses tools, it never runs them — it only PROPOSES:
    ai_msg.tool_calls = [{"name": "issue_refund", "args": {...}, "id": "..."}]
That proposal is the perfect place for a human check.

    user ─► model.bind_tools ─► proposed tool_calls ─► 👨‍🍳 review each ─► run / skip
                                                                         │
                         final reply ◄─ model ◄─ ToolMessages (results) ◄┘
"""

import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq

load_dotenv()  # expects GROQ_API_KEY in .env

model = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
)


# ---------- Tools (fake — print instead of real side effects) ----------
@tool
def issue_refund(order_id: str, amount: float) -> str:
    """Refund money to a customer for an order."""
    return f"Refunded ₹{amount} for order {order_id}"


@tool
def send_email(to: str, body: str) -> str:
    """Send an email to a customer."""
    return f"Email sent to {to}"


TOOLS = {t.name: t for t in [issue_refund, send_email]}
model_with_tools = model.bind_tools(list(TOOLS.values()))


# ---------- The head chef reviews one slip ----------
def head_chef_review(call: dict) -> ToolMessage:
    print(f"\n📝 Cook wants to run: {call['name']}")
    for k, v in call["args"].items():
        print(f"     {k} = {v}")
    choice = input("👨‍🍳 [a]pprove  [e]dit  [r]eject : ").strip().lower()

    if choice == "e":
        for k, v in call["args"].items():
            new = input(f"     {k} [{v}]: ").strip()
            if new:
                call["args"][k] = float(new) if isinstance(v, (int, float)) else new
        choice = "a"

    if choice == "a":
        result = TOOLS[call["name"]].invoke(call["args"])
        print("     ✅", result)
    else:
        reason = input("     Why reject? ") or "Rejected by head chef."
        result = f"NOT EXECUTED. Human rejected this action: {reason}"
        print("     ❌", result)

    # Tell the model what happened, linked by tool_call_id
    return ToolMessage(content=result, tool_call_id=call["id"])


if __name__ == "__main__":
    messages = [
        SystemMessage(
            "You are a support agent for Parottasalna restaurant. Use tools when needed."
        ),
        HumanMessage(
            "Order 1234 came cold. Refund ₹120 and email ravi@example.com saying sorry."
        ),
    ]

    ai_msg = model_with_tools.invoke(messages)
    messages.append(ai_msg)

    # The model often proposes one tool per turn (refund first, then the email), so keep
    # looping until it stops asking: the human reviews EVERY proposed call.
    while ai_msg.tool_calls:
        for call in ai_msg.tool_calls:
            messages.append(head_chef_review(call))

        # Give results back to the model: it either proposes the next tool or replies
        ai_msg = model_with_tools.invoke(messages)
        messages.append(ai_msg)

    print("\n💬 Final reply:\n" + ai_msg.content)
