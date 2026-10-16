# llm.py (version 2) - the same helper as Session 2, now with error handling.
# Replace your old llm.py with this one.
import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("LLM_API_KEY", "")
BASE_URL = os.getenv("LLM_BASE_URL", "").rstrip("/")
MODEL = os.getenv("LLM_MODEL", "")

RETRY_STATUS = {429, 500, 502, 503, 504}     # "try again later" errors


class LLMError(Exception):
    """A problem talking to the AI, with a message a human can understand."""


def call_api(body, retries=3):
    """Send a request body to the AI. Returns the full JSON answer (a dict).

    Retries politely (1s, 2s, 4s ...) when the server is busy, and raises LLMError otherwise.
    """
    body = {"model": MODEL, **body}
    last_problem = ""
    for attempt in range(retries + 1):
        try:
            response = requests.post(
                f"{BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {API_KEY}"},
                json=body,
                timeout=60,
            )
        except (requests.Timeout, requests.ConnectionError) as error:
            last_problem = f"network problem ({error.__class__.__name__})"
        else:
            if response.status_code == 200:
                return response.json()
            if response.status_code in (401, 403):
                raise LLMError("The provider rejected your API key. Check LLM_API_KEY in your .env file.")
            if response.status_code == 404:
                raise LLMError(f"Model or URL not found. Check LLM_MODEL and LLM_BASE_URL. ({response.text[:120]})")
            if response.status_code not in RETRY_STATUS:
                raise LLMError(f"The provider answered {response.status_code}: {response.text[:200]}")
            last_problem = f"server busy (status {response.status_code})"
        if attempt < retries:
            wait = 2 ** attempt                      # 1, 2, 4 seconds
            print(f"  ...{last_problem}. Waiting {wait}s, then trying again ({attempt + 1}/{retries})")
            time.sleep(wait)
    raise LLMError(f"Gave up after {retries + 1} tries: {last_problem}")


def chat(messages, temperature=0.7, max_tokens=300, model=None):
    """Simple helper: send messages, get back (reply_text, usage)."""
    body = {"messages": messages, "temperature": temperature, "max_tokens": max_tokens}
    if model:
        body["model"] = model
    data = call_api(body)
    return data["choices"][0]["message"]["content"], data.get("usage", {})
