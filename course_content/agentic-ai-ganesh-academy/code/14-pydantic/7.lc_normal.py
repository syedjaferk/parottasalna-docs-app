from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)

response = llm.invoke(
    "Give me the name, rating out of 10, and one-line summary for the movie Interstellar. "
    "Format: Name | Rating | Summary"
)

text = response.content
print(text)
# "Interstellar | 9 | A team travels through a wormhole to save humanity."

# Now YOU have to parse this fragile string yourself:
parts = text.split("|")
name = parts[0].strip()
rating = int(parts[1].strip())  # crashes if the model adds "9/10" or "Rating: 9"
summary = parts[2].strip()
