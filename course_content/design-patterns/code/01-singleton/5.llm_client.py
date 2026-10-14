"""One LLM client per process: lru_cache(maxsize=1) on a function with no arguments.

Runs offline with a stand-in client. With langchain-groq installed and GROQ_API_KEY set, it
creates a real ChatGroq client instead.
"""
import os
from functools import lru_cache


class FakeLLM:
    def invoke(self, prompt):
        return type("Msg", (), {"content": f"(fake answer to: {prompt})"})()


@lru_cache(maxsize=1)
def get_llm():
    print("Creating LLM client...")
    if os.getenv("GROQ_API_KEY"):
        from langchain_groq import ChatGroq
        return ChatGroq(model="openai/gpt-oss-120b")
    return FakeLLM()


llm_1 = get_llm()
llm_2 = get_llm()
print(llm_1 is llm_2)    # True, "Creating LLM client..." printed once
print(llm_1.invoke("What is a Singleton?").content)
