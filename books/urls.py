from django.urls import path

from . import views

urlpatterns = [
    path("stories/", views.book_index, name="book_index"),
    path("stories/media/<str:name>", views.book_media, name="book_media"),
    path("stories/<slug:slug>/", views.book_chapter, name="book_chapter"),
]
