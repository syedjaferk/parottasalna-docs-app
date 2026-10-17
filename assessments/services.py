"""All the rules of a timed assessment live here, so views stay thin and the rules are easy to test.

The time limit is enforced on the SERVER: the deadline is stored when the attempt starts, and every
save or submit is checked against it. The countdown in the browser is only a display.
"""
import random
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from courses.services import can_track

from .models import Assessment, AssessmentAttempt

GRACE_SECONDS = 15        # network delay allowed after the deadline for the final auto-submit


class AssessmentError(Exception):
    """A problem a student can understand (shown as a message)."""


def can_open(user, assessment):
    if not user.is_authenticated:
        return False
    return assessment.course_id is None or can_track(user, assessment.course)


def visible_assessments(user):
    rows = Assessment.objects.filter(is_published=True).select_related("course")
    return [a for a in rows if a.questions.exists() and can_open(user, a)]


def clean_answers(raw, questions):
    """Keep only valid {question id: [choice indexes]} (anything else in the payload is dropped)."""
    cleaned = {}
    for question in questions:
        picked = raw.get(str(question.pk), []) if isinstance(raw, dict) else []
        count = len(question.parsed_choices())
        values = set()
        for item in picked if isinstance(picked, (list, tuple)) else []:
            if isinstance(item, int) and not isinstance(item, bool) and 0 <= item < count:
                values.add(item)
            elif isinstance(item, str) and item.isdigit() and int(item) < count:
                values.add(int(item))
        cleaned[str(question.pk)] = sorted(values)
    return cleaned


def answers_from_post(post, questions):
    return clean_answers({str(q.pk): post.getlist(f"q{q.pk}") for q in questions}, questions)


def grade(questions, answers):
    """All-or-nothing per question. Returns (score, max_score)."""
    score = max_score = 0
    for question in questions:
        max_score += question.points
        if set(answers.get(str(question.pk), [])) == question.correct_indexes():
            score += question.points
    return score, max_score


def attempts_used(assessment, user):
    return AssessmentAttempt.objects.filter(assessment=assessment, user=user).count()


def attempts_left(assessment, user):
    """None means unlimited."""
    if not assessment.max_attempts:
        return None
    return max(assessment.max_attempts - attempts_used(assessment, user), 0)


def remaining_seconds(attempt, now=None):
    now = now or timezone.now()
    return max(0, int((attempt.deadline - now).total_seconds()))


def is_past_deadline(attempt, now=None, grace=GRACE_SECONDS):
    now = now or timezone.now()
    return now > attempt.deadline + timedelta(seconds=grace)


def choice_sequence(attempt, question):
    """Original choice indexes in the order this student sees them. Answers are always stored by the ORIGINAL index,
    so shuffling the display never changes grading."""
    count = len(question.parsed_choices())
    saved = (attempt.choice_order or {}).get(str(question.pk))
    if isinstance(saved, list) and sorted(saved) == list(range(count)):
        return saved
    return list(range(count))


def ordered_questions(attempt):
    """The attempt's questions in the order this student was given."""
    by_id = {q.pk: q for q in attempt.assessment.questions.all()}
    ordered = [by_id[i] for i in attempt.question_order if i in by_id]
    ordered += [q for q in by_id.values() if q.pk not in set(attempt.question_order)]   # added after the attempt began
    return ordered


@transaction.atomic
def finalize(attempt_id, answers=None, timed_out=False, now=None):
    """Grade and close an attempt. Safe to call twice: a submitted attempt is never changed."""
    attempt = AssessmentAttempt.objects.select_for_update().select_related("assessment").get(pk=attempt_id)
    if attempt.submitted_at is not None:
        return attempt
    questions = list(attempt.assessment.questions.all())
    final = clean_answers(answers if answers is not None else attempt.answers, questions)
    attempt.answers = final
    attempt.score, attempt.max_score = grade(questions, final)
    attempt.submitted_at = min(now or timezone.now(), attempt.deadline) if timed_out else (now or timezone.now())
    attempt.timed_out = timed_out
    attempt.save()
    return attempt


def expire_stale(user=None, now=None):
    """Close attempts whose time ran out (and that nobody submitted), using the answers saved so far."""
    now = now or timezone.now()
    stale = AssessmentAttempt.objects.filter(submitted_at__isnull=True,
                                             deadline__lt=now - timedelta(seconds=GRACE_SECONDS))
    if user is not None:
        stale = stale.filter(user=user)
    count = 0
    for attempt_id in list(stale.values_list("pk", flat=True)):
        finalize(attempt_id, timed_out=True, now=now)
        count += 1
    return count


@transaction.atomic
def start_attempt(assessment, user, now=None):
    """Start (or resume) an attempt. Returns (attempt, resumed)."""
    now = now or timezone.now()
    Assessment.objects.select_for_update().filter(pk=assessment.pk).exists()      # serialise double clicks
    expire_stale(user, now)
    running = AssessmentAttempt.objects.filter(assessment=assessment, user=user, submitted_at__isnull=True).first()
    if running:
        return running, True
    status = assessment.window_status(now)
    if status == "upcoming":
        raise AssessmentError("This assessment has not opened yet.")
    if status == "closed":
        raise AssessmentError("This assessment is closed.")
    if attempts_left(assessment, user) == 0:
        raise AssessmentError("You have used all your attempts for this assessment.")
    questions = list(assessment.questions.all())
    if not questions:
        raise AssessmentError("This assessment has no questions yet.")
    ids = [q.pk for q in questions]
    if assessment.shuffle_questions:
        random.shuffle(ids)
    choice_order = {}
    if assessment.shuffle_choices:
        for q in questions:
            order = list(range(len(q.parsed_choices())))
            random.shuffle(order)
            choice_order[str(q.pk)] = order
    deadline = now + timedelta(minutes=assessment.time_limit_minutes)
    if assessment.closes_at:
        deadline = min(deadline, assessment.closes_at)
    attempt = AssessmentAttempt.objects.create(assessment=assessment, user=user, started_at=now,
                                               deadline=deadline, question_order=ids, choice_order=choice_order)
    return attempt, False


def save_answers(attempt, posted, now=None):
    """Autosave while the student works. Returns False when it's too late to accept answers."""
    if attempt.submitted_at is not None or is_past_deadline(attempt, now):
        return False
    questions = list(attempt.assessment.questions.all())
    attempt.answers = clean_answers(posted, questions)
    attempt.save(update_fields=["answers"])
    return True


def best_attempts(user, assessments):
    best = {}
    for a in AssessmentAttempt.objects.filter(user=user, assessment__in=assessments,
                                              submitted_at__isnull=False).order_by("-score", "-submitted_at"):
        best.setdefault(a.assessment_id, a)
    return best
