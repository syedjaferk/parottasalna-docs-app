# classify_llm.py - System 2: ask a big, slow, smart LLM to put a message into a category.
import json
import time

from llm import call_api
from messages import CATEGORIES

SYSTEM = (
    "You sort customer messages into ONE category. "
    f"Allowed categories: {', '.join(CATEGORIES)}. "
    'Reply ONLY with JSON like {"category": "billing"}.'
)


def llm_classify(text):
    """Return (label, seconds_taken)."""
    start = time.time()
    data = call_api({
        "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": text}],
        "temperature": 0,
        "response_format": {"type": "json_object"},
        "max_tokens": 30,
    })
    label = json.loads(data["choices"][0]["message"]["content"]).get("category", "other")
    return (label if label in CATEGORIES else "other"), time.time() - start


if __name__ == "__main__":
    print(llm_classify("I was charged twice for my order"))
