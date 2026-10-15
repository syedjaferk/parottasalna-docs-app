# json_mode.py - make the AI return JSON your code can read
import json

from llm import call_api

REVIEW = "The food was cold and the waiter was rude, but the dessert was amazing."

body = {
    "messages": [
        {"role": "system",
         "content": 'You are a review analyser. Reply ONLY with JSON in this exact shape: '
                    '{"sentiment": "positive|negative|mixed", "score": <0-10>, "topics": ["..."]}'},
        {"role": "user", "content": REVIEW},
    ],
    "temperature": 0,
    "response_format": {"type": "json_object"},       # ask the provider to enforce valid JSON
    "max_tokens": 200,
}

data = call_api(body)
text = data["choices"][0]["message"]["content"]
print("Raw text from the AI:\n", text)

# Never trust the output blindly: parse it and check it.
try:
    result = json.loads(text)
except json.JSONDecodeError:
    raise SystemExit("The AI did not return valid JSON. Try again or lower the temperature.")

missing = [key for key in ("sentiment", "score", "topics") if key not in result]
if missing:
    raise SystemExit(f"The AI forgot these keys: {missing}")
if result["sentiment"] not in ("positive", "negative", "mixed"):
    raise SystemExit(f"Unexpected sentiment: {result['sentiment']!r}")

print("\nNow it is a Python dictionary we can use:")
print("Sentiment:", result["sentiment"])
print("Score    :", result["score"])
print("Topics   :", ", ".join(result["topics"]))
