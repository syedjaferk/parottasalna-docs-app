# Session 18 · Chain of Responsibility pattern

## The big idea

A request needs to be handled, but **you don't know in advance who should handle it**, or several
checks must run one after another. The **Chain of Responsibility** pattern links handlers in a line.
Each handler either **handles** the request, **rejects** it, or **passes it on** to the next.

**Everyday example:** support escalation. First-level support tries your issue. If they can't solve
it, it goes to the senior engineer, then to the manager. You don't choose who; the chain does.

:::{admonition} In plain words
:class: tip
Send a request down a **line of handlers**. Each one either deals with it (and stops the line) or passes it on to the next.

**Reach for it when:**

- several checks or handlers run in order, and any one may stop the request
- you want to add, remove or reorder steps easily
- you don't know in advance who will handle the request
:::

## Without Chain of Responsibility

`0.no_chain.py`: one big function with all checks.

```python
def handle_request(req):
    if not req.get("token"):
        return "401 not logged in"
    if req["user"] in blocked_users:
        return "403 blocked"
    if req["count"] > 100:
        return "429 too many requests"
    if len(req["body"]) > 1000:
        return "413 too large"
    return "200 ok"
```

It works, but adding, removing or reordering a check means editing this function, and you can't
reuse a single check elsewhere.

## With Chain of Responsibility

`1.chain.py`:

```python
from abc import ABC, abstractmethod

class Handler(ABC):
    def __init__(self):
        self._next: "Handler | None" = None

    def set_next(self, handler: "Handler") -> "Handler":
        self._next = handler
        return handler                   # lets us chain set_next calls

    def handle(self, req: dict) -> str:
        result = self.check(req)
        if result is not None:           # this handler stops the chain
            return result
        if self._next:
            return self._next.handle(req)
        return "200 ok"

    @abstractmethod
    def check(self, req: dict) -> str | None:
        """Return an error string to stop, or None to continue."""

class AuthCheck(Handler):
    def check(self, req):
        return None if req.get("token") else "401 not logged in"

class BlockedCheck(Handler):
    blocked = {"spammer"}
    def check(self, req):
        return "403 blocked" if req["user"] in self.blocked else None

class RateLimitCheck(Handler):
    def check(self, req):
        return "429 too many requests" if req["count"] > 100 else None

class SizeCheck(Handler):
    def check(self, req):
        return "413 too large" if len(req["body"]) > 1000 else None

chain = AuthCheck()
chain.set_next(BlockedCheck()).set_next(RateLimitCheck()).set_next(SizeCheck())

print(chain.handle({"token": "abc", "user": "kavya", "count": 5, "body": "hi"}))        # 200 ok
print(chain.handle({"token": "abc", "user": "spammer", "count": 5, "body": "hi"}))      # 403 blocked
print(chain.handle({"token": None, "user": "kavya", "count": 5, "body": "hi"}))         # 401 not logged in
```

Each check is small and testable. You can reorder or drop any link when building the chain.

```{raw} html
:file: ../diagrams/s18-chain.html
```

## Where you already use it

Web **middleware** is a chain: request → auth → logging → CORS → your view. Django, FastAPI and
Express all work this way. Python's `logging` handlers and exception handling (`except` blocks tried
in order) follow the same idea.

## A simple function-based chain

For small cases, a list of functions is enough (`2.func_chain.py`):

```python
def has_token(req):  return None if req.get("token") else "401 not logged in"
def not_blocked(req): return "403 blocked" if req["user"] == "spammer" else None

checks = [has_token, not_blocked]

def run(req):
    for check in checks:
        error = check(req)
        if error:
            return error
    return "200 ok"
```

## Chain + AI: guardrails around an LLM

Before the prompt reaches the model, and before the answer reaches the user, run it through checks
(`3.guardrails.py`):

```python
import re

def no_empty(text):
    return "Please type something." if not text.strip() else None

def no_secrets(text):
    return "Don't share API keys." if re.search(r"sk-[A-Za-z0-9]{10,}", text) else None

def max_length(text):
    return "Message too long." if len(text) > 2000 else None

input_guards = [no_empty, max_length, no_secrets]

def safe_ask(user_text):
    for guard in input_guards:
        problem = guard(user_text)
        if problem:
            return problem                  # stop: never reaches the LLM
    return llm.invoke(user_text).content    # all checks passed
```

Cheap checks first, so you don't pay for an LLM call you were going to reject.

## Chain vs Decorator

- **Decorator** always runs the wrapped function and adds to it.
- **Chain** may **stop** the request early. Handlers decide whether to continue.

## Common mistakes

- **Nobody handles it.** If every handler passes, define what happens at the end (default result or error).
- **Wrong order.** Run cheap, likely-to-fail checks first (auth before database work).
- **A cycle.** Linking a handler back to an earlier one loops forever.
- **Handlers with hidden side effects.** One that modifies the request surprises later handlers.
  Document or avoid it.

## Hands-on exercises

**Exercise 1 · Add a handler.** Add `ContentCheck` that rejects a body containing the word "spam".

<details class="solution"><summary>Solution</summary>

```python
class ContentCheck(Handler):
    def check(self, req):
        return "400 spam detected" if "spam" in req["body"].lower() else None

chain = AuthCheck()
chain.set_next(BlockedCheck()).set_next(RateLimitCheck()).set_next(SizeCheck()).set_next(ContentCheck())

print(chain.handle({"token": "abc", "user": "kavya", "count": 5, "body": "Buy SPAM now"}))   # 400 spam detected
```

Build the chain in the order you want, ending with the new handler.

</details>

**Exercise 2 · Support escalation.** `Level1` handles "password", `Level2` handles "billing",
`Manager` handles everything else.

<details class="solution"><summary>Solution</summary>

```python
class Support:
    def __init__(self, name, topic=None):
        self.name, self.topic, self._next = name, topic, None

    def set_next(self, s):
        self._next = s
        return s

    def handle(self, issue):
        if self.topic is None or self.topic in issue:
            return f"{self.name} handled: {issue}"
        if self._next:
            return self._next.handle(issue)
        return "nobody could help"

l1 = Support("Level 1", "password")
l1.set_next(Support("Level 2", "billing")).set_next(Support("Manager"))

print(l1.handle("password reset"))       # Level 1 handled
print(l1.handle("billing error"))        # Level 2 handled
print(l1.handle("legal complaint"))      # Manager handled
```

</details>

**Exercise 3 · Expense approval.** Up to ₹5,000: team lead; up to ₹50,000: manager; above: director.

<details class="solution"><summary>Solution</summary>

```python
class Approver:
    def __init__(self, name, limit):
        self.name, self.limit, self._next = name, limit, None

    def set_next(self, a):
        self._next = a
        return a

    def approve(self, amount):
        if amount <= self.limit:
            return f"{self.name} approved ₹{amount}"
        if self._next:
            return self._next.approve(amount)
        return "rejected: no one can approve this"

lead = Approver("Team lead", 5_000)
lead.set_next(Approver("Manager", 50_000)).set_next(Approver("Director", float("inf")))

print(lead.approve(3_000))      # Team lead approved
print(lead.approve(20_000))     # Manager approved
print(lead.approve(200_000))    # Director approved
```

</details>

## Full source

<details class="source">
<summary>1.chain.py</summary>

```{literalinclude} ../code/18-chain/1.chain.py
:language: python
```

</details>

<details class="source">
<summary>3.guardrails.py</summary>

```{literalinclude} ../code/18-chain/3.guardrails.py
:language: python
```

</details>

**Downloads:**
{download}`0.no_chain.py <../code/18-chain/0.no_chain.py>` ·
{download}`1.chain.py <../code/18-chain/1.chain.py>` ·
{download}`2.func_chain.py <../code/18-chain/2.func_chain.py>` ·
{download}`3.guardrails.py <../code/18-chain/3.guardrails.py>`
