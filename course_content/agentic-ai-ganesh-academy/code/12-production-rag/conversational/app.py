# app.py

import os
import json
import redis

from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings



redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)



embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)



db = Chroma(
    persist_directory="chroma_db",
    embedding_function=embedding
)

retriever = db.as_retriever(
    search_kwargs={"k":4}
)


llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=os.environ["GROQ_API_KEY"]
)



SESSION_ID = "user_123"


def save_chat(question, answer):

    history = redis_client.get(SESSION_ID)

    if history:

        history = json.loads(history)

    else:

        history = []

    history.append({
        "user": question,
        "assistant": answer
    })

    redis_client.set(
        SESSION_ID,
        json.dumps(history)
    )



def get_history():

    history = redis_client.get(SESSION_ID)

    if history:

        return json.loads(history)

    return []



def format_history():

    history = get_history()

    output = ""

    for item in history[-5:]:

        output += f"User: {item['user']}\n"

        output += f"Assistant: {item['assistant']}\n"

    return output



prompt = PromptTemplate.from_template("""

You are a helpful assistant.

Conversation History

{history}

Relevant Documents

{context}

Current Question

{question}

Answer the question using the documents and conversation.

""")


while True:

    question = input("\nYou : ")

    if question.lower() == "exit":
        break

    docs = retriever.invoke(question)

    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )

    history = format_history()

    final_prompt = prompt.format(
        history=history,
        context=context,
        question=question
    )

    answer = llm.invoke(final_prompt).content

    print("\nAssistant :", answer)

    save_chat(question, answer)
