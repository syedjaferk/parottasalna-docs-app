"""Adapter + AI: one ask() interface over SDKs that each have their own call style.

The two "SDK" clients below are small fakes shaped like the real OpenAI and Ollama responses,
so the file runs offline.
"""
from abc import ABC, abstractmethod
from types import SimpleNamespace as NS


class FakeOpenAIClient:      # shaped like openai.OpenAI()
    def __init__(self):
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, model, messages):
        text = f"[{model}] {messages[-1]['content']}"
        return NS(choices=[NS(message=NS(content=text))])


class FakeOllamaClient:      # shaped like ollama.Client()
    def generate(self, model, prompt):
        return {"response": f"[{model}] {prompt}"}


class LLM(ABC):
    @abstractmethod
    def ask(self, prompt: str) -> str: ...


class OpenAIAdapter(LLM):
    def __init__(self, client):
        self.client = client

    def ask(self, prompt):
        r = self.client.chat.completions.create(
            model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
        return r.choices[0].message.content


class OllamaAdapter(LLM):
    def __init__(self, client):
        self.client = client

    def ask(self, prompt):
        r = self.client.generate(model="llama3", prompt=prompt)
        return r["response"]


def answer(llm: LLM, question: str):        # the app only knows LLM.ask
    print(llm.ask(question))


answer(OpenAIAdapter(FakeOpenAIClient()), "What is an adapter?")
answer(OllamaAdapter(FakeOllamaClient()), "What is an adapter?")
