from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_page, name="login"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("courses/<slug:slug>/progress.json", views.progress_json, name="course_progress"),
    path("courses/<slug:slug>/progress/", views.progress_update, name="course_progress_update"),
    path("courses/<slug:slug>/docs/", views.course_docs, name="course_docs"),
    path("courses/<slug:slug>/docs/<path:path>", views.course_docs, name="course_docs_file"),
]
