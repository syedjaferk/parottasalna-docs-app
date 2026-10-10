import asyncio

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
)


async def main():
    response = await llm.ainvoke("What is LangChain in one sentence?")
    print(response.content)


asyncio.run(main())
