import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_groq import ChatGroq

load_dotenv()  # expects GROQ_API_KEY in .env

model = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
)

prompt = ChatPromptTemplate.from_template("Say hi to {name}")
parser = StrOutputParser()
chain = prompt | model | parser

for name, obj in [
    ("prompt", prompt),
    ("model", model),
    ("parser", parser),
    ("chain", chain),
]:
    print(
        f"{name:7} → is Runnable? {isinstance(obj, Runnable)}   type = {type(obj).__name__}"
    )

# Every one of them has the same buttons
print(prompt.invoke({"name": "Jafer"}))  # → ChatPromptValue (messages)
print(model.invoke("Say hi").content)  # → AIMessage
print(parser.invoke("plain text stays text"))  # → str
print(chain.invoke({"name": "Jafer"}))  # → str
