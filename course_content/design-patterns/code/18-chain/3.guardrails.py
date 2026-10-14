"""Chain + AI: cheap input guardrails run before a (paid) LLM call."""
import re


class FakeLLM:
    def __init__(self):
        self.calls = 0

    def invoke(self, prompt):
        self.calls += 1
        return type("Msg", (), {"content": f"(answer to: {prompt[:30]})"})()


llm = FakeLLM()


def no_empty(text):
    return "Please type something." if not text.strip() else None


def no_secrets(text):
    return "Don't share API keys." if re.search(r"sk-[A-Za-z0-9]{10,}", text) else None


def max_length(text):
    return "Message too long." if len(text) > 2000 else None


input_guards = [no_empty, max_length, no_secrets]      # cheap checks first


def safe_ask(user_text):
    for guard in input_guards:
        problem = guard(user_text)
        if problem:
            return problem                  # stop: never reaches the LLM
    return llm.invoke(user_text).content    # all checks passed


print(safe_ask("   "))
print(safe_ask("my key is sk-abcdefghijklmnop, why does it fail?"))
print(safe_ask("x" * 5000))
print(safe_ask("What is the chain of responsibility pattern?"))
print(f"LLM calls: {llm.calls}")             # 1: only the good message cost money
