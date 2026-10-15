---
name: study-buddy
description: Quiz the user on a topic they are learning, one question at a time, and keep score.
version: 1.0.0
metadata:
  hermes:
    tags: [learning, quiz]
    category: personal
---

# Study Buddy

## When to Use
Use this when the user says "quiz me on <topic>" or "test my knowledge of <topic>".

## Procedure
1. Ask which topic and how many questions (default 5), unless the user already said.
2. Ask **one** question at a time. Wait for the answer before continuing.
3. After each answer say whether it was right, give a one-sentence explanation, then ask the next question.
4. Keep a running score. After the last question, show the score and name one thing to revise.

## Pitfalls
- Do not reveal the answer before the user tries.
- Mix easy and medium questions. Never ask trick questions.
- If the user says "stop", show the score so far and finish.

## Verification
Each turn contains exactly one question, and the final message contains a score like "4/5".
