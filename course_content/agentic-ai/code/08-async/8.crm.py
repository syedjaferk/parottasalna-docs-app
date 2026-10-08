import asyncio

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent

load_dotenv()


@tool
def get_weather(city: str) -> str:
    """Get the weather for a city."""
    return f"It's sunny and 32°C in {city}"


llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)

agent = create_react_agent(model=llm, tools=[get_weather])


# async def main():
#     response = await agent.ainvoke(
#         {"messages": [{"role": "user", "content": "What's the weather in Coimbatore?"}]}
#     )
#     print(response["messages"][-1].content)


# async def main():
#     async for chunk in agent.astream(
#         {
#             "messages": [
#                 {"role": "user", "content": "Explain async in Python simply in detail "}
#             ]
#         }
#     ):
#         print(chunk)
#         print("#" * 30)


async def main():
    results = await asyncio.gather(
        agent.ainvoke(
            {"messages": [{"role": "user", "content": "Weather in Chennai?"}]}
        ),
        agent.ainvoke(
            {"messages": [{"role": "user", "content": "Weather in Bangalore?"}]}
        ),
        agent.ainvoke(
            {"messages": [{"role": "user", "content": "Weather in Mumbai?"}]}
        ),
    )
    for r in results:
        print(r["messages"][-1].content)


asyncio.run(main())
