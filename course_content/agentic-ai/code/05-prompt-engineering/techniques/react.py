from groq_client import run_prompt
from langchain_core.prompts import ChatPromptTemplate

SAMPLE_INPUT = "What is the weather in Chennai?"


def get_weather(city: str) -> str:
    """Mock external tool: Returns weather data for a given city."""
    data = {"London": "15°C and Rainy", "Chennai": "32°C and Sunny"}
    return data.get(city.strip(), f"Weather data not found for {city}.")


def build_before_prompt() -> ChatPromptTemplate:
    """Naive prompt: asks directly without tools."""
    return ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant. Do your best to answer."),
            ("human", "{question}"),
        ]
    )


def build_react_prompt() -> ChatPromptTemplate:
    """
    ReAct prompt: defines the Thought-Action-Observation loop constraint.
    """
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a ReAct Agent. You solve problems by alternating between Thought, Action, and Observation.\n"
                "Available tools:\n"
                "- get_weather[city]: Returns the current weather.\n\n"
                "Format:\n"
                "Thought: [Your reasoning]\n"
                "Action: [tool_name][argument]\n"
                "Observation: [Result from tool]\n"
                "... (repeat until done)\n"
                "Final Answer: [The result]",
            ),
            ("human", "{question}\n\n{agent_scratchpad}"),
        ]
    )


def get_react(
    question: str = SAMPLE_INPUT, mode: str = "after", max_iterations: int = 3
) -> str:
    """Run the ReAct loop against Groq."""
    if mode == "before":
        prompt = build_before_prompt()
        return run_prompt(prompt, {"question": question})

    # mode == "after": Execute ReAct Loop
    prompt = build_react_prompt()
    agent_scratchpad = ""

    print(f"User: {question}\n")

    for i in range(max_iterations):
        # Generate the next thought/action
        ai_text = run_prompt(
            prompt, {"question": question, "agent_scratchpad": agent_scratchpad}
        )
        print(ai_text)

        # Check if the model wants to take an action
        if "Action:" in ai_text:
            # Append the AI's generation to the scratchpad to maintain history
            agent_scratchpad += f"\n{ai_text}"

            # Very simple parsing logic to extract tool name and argument
            try:
                tool_call = ai_text.split("Action:")[1].strip()
                tool_name = tool_call.split("[")[0].strip()
                arg = tool_call.split("[")[1].split("]")[0].strip()
            except IndexError:
                print("Failed to parse Action format. Breaking loop.")
                break

            print(f"-- Tool Execution: {tool_name} with arg {arg} --")

            if tool_name == "get_weather":
                obs = get_weather(arg)
            else:
                obs = "Unknown tool."

            print(f"Observation: {obs}\n")

            # Feed the Observation back into the scratchpad
            agent_scratchpad += f"\nObservation: {obs}"
        else:
            # If no Action is requested, the model has likely produced the Final Answer
            return "\nAgent finished loop."

    return "\nMax iterations reached without Final Answer."


if __name__ == "__main__":
    print("--- BEFORE (No Tools) ---")
    print(get_react(mode="before"))
    print("\n\n--- AFTER (ReAct Loop) ---")
    print(get_react(mode="after"))
