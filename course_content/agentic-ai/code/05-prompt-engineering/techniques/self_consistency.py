import re
from collections import Counter

from groq_client import run_prompt
from langchain_core.prompts import ChatPromptTemplate

SAMPLE_INPUT = "Find the sum of all even numbers between 1 and 50."


def build_consistency_prompt() -> ChatPromptTemplate:
    """
    Prompt designed for Self-Consistency. We use a CoT-like format so the
    model shows its work and ends with a parseable final answer.
    """
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Solve the problem step-by-step. End your response with a final line: "
                "'Final Answer: <number>'",
            ),
            ("human", "{question}"),
        ]
    )


def extract_final_answer(text: str) -> str | None:
    """Extracts the final numeric answer from the text."""
    match = re.search(r"Final Answer:\s*(-?\d+)", text, re.IGNORECASE)
    return match.group(1) if match else None


def get_self_consistency(
    question: str = SAMPLE_INPUT, mode: str = "after", num_samples: int = 5
) -> str:
    """
    Run the self-consistency prompt against Groq.
    If mode == "before", we just run it once.
    If mode == "after", we run it `num_samples` times and take a majority vote.
    """
    prompt = build_consistency_prompt()

    if mode == "before":
        # Just run once at temperature 0 (or default)
        result_text = run_prompt(prompt, {"question": question}, temperature=0)
        answer = extract_final_answer(result_text)
        return f"Single Run Output:\n{result_text}\n\nExtracted Answer: {answer}"

    # mode == "after": Run multiple times with higher temperature
    print(f"Generating {num_samples} reasoning paths...")
    results = []

    for i in range(num_samples):
        # We use a higher temperature to allow for diverse reasoning paths
        text = run_prompt(prompt, {"question": question}, temperature=0.7)
        answer = extract_final_answer(text)

        if answer:
            results.append(answer)
            print(f" Sample {i + 1}: Found answer {answer}")
        else:
            print(f" Sample {i + 1}: No parseable answer found.")

    if not results:
        return "No valid answers found across all samples."

    # Determine the majority vote
    vote_count = Counter(results)
    final_answer, count = vote_count.most_common(1)[0]

    return f"\nConsistent Answer: {final_answer} (Found in {count}/{num_samples} paths)"


if __name__ == "__main__":
    print("--- BEFORE (Single Run) ---")
    print(get_self_consistency(mode="before"))
    print("\n--- AFTER (Majority Vote) ---")
    print(get_self_consistency(mode="after", num_samples=3))
