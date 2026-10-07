from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_page, name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("courses/<slug:slug>/docs/", views.course_docs, name="course_docs"),
    path("courses/<slug:slug>/docs/<path:path>", views.course_docs, name="course_docs_file"),
]
