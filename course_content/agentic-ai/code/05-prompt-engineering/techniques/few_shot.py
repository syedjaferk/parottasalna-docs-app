from groq_client import run_prompt
from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
)

SAMPLE_INPUT = "The screen flickers randomly and sometimes the laptop won't turn on."

EXAMPLES = [
    {
        "ticket": "My order arrived broken and the box was crushed.",
        "output": "Category: Shipping Damage | Reason: physical damage reported on arrival.",
    },
    {
        "ticket": "I was charged twice for the same subscription this month.",
        "output": "Category: Billing | Reason: duplicate charge on subscription.",
    },
    {
        "ticket": "The app crashes every time I try to upload a photo.",
        "output": "Category: Bug Report | Reason: reproducible crash on a specific action.",
    },
]


def build_before_prompt() -> ChatPromptTemplate:
    """Zero-shot version of the same classification task (no examples)."""
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Classify the support ticket into a category with a one-line reason.",
            ),
            ("human", "{ticket}"),
        ]
    )


def build_after_prompt() -> ChatPromptTemplate:
    """Few-shot version: examples teach the model the exact output format."""
    example_prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "{ticket}"),
            ("ai", "{output}"),
        ]
    )

    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=EXAMPLES,
    )

    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Classify each support ticket into a category with a one-line reason. "
                "Always reply in the exact format: 'Category: <category> | Reason: <reason>'. "
                "No extra commentary.",
            ),
            few_shot_prompt,
            ("human", "{ticket}"),
        ]
    )


def get_few_shot(ticket: str = SAMPLE_INPUT, mode: str = "after") -> str:
    """Run the few-shot classification prompt against Groq."""
    prompt = build_before_prompt() if mode == "before" else build_after_prompt()
    return run_prompt(prompt, {"ticket": ticket})


if __name__ == "__main__":
    print("--- BEFORE ---")
    print(get_few_shot(mode="before"))
    print("\n--- AFTER ---")
    print(get_few_shot(mode="after"))
