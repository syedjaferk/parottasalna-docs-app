import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_groq import ChatGroq

load_dotenv()  # expects GROQ_API_KEY in .env

model = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
)

parser = StrOutputParser()

# A pretend knowledge base + retriever
docs = {
    "timing": "Parottasalna is open 7 AM to 11 PM daily.",
    "location": "Parottasalna is near Anna Nagar bus depot, Chennai.",
}


def retrieve(question: str) -> str:
    return docs["timing"] if "open" in question.lower() else docs["location"]


rag_prompt = ChatPromptTemplate.from_template(
    "Answer only from the context.\nContext: {context}\nQuestion: {question}"
)

# (a) RunnablePassthrough() — input goes forward unchanged
rag_chain = (
    {"context": retrieve, "question": RunnablePassthrough()}
    | rag_prompt
    | model
    | parser
)
print("(a)", rag_chain.invoke("What time do you open?"))

# (b) .assign() — keep existing keys, add new ones
step_by_step = RunnablePassthrough.assign(
    context=lambda x: retrieve(x["question"])
) | RunnablePassthrough.assign(answer=rag_prompt | model | parser)
result = step_by_step.invoke({"question": "Where are you located?"})
print("(b) keys:", list(result.keys()))  # ['question', 'context', 'answer']
print("(b) answer:", result["answer"])

# (c) .pick() — keep only the key(s) you want
only_answer = step_by_step.pick("answer")
print("(c)", only_answer.invoke({"question": "What time do you open?"}))

answer_and_context = step_by_step.pick(["answer", "context"])
print("(c)", answer_and_context.invoke({"question": "Where are you?"}))

# (d) .assign() on a RunnableParallel
both = RunnableParallel(question=RunnablePassthrough()).assign(
    context=lambda x: retrieve(x["question"])
)
print("(d)", both.invoke("Are you open on Sunday?"))
