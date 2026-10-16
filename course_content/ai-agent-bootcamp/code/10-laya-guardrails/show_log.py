# show_log.py - read decisions.jsonl and print a summary. Logs are how you find out what your bot really did.
import json
from collections import Counter

rows = [json.loads(line) for line in open("decisions.jsonl", encoding="utf-8")]
print(f"{len(rows)} decisions logged\n")
print("Routes:", dict(Counter(r.get("route") for r in rows)))
print("Guard :", dict(Counter(r.get("guard") for r in rows)))
print("\nLast 5:")
for r in rows[-5:]:
    print(f"  {r['time']}  {str(r.get('route')):<13} guard={str(r.get('guard')):<6} {r['text'][:50]}")
