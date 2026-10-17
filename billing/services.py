"""Pro membership checks, Razorpay order creation and signature checks, and order fulfilment."""
import hashlib
import hmac
from datetime import timedelta

import requests
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from courses.models import Enrollment

from .models import Cohort, Membership, Order, Plan

RAZORPAY_API = "https://api.razorpay.com/v1"


class PaymentsUnavailable(Exception):
    """Razorpay keys are not configured (or Razorpay could not be reached)."""


def payments_enabled():
    return bool(settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET)


def has_pro(user):
    """Staff always have Pro; everyone else needs a membership that has not ended."""
    if not user.is_authenticated:
        return False
    if user.is_staff:
        return True
    return Membership.objects.filter(user=user, ends_at__gt=timezone.now()).exists()


def membership_end(user):
    m = Membership.objects.filter(user=user, ends_at__gt=timezone.now()).order_by("-ends_at").first()
    return m.ends_at if m else None


def create_order(user, plan=None, cohort=None):
    """Create a Razorpay order for one plan or cohort seat and remember it locally."""
    if (plan is None) == (cohort is None):
        raise ValueError("Give exactly one of plan or cohort.")
    if not payments_enabled():
        raise PaymentsUnavailable("Payments are not enabled yet.")
    item = plan or cohort
    amount = item.price_paise
    try:
        res = requests.post(
            f"{RAZORPAY_API}/orders", auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET), timeout=15,
            json={"amount": amount, "currency": "INR", "receipt": f"u{user.pk}-{timezone.now():%y%m%d%H%M%S}",
                  "notes": {"user_id": str(user.pk), "kind": "plan" if plan else "cohort", "item": item.slug}},
        )
        res.raise_for_status()
        remote = res.json()
    except (requests.RequestException, ValueError) as error:
        raise PaymentsUnavailable("Could not reach the payment provider. Try again in a moment.") from error
    return Order.objects.create(user=user, plan=plan, cohort=cohort, amount_paise=amount,
                                razorpay_order_id=remote["id"])


def _signature(secret, message):
    return hmac.new(secret.encode(), message.encode() if isinstance(message, str) else message, hashlib.sha256).hexdigest()


def verify_checkout_signature(order_id, payment_id, signature):
    """Razorpay signs `order_id|payment_id` with the key secret after a successful checkout."""
    if not (settings.RAZORPAY_KEY_SECRET and signature):
        return False
    return hmac.compare_digest(_signature(settings.RAZORPAY_KEY_SECRET, f"{order_id}|{payment_id}"), signature)


def verify_webhook_signature(body, signature):
    """Webhooks are signed over the raw body with the webhook secret."""
    if not (settings.RAZORPAY_WEBHOOK_SECRET and signature):
        return False
    return hmac.compare_digest(_signature(settings.RAZORPAY_WEBHOOK_SECRET, body), signature)


@transaction.atomic
def fulfil(razorpay_order_id, payment_id, amount_paise=None):
    """Mark an order paid and grant what it bought. Safe to call twice (checkout verify + webhook)."""
    order = Order.objects.select_for_update().filter(razorpay_order_id=razorpay_order_id).first()
    if order is None:
        return None
    if order.status == Order.Status.PAID:
        return order
    if amount_paise is not None and int(amount_paise) != order.amount_paise:
        return None  # never grant access for a different amount than we asked for
    order.status, order.razorpay_payment_id, order.paid_at = Order.Status.PAID, payment_id, timezone.now()
    order.save(update_fields=["status", "razorpay_payment_id", "paid_at"])
    if order.plan_id:
        start = membership_end(order.user) or timezone.now()
        Membership.objects.create(user=order.user, plan=order.plan, order=order, starts_at=timezone.now(),
                                  ends_at=start + timedelta(days=order.plan.duration_days))
    elif order.cohort_id and order.cohort.course_id and order.user.email:
        enrol, created = Enrollment.objects.get_or_create(
            course=order.cohort.course, email=order.user.email.lower(),
            defaults={"user": order.user, "source": Enrollment.Source.COHORT})
        if not created and enrol.user_id is None:
            enrol.user = order.user
            enrol.save(update_fields=["user"])
    return order
