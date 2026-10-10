from django.urls import path

from . import views

urlpatterns = [
    path("streak.json", views.streak_json, name="streak_json"),
    path("streak/ping/", views.streak_ping, name="streak_ping"),
]
