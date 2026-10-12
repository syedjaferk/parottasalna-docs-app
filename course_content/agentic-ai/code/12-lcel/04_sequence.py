import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_groq import ChatGroq

load_dotenv()  # expects GROQ_API_KEY in .env

model = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
)

prompt = ChatPromptTemplate.from_template("Give a 2-line recipe summary for {dish}.")
parser = StrOutputParser()

# Way 1 — pipe operator (most common)
recipe_chain = prompt | model | parser

# Way 2 — explicit class (exactly the same)
recipe_chain_explicit = RunnableSequence(prompt, model, parser)

print(type(recipe_chain).__name__)  # RunnableSequence
print("Steps:", [type(s).__name__ for s in recipe_chain.steps])
print(recipe_chain.invoke({"dish": "Kothu Parotta"}))
print(recipe_chain_explicit.invoke({"dish": "Chicken Salna"}))

# Chain of chains — output of chain 1 becomes input of chain 2
translate_chain = (
    ChatPromptTemplate.from_template("Translate to simple Tamil:\n{text}")
    | model
    | parser
)

recipe_in_tamil = (
    recipe_chain
    | (lambda text: {"text": text})  # reshape str → dict for the next prompt
    | translate_chain
)
print(recipe_in_tamil.invoke({"dish": "Egg Parotta"}))

# Because it's a Runnable, batch works too
print(recipe_chain.batch([{"dish": "Idli"}, {"dish": "Pongal"}]))
