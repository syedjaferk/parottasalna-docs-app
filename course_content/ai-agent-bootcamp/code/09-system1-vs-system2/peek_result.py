# peek_result.py - look INSIDE a Laya answer: three kinds of questions, one quick call.
import json

from laya import Router

router = Router(device="cpu")

state = {"message": "URGENT: my payment failed and I was charged twice! Fix this now or I will cancel."}

questions = {
    # choice: pick ONE label
    "category": {"type": "choice", "instructions": "Which kind of customer message is `message`?",
                 "criteria": {"billing": "payments, charges, refunds", "technical": "bugs and crashes",
                              "account": "login or profile", "other": "anything else"}},
    # noul: a yes/no question answered as a probability from 0.0 to 1.0
    "is_urgent": {"type": "noul", "instructions": "Does `message` say the problem is urgent?"},
    # score: a number on a scale, with a meaning for each step
    "anger": {"type": "score", "instructions": "How angry is the writer of `message`?",
              "criteria": ["calm", "a little annoyed", "clearly annoyed", "very angry"]},
}

result = router.predict(state, questions)

answers = result["answers"]
print("category  :", answers["category"]["choice"], f"(sure: {answers['category']['probabilities'][answers['category']['choice']]:.2f})")
print("is_urgent :", round(answers["is_urgent"]["noul"], 2), "  <- probability of 'yes'")
print("anger     :", round(answers["anger"]["score"], 2), "  <- 0 = calm ... 3 = very angry")
print("tokens    :", result["usage"])

print("\nThe full raw answer for 'category' looks like this:")
print(json.dumps(answers["category"], indent=2)[:700])
