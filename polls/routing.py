from django.urls import re_path

from . import consumers
from .models import CODE_ALPHABET, CODE_LENGTH

websocket_urlpatterns = [
    re_path(rf"^ws/polls/(?P<code>[{CODE_ALPHABET}]{{{CODE_LENGTH}}})/$", consumers.PollConsumer.as_asgi()),
]
