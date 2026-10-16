# budget.py - a daily TOKEN budget, so a bug or a flood of messages can never run up a big bill.
import json
import os
from datetime import date

from llm import LLMError, call_api


class BudgetExceeded(LLMError):
    """Raised when today's token budget is used up."""


class Budget:
    def __init__(self, daily_tokens=50_000, file="budget.json"):
        self.daily_tokens = daily_tokens
        self.file = file

    def _load(self):
        if os.path.exists(self.file):
            with open(self.file, encoding="utf-8") as f:
                data = json.load(f)
            if data.get("day") == date.today().isoformat():
                return data
        return {"day": date.today().isoformat(), "used": 0}      # a new day starts at zero

    def used(self):
        return self._load()["used"]

    def remaining(self):
        return max(0, self.daily_tokens - self.used())

    def add(self, tokens):
        data = self._load()
        data["used"] += tokens or 0
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def check(self):
        if self.remaining() <= 0:
            raise BudgetExceeded(f"Daily budget of {self.daily_tokens} tokens is used up. Try again tomorrow.")


budget = Budget()


def safe_call_api(body):
    """Like call_api, but refuses when the budget is used up, and records every call's tokens."""
    budget.check()
    data = call_api(body)
    budget.add(data.get("usage", {}).get("total_tokens", 0))
    return data


if __name__ == "__main__":
    budget.daily_tokens = 100                 # a tiny budget, just for this demo
    for i in range(1, 8):
        try:
            data = safe_call_api({"messages": [{"role": "user", "content": f"Say the number {i}."}], "max_tokens": 10})
            print(f"call {i}: ok, used {budget.used()} / {budget.daily_tokens} tokens")
        except BudgetExceeded as error:
            print(f"call {i}: STOPPED -> {error}")
            break
