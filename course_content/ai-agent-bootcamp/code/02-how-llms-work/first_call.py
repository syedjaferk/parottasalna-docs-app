# first_call.py - your very first AI call, with NOTHING hidden.
# We use plain `requests` so you can see the real request and the real answer.
import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("LLM_BASE_URL").rstrip("/") + "/chat/completions"
headers = {"Authorization": "Bearer " + os.getenv("LLM_API_KEY")}
body = {
    "model": os.getenv("LLM_MODEL"),
    "messages": [{"role": "user", "content": "Explain what a variable is in one sentence."}],
}

response = requests.post(url, headers=headers, json=body, timeout=60)
print("Status code:", response.status_code)
print(json.dumps(response.json(), indent=2))
