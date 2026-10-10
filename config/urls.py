from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),  # provides /accounts/google/login/callback/
    path("", include("blog.urls")),
    path("", include("quizzes.urls")),
    path("", include("notes.urls")),
    path("", include("streaks.urls")),
    path("", include("courses.urls")),
]
