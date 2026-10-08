from django.db.models import Count

from .models import Attempt, CardReview, Deck, Quiz


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


def published_decks(course):
    return Deck.objects.filter(course=course, is_published=True).annotate(
        card_count=Count("cards")
    ).filter(card_count__gt=0)


def known_counts(user, decks):
    """{deck_id: number of cards this user marked "Got it"}."""
    if not user.is_authenticated:
        return {}
    rows = (
        CardReview.objects.filter(user=user, known=True, card__deck__in=decks)
        .values("card__deck").annotate(n=Count("id"))
    )
    return {row["card__deck"]: row["n"] for row in rows}


def parse_bulk_cards(text: str):
    """'front :: back' per line → [(front, back)]; returns (cards, bad_line_numbers)."""
    cards, bad = [], []
    for number, line in enumerate((text or "").splitlines(), start=1):
        if not line.strip():
            continue
        front, sep, back = line.partition("::")
        if not sep or not front.strip() or not back.strip():
            bad.append(number)
            continue
        cards.append((front.strip(), back.strip()))
    return cards, bad
