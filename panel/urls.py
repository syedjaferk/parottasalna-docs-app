from django.urls import path

from . import views

urlpatterns = [
    path("panel/", views.home, name="panel_home"),
]
