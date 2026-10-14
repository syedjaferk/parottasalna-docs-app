from django.urls import path

from . import views

urlpatterns = [
    path("smells/today.json", views.today_json, name="smell_today"),
    path("smells/answer/", views.answer, name="smell_answer"),
]
