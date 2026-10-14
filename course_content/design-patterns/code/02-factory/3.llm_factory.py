"""Factory + AI: pick the LLM provider from a setting.

Imports sit inside the branches, so you only need the package for the provider you use.
LLM_PROVIDER=fake (the default here) runs offline.
"""
import os


class FakeLLM:
    def invoke(self, prompt):
        return type("Msg", (), {"content": f"(fake answer to: {prompt})"})()


def create_llm(provider: str):
    if provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(model="openai/gpt-oss-120b")
    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model="gpt-4o-mini")
    if provider == "fake":
        return FakeLLM()
    raise ValueError(f"unknown provider {provider!r}")


llm = create_llm(os.getenv("LLM_PROVIDER", "fake"))
print(type(llm).__name__)
print(llm.invoke("Explain the factory pattern in one line.").content)
