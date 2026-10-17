from django.urls import path

from . import views

urlpatterns = [
    path("pricing/", views.pricing, name="pricing"),
    path("billing/checkout/", views.checkout, name="billing_checkout"),
    path("billing/verify/", views.verify, name="billing_verify"),
    path("billing/webhook/", views.webhook, name="billing_webhook"),
]
