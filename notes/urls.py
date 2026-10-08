from django.urls import path

from . import views

urlpatterns = [
    path("courses/<slug:slug>/notes.json", views.notes_json, name="notes_json"),
    path("courses/<slug:slug>/notes.md", views.course_notes_markdown, name="course_notes_markdown"),
    path("courses/<slug:slug>/notes/", views.course_notes, name="course_notes"),
    path("courses/<slug:slug>/notes/new/", views.note_create, name="note_create"),
    path("courses/<slug:slug>/notes/<int:pk>/", views.note_update, name="note_update"),
    path("courses/<slug:slug>/notes/<int:pk>/delete/", views.note_delete, name="note_delete"),
]
