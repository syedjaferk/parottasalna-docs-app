import datetime

from django.db.models import Count, Q
from django.utils import timezone

from .models import CodeSmell, SmellAnswer

EPOCH = datetime.date(2026, 1, 1)


def smell_for(day=None):
    """The smell of the day: the active, quiz-bearing smells take turns, one per local (IST) day."""
    day = day or timezone.localdate()
    smells = list(CodeSmell.objects.filter(is_active=True, quiz__isnull=False).select_related("quiz"))
    if not smells:
        return None
    return smells[(day - EPOCH).days % len(smells)]


def daily_context(user, day=None):
    smell = smell_for(day)
    if smell is None:
        return None
    previous = SmellAnswer.objects.filter(user=user, smell=smell).first()
    stats = SmellAnswer.objects.filter(user=user).aggregate(total=Count("id"), correct=Count("id", filter=Q(is_correct=True)))
    return {"smell": smell, "quiz": smell.quiz, "previous": previous, "stats": stats}


def record_answer(user, smell, choice):
    """Store the first answer; return (answer, already_answered)."""
    answer, created = SmellAnswer.objects.get_or_create(
        user=user, smell=smell, defaults={"choice": choice, "is_correct": choice == smell.quiz.answer})
    return answer, not created
