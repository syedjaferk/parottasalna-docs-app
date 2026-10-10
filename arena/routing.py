from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"^ws/arena/(?P<pin>\d{6})/play/$", consumers.PlayerConsumer.as_asgi()),
    re_path(r"^ws/arena/(?P<pin>\d{6})/host/$", consumers.HostConsumer.as_asgi()),
]
