from groq_client import run_prompt
from langchain_core.prompts import ChatPromptTemplate

SAMPLE_INPUT = "Find the sum of all even numbers between 1 and 50."
SAMPLE_CONTEXT = (
    "The user is learning about Gaussian Summation. "
    "The formula for the sum of the first 'n' even numbers is n(n + 1). "
    "In the range 1-50, there are exactly 25 even numbers."
)


def build_before_prompt() -> ChatPromptTemplate:
    """Naive prompt: asks the question without any background context."""
    return ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful AI assistant."),
            ("human", "{question}"),
        ]
    )


def build_after_prompt() -> ChatPromptTemplate:
    """
    Contextual prompt: feeds background facts to the model before asking
    the question, forcing it to use the provided information.
    """
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Use the provided context to answer the user's question accurately. "
                "If the context provides a formula or fact, you must use it in your answer.",
            ),
            ("human", "Context: {context}\n\nQuestion: {question}"),
        ]
    )


def get_contextual_prompt(
    question: str = SAMPLE_INPUT, context: str = SAMPLE_CONTEXT, mode: str = "after"
) -> str:
    """Run the contextual prompt against Groq."""
    if mode == "before":
        prompt = build_before_prompt()
        return run_prompt(prompt, {"question": question})
    else:
        prompt = build_after_prompt()
        return run_prompt(prompt, {"question": question, "context": context})


if __name__ == "__main__":
    print("--- BEFORE ---")
    print(get_contextual_prompt(mode="before"))
    print("\n--- AFTER ---")
    print(get_contextual_prompt(mode="after"))
