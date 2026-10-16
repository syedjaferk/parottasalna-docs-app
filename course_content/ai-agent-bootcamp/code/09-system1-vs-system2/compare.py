# compare.py - System 2 (LLM) vs System 1 (Laya) on the same 12 messages
from classify_laya import laya_classify
from classify_llm import llm_classify
from messages import SAMPLES

laya_classify("warm up")                      # the first call loads the model; don't count it

print(f"{'message':<46} {'right':<10} {'LLM':<10} {'LLM s':>6} {'Laya':<10} {'Laya s':>7} {'conf':>5}")
print("-" * 100)

llm_right = laya_right = 0
llm_time = laya_time = 0.0

for text, right in SAMPLES:
    llm_label, t1 = llm_classify(text)
    laya_label, conf, t2 = laya_classify(text)
    llm_right += llm_label == right
    laya_right += laya_label == right
    llm_time += t1
    laya_time += t2
    print(f"{text[:44]:<46} {right:<10} {llm_label:<10} {t1:>6.2f} {laya_label:<10} {t2:>7.2f} {conf:>5.2f}")

n = len(SAMPLES)
print("-" * 100)
print(f"LLM  (System 2): {llm_right}/{n} correct, average {llm_time / n:.2f} s per message")
print(f"Laya (System 1): {laya_right}/{n} correct, average {laya_time / n:.2f} s per message")
