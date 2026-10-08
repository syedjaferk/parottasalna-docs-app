from groq_client import run_prompt
from langchain_core.prompts import ChatPromptTemplate

SAMPLE_INPUT = "I want to integrate an API Gateway for my microservices."


def build_before_prompt() -> ChatPromptTemplate:
    """Naive prompt: asks for a solution in one go."""
    return ChatPromptTemplate.from_messages(
        [
            ("system", "You are an expert system architect."),
            ("human", "{question}"),
        ]
    )


def build_propose_prompt() -> ChatPromptTemplate:
    """ToT Step 1: Propose multiple distinct approaches."""
    return ChatPromptTemplate.from_messages(
        [
            ("system", "You are a creative technical strategist."),
            (
                "human",
                "Question: {question}\n\n"
                "Provide 3 distinct possible first steps or architectural approaches "
                "to solve this problem. Label them 'Approach A:', 'Approach B:', and "
                "'Approach C:'. Keep each approach concise (1-2 sentences).",
            ),
        ]
    )


def build_evaluate_prompt() -> ChatPromptTemplate:
    """ToT Step 2: Evaluate the proposed approaches and select the best one."""
    return ChatPromptTemplate.from_messages(
        [
            ("system", "You are a critical, detail-oriented technical reviewer."),
            (
                "human",
                "Here are 3 possible architectural approaches to solve: {question}\n\n"
                "{branches}\n\n"
                "Analyze each approach for scalability and ease of implementation. "
                "Which one is the most robust? Respond ONLY with the label "
                "(e.g., 'Approach A') and a brief 1-sentence justification.",
            ),
        ]
    )


def build_final_prompt() -> ChatPromptTemplate:
    """ToT Step 3: Execute the chosen approach to completion."""
    return ChatPromptTemplate.from_messages(
        [
            ("system", "You are an expert system architect."),
            (
                "human",
                "Based on this winning strategy: {best_path}\n\n"
                "Flesh out the implementation details for the original question: {question}\n"
                "Provide a clear, actionable summary of the final architecture.",
            ),
        ]
    )


def get_tree_of_thought(question: str = SAMPLE_INPUT, mode: str = "after") -> str:
    """Run the Tree of Thought workflow against Groq."""
    if mode == "before":
        prompt = build_before_prompt()
        return run_prompt(prompt, {"question": question})

    # mode == "after": Execute ToT Workflow
    print("--- ToT Step 1: Proposing Branches ---")
    branches = run_prompt(
        build_propose_prompt(), {"question": question}, temperature=0.7
    )
    print(branches)

    print("\n--- ToT Step 2: Evaluating Branches ---")
    best_path_evaluation = run_prompt(
        build_evaluate_prompt(), {"question": question, "branches": branches}
    )
    print(best_path_evaluation)

    print("\n--- ToT Step 3: Final Execution ---")
    final_output = run_prompt(
        build_final_prompt(), {"question": question, "best_path": best_path_evaluation}
    )
    return final_output


if __name__ == "__main__":
    print("--- BEFORE (Single Pass) ---")
    print(get_tree_of_thought(mode="before"))
    print("\n\n--- AFTER (Tree of Thought) ---")
    print(get_tree_of_thought(mode="after"))
