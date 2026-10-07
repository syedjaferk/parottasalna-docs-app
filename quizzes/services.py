from django.db.models import Count

from .models import Attempt, Quiz


def published_quizzes(course):
    return Quiz.objects.filter(course=course, is_published=True).annotate(
        question_count=Count("questions")
    ).filter(question_count__gt=0)


def selected_answers(post, questions):
    """Read submitted choice indexes per question from a POST body."""
    answers = {}
    for question in questions:
        count = len(question.parsed_choices())
        picked = set()
        for raw in post.getlist(f"q{question.pk}"):
            if raw.isdigit() and int(raw) < count:
                picked.add(int(raw))
        answers[str(question.pk)] = sorted(picked)
    return answers


def grade(questions, answers):
    """All-or-nothing per question. Returns (score, max_score)."""
    score = max_score = 0
    for question in questions:
        max_score += question.points
        if set(answers.get(str(question.pk), [])) == question.correct_indexes():
            score += question.points
    return score, max_score


def attempts_used(quiz, user):
    return Attempt.objects.filter(quiz=quiz, user=user).count()


def attempts_left(quiz, user):
    """None means unlimited."""
    if not quiz.max_attempts:
        return None
    return max(quiz.max_attempts - attempts_used(quiz, user), 0)


def best_scores(user, quizzes):
    """{quiz_id: best attempt} for this user."""
    best = {}
    for attempt in Attempt.objects.filter(user=user, quiz__in=quizzes).order_by("-score", "-submitted_at"):
        best.setdefault(attempt.quiz_id, attempt)
    return best
