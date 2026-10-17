import json

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_safe

from courses.security import api_login_required, no_store

from . import services
from .models import Cohort, Order, Plan


@require_safe
def pricing(request):
    plans = Plan.objects.filter(is_active=True)
    cohorts = Cohort.objects.filter(is_listed=True).exclude(status=Cohort.Status.CLOSED).select_related("course")
    return render(request, "billing/pricing.html", {
        "plans": plans, "cohorts": cohorts,
        "has_links": any(p.payment_url for p in plans) or any(c.payment_url for c in cohorts),
        "payments_on": services.payments_enabled(),
        "pro_until": services.membership_end(request.user) if request.user.is_authenticated else None,
        "is_pro": services.has_pro(request.user),
        "contact_email": settings.CONTACT_EMAIL,
    })


@require_POST
@api_login_required
def checkout(request):
    """Start a payment for one plan or one cohort seat. Returns what Razorpay's checkout window needs."""
    kind, slug = request.POST.get("kind"), request.POST.get("slug", "")
    plan = cohort = None
    if kind == "plan":
        plan = get_object_or_404(Plan, slug=slug, is_active=True)
    elif kind == "cohort":
        cohort = get_object_or_404(Cohort, slug=slug)
        if not cohort.can_reserve:
            return JsonResponse({"error": "This batch is not open for booking."}, status=409)
    else:
        return JsonResponse({"error": "Unknown item."}, status=400)
    try:
        order = services.create_order(request.user, plan=plan, cohort=cohort)
    except services.PaymentsUnavailable as error:
        return JsonResponse({"error": str(error)}, status=503)
    return no_store(JsonResponse({
        "key": settings.RAZORPAY_KEY_ID, "order_id": order.razorpay_order_id, "amount": order.amount_paise,
        "currency": order.currency, "name": "Parottasalna", "description": order.item_name,
        "prefill": {"email": request.user.email},
    }))


@require_POST
@api_login_required
def verify(request):
    """The browser reports a finished payment. Trust it only if the signature checks out."""
    order_id = request.POST.get("razorpay_order_id", "")
    payment_id = request.POST.get("razorpay_payment_id", "")
    signature = request.POST.get("razorpay_signature", "")
    mine = Order.objects.filter(razorpay_order_id=order_id, user=request.user).exists()
    if not mine or not services.verify_checkout_signature(order_id, payment_id, signature):
        return JsonResponse({"ok": False, "error": "Could not verify this payment."}, status=400)
    order = services.fulfil(order_id, payment_id)
    return no_store(JsonResponse({"ok": bool(order)}))


@csrf_exempt
@require_POST
def webhook(request):
    """Razorpay calls this when a payment is captured, even if the buyer closed the tab."""
    body = request.body
    if not services.verify_webhook_signature(body, request.headers.get("X-Razorpay-Signature", "")):
        return HttpResponse(status=400)
    try:
        event = json.loads(body)
        if event.get("event") in {"payment.captured", "order.paid"}:
            payment = event["payload"]["payment"]["entity"]
            services.fulfil(payment["order_id"], payment["id"], payment.get("amount"))
    except (ValueError, KeyError, TypeError):
        return HttpResponse(status=400)
    return HttpResponse(status=200)
