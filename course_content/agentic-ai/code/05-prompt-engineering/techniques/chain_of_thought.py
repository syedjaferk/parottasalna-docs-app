import re

from groq_client import run_prompt
from langchain_core.prompts import ChatPromptTemplate

SAMPLE_INPUT = (
    "A store had 42 notebooks. It sold 17 on Monday and received a new "
    "shipment of 25 on Tuesday, then sold 13 more on Wednesday. How many "
    "notebooks does the store have now?"
)


def build_before_prompt() -> ChatPromptTemplate:
    """Naive prompt: asks straight for the answer, no reasoning scaffold."""
    return ChatPromptTemplate.from_messages(
        [
            ("human", "{problem}\nAnswer with just the number."),
        ]
    )


def build_after_prompt() -> ChatPromptTemplate:
    """
    CoT prompt: forces step-by-step reasoning and a clearly delimited
    final answer, so it's both more accurate and machine-parseable.
    """
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a careful math tutor. Always solve problems by breaking "
                "them into numbered steps before giving the final answer.",
            ),
            (
                "human",
                "{problem}\n\n"
                "Think through this step by step, showing each calculation on its "
                "own numbered line. Then, on a final line by itself, write:\n"
                "FINAL ANSWER: <number>",
            ),
        ]
    )


def extract_final_answer(text: str) -> str:
    """Utility: pull just the numeric answer out of a CoT response."""
    match = re.search(r"FINAL ANSWER:\s*(-?\d+)", text)
    return match.group(1) if match else text.strip()


def get_chain_of_thought(problem: str = SAMPLE_INPUT, mode: str = "after") -> str:
    """Run the CoT reasoning prompt against Groq."""
    prompt = build_before_prompt() if mode == "before" else build_after_prompt()
    return run_prompt(prompt, {"problem": problem})


if __name__ == "__main__":
    print("--- BEFORE ---")
    print(get_chain_of_thought(mode="before"))
    print("\n--- AFTER ---")
    result = get_chain_of_thought(mode="after")
    print(result)
    print("\nExtracted final answer:", extract_final_answer(result))
