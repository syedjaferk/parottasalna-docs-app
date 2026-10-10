from fastapi import FastAPI
from sse_starlette.sse import EventSourceResponse

from rag import retrieve
from llm import stream_answer

app = FastAPI()


@app.get("/chat")
async def chat(question: str):

    async def event_generator():

        context = retrieve(question)

        for token in stream_answer(question, context):

            yield {
                "event": "token",
                "data": token
            }

        yield {
            "event": "done",
            "data": "END"
        }

    return EventSourceResponse(event_generator())
