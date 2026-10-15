# prompt_patterns.py - the same task with weak, then strong prompts
from llm import chat

REVIEW = "The food was cold and the waiter was rude, but the dessert was amazing."


def ask(title, prompt):
    reply, _ = chat([{"role": "user", "content": prompt}], temperature=0, max_tokens=120)
    print(f"\n=== {title} ===\n{reply.strip()}")


# 1. Weak: no instructions, so the answer can be anything
ask("Weak prompt", f"Review: {REVIEW}\nSentiment?")

# 2. Instructions + constraints
ask("Instructions + constraints",
    f"Classify the sentiment of the review as exactly one word: positive, negative or mixed.\n"
    f"Reply with only that word.\n\nReview: {REVIEW}")

# 3. Few-shot: show examples of what you want
ask("Few-shot examples",
    "Classify the sentiment as positive, negative or mixed. Reply with only that word.\n\n"
    "Review: Loved everything! -> positive\n"
    "Review: Terrible service, never again. -> negative\n"
    "Review: Great view but the room was dirty. -> mixed\n"
    f"Review: {REVIEW} ->")
