from groq_client import run_prompt
from langchain_core.prompts import ChatPromptTemplate

SAMPLE_INPUT = "Explain what RAG (Retrieval-Augmented Generation) is."


def build_before_prompt() -> ChatPromptTemplate:
    """Naive zero-shot prompt: just forwards the raw user question."""
    return ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful AI assistant."),
            ("human", "{question}"),
        ]
    )


def build_after_prompt() -> ChatPromptTemplate:
    """
    Engineered zero-shot prompt:
    - defines the audience
    - constrains length
    - specifies structure
    - forbids jargon without definition
    """
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a technical writer creating documentation for junior "
                "software engineers who know Python but have never used LLMs.",
            ),
            (
                "human",
                "{question}\n\n"
                "Requirements:\n"
                "- Answer in exactly 3 short paragraphs.\n"
                "- Paragraph 1: one-sentence definition.\n"
                "- Paragraph 2: why it matters / what problem it solves.\n"
                "- Paragraph 3: a concrete, everyday analogy.\n"
                "- Do not use the words 'leverage' or 'utilize'.\n"
                "- Define any acronym the first time you use it.",
            ),
        ]
    )


def get_zero_shot(question: str = SAMPLE_INPUT, mode: str = "after") -> str:
    """
    Run the zero-shot prompt against Groq.

    Args:
        question: the user's raw question
        mode: "before" or "after" — which prompt variant to use
    """
    prompt = build_before_prompt() if mode == "before" else build_after_prompt()
    return run_prompt(prompt, {"question": question})


if __name__ == "__main__":
    print("--- BEFORE ---")
    print(get_zero_shot(mode="before"))
    print("\n--- AFTER ---")
    print(get_zero_shot(mode="after"))
