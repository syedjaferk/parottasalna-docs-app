"""WebSocket endpoints for live quizzes.

/ws/arena/<pin>/play/  a player's phone. Identified by the signed `arena_player` cookie set when
                       joining (no login). Sends {"action": "answer", "choice": n}.
/ws/arena/<pin>/host/  the host's big screen. Staff only (session login). Sends
                       {"action": "start" | "next" | "reveal" | "leaderboard" | "finish"}.

Every state change is broadcast to the game's group; each player connection adds its own score/rank.
"""
import asyncio
import time

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.core import signing

from . import services
from .models import LiveGame

COOKIE = "arena_player"
COOKIE_SALT = "arena.player"
MAX_MESSAGES_PER_SECOND = 5


def read_player_cookie(raw):
    """'<player_id>:<token>' signed with SECRET_KEY → (player_id, token) or (None, None)."""
    try:
        value = signing.loads(raw, salt=COOKIE_SALT, max_age=12 * 3600)
        player_id, token = value.split(":", 1)
        return int(player_id), token
    except (signing.BadSignature, ValueError, AttributeError, TypeError):
        return None, None


def make_player_cookie(player_id, token):
    return signing.dumps(f"{player_id}:{token}", salt=COOKIE_SALT)


class _Throttled(AsyncJsonWebsocketConsumer):
    """Drop clients that flood the socket."""

    async def receive_json(self, content, **kwargs):
        now = time.monotonic()
        window = [t for t in getattr(self, "_recent", []) if now - t < 1]
        window.append(now)
        self._recent = window
        if len(window) > MAX_MESSAGES_PER_SECOND:
            await self.close(code=4029)
            return
        if not isinstance(content, dict):
            return
        await self.handle(content)


class PlayerConsumer(_Throttled):
    async def connect(self):
        self.pin = self.scope["url_route"]["kwargs"]["pin"]
        player_id, token = read_player_cookie(self.scope.get("cookies", {}).get(COOKIE))
        self.player = await database_sync_to_async(services.player_for)(self.pin, player_id, token)
        if self.player is None:
            await self.close(code=4403)
            return
        self.group = services.game_group(self.pin)
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()
        await self.send_state(await database_sync_to_async(self._state)())

    async def disconnect(self, code):
        if getattr(self, "group", None):
            await self.channel_layer.group_discard(self.group, self.channel_name)

    def _state(self):
        self.player.game.refresh_from_db()
        return services.state(self.player.game)

    async def send_state(self, state):
        you = await database_sync_to_async(services.personal)(self.player)
        await self.send_json({"type": "state", "state": state, "you": you})

    async def handle(self, content):
        if content.get("action") != "answer":
            return
        try:
            _, everyone = await database_sync_to_async(services.submit_answer)(self.player.pk, content.get("choice"))
        except services.GameError as exc:
            await self.send_json({"type": "error", "message": str(exc)})
            return
        await self.send_json({"type": "answered", "choice": content.get("choice")})
        game = await database_sync_to_async(lambda: LiveGame.objects.get(pk=self.player.game_id))()
        await database_sync_to_async(services.notify_host)(game)
        if everyone:  # the last player answered: reveal now instead of waiting for the timer
            await database_sync_to_async(services.broadcast)(game)

    async def game_state(self, event):
        await self.send_state(event["state"])

    async def game_counts(self, event):
        pass  # host-only message; players are in the game group, not the host group


class HostConsumer(_Throttled):
    async def connect(self):
        self.pin = self.scope["url_route"]["kwargs"]["pin"]
        user = self.scope.get("user")
        self.game = await database_sync_to_async(self._load_game)(user)
        if self.game is None:
            await self.close(code=4403)
            return
        self.timer = None
        for group in (services.game_group(self.pin), services.host_group(self.pin)):
            await self.channel_layer.group_add(group, self.channel_name)
        await self.accept()
        state = await database_sync_to_async(services.state)(self.game)
        await self.send_json({"type": "state", "state": state,
                              "extras": await database_sync_to_async(services.host_extras)(self.game)})
        self._arm_timer(state)

    def _load_game(self, user):
        if not (user and user.is_authenticated and user.is_staff):
            return None
        game = services.active_game(self.pin)
        if game and (game.host_id == user.pk or user.is_superuser):
            return game
        return None

    async def disconnect(self, code):
        if getattr(self, "timer", None):
            self.timer.cancel()
        for group in (services.game_group(self.pin), services.host_group(self.pin)):
            await self.channel_layer.group_discard(group, self.channel_name)

    async def handle(self, content):
        action = content.get("action")
        try:
            self.game = await database_sync_to_async(services.host_action)(self.game.pk, action)
        except services.GameError as exc:
            await self.send_json({"type": "error", "message": str(exc)})
            return
        await database_sync_to_async(services.broadcast)(self.game)

    # Server-side timer: reveal automatically when time is up, even if the host's browser lags.
    def _arm_timer(self, state):
        if self.timer:
            self.timer.cancel()
            self.timer = None
        if state["status"] == LiveGame.Status.QUESTION and "question" in state:
            delay = state["question"]["remaining_ms"] / 1000 + services.GRACE_MS / 1000
            self.timer = asyncio.ensure_future(self._reveal_later(delay, state["index"]))

    async def _reveal_later(self, delay, index):
        await asyncio.sleep(delay)
        game = await database_sync_to_async(services.reveal_if_due)(self.game.pk, index)
        if game:
            await database_sync_to_async(services.broadcast)(game)

    async def game_state(self, event):
        self._arm_timer(event["state"])
        extras = await database_sync_to_async(services.host_extras)(self.game)
        await self.send_json({"type": "state", "state": event["state"], "extras": extras})

    async def game_counts(self, event):
        await self.send_json({"type": "counts", "players": event["players"], "answered": event["answered"],
                              "nicknames": event["nicknames"]})
