# analyse.py - ONE quick Laya call that answers four questions about a customer message:
# what is it about, is it urgent, how upset is the person, and how hard is it to answer?
from laya import Router

router = Router(device="cpu")

QUESTIONS = {
    "category": {
        "type": "choice",
        "instructions": "Which kind of customer message is `message`?",
        "criteria": {
            "billing": "payments, charges, refunds, invoices or prices",
            "technical": "bugs, crashes, errors, slowness or things that do not work",
            "account": "login, password, email, profile or deleting an account",
            "other": "anything else: general questions, thanks, shipping, opening hours",
        },
    },
    "is_urgent": {"type": "noul", "instructions": "Does `message` say the problem is urgent or time-critical?"},
    "anger": {
        "type": "score",
        "instructions": "How upset is the writer of `message`?",
        "criteria": ["calm", "a little annoyed", "clearly annoyed", "very angry"],
    },
    "difficulty": {
        "type": "choice",
        "instructions": "How hard is `message` to answer well?",
        "criteria": {
            "easy": "a short, common question with a simple factual answer",
            "hard": "a complicated problem that needs careful reasoning, several steps or an apology and judgement",
        },
    },
}

MIN_CONFIDENCE = 0.60     # below this, we do not trust the category


def analyse(text):
    answers = router.predict({"message": text}, QUESTIONS)["answers"]
    category = answers["category"]
    label = category["choice"]
    confidence = category["probabilities"][label]
    difficulty = answers["difficulty"]
    hard = difficulty["choice"] == "hard"
    return {
        "category": label if confidence >= MIN_CONFIDENCE else "unsure",
        "category_confidence": round(confidence, 2),
        "urgent": round(answers["is_urgent"]["noul"], 2),
        "anger": round(answers["anger"]["score"], 2),
        "hard": hard,
        "difficulty_confidence": round(difficulty["probabilities"][difficulty["choice"]], 2),
    }


if __name__ == "__main__":
    for t in ["What are your opening hours?", "URGENT: I was charged twice and nobody is answering me!!!"]:
        print(t, "->", analyse(t))
