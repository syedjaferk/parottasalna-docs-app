from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.tools import StructuredTool
from model import model
from pydantic import BaseModel, Field


# ---------------------------------------------------------------
# WAY 1: @tool decorator (fastest). Docstring = description for the LLM.
# Type hints = argument schema.
# ---------------------------------------------------------------
@tool
def word_count(text: str) -> int:
    """Count the number of words in the given text."""
    return len(text.split())


# ---------------------------------------------------------------
# WAY 2: Pydantic args_schema (rich validation + per-field descriptions)
# ---------------------------------------------------------------
class DiscountInput(BaseModel):
    price: float = Field(gt=0, description="Original price of the item")
    percent: float = Field(ge=0, le=100, description="Discount percentage, 0-100")


@tool("apply_discount", args_schema=DiscountInput)
def apply_discount(price: float, percent: float) -> str:
    """Calculate the final price after applying a percentage discount."""
    final = price * (1 - percent / 100)
    return f"Final price: {final:.2f}"


# ---------------------------------------------------------------
# WAY 3: StructuredTool.from_function (wrap existing functions/libraries)
# ---------------------------------------------------------------
def _celsius_to_fahrenheit(celsius: float) -> float:
    return celsius * 9 / 5 + 32


c_to_f = StructuredTool.from_function(
    func=_celsius_to_fahrenheit,
    name="celsius_to_fahrenheit",
    description="Convert a temperature from Celsius to Fahrenheit.",
)

tools = [word_count, apply_discount, c_to_f]

# ---------------------------------------------------------------
# What the LLM actually sees about each tool
# ---------------------------------------------------------------
print("=== Tool metadata the LLM receives ===")
for t in tools:
    print(f"\nname       : {t.name}")
    print(f"description: {t.description}")
    print(f"args       : {t.args}")

# Tools can be tested directly, no LLM needed
print("\nDirect call:", apply_discount.invoke({"price": 2000, "percent": 15}))

# ---------------------------------------------------------------
# Give the tools to an agent
# ---------------------------------------------------------------
agent = create_agent(
    model,
    tools=tools,
    system_prompt="You are a helpful assistant. Use tools for calculations.",
)

question = (
    "A jacket costs 2000 and has a 15% discount. What is the final price? "
    "Also convert 36.6 Celsius to Fahrenheit, and count the words in "
    "'tools make agents useful'."
)
result = agent.invoke({"messages": [{"role": "user", "content": question}]})

print("\n=== Conversation trace ===")
for m in result["messages"]:
    m.pretty_print()
