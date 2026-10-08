from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

load_dotenv()


class MovieReview(BaseModel):
    name: str = Field(description="Movie title")
    rating: int = Field(ge=1, le=10, description="Rating out of 10")
    summary: str = Field(description="One-line summary")


llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)
structured_llm = llm.with_structured_output(MovieReview)

result = structured_llm.invoke("Give me details for the movie Interstellar")

print(result)  # MovieReview(name='Interstellar', rating=9, summary='...')
print(type(result))  # <class '__main__.MovieReview'>
print(result.rating)  # 9  — guaranteed to be an int between 1 and 10
print(result.name)
