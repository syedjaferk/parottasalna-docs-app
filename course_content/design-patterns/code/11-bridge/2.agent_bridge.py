"""Bridge + AI: agent type x model backend, mixed and matched freely.

The backends are offline stand-ins; a real one would call Groq, OpenAI or a local model.
"""
from abc import ABC, abstractmethod


class Backend(ABC):
    @abstractmethod
    def complete(self, prompt: str) -> str: ...


class FakeGroq(Backend):
    def complete(self, prompt): return f"[groq] {prompt.splitlines()[0]}"


class FakeLocal(Backend):
    def complete(self, prompt): return f"[local] {prompt.splitlines()[0]}"


class Agent:
    system_prompt = ""

    def __init__(self, backend: Backend):
        self.backend = backend

    def ask(self, question: str) -> str:
        return self.backend.complete(f"{self.system_prompt}\n\n{question}")


class SupportAgent(Agent):
    system_prompt = "You are a polite customer support agent."


class ResearchAgent(Agent):
    system_prompt = "You are a careful researcher. Cite sources."


for agent in (SupportAgent(FakeGroq()), SupportAgent(FakeLocal()), ResearchAgent(FakeLocal())):
    print(type(agent).__name__, type(agent.backend).__name__, "->", agent.ask("Where is my order?"))
