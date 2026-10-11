"""Poll rules and live updates. Votes arrive over plain HTTP POST (CSRF-protected, works without JavaScript);
every change is pushed to the poll's WebSocket group so the teacher's screen and voters' phones update live."""
import secrets

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import IntegrityError, transaction
from django.db.models import Count
from django.utils import timezone

from .models import CODE_ALPHABET, CODE_LENGTH, Poll, Vote


class PollError(Exception):
    """A rule was broken (poll closed, bad choice). The message is shown to the user."""


def group_name(code):
    return f"poll_{code}"


def new_code():
    for _ in range(50):
        code = "".join(secrets.choice(CODE_ALPHABET) for _ in range(CODE_LENGTH))
        if not Poll.objects.filter(code=code).exists():
            return code
    raise PollError("Couldn't find a free poll code, try again.")


def create_poll(question, options_text, user, show_results=True):
    """Validate and create a poll. Raises django ValidationError for bad input."""
    poll = Poll(question=question.strip(), options=options_text, created_by=user, show_results=show_results)
    poll.full_clean(exclude=["code"])
    poll.options = "\n".join(poll.option_list())   # store the cleaned lines
    for _ in range(3):
        poll.code = new_code()
        try:
            with transaction.atomic():
                poll.save()
            return poll
        except IntegrityError:   # two polls picked the same code at the same moment
            continue
    raise PollError("Couldn't create the poll, try again.")


def counts(poll):
    by_choice = dict(poll.votes.values_list("choice").annotate(n=Count("id")))
    return [by_choice.get(i, 0) for i in range(len(poll.option_list()))]


def state(poll):
    """Everything a screen needs, without anything about individual voters."""
    c = counts(poll)
    return {
        "code": poll.code,
        "question": poll.question,
        "options": poll.option_list(),
        "counts": c,
        "total": sum(c),
        "is_open": poll.is_open,
        "show_results": poll.show_results,
    }


def my_choice(poll, token):
    if not token:
        return None
    vote = poll.votes.filter(voter_hash=Vote.hash_voter(token, poll.code)).first()
    return vote.choice if vote else None


def cast(poll, token, choice):
    """Record (or change) this browser's vote. Returns the chosen index."""
    if not poll.is_open:
        raise PollError("Voting is closed for this poll.")
    try:
        choice = int(choice)
    except (TypeError, ValueError):
        raise PollError("Pick one of the options.")
    if not 0 <= choice < len(poll.option_list()):
        raise PollError("Pick one of the options.")
    Vote.objects.update_or_create(poll=poll, voter_hash=Vote.hash_voter(token, poll.code),
                                  defaults={"choice": choice})
    return choice


def set_open(poll, is_open):
    poll.is_open = is_open
    poll.closed_at = None if is_open else timezone.now()
    poll.save(update_fields=["is_open", "closed_at"])


def reset(poll):
    poll.votes.all().delete()


def broadcast(poll):
    layer = get_channel_layer()
    if layer is None:
        return
    async_to_sync(layer.group_send)(group_name(poll.code), {"type": "poll.update", "state": state(poll)})
