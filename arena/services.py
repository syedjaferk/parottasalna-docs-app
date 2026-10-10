"""Game rules for live quizzes. All functions are synchronous (database work); the WebSocket
consumers call them through database_sync_to_async and broadcast the resulting state.

Flow:  lobby → question → reveal → leaderboard → question → … → finished
Scoring (like Kahoot): a correct answer earns between 100 % (instant) and 50 % (last second) of the
question's points; wrong or missing answers earn nothing.
"""
import secrets

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import IntegrityError, transaction
from django.db.models import Count, F
from django.utils import timezone

from .models import MAX_PLAYERS, NICKNAME_MAX, LiveGame, LiveQuestion, Player, PlayerAnswer

GRACE_MS = 1000          # network delay allowance after the timer ends
LEADERBOARD_SIZE = 10


class GameError(Exception):
    """A rule was broken (wrong state, duplicate answer, bad input). The message is shown to the user."""


def game_group(pin):
    return f"arena_{pin}"


def host_group(pin):
    return f"arena_{pin}_host"


# ---------------------------------------------------------------- creating and joining

def new_pin():
    """A 6-digit PIN not used by any unfinished game."""
    for _ in range(50):
        pin = f"{secrets.randbelow(900000) + 100000}"
        if not LiveGame.objects.filter(pin=pin).exclude(status=LiveGame.Status.FINISHED).exists():
            return pin
    raise GameError("Couldn't find a free PIN, try again.")


def create_game(quiz, host):
    if not quiz.questions.exists():
        raise GameError("Add at least one question to this quiz first.")
    for _ in range(3):
        try:
            return LiveGame.objects.create(quiz=quiz, host=host, pin=new_pin())
        except IntegrityError:  # two hosts picked the same PIN at the same moment
            continue
    raise GameError("Couldn't create the game, try again.")


def active_game(pin):
    return (LiveGame.objects.select_related("quiz").filter(pin=pin)
            .exclude(status=LiveGame.Status.FINISHED).first())


def clean_nickname(raw):
    """Any printable text (Tamil names welcome), spaces collapsed, 1–NICKNAME_MAX characters.
    Nicknames are always shown with textContent / template escaping, never as HTML."""
    nickname = " ".join((raw or "").split())
    if not nickname or len(nickname) > NICKNAME_MAX or not nickname.isprintable():
        raise GameError(f"Pick a nickname of 1–{NICKNAME_MAX} characters.")
    return nickname


def join(game, raw_nickname):
    """Create a player. Returns (player, secret token); only the token's hash is stored."""
    nickname = clean_nickname(raw_nickname)
    if game.status == LiveGame.Status.FINISHED:
        raise GameError("This game has ended.")
    if game.players.count() >= MAX_PLAYERS:
        raise GameError("This game is full.")
    if game.players.filter(nickname__iexact=nickname).exists():
        raise GameError("That nickname is taken in this game. Try another.")
    token = secrets.token_urlsafe(24)
    try:
        player = Player.objects.create(game=game, nickname=nickname, token_hash=Player.hash_token(token))
    except IntegrityError:
        raise GameError("That nickname is taken in this game. Try another.")
    return player, token


def player_for(pin, player_id, token):
    if not (player_id and token):
        return None
    return (Player.objects.select_related("game", "game__quiz")
            .filter(pk=player_id, game__pin=pin, token_hash=Player.hash_token(token))
            .exclude(game__status=LiveGame.Status.FINISHED).first())


# ---------------------------------------------------------------- host actions

def _questions(game):
    return list(game.quiz.questions.all())


def current_question(game):
    questions = _questions(game)
    if 0 <= game.current_index < len(questions):
        return questions[game.current_index]
    return None


@transaction.atomic
def host_action(game_id, action):
    """Apply one host action and return the updated game. Raises GameError if not allowed now."""
    game = LiveGame.objects.select_for_update().select_related("quiz").get(pk=game_id)
    S = LiveGame.Status
    total = game.quiz.questions.count()
    if action in ("start", "next"):
        allowed = {S.LOBBY} if action == "start" else {S.REVEAL, S.LEADERBOARD}
        if game.status not in allowed:
            raise GameError("Can't go to the next question right now.")
        if game.current_index + 1 >= total:
            _finish(game)
        else:
            game.current_index += 1
            game.status = S.QUESTION
            game.question_started_at = timezone.now()
            game.save(update_fields=["current_index", "status", "question_started_at"])
    elif action == "reveal":
        if game.status != S.QUESTION:
            raise GameError("No question is open.")
        game.status = S.REVEAL
        game.save(update_fields=["status"])
    elif action == "leaderboard":
        if game.status != S.REVEAL:
            raise GameError("Reveal the answer first.")
        game.status = S.LEADERBOARD
        game.save(update_fields=["status"])
    elif action == "finish":
        _finish(game)
    else:
        raise GameError("Unknown action.")
    return game


def _finish(game):
    game.status = LiveGame.Status.FINISHED
    game.ended_at = timezone.now()
    game.save(update_fields=["status", "ended_at"])


def reveal_if_due(game_id, question_index):
    """Reveal automatically when the timer ran out (called by the host connection's timer)."""
    with transaction.atomic():
        game = LiveGame.objects.select_for_update().get(pk=game_id)
        if game.status != LiveGame.Status.QUESTION or game.current_index != question_index:
            return None
        game.status = LiveGame.Status.REVEAL
        game.save(update_fields=["status"])
    return game


# ---------------------------------------------------------------- answering

def score_for(question, elapsed_ms, correct):
    if not correct:
        return 0
    limit_ms = question.time_limit * 1000
    fraction = min(max(elapsed_ms, 0), limit_ms) / limit_ms
    return round(question.points * (1 - fraction / 2))


def submit_answer(player_id, choice):
    """Record one answer for the open question. Returns (answer, everyone_answered)."""
    with transaction.atomic():
        player = Player.objects.select_related("game").get(pk=player_id)
        game = LiveGame.objects.select_for_update().get(pk=player.game_id)
        if game.status != LiveGame.Status.QUESTION:
            raise GameError("Time's up for this question.")
        question = current_question(game)
        if not isinstance(choice, int) or not 0 <= choice < len(question.parsed_choices()):
            raise GameError("Invalid choice.")
        elapsed_ms = int((timezone.now() - game.question_started_at).total_seconds() * 1000)
        if elapsed_ms > question.time_limit * 1000 + GRACE_MS:
            raise GameError("Time's up for this question.")
        correct = choice in question.correct_indexes()
        points = score_for(question, elapsed_ms, correct)
        try:
            with transaction.atomic():
                answer = PlayerAnswer.objects.create(player=player, question=question, choice=choice,
                                                     correct=correct, points=points, elapsed_ms=elapsed_ms)
        except IntegrityError:
            raise GameError("You've already answered this question.")
        if points:
            Player.objects.filter(pk=player.pk).update(score=F("score") + points)
        answered = PlayerAnswer.objects.filter(question=question, player__game=game).count()
        everyone = answered >= game.players.count()
        if everyone:
            game.status = LiveGame.Status.REVEAL
            game.save(update_fields=["status"])
    return answer, everyone


# ---------------------------------------------------------------- state snapshots

def leaderboard(game, size=LEADERBOARD_SIZE):
    return [{"nickname": p.nickname, "score": p.score}
            for p in game.players.order_by("-score", "joined_at")[:size]]


def state(game):
    """What every screen needs; the same for all players (no personal data)."""
    S = LiveGame.Status
    questions = _questions(game)
    data = {
        "status": game.status,
        "pin": game.pin,
        "title": game.quiz.title,
        "description": game.quiz.description,
        "index": game.current_index,
        "total": len(questions),
        "players": game.players.count(),
    }
    question = questions[game.current_index] if 0 <= game.current_index < len(questions) else None
    if question and game.status != S.LOBBY:
        remaining = 0
        if game.status == S.QUESTION and game.question_started_at:
            spent = (timezone.now() - game.question_started_at).total_seconds() * 1000
            remaining = max(0, int(question.time_limit * 1000 - spent))
        data["question"] = {
            "text": question.text,
            "choices": [text for text, _ in question.parsed_choices()],
            "time_limit": question.time_limit,
            "remaining_ms": remaining,
            "points": question.points,
        }
        answers = PlayerAnswer.objects.filter(question=question, player__game=game)
        data["answered"] = answers.count()
        if game.status in (S.REVEAL, S.LEADERBOARD, S.FINISHED):
            counts = dict(answers.values_list("choice").annotate(n=Count("id")))
            data["reveal"] = {
                "correct": sorted(question.correct_indexes()),
                "counts": [counts.get(i, 0) for i in range(len(data["question"]["choices"]))],
            }
    if game.status in (S.LEADERBOARD, S.FINISHED):
        data["leaderboard"] = leaderboard(game)
    return data


def personal(player):
    """The player's own score, rank and result for the current question."""
    player.refresh_from_db(fields=["score"])
    game = player.game
    game.refresh_from_db()
    rank = game.players.filter(score__gt=player.score).count() + 1
    you = {"nickname": player.nickname, "score": player.score, "rank": rank}
    question = current_question(game)
    if question:
        answer = PlayerAnswer.objects.filter(player=player, question=question).first()
        you["answered"] = answer is not None
        if answer and game.status != LiveGame.Status.QUESTION:
            you["last"] = {"choice": answer.choice, "correct": answer.correct, "points": answer.points}
    return you


def host_extras(game):
    return {"nicknames": list(game.players.order_by("joined_at").values_list("nickname", flat=True)[:MAX_PLAYERS])}


# ---------------------------------------------------------------- broadcasting

def broadcast(game):
    """Send the new state to every player and host connection of this game."""
    layer = get_channel_layer()
    if layer is None:
        return
    async_to_sync(layer.group_send)(game_group(game.pin), {"type": "game.state", "state": state(game)})


def notify_host(game):
    """Lighter update for the host screen: who joined, how many answered."""
    layer = get_channel_layer()
    if layer is None:
        return
    question = current_question(game)
    answered = PlayerAnswer.objects.filter(question=question, player__game=game).count() if question else 0
    async_to_sync(layer.group_send)(host_group(game.pin), {
        "type": "game.counts", "players": game.players.count(), "answered": answered, **host_extras(game),
    })
