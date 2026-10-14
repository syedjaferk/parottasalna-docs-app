"""Chain of Responsibility: small handlers in a line; each handles, stops or passes on."""
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
    def check(self, req: dict) -> "str | None":
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
