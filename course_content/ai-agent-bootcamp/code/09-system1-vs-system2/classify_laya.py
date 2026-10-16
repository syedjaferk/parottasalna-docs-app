# classify_laya.py - System 1: a small, fast classifier that answers in one quick step.
import time

from laya import Router

from messages import CATEGORIES

router = Router(device="cpu")

# One question of type "choice": the model picks exactly one label, and also tells us how sure it is.
# Tip from the Laya authors: use meaningful labels (not yes/no or true/false) in choice questions.
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
    }
}


def laya_classify(text):
    """Return (label, confidence 0-1, seconds_taken)."""
    start = time.time()
    result = router.predict({"message": text}, QUESTIONS)
    answer = result["answers"]["category"]
    label = answer["choice"]
    confidence = answer["probabilities"][label]
    return (label if label in CATEGORIES else "other"), confidence, time.time() - start


if __name__ == "__main__":
    print(laya_classify("I was charged twice for my order"))
