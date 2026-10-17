"""Spaced re-solving: the rules that turn an attempt into the next review date.

A problem moves through stages:

    0  not solved on its own yet (retry tomorrow)
    1  solved once       -> re-solve from scratch after 1 day
    2  passed the 1-day  -> re-solve after 1 week
    3  passed the 1-week -> re-solve after 3-4 weeks (25 days)
    4  passed that too   -> mastered, no more reviews

Solving on your own with decent confidence moves a problem up one stage. Needing a hint, a low
confidence rating, or failing sends it back to the start of the queue, so it is retried tomorrow.
"""
from datetime import timedelta

INTERVAL_DAYS = {1: 1, 2: 7, 3: 25}
MASTERED = 4
LOW_CONFIDENCE = 2
STAGE_LABELS = {0: "Retry tomorrow", 1: "1-day re-solve", 2: "1-week re-solve", 3: "3-4 week re-solve", 4: "Mastered"}


def next_stage(stage, outcome, confidence=None):
    """Returns the new stage after an attempt with ``outcome`` in {"cold", "hint", "fail"}."""
    if outcome == "cold" and confidence is not None and confidence <= LOW_CONFIDENCE:
        outcome = "hint"                     # "I solved it but barely": treat it as not solid yet
    if outcome == "cold":
        return min(stage + 1, MASTERED)
    if outcome == "hint":
        return 1
    return 0


def review_date(stage, today):
    """When a problem at ``stage`` should next be re-solved (None when mastered)."""
    if stage >= MASTERED:
        return None
    return today + timedelta(days=INTERVAL_DAYS.get(stage, 1))


def apply_attempt(stage, outcome, confidence, today):
    """-> (new_stage, next_review_date or None)."""
    new = next_stage(stage, outcome, confidence)
    return new, review_date(new, today)
