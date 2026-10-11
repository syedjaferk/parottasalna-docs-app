"""/ws/polls/<code>/: a read-only live feed of one poll's results.

Votes and teacher actions are ordinary POST requests; this socket only pushes updates. The poll's
creator (or a superuser) always gets the counts; everyone else gets them only while show_results is on.
"""
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from . import services
from .models import Poll


class PollConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.code = self.scope["url_route"]["kwargs"]["code"]
        found = await database_sync_to_async(self._load)()
        if not found:
            await self.close(code=4404)
            return
        self.group = services.group_name(self.code)
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()
        await self.send_state(self.initial_state)

    def _load(self):
        poll = Poll.objects.filter(code=self.code).first()
        if poll is None:
            return False
        user = self.scope.get("user")
        self.is_owner = bool(user and user.is_authenticated and user.is_active and user.is_staff
                             and (poll.created_by_id == user.pk or user.is_superuser))
        self.initial_state = services.state(poll)
        return True

    async def disconnect(self, code):
        if getattr(self, "group", None):
            await self.channel_layer.group_discard(self.group, self.channel_name)

    async def receive_json(self, content, **kwargs):
        pass  # nothing to receive: votes go through the CSRF-protected form

    async def poll_update(self, event):
        await self.send_state(event["state"])

    async def send_state(self, state):
        if not (self.is_owner or state["show_results"]):
            state = {**state, "counts": None, "total": None}
        await self.send_json({"type": "state", "state": state})
