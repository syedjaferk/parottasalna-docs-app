# llm.py - ONE small helper that talks to any OpenAI-compatible AI provider
# (Groq, OpenRouter, Ollama...). Every later session imports this file.
import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("LLM_API_KEY", "")
BASE_URL = os.getenv("LLM_BASE_URL", "").rstrip("/")
MODEL = os.getenv("LLM_MODEL", "")


def chat(messages, temperature=0.7, max_tokens=300, model=None):
    """Send a list of messages to the AI. Returns (reply_text, usage_dict)."""
    response = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "model": model or MODEL,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    reply = data["choices"][0]["message"]["content"]
    return reply, data.get("usage", {})
