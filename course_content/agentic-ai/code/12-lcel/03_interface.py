import asyncio
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()  # expects GROQ_API_KEY in .env

model = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
)

# 1) invoke — one input, one output (an AIMessage)
msg = model.invoke("What is a parotta? Answer in one line.")
print("invoke  :", msg.content)
print("tokens  :", msg.usage_metadata)  # input/output token counts
print("thinking:", msg.additional_kwargs.get("reasoning_content", "")[:150], "...")

# 2) batch — many inputs, run concurrently
answers = model.batch(
    [
        "Capital of Tamil Nadu? One word.",
        "Capital of Karnataka? One word.",
        "Capital of Kerala? One word.",
    ],
    config={"max_concurrency": 3},
)
print("batch   :", [a.content for a in answers])

# 3) stream — tokens arrive as they're generated
print("stream  : ", end="")
for chunk in model.stream("Count from 1 to 10 in words, comma separated."):
    print(chunk.content, end="", flush=True)
print()


# 4) async versions
async def main():
    m = await model.ainvoke("Say 'vanakkam' and its meaning in one line.")
    print("ainvoke :", m.content)

    rs = await model.abatch(["2+2? Number only.", "3+3? Number only."])
    print("abatch  :", [r.content for r in rs])

    print("astream : ", end="")
    async for chunk in model.astream(
        "Name 3 South Indian breakfasts, comma separated."
    ):
        print(chunk.content, end="", flush=True)
    print()


asyncio.run(main())
