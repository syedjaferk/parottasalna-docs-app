from django.urls import path

from . import views

urlpatterns = [
    path("courses/<slug:slug>/quizzes/", views.quiz_list, name="quiz_list"),
    path("courses/<slug:slug>/quizzes/<int:pk>/", views.quiz_take, name="quiz_take"),
    path("courses/<slug:slug>/quizzes/attempts/<int:pk>/", views.quiz_result, name="quiz_result"),
    path("courses/<slug:slug>/quizzes.json", views.quiz_feed, name="quiz_feed"),
    path("courses/<slug:slug>/quizzes/scores/", views.scoreboard, name="quiz_scoreboard"),
    path("courses/<slug:slug>/quizzes/scores.csv", views.scoreboard_csv, name="quiz_scoreboard_csv"),
]
