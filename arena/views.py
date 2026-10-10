import csv

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST, require_safe

from courses.security import csv_safe, no_store

from . import services
from .consumers import COOKIE, make_player_cookie, read_player_cookie
from .models import LiveGame, LiveQuiz


def _current_player(request, pin):
    player_id, token = read_player_cookie(request.COOKIES.get(COOKIE))
    return services.player_for(pin, player_id, token)


@require_http_methods(["GET", "POST"])
def join(request):
    """Step 1: enter the game PIN."""
    error = None
    pin = "".join(ch for ch in request.POST.get("pin", "") if ch.isdigit())[:6]
    if request.method == "POST":
        if len(pin) == 6 and services.active_game(pin):
            return redirect("arena_nickname", pin=pin)
        error = "We couldn't find a game with that PIN. Check the number on the host's screen."
    return no_store(render(request, "arena/join.html", {"error": error, "pin": pin}))


@require_http_methods(["GET", "POST"])
def nickname(request, pin):
    """Step 2: choose a nickname. Sets a signed, HTTP-only cookie that identifies the player."""
    game = services.active_game(pin)
    if game is None:
        messages.info(request, "That game has ended or doesn't exist.")
        return redirect("arena_join")
    if _current_player(request, pin):
        return redirect("arena_play", pin=pin)
    error = None
    if request.method == "POST":
        try:
            player, token = services.join(game, request.POST.get("nickname", ""))
        except services.GameError as exc:
            error = str(exc)
        else:
            services.notify_host(game)
            response = redirect("arena_play", pin=pin)
            response.set_cookie(COOKIE, make_player_cookie(player.pk, token), max_age=12 * 3600,
                                httponly=True, samesite="Lax", secure=not settings.DEBUG)
            return response
    return no_store(render(request, "arena/nickname.html", {"game": game, "error": error,
                                                            "value": request.POST.get("nickname", "")}))


@require_safe
def play(request, pin):
    """Step 3: the player's screen (updates over a WebSocket)."""
    player = _current_player(request, pin)
    if player is None:
        return redirect("arena_nickname", pin=pin)
    return no_store(render(request, "arena/play.html", {"game": player.game, "player": player}))


# ---------------------------------------------------------------- host (staff)

@staff_member_required
@require_safe
def host_home(request):
    quizzes = LiveQuiz.objects.prefetch_related("questions")
    games = LiveGame.objects.select_related("quiz").filter(host=request.user)[:10]
    return render(request, "arena/host_home.html", {"quizzes": quizzes, "games": games})


@staff_member_required
@require_POST
def host_start(request, quiz_id):
    quiz = get_object_or_404(LiveQuiz, pk=quiz_id)
    try:
        game = services.create_game(quiz, request.user)
    except services.GameError as exc:
        messages.error(request, str(exc))
        return redirect("arena_host_home")
    return redirect("arena_host", pin=game.pin)


@staff_member_required
@require_safe
def host(request, pin):
    game = services.active_game(pin)
    if game is None or not (game.host_id == request.user.pk or request.user.is_superuser):
        raise Http404
    join_url = request.build_absolute_uri("/join")
    return no_store(render(request, "arena/host.html", {"game": game, "join_url": join_url}))


@staff_member_required
@require_safe
def results_csv(request, game_id):
    game = get_object_or_404(LiveGame.objects.select_related("quiz"), pk=game_id)
    if not (game.host_id == request.user.pk or request.user.is_superuser):
        raise Http404
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="live-quiz-{game.pin}-results.csv"'
    writer = csv.writer(response)
    questions = list(game.quiz.questions.all())
    writer.writerow(["Rank", "Nickname", "Score"] + [f"Q{i + 1} points" for i in range(len(questions))])
    for rank, player in enumerate(game.players.prefetch_related("answers"), start=1):
        points = {a.question_id: a.points for a in player.answers.all()}
        writer.writerow([rank, csv_safe(player.nickname), player.score] + [points.get(q.pk, "") for q in questions])
    return no_store(response)
