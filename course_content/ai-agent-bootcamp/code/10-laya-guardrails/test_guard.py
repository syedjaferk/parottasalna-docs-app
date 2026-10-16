# test_guard.py - MEASURE the guard. A guard you haven't tested is a guess.
from attacks import ANGRY, ATTACKS, NORMAL
from guard import check_message

check_message("warm up")


def run(title, wanted, messages):
    print(f"\n{title}  (we want: {wanted})")
    counts = {"allow": 0, "review": 0, "block": 0}
    for text in messages:
        r = check_message(text)
        counts[r["action"]] += 1
        print(f"  {r['action']:<7} {r['attack_score']:.2f}  {text[:70]}")
    return counts


attacks = run("ATTACKS", "block", ATTACKS)
normal = run("NORMAL messages", "allow", NORMAL)
angry = run("UPSET customers", "allow", ANGRY)

print("\n================ SUMMARY ================")
print(f"Attacks    : {attacks['block']}/{len(ATTACKS)} blocked, {attacks['review']} sent to review, {attacks['allow']} got through")
print(f"Normal     : {normal['block']}/{len(NORMAL)} wrongly blocked, {normal['review']} sent to review")
print(f"Upset      : {angry['block']}/{len(ANGRY)} wrongly blocked, {angry['review']} sent to review")
