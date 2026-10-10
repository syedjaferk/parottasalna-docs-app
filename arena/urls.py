from django.urls import path

from . import views

urlpatterns = [
    path("join", views.join, name="arena_join"),
    path("join/<str:pin>", views.nickname, name="arena_nickname"),
    path("play/<str:pin>", views.play, name="arena_play"),
    path("arena/", views.host_home, name="arena_host_home"),
    path("arena/start/<int:quiz_id>/", views.host_start, name="arena_host_start"),
    path("arena/host/<str:pin>/", views.host, name="arena_host"),
    path("arena/results/<int:game_id>.csv", views.results_csv, name="arena_results_csv"),
]
