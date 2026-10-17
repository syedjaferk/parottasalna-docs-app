from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_page, name="login"),
    path("privacy/", views.privacy, name="privacy"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("paths/", views.paths, name="paths"),
    path("paths/<slug:slug>/", views.path_detail, name="path_detail"),
    path("courses/", views.catalog, name="course_catalog"),
    path("courses/insights/", views.insights, name="course_insights"),
    path("courses/insights/<slug:slug>/", views.insights, name="course_insights_detail"),
    path("courses/<slug:slug>/", views.course_detail, name="course_detail"),
    path("courses/<slug:slug>/enroll/", views.enroll, name="course_enroll"),
    path("courses/<slug:slug>/progress.json", views.progress_json, name="course_progress"),
    path("courses/<slug:slug>/progress/", views.progress_update, name="course_progress_update"),
    path("courses/<slug:slug>/docs/", views.course_docs, name="course_docs"),
    path("courses/<slug:slug>/docs/<path:path>", views.course_docs, name="course_docs_file"),
]
