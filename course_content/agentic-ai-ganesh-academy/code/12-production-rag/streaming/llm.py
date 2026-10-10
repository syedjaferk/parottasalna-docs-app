import os
from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])


def stream_answer(question, context):
    prompt = f"""
Answer only from the context.

Context:
{context}

Question:
{question}
"""

    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        stream=True,
        messages=[{"role": "user", "content": prompt}],
    )

    for chunk in completion:
        if chunk.choices:
            delta = chunk.choices[0].delta.content

            if delta:
                yield delta
