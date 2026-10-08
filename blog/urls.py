from django.urls import path

from . import views
from .feeds import LatestPostsFeed

urlpatterns = [
    path("blog/", views.blog_index, name="blog_index"),
    path("blog/feed.xml", LatestPostsFeed(), name="blog_feed"),
    path("blog/media/<path:path>", views.blog_media, name="blog_media"),
    path("blog/<slug:slug>/", views.blog_post, name="blog_post"),
]
