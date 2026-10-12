import os
import time

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel
from langchain_groq import ChatGroq

load_dotenv()  # expects GROQ_API_KEY in .env

model = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
)

parser = StrOutputParser()
p = ChatPromptTemplate.from_template

pros = p("List 3 pros of {topic}. Short bullets only.") | model | parser
cons = p("List 3 cons of {topic}. Short bullets only.") | model | parser
verdict = p("One-line verdict: should a beginner learn {topic}?") | model | parser

# Way 1 — explicit class
review = RunnableParallel(pros=pros, cons=cons, verdict=verdict)

t = time.time()
out = review.invoke({"topic": "Kubernetes"})
print(f"Parallel took {time.time() - t:.1f}s")
for key, value in out.items():
    print(f"\n== {key} ==\n{value}")

# Sequential, for comparison
t = time.time()
for c in (pros, cons, verdict):
    c.invoke({"topic": "Kubernetes"})
print(f"\nSequential took {time.time() - t:.1f}s")

# Way 2 — a plain dict inside a chain is auto-converted to RunnableParallel
summary_chain = (
    {"pros": pros, "cons": cons, "verdict": verdict}
    | p("Write a 4-line summary.\nPros:{pros}\nCons:{cons}\nVerdict:{verdict}")
    | model
    | parser
)
print("\n== summary ==\n", summary_chain.invoke({"topic": "Kubernetes"}))
