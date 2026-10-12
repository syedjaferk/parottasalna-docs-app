"""
Level 1 — Approval gate inside an LCEL chain
--------------------------------------------
Head chef analogy: the cook prepares the dish (LLM writes a reply),
the head chef TASTES it (input()), and only then is it SERVED (sent).

    complaint ─► [prompt] ─► [model] ─► [parser] ─► taste (input) ─► serve

Good for: notebooks, CLI scripts, learning.
Not for:  web apps (input() blocks, nothing survives a restart).
"""

import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_groq import ChatGroq

load_dotenv()  # expects GROQ_API_KEY in .env

model = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
)


class RejectedByChef(Exception):
    pass


# 1) The cook — LLM drafts a reply
cook = (
    ChatPromptTemplate.from_template(
        "You work at Parottasalna restaurant. Write a polite 3-line reply "
        "to this customer complaint:\n{complaint}"
    )
    | model
    | StrOutputParser()
)


# 2) The head chef — a human tastes before serving
def head_chef_tastes(dish: str) -> str:
    print("\n🍽️  DISH READY FOR TASTING")
    print("-" * 50)
    print(dish)
    print("-" * 50)
    choice = input("👨‍🍳 [a]pprove  [e]dit  [r]eject : ").strip().lower()

    if choice == "a":
        return dish
    if choice == "e":
        return input("✏️  Type the corrected reply:\n> ")
    raise RejectedByChef("Head chef rejected the dish — nothing served.")


# 3) Serve — only reached if the chef approved/edited
def serve(dish: str) -> str:
    print("\n📧 SERVED (email sent):\n" + dish)  # replace with a real email API
    return "served"


# The whole kitchen as ONE LCEL chain
kitchen = cook | RunnableLambda(head_chef_tastes) | RunnableLambda(serve)

if __name__ == "__main__":
    try:
        kitchen.invoke(
            {"complaint": "My parotta order came cold after 1 hour of waiting!"}
        )
    except RejectedByChef as e:
        print("\n❌", e)
