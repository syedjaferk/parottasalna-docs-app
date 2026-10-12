# Session 13 · Human in the Loop: Approve Before the Agent Acts

## The big idea

An agent that can *do* things ([Session 11](11-tools-and-mcp.md)) can also do the **wrong** things:
refund too much, email the wrong customer, delete the wrong row. **Human in the loop (HITL)** means
the agent stops at the risky moments and a person decides: **approve**, **edit** or **reject**.

**Everyday example:** a restaurant kitchen. The cook (the AI) prepares the dish, but the **head chef
tastes it before it's served**. For small things (checking an order's status) the cook just goes
ahead. For anything involving money or the customer, the head chef signs off first.

:::{admonition} Under the hood
:class: hint
HITL is a **checkpoint before a side effect**. The model only ever *proposes* actions: text, or tool
calls with arguments. Nothing happens in the real world until your code executes them. That gap
between "proposed" and "executed" is where a person can step in. The three levels below differ in
*where* you put that check, and whether the agent can **wait** for the answer without blocking a
program.
:::

```{raw} html
:file: ../diagrams/s13-levels.html
```

**What needs a human?** A useful rule: anything that is **hard to undo** or **visible to someone else**.

| Action | Approval? | Why |
|---|---|---|
| look up an order, search, read a file | no | nothing changes; asking every time just slows everyone down |
| refund money, place an order | yes (maybe only above a limit) | costs money, hard to reverse |
| email or message a customer | yes | can't be unsent; it speaks for your business |
| delete or update data | yes | may be impossible to undo |

## Level 1: an approval gate inside a chain

```{raw} html
:file: ../diagrams/s13-gate.html
```

**In plain words:** the AI writes a reply to a complaint. Before it's sent, the program stops and
shows it to you. Approve it, type a better one, or reject it.

```python
class RejectedByChef(Exception):
    pass

# 1) The cook: LLM drafts a reply (an LCEL chain from Session 12)
cook = (
    ChatPromptTemplate.from_template(
        "You work at Parottasalna restaurant. Write a polite 3-line reply "
        "to this customer complaint:\n{complaint}")
    | model
    | StrOutputParser()
)

# 2) The head chef: a person tastes it before it's served
def head_chef_tastes(dish: str) -> str:
    print(dish)
    choice = input("👨‍🍳 [a]pprove  [e]dit  [r]eject : ").strip().lower()
    if choice == "a":
        return dish
    if choice == "e":
        return input("✏️  Type the corrected reply:\n> ")
    raise RejectedByChef("Head chef rejected the dish — nothing served.")

# 3) Serve: only reached if the chef approved or edited
def serve(dish: str) -> str:
    print("\n📧 SERVED (email sent):\n" + dish)
    return "served"

kitchen = cook | RunnableLambda(head_chef_tastes) | RunnableLambda(serve)
kitchen.invoke({"complaint": "My parotta order came cold after 1 hour of waiting!"})
```

```text
🍽️  DISH READY FOR TASTING
We're very sorry to hear your parotta arrived cold after such a long wait.
Please let us know a convenient time, and we'll gladly prepare a fresh replacement or issue a refund.
Thank you for bringing this to our attention—we'll work to ensure it doesn't happen again.
👨‍🍳 [a]pprove  [e]dit  [r]eject : r

❌ Head chef rejected the dish — nothing served.
```

:::{admonition} Under the hood
:class: hint
- `RunnableLambda` turns the plain function into a chain step ([Session 12](12-lcel.md)). The gate is
  just another station on the line.
- **Reject = raise.** The exception travels up out of `invoke`, so `serve` never runs. This is safer
  than returning something like `None`, which the next step might happily send.
- **The limit:** `input()` **blocks** the program until someone types. In a web app there's no
  terminal to type into, a request can't wait for hours, and if the server restarts the draft is
  lost. Fine for scripts and notebooks; for apps, see Level 3.
:::

## Level 2: review each tool call by hand

```{raw} html
:file: ../diagrams/s13-tool-review.html
```

**In plain words:** with tools, the AI never touches the cash box itself. It writes a **slip**:
*"refund ₹120 for order 1234"*. You read the slip and decide. Whatever you decide, you tell the AI
what happened, so it can write a sensible final reply.

```python
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

def head_chef_review(call: dict) -> ToolMessage:
    choice = input("👨‍🍳 [a]pprove  [e]dit  [r]eject : ").strip().lower()
    if choice == "e":
        ...                                   # ask for new values, update call["args"], then approve
        choice = "a"
    if choice == "a":
        result = TOOLS[call["name"]].invoke(call["args"])
    else:
        reason = input("     Why reject? ") or "Rejected by head chef."
        result = f"NOT EXECUTED. Human rejected this action: {reason}"
    return ToolMessage(content=result, tool_call_id=call["id"])   # always answer the slip

ai_msg = model_with_tools.invoke(messages)
messages.append(ai_msg)
while ai_msg.tool_calls:                      # the model may propose more tools after each result
    for call in ai_msg.tool_calls:
        messages.append(head_chef_review(call))
    ai_msg = model_with_tools.invoke(messages)
    messages.append(ai_msg)
print(ai_msg.content)
```

**A real run:** approve the refund, reject the email with a reason:

```text
📝 Cook wants to run: issue_refund     amount = 120   order_id = 1234
👨‍🍳 [a]pprove  [e]dit  [r]eject : a       ✅ Refunded ₹120.0 for order 1234

📝 Cook wants to run: send_email       to = ravi@example.com   body = Dear Customer, We sincerely apologize...
👨‍🍳 [a]pprove  [e]dit  [r]eject : r       Why reject? The customer asked us to call, not email
     ❌ NOT EXECUTED. Human rejected this action: The customer asked us to call, not email

💬 Final reply:
✅ Your refund of ₹120 for order #1234 has been processed.
We'd like to apologize personally for the inconvenience. Could you please share a phone number
where we can reach you? We'll give you a call right away to ensure everything is resolved.
```

The model read the rejection reason and changed its plan: no email, it asks for a phone number instead.

:::{admonition} Under the hood
:class: hint
- `bind_tools` sends the tools' names, descriptions and argument schemas to the model. The reply is an
  `AIMessage` whose `tool_calls` is a list like
  `[{"name": "issue_refund", "args": {"order_id": "1234", "amount": 120}, "id": "call_…"}]`.
  **The model never runs anything.** Your loop does.
- **Every tool call must get a `ToolMessage` with the same `tool_call_id`**, even a rejected one. Chat
  APIs reject a conversation where a tool call has no answer. A rejection *as the tool's result* is also
  how the model learns what happened.
- **Loop until there are no tool calls.** Models often do one action per turn: here the refund came
  first, and the email was only proposed after the model saw the refund succeed. A single review
  round would never see the email, and the "final" reply would be empty.
- **Edits are your responsibility.** Values typed at a prompt are strings. Convert them (`float(...)`)
  and check them before the tool runs.
:::

## Level 3: middleware, a rule book and pause/resume (the production pattern)

**In plain words:** a big restaurant writes the rules down once, in a **rule book**, instead of the head
chef watching every move:

- checking an order status: go ahead
- refunds above ₹200: head chef approves first (and can change the amount)
- emailing a customer: head chef approves first
- asking the customer a question: the head chef answers on the customer's behalf

When a rule is hit, the cook **pauses** and pins the order ticket on the board. The head chef can answer
in five seconds or five hours, from any till. Then the cook picks the ticket up and **carries on from
exactly where it stopped**.

```{raw} html
:file: ../diagrams/s13-pause-resume.html
```

**The rule book** is a `HumanInTheLoopMiddleware` attached to the agent:

```python
def is_big_refund(request: ToolCallRequest) -> bool:
    """Only pause refunds above ₹200. Small ones run automatically."""
    return float(request.tool_call["args"].get("amount", 0)) > 200

agent = create_agent(
    model=model,
    tools=[check_order_status, issue_refund, send_email, ask_user],
    system_prompt="You are a support agent for Parottasalna restaurant. "
                  "If the order id is missing, use ask_user to get it. "
                  "Check the order status before refunding.",
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "check_order_status": False,                                    # safe → never pause
                "issue_refund": {"allowed_decisions": ["approve", "edit", "reject"],
                                 "when": is_big_refund},                        # only above ₹200
                "send_email":   {"allowed_decisions": ["approve", "edit", "reject"]},
                "ask_user":     {"allowed_decisions": ["respond"]},             # the human IS the tool
            },
            description_prefix="👨‍🍳 Head chef approval needed",
        )
    ],
    checkpointer=InMemorySaver(),       # production: PostgresSaver / MongoDBSaver
)
```

**Run, pause, decide, resume:**

```python
config = {"configurable": {"thread_id": "ticket-001"}}     # which ticket we're working on

result = agent.invoke({"messages": [{"role": "user", "content":
          "My parotta came cold. Refund ₹300 and email me sorry at ravi@example.com"}]},
          config=config, version="v2")

while result.interrupts:                                    # paused: someone has to decide
    request = result.interrupts[0].value                    # {"action_requests": [...], "review_configs": [...]}
    decisions = [head_chef_decides(a, ...) for a in request["action_requests"]]   # one per action, same order
    result = agent.invoke(Command(resume={"decisions": decisions}),
                          config=config, version="v2")      # same thread_id → carry on

print(result.value["messages"][-1].content)
```

The four kinds of decision:

| Decision | Shape | What happens |
|---|---|---|
| approve | `{"type": "approve"}` | the tool runs as proposed |
| edit | `{"type": "edit", "edited_action": {"name": …, "args": {…}}}` | the tool runs with *your* arguments |
| reject | `{"type": "reject", "message": "why"}` | the tool doesn't run; the model reads your reason |
| respond | `{"type": "respond", "message": "answer"}` | the tool doesn't run; your text *is* its result |

**A real run:** the message has no order ID, so the agent asks first. Then the head chef cuts the
₹300 refund to ₹250:

```text
👨‍🍳 Head chef approval needed
Tool: ask_user
Args: {'question': 'Could you please provide the order ID for your order?'}
Allowed: respond
💬 Your answer: 1234

👨‍🍳 Head chef approval needed
Tool: issue_refund
Args: {'amount': 300, 'order_id': '1234'}
Allowed: approve, edit, reject
👨‍🍳 [a]pprove  [e]dit  [r]eject : e
   amount [300]: 250
   order_id [1234]:

👨‍🍳 Head chef approval needed
Tool: send_email
Args: {'body': '... We have processed a refund of ₹250 for your order #1234 ...', 'to': 'ravi@example.com'}
👨‍🍳 [a]pprove  [e]dit  [r]eject : a

✅ FINAL ANSWER:
Your refund of ₹250 for order #1234 has been processed, and an apology email has been sent to ravi@example.com.
```

The edit carried through: the email the agent wrote next says ₹250, not ₹300.

:::{admonition} Under the hood
:class: hint
- `create_agent` builds a **LangGraph** graph: a model node and a tools node in a loop (the agent loop
  from [Session 11](11-tools-and-mcp.md)). Middleware hooks into that loop. `HumanInTheLoopMiddleware`
  runs **after the model** and before any tool.
- It looks at the latest `AIMessage`'s `tool_calls`. Tools missing from `interrupt_on`, set to `False`,
  or whose `when` function returns `False`, pass straight through. The rest are collected into **one**
  request (`action_requests` and `review_configs`), and the middleware calls LangGraph's `interrupt()`.
- `interrupt()` **stops the graph** and the **checkpointer** saves its whole state under the
  `thread_id`. `invoke` returns, with the request in `result.interrupts`. Nothing is blocked: the
  program is free, and the decision can come from another request or another process.
- `Command(resume={"decisions": [...]})` with the **same `thread_id`** loads that state and continues
  inside the middleware. There must be **exactly one decision per action, in the same order**, or it
  raises `ValueError`.
- Approved and edited calls go on to the tools node. Rejected and responded ones get a `ToolMessage`
  without running the tool. After an edit, the middleware also tells the model the call was changed on
  purpose, so it doesn't try the original again.
- `InMemorySaver` lives in RAM: restart the program and every paused ticket is gone. In production
  use a database-backed checkpointer such as `PostgresSaver`.
- `version="v2"` returns an object with `.value` and `.interrupts`. On older LangGraph versions, read
  `result["__interrupt__"]` and `result["messages"]` instead.
:::

**In a web app**, the two halves usually live in two different requests:

```text
POST /support/chat     → agent.invoke(...)                  → paused: the UI shows "waiting for approval"
POST /support/approve  → agent.invoke(Command(resume=...))  → same thread_id: the agent finishes the job
```

The checkpointer is what connects them. That's why it has to be a real database in production.

## Common mistakes

- **No `.env` in the folder.** `load_dotenv()` looks in the script's folder and its parents. The
  `13.HIL` folder needs its own `.env` with `GROQ_API_KEY`, like the other sessions.
- **Reviewing only the first round of tool calls.** The model often proposes tools one turn at a time.
  Loop until `ai_msg.tool_calls` is empty, or the later actions run without review (or never run at all).
- **Forgetting the `ToolMessage` for a rejected call.** Every `tool_call_id` needs an answer, otherwise the
  next model call fails.
- **Reading the wrong key.** An action request has `name`, `args` and `description`, not `arguments`.
- **Decisions out of order or missing.** One decision per action request, in the same order, or you get a
  `ValueError`.
- **A new `thread_id` on resume.** It starts a brand-new conversation, with nothing to resume. Keep the ID with the ticket.
- **`InMemorySaver` in production.** A restart forgets every paused approval.
- **Approving everything.** If people are asked about every harmless lookup, they start clicking "approve"
  without reading. Pause only on what's risky (`when` helps).
- **Rejecting without a reason.** The model then guesses, and may try again. Say what to do instead.

## Try it yourself

1. In Level 1, add a `[s]horten` choice that sends the draft back to the model with "make it 1 line".
2. In Level 2, make `send_email` refuse (without asking) any address that isn't `@example.com`.
3. In Level 3, run *"Order 5678 came cold, refund ₹120"*. Does the head chef get asked about the refund? Why?
4. In Level 3, change the checkpointer to `SqliteSaver` (from `langgraph-checkpoint-sqlite`), stop the
   program at the first pause, and resume the same `thread_id` from a second script.

<details class="source"><summary>Answers</summary>

1. Add a branch: `if choice == "s": return (ChatPromptTemplate.from_template("Make this 1 line:\n{t}") | model | StrOutputParser()).invoke({"t": dish})`.
2. In `head_chef_review`, before asking: if `call["name"] == "send_email"` and the address doesn't end with
   `@example.com`, return `ToolMessage("NOT EXECUTED: address not allowed", tool_call_id=call["id"])`.
3. No. ₹120 is not above ₹200, so `is_big_refund` returns `False` and the refund runs automatically. The
   email still pauses, because `send_email` has no `when`.
4. `from langgraph.checkpoint.sqlite import SqliteSaver`, then
   `with SqliteSaver.from_conn_string("tickets.db") as saver:` and pass `checkpointer=saver`. The second
   script builds the same agent, then calls `agent.invoke(Command(resume=...), config={"configurable": {"thread_id": "ticket-001"}}, version="v2")`.

</details>

## Full source

<details class="source"><summary>00.level-approval-1.py</summary>

```{literalinclude} ../code/13-human-in-the-loop/00.level-approval-1.py
:language: python
```

</details>

<details class="source"><summary>01.tool_call.py</summary>

```{literalinclude} ../code/13-human-in-the-loop/01.tool_call.py
:language: python
```

</details>

<details class="source"><summary>02.middleware.py</summary>

```{literalinclude} ../code/13-human-in-the-loop/02.middleware.py
:language: python
```

</details>
