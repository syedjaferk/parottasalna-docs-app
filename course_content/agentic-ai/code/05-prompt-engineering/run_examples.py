"""
run_examples.py
----------------
CLI entry point. Runs BEFORE/AFTER comparisons for one or all prompt
engineering techniques against Groq (via the raw HTTP call_groq()).

Usage:
    python run_examples.py
    python run_examples.py --technique few_shot
    python run_examples.py --model llama-3.3-70b-versatile
"""

import argparse

import groq_client
from techniques import (
    zero_shot, few_shot, chain_of_thought, role_based, instruction_based,
    contextual_prompting, self_consistency, tree_of_thought, react
)


def print_section(title: str):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def run_zero_shot():
    print("\n--- BEFORE ---")
    print(zero_shot.get_zero_shot(mode="before"))
    print("\n--- AFTER ---")
    print(zero_shot.get_zero_shot(mode="after"))


def run_few_shot():
    print("\n--- BEFORE ---")
    print(few_shot.get_few_shot(mode="before"))
    print("\n--- AFTER ---")
    print(few_shot.get_few_shot(mode="after"))


def run_chain_of_thought():
    print("\n--- BEFORE ---")
    print(chain_of_thought.get_chain_of_thought(mode="before"))
    print("\n--- AFTER ---")
    result = chain_of_thought.get_chain_of_thought(mode="after")
    print(result)
    print("\nExtracted final answer:", chain_of_thought.extract_final_answer(result))


def run_role_based():
    print("\n--- BEFORE ---")
    print(role_based.get_role_based(mode="before"))
    print("\n--- AFTER ---")
    print(role_based.get_role_based(mode="after"))


def run_instruction_based():
    print("\n--- BEFORE (free text) ---")
    print(instruction_based.get_instruction_based_before())
    print("\n--- AFTER (structured, validated) ---")
    print(instruction_based.get_instruction_based_after().model_dump_json(indent=2))


def run_contextual_prompting():
    print("\n--- BEFORE ---")
    print(contextual_prompting.get_contextual_prompt(mode="before"))
    print("\n--- AFTER ---")
    print(contextual_prompting.get_contextual_prompt(mode="after"))


def run_self_consistency():
    print("\n--- BEFORE (Single Run) ---")
    print(self_consistency.get_self_consistency(mode="before"))
    print("\n--- AFTER (Majority Vote) ---")
    print(self_consistency.get_self_consistency(mode="after", num_samples=3))


def run_tree_of_thought():
    print("\n--- BEFORE (Single Pass) ---")
    print(tree_of_thought.get_tree_of_thought(mode="before"))
    print("\n--- AFTER (Tree of Thought) ---")
    print(tree_of_thought.get_tree_of_thought(mode="after"))


def run_react():
    print("\n--- BEFORE (No Tools) ---")
    print(react.get_react(mode="before"))
    print("\n--- AFTER (ReAct Loop) ---")
    print(react.get_react(mode="after"))


TECHNIQUE_RUNNERS = {
    "zero_shot": run_zero_shot,
    "few_shot": run_few_shot,
    "chain_of_thought": run_chain_of_thought,
    "role_based": run_role_based,
    "instruction_based": run_instruction_based,
    "contextual_prompting": run_contextual_prompting,
    "self_consistency": run_self_consistency,
    "tree_of_thought": run_tree_of_thought,
    "react": run_react,
}


def main():
    parser = argparse.ArgumentParser(description="Run prompt engineering demos against Groq.")
    parser.add_argument(
        "--technique",
        choices=list(TECHNIQUE_RUNNERS.keys()) + ["all"],
        default="all",
        help="Which technique to run (default: all)",
    )
    parser.add_argument(
        "--model",
        default=groq_client.DEFAULT_MODEL,
        help=f"Groq model id (default: {groq_client.DEFAULT_MODEL})",
    )
    args = parser.parse_args()

    # Let --model override the shared default used by groq_client.run_prompt()
    groq_client.DEFAULT_MODEL = args.model

    names = TECHNIQUE_RUNNERS.keys() if args.technique == "all" else [args.technique]
    for name in names:
        print_section(f"TECHNIQUE: {name}")
        TECHNIQUE_RUNNERS[name]()


if __name__ == "__main__":
    main()
