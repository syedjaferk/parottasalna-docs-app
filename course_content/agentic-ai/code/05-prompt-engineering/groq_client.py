import os

import requests
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "openai/gpt-oss-120b"


def call_groq(
    messages: list[dict], model: str = DEFAULT_MODEL, temperature: float = 0
) -> str:
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY not set. Copy .env.example to .env and add your key "
            "(get one free at https://console.groq.com/keys)."
        )

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"model": model, "messages": messages, "temperature": temperature}
    response = requests.post(GROQ_URL, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Request failed: {response.status_code} - {response.text}"


def render_messages(prompt: ChatPromptTemplate, variables: dict) -> list[dict]:
    """
    Bridge function: takes a LangChain ChatPromptTemplate, fills in the
    variables, and converts the result into the plain
    [{"role": ..., "content": ...}] list that call_groq() expects.

    This is the one place LangChain's prompt objects meet the raw Groq
    HTTP call, so every technique module can build prompts with LangChain
    while still using your `requests`-based call_groq under the hood.
    """
    formatted = prompt.format_messages(**variables)
    role_map = {"human": "user", "ai": "assistant", "system": "system"}
    return [
        {"role": role_map.get(m.type, m.type), "content": m.content} for m in formatted
    ]


def run_prompt(
    prompt: ChatPromptTemplate,
    variables: dict,
    model: str = DEFAULT_MODEL,
    temperature: float = 0,
) -> str:
    """Convenience one-liner: render a LangChain prompt and call Groq."""
    messages = render_messages(prompt, variables)
    return call_groq(messages, model=model, temperature=temperature)
