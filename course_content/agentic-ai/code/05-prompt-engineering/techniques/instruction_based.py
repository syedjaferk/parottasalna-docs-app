import json

from groq_client import run_prompt
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field, ValidationError

SAMPLE_INPUT = (
    "LangChain is a framework for building LLM applications, released in "
    "2022, written primarily in Python, with over 90k GitHub stars."
)


class ProjectFacts(BaseModel):
    """Schema the model must fill in for the AFTER (structured) variant."""

    name: str = Field(description="Name of the software project")
    category: str = Field(description="What kind of tool/framework it is")
    release_year: int | None = Field(
        default=None, description="Year released, if mentioned"
    )
    primary_language: str | None = Field(
        default=None, description="Main language, if mentioned"
    )
    popularity_signal: str | None = Field(
        default=None, description="Any popularity metric mentioned, e.g. GitHub stars"
    )


def build_before_prompt() -> ChatPromptTemplate:
    """Naive instruction: free-text extraction, no schema."""
    return ChatPromptTemplate.from_messages(
        [
            ("human", "Tell me the key facts about this project:\n{text}"),
        ]
    )


def build_after_prompt() -> ChatPromptTemplate:
    """
    Structured instruction: fill exactly this JSON schema, nothing else.
    The schema is spelled out in the prompt itself since we're not using
    a LangChain-native structured-output binding here.
    """
    schema_hint = json.dumps(ProjectFacts.model_json_schema()["properties"], indent=2)
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Extract structured facts from the given text and respond with "
                "ONLY a single valid JSON object — no markdown fences, no prose "
                "before or after. Use null for any field not mentioned in the "
                "text. Do not guess.\n\n"
                f"JSON fields required:\n{schema_hint}",
            ),
            ("human", "{text}"),
        ]
    )


def get_instruction_based_before(text: str = SAMPLE_INPUT) -> str:
    """Unstructured free-text extraction."""
    prompt = build_before_prompt()
    return run_prompt(prompt, {"text": text})


def get_instruction_based_after(text: str = SAMPLE_INPUT) -> ProjectFacts:
    """
    Structured extraction: prompts for strict JSON, then parses and
    validates it against ProjectFacts. Raises ValueError if the model's
    output isn't valid JSON matching the schema.
    """
    prompt = build_after_prompt()
    raw = run_prompt(prompt, {"text": text}, temperature=0)

    cleaned = (
        raw.strip()
        .removeprefix("```json")
        .removeprefix("```")
        .removesuffix("```")
        .strip()
    )

    try:
        data = json.loads(cleaned)
        return ProjectFacts.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as e:
        raise ValueError(
            f"Model did not return valid structured output: {e}\nRaw output: {raw}"
        )


if __name__ == "__main__":
    print("--- BEFORE (free text) ---")
    print(get_instruction_based_before())

    print("\n--- AFTER (structured, validated) ---")
    result = get_instruction_based_after()
    print(result.model_dump_json(indent=2))
