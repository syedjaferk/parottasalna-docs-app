from django.urls import path

from . import views

urlpatterns = [
    path("p/", views.enter, name="poll_enter"),
    path("p/<str:code>/", views.vote, name="poll_vote"),
    path("polls/", views.manage, name="poll_manage"),
    path("polls/<str:code>/", views.present, name="poll_present"),
    path("polls/<str:code>/action/", views.action, name="poll_action"),
    path("polls/<str:code>/qr.svg", views.qr_svg, name="poll_qr"),
]
