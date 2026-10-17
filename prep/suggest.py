"""What should this student do next?

Pure functions over plain data, so they are easy to test. ``prep/services.py`` feeds them from the database.

The plan has three parts:

* **reviews**: problems whose spaced re-solve date has arrived (``scheduling.py``).
* **next problems**: new problems, one per pattern, chosen so the student *spreads out* instead of
  binge-solving one pattern: the least-covered patterns come first, a pattern the student just did
  several times in a row is rotated out, and difficulty rises with the number solved in that pattern.
* **pattern coverage**: for every pattern how many are solved against a target of ``TARGET``.
"""
from datetime import timedelta

from .scheduling import MASTERED, STAGE_LABELS

TARGET = 6          # problems of rising difficulty per pattern (5-8 is the usual advice)
BATCH = 5           # how many new problems to suggest at once
BINGE_WINDOW = 3    # look at the last few new solves...
BINGE_LIMIT = 2     # ...and rotate a pattern out if it made up this many of them
FAMILIAR_CREDIT = 2  # a pattern recognised in the placement quiz counts as this many solved

# Learning order: foundations first, then the rest. Patterns not listed come after, in catalog order.
CORE_ORDER = [
    "Hash Map", "Two Pointers", "Sliding Window", "Prefix Sum", "Modified Binary Search", "Monotonic Stack",
    "Overlapping Intervals", "Breadth First Search (BFS)", "Depth First Search (DFS)", "Trees", "Graphs",
    "Backtracking", "Greedy", "Dynamic Programming", "Top K Elements", "Design Data Structure",
]
ORDER = {name: i for i, name in enumerate(CORE_ORDER)}
DIFFICULTY = ["Basic", "Easy", "Medium", "Hard"]


def difficulty_preference(credit):
    """Difficulty ids (0 basic .. 3 hard) in the order we would like to pick them for a pattern with ``credit`` solved."""
    if credit < 2:
        return [1, 0, 2, 3]
    if credit == 2:
        return [1, 2, 0, 3]
    if credit == 3:
        return [2, 1, 3, 0]
    if credit < 6:
        return [2, 3, 1, 0]
    return [3, 2, 1, 0]


def is_familiar(diagnostic, pattern):
    d = (diagnostic or {}).get(pattern)
    return bool(d and d.get("asked") and d.get("right", 0) / d["asked"] >= 0.5)


def pattern_rows(cat, progress, diagnostic, today):
    """One row per pattern: solved / due / mastered counts and whether the placement quiz showed familiarity."""
    rows = []
    for name in cat["patterns"]:
        ids = cat["by_pattern"][name]
        solved = due = mastered = 0
        for i in ids:
            pr = progress.get(cat["problems"][i]["id"])
            if not pr:
                continue
            solved += bool(pr["solved"])
            mastered += pr["stage"] >= MASTERED
            due += bool(pr["next_review"] and pr["next_review"] <= today)
        rows.append({"name": name, "total": len(ids), "solved": solved, "due": due, "mastered": mastered,
                     "target": TARGET, "familiar": is_familiar(diagnostic, name)})
    return rows


def due_reviews(cat, progress, today):
    out = []
    for pid, pr in progress.items():
        nr = pr["next_review"]
        if nr and nr <= today and pid in cat["by_id"]:
            p = cat["problems"][cat["by_id"][pid]]
            out.append({"id": pid, "title": p["t"], "url": p["u"], "difficulty": p["d"],
                        "patterns": [cat["patterns"][x] for x in p["pa"]], "stage": pr["stage"],
                        "stage_label": STAGE_LABELS[pr["stage"]] if pr["stage"] == 0 else f"{STAGE_LABELS[pr['stage']]} due",
                        "overdue": (today - nr).days, "note": pr["note"], "attempts": pr["attempts"]})
    out.sort(key=lambda r: (-r["overdue"], r["stage"]))
    return out


def pick_problem(cat, pattern, progress, credit):
    """Best unsolved problem of ``pattern`` for a student with ``credit`` solved there, or None."""
    candidates = [i for i in cat["by_pattern"][pattern]
                  if not (progress.get(cat["problems"][i]["id"]) or {}).get("solved")
                  and cat["problems"][i]["pl"] in ("leetcode", "geeksforgeeks")]
    if not candidates:
        return None
    for want in difficulty_preference(credit):
        tier = [i for i in candidates if cat["problems"][i]["d"] == want]
        if tier:
            return max(tier, key=lambda i: cat["problems"][i]["pop"])
    return None


def next_problems(cat, progress, diagnostic, recent_patterns, level, rows):
    """Up to ``BATCH`` new problems, at most one per pattern. ``recent_patterns``: pattern-name lists of the latest first solves."""
    recent = recent_patterns[:BINGE_WINDOW]
    counts = {}
    for names in recent:
        for n in set(names):
            counts[n] = counts.get(n, 0) + 1
    blocked = {n for n, c in counts.items() if c >= BINGE_LIMIT}
    bump = 1 if level == "advanced" else 0

    def credit(r):
        return r["solved"] + (FAMILIAR_CREDIT if r["familiar"] else 0) + bump

    # Least-covered first; foundations before the rest; ties by curriculum order.
    ranked = sorted((r for r in rows if r["solved"] < TARGET and r["total"]),
                    key=lambda r: (min(credit(r), TARGET) / TARGET, ORDER.get(r["name"], 99)))
    out = []
    rotated = sorted(r["name"] for r in ranked if r["name"] in blocked)    # patterns skipped on purpose, to tell the student
    for r in ranked:
        if len(out) >= BATCH:
            break
        if r["name"] in blocked:
            continue
        i = pick_problem(cat, r["name"], progress, credit(r))
        if i is None:
            continue
        p = cat["problems"][i]
        if r["solved"] == 0 and not r["familiar"]:
            why = f"New pattern for you. Start with an {DIFFICULTY[p['d']].lower()} one."
        elif r["solved"] == 0:
            why = "You recognised this pattern in the placement quiz. A step up to confirm it."
        else:
            why = f"{r['solved']} of {TARGET} solved. The next step up in difficulty."
        out.append({"id": p["id"], "title": p["t"], "url": p["u"], "difficulty": p["d"], "platform": p["pl"],
                    "pattern": r["name"], "solved": r["solved"], "why": why})
    return out, rotated


def streak(days, today):
    """Consecutive days (ending today, or yesterday if nothing yet today) with at least one attempt."""
    have = set(days)
    day = today if today in have else today - timedelta(days=1)
    n = 0
    while day in have:
        n += 1
        day -= timedelta(days=1)
    return n


def build_plan(cat, progress, diagnostic, level, recent_patterns, attempt_days, today, week_solved=0, week_reviews=0):
    rows = pattern_rows(cat, progress, diagnostic, today)
    reviews = due_reviews(cat, progress, today)
    new, rotated = next_problems(cat, progress, diagnostic, recent_patterns, level, rows)
    upcoming = sum(1 for pr in progress.values() if pr["next_review"] and today < pr["next_review"] <= today + timedelta(days=7))
    return {
        "reviews": reviews, "next": new, "rotated": rotated, "patterns": rows,
        "stats": {"solved": sum(1 for pr in progress.values() if pr["solved"]), "mastered": sum(1 for pr in progress.values() if pr["stage"] >= MASTERED),
                  "due": len(reviews), "upcoming": upcoming, "streak": streak(attempt_days, today),
                  "week_solved": week_solved, "week_reviews": week_reviews},
    }
