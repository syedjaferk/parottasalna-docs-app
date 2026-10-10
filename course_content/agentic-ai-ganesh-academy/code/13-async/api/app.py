from dotenv import load_dotenv
from fastapi import FastAPI
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel

load_dotenv()

app = FastAPI()


@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    return f"It's sunny and 32°C in {city}"


@tool
def get_time(city: str) -> str:
    """Get the current time for a city (mocked)."""
    return f"It's 4:30 PM in {city}"


llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)
agent = create_react_agent(model=llm, tools=[get_weather, get_time])


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": req.message}]}
    )
    reply = response["messages"][-1].content
    return ChatResponse(reply=reply)
