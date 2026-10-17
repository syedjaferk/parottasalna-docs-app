"""Database glue for the interview-prep app: progress JSON, attempt logging, the plan and the placement quiz."""
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .catalog import catalog, placement_questions
from .models import Attempt, PrepProfile, ProblemProgress
from .scheduling import apply_attempt, MASTERED
from .suggest import build_plan

LEVELS = ((16, "advanced"), (8, "intermediate"), (0, "beginner"))


def progress_json(user):
    """What the tracker needs per problem: s solved, b bookmarked, n note, st stage, nr next review, cf confidence, at attempts."""
    out = {}
    for r in ProblemProgress.objects.filter(user=user):
        if r.solved or r.bookmarked or r.note or r.attempts:
            out[r.problem_id] = {"s": r.solved, "b": r.bookmarked, "n": r.note, "st": r.stage,
                                 "nr": r.next_review.isoformat() if r.next_review else None, "cf": r.confidence, "at": r.attempts}
    return out


@transaction.atomic
def log_attempt(user, pid, outcome, confidence=None, minutes=None, note=None, now=None):
    """Record one try at a problem and move it through the spaced re-solve schedule."""
    now = now or timezone.now()
    today = timezone.localtime(now).date()
    row, _ = ProblemProgress.objects.select_for_update().get_or_create(user=user, problem_id=pid)
    was_solved = row.solved
    Attempt.objects.create(user=user, problem_id=pid, outcome=outcome, confidence=confidence, minutes=minutes, is_review=was_solved)
    row.stage, row.next_review = apply_attempt(row.stage, outcome, confidence, today)
    if outcome in ("cold", "hint") and not was_solved:
        row.solved, row.solved_at = True, now
    row.attempts += 1
    row.last_attempt_at = now
    row.confidence = confidence
    if note is not None:
        row.note = note
    row.save()
    return row


def reset_schedule(row):
    """Used when a student un-ticks a problem: forget the schedule but keep notes and bookmarks."""
    row.solved, row.solved_at, row.stage, row.next_review, row.attempts, row.confidence = False, None, 0, None, 0, None


def _progress_for_plan(user):
    return {r.problem_id: {"solved": r.solved, "stage": r.stage, "next_review": r.next_review, "note": r.note, "attempts": r.attempts}
            for r in ProblemProgress.objects.filter(user=user)}


def plan_for_user(user, now=None):
    now = now or timezone.now()
    today = timezone.localtime(now).date()
    cat = catalog()
    profile = PrepProfile.objects.filter(user=user).first()
    # Patterns of the most recent first-time solves (newest first), to stop a student binge-solving one pattern.
    firsts = ProblemProgress.objects.filter(user=user, solved=True, solved_at__isnull=False).order_by("-solved_at")[:5]
    recent = [[cat["patterns"][x] for x in cat["problems"][cat["by_id"][r.problem_id]]["pa"]] for r in firsts if r.problem_id in cat["by_id"]]
    week = now - timedelta(days=7)
    days = {timezone.localtime(t).date() for t in Attempt.objects.filter(user=user, created_at__gte=now - timedelta(days=60)).values_list("created_at", flat=True)}
    plan = build_plan(cat, _progress_for_plan(user), profile.diagnostic if profile else {}, profile.level if profile else "", recent, days, today,
                      week_solved=ProblemProgress.objects.filter(user=user, solved_at__gte=week).count(),
                      week_reviews=Attempt.objects.filter(user=user, created_at__gte=week, is_review=True).count())
    plan["placement"] = {"taken": bool(profile and profile.taken_at), "level": profile.level if profile else "",
                         "score": profile.score if profile else 0, "total": profile.total if profile else 0}
    return plan


# ---- placement quiz -------------------------------------------------------------------------------
def public_questions():
    """The quiz without the answers, for the browser."""
    return [{"id": q["id"], "q": q["q"], "options": q["options"]} for q in placement_questions()]


def grade_placement(answers):
    """``answers``: {question id: chosen option index, or -1/None for "I don't know yet"}.
    -> (results per question, per-pattern diagnostic, score, total, level)."""
    results, diag = [], {}
    for q in placement_questions():
        choice = answers.get(q["id"])
        ok = isinstance(choice, int) and not isinstance(choice, bool) and choice == q["answer"]
        d = diag.setdefault(q["pattern"], {"asked": 0, "right": 0})
        d["asked"] += 1
        d["right"] += ok
        results.append({"id": q["id"], "pattern": q["pattern"], "correct": ok, "answer": q["answer"], "chosen": choice if isinstance(choice, int) else -1,
                        "why": q["why"], "session": q["session"]})
    score, total = sum(r["correct"] for r in results), len(results)
    level = next(name for floor, name in LEVELS if score >= floor)
    return results, diag, score, total, level


def save_placement(user, diag, score, total, level):
    PrepProfile.objects.update_or_create(user=user, defaults={"diagnostic": diag, "score": score, "total": total, "level": level, "taken_at": timezone.now()})
