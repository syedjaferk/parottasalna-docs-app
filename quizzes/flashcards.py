"""Flashcard study page and the API that records "Got it" / "Again"."""
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_POST, require_safe

from courses.security import api_login_required, no_store
from courses.services import can_track
from courses.models import Course

from .models import CardReview, Deck
from .templatetags.quiz_extras import markdown
from .views import _course_for


def _deck_for(request, course, pk):
    decks = course.decks.all() if request.user.is_staff else course.decks.filter(is_published=True)
    return get_object_or_404(decks, pk=pk)   # staff can preview drafts


@login_required
@require_safe
def deck_study(request, slug, pk):
    course = _course_for(request, slug)      # enrolled students and staff only
    deck = _deck_for(request, course, pk)
    cards = list(deck.cards.all())
    known = set(
        CardReview.objects.filter(user=request.user, card__in=cards, known=True).values_list("card_id", flat=True)
    )
    data = {
        "reviewUrl": reverse("deck_review", args=[course.slug, deck.pk]),
        "cards": [
            {"id": c.pk, "front": str(markdown(c.front)), "back": str(markdown(c.back)), "known": c.pk in known}
            for c in cards
        ],
    }
    return render(request, "quizzes/deck_study.html", {"course": course, "deck": deck, "data": data})


@require_POST
@api_login_required
def deck_review(request, slug, pk):
    """Save one card's result. Checks: CSRF, signed in, enrolled, card belongs to this deck."""
    course = Course.objects.filter(slug=slug, is_active=True).first()
    if course is None or not can_track(request.user, course):
        return JsonResponse({"error": "Not found"}, status=404)
    deck = Deck.objects.filter(pk=pk, course=course)
    if not request.user.is_staff:
        deck = deck.filter(is_published=True)
    deck = deck.first()
    if deck is None:
        return JsonResponse({"error": "Not found"}, status=404)

    card_id, known = request.POST.get("card", ""), request.POST.get("known")
    if not card_id.isdigit() or known not in ("true", "false"):
        return JsonResponse({"error": "Invalid card or known value"}, status=400)
    card = deck.cards.filter(pk=int(card_id)).first()
    if card is None:
        return JsonResponse({"error": "Card is not in this deck"}, status=400)

    review, _ = CardReview.objects.get_or_create(user=request.user, card=card)
    CardReview.objects.filter(pk=review.pk).update(known=known == "true", times_seen=F("times_seen") + 1)
    known_total = CardReview.objects.filter(user=request.user, card__deck=deck, known=True).count()
    return no_store(JsonResponse({"card": card.pk, "known": known == "true",
                                  "known_total": known_total, "total": deck.cards.count()}))
