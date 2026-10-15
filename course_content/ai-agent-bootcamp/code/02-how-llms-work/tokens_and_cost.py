# tokens_and_cost.py - see how many tokens a call uses (this is what you pay for)
from llm import chat

messages = [{"role": "user", "content": "Write two sentences about the Marina Beach in Chennai."}]
reply, usage = chat(messages, max_tokens=120)

print("Reply:", reply.strip())
print()
print("Tokens you SENT     :", usage.get("prompt_tokens"))
print("Tokens the AI WROTE :", usage.get("completion_tokens"))
print("Total tokens        :", usage.get("total_tokens"))

# A rough rule for English: 1 token is about 4 letters.
words = len(messages[0]["content"].split())
print(f"\nYour message has {words} words, so we expect roughly {round(words * 1.3)} tokens.")

# Example price calculation (the numbers are made up, just to show the idea):
PRICE_PER_MILLION_INPUT = 0.05      # dollars per 1,000,000 input tokens
PRICE_PER_MILLION_OUTPUT = 0.08     # dollars per 1,000,000 output tokens
cost = (usage.get("prompt_tokens", 0) * PRICE_PER_MILLION_INPUT +
        usage.get("completion_tokens", 0) * PRICE_PER_MILLION_OUTPUT) / 1_000_000
print(f"This one call would cost about ${cost:.8f}")
