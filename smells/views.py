from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_safe

from courses.security import api_login_required, no_store

from .services import record_answer, smell_for


def _smell_json(smell):
    return {
        "slug": smell.slug, "number": smell.number, "title": smell.title, "level": smell.level,
        "tags": smell.tags, "summary": smell.summary, "problem": smell.problem, "why_bad": smell.why_bad,
        "bad_code": smell.bad_code, "good_code": smell.good_code, "language": smell.language,
        "fix": smell.fix, "source_url": smell.source_url,
        "quiz": {"question": smell.quiz.question, "choices": smell.quiz.choices},  # never the answer
    }


@require_safe
@api_login_required
def today_json(request):
    smell = smell_for()
    if smell is None:
        return no_store(JsonResponse({"smell": None}))
    return no_store(JsonResponse({"smell": _smell_json(smell)}))


@require_POST
@api_login_required
def answer(request):
    """Check the answer for today's smell. Only today's quiz can be answered."""
    smell = smell_for()
    if smell is None or request.POST.get("slug") != smell.slug:
        return JsonResponse({"error": "Not today's quiz"}, status=404)
    try:
        choice = int(request.POST.get("choice", ""))
    except ValueError:
        return JsonResponse({"error": "Invalid choice"}, status=400)
    if not 0 <= choice < len(smell.quiz.choices):
        return JsonResponse({"error": "Invalid choice"}, status=400)
    stored, already = record_answer(request.user, smell, choice)
    return no_store(JsonResponse({
        "correct": stored.is_correct, "your_choice": stored.choice, "answer": smell.quiz.answer,
        "explanation": smell.quiz.explanation, "already_answered": already,
    }))
