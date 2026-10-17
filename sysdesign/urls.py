from django.urls import path

from . import views

urlpatterns = [
    path("system-design/", views.index, name="sysdesign_index"),
    path("system-design/<slug:slug>/", views.problem, name="sysdesign_problem"),
    path("system-design/<slug:slug>/progress.json", views.progress_get, name="sysdesign_progress"),
    path("system-design/<slug:slug>/progress/save/", views.progress_save, name="sysdesign_progress_save"),
]
