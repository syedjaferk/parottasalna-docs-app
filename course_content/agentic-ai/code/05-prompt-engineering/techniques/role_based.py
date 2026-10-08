from groq_client import run_prompt
from langchain_core.prompts import ChatPromptTemplate

SAMPLE_INPUT = "Is it safe to store API keys in a .env file?"


def build_before_prompt() -> ChatPromptTemplate:
    """No persona — generic assistant behavior."""
    return ChatPromptTemplate.from_messages(
        [
            ("human", "{question}"),
        ]
    )


def build_after_prompt() -> ChatPromptTemplate:
    """
    Persona prompt: a senior application security engineer, terse,
    risk-focused, and opinionated — a very different answer shape than
    a generic assistant would give.
    """
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a senior application security engineer doing a code "
                "review. You are terse, risk-focused, and always state the "
                "practical severity (Low/Medium/High) of any issue you flag. "
                "You give concrete mitigations, not just warnings.",
            ),
            ("human", "{question}"),
        ]
    )


def get_role_based(question: str = SAMPLE_INPUT, mode: str = "after") -> str:
    """Run the role-based prompt against Groq."""
    prompt = build_before_prompt() if mode == "before" else build_after_prompt()
    return run_prompt(prompt, {"question": question})


if __name__ == "__main__":
    print("--- BEFORE ---")
    print(get_role_based(mode="before"))
    print("\n--- AFTER ---")
    print(get_role_based(mode="after"))
