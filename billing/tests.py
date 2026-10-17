import hashlib
import hmac
import json
from datetime import timedelta
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from courses.models import Course, Enrollment
from courses.services import accessible_courses, enrol_user

from . import services
from .models import Cohort, Membership, Order, Plan

KEYS = dict(RAZORPAY_KEY_ID="rzp_test_x", RAZORPAY_KEY_SECRET="secret123", RAZORPAY_WEBHOOK_SECRET="whsec")


def sign(secret, message):
    return hmac.new(secret.encode(), message.encode() if isinstance(message, str) else message, hashlib.sha256).hexdigest()


@override_settings(**KEYS)
class BillingTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("a", "a@example.com", "pw")
        self.plan = Plan.objects.create(slug="pro", name="Pro", price_paise=99900, duration_days=365)
        self.course = Course.objects.create(slug="adv", title="Adv", access=Course.Access.PRO, is_active=True)

    def make_order(self, **kw):
        return Order.objects.create(user=self.user, plan=kw.get("plan", self.plan), cohort=kw.get("cohort"),
                                    amount_paise=kw.get("amount", 99900), razorpay_order_id=kw.get("oid", "order_1"))

    def test_checkout_signature(self):
        good = sign("secret123", "order_1|pay_1")
        self.assertTrue(services.verify_checkout_signature("order_1", "pay_1", good))
        self.assertFalse(services.verify_checkout_signature("order_1", "pay_2", good))
        self.assertFalse(services.verify_checkout_signature("order_1", "pay_1", ""))

    def test_fulfil_grants_pro_once_and_stacks(self):
        self.make_order()
        services.fulfil("order_1", "pay_1")
        services.fulfil("order_1", "pay_1")  # webhook after verify: must not double-grant
        self.assertEqual(Membership.objects.filter(user=self.user).count(), 1)
        self.assertTrue(services.has_pro(self.user))
        first_end = services.membership_end(self.user)
        self.make_order(oid="order_2")
        services.fulfil("order_2", "pay_2")
        self.assertEqual(services.membership_end(self.user), first_end + timedelta(days=365))

    def test_wrong_amount_grants_nothing(self):
        self.make_order()
        self.assertIsNone(services.fulfil("order_1", "pay_1", amount_paise=100))
        self.assertFalse(services.has_pro(self.user))
        self.assertEqual(Order.objects.get().status, Order.Status.CREATED)

    def test_cohort_payment_enrols_in_course(self):
        cohort = Cohort.objects.create(slug="c", title="C", course=self.course, price_paise=500000, seats=1)
        Order.objects.create(user=self.user, cohort=cohort, amount_paise=500000, razorpay_order_id="order_c")
        services.fulfil("order_c", "pay_c")
        enrol = Enrollment.objects.get(course=self.course, email="a@example.com")
        self.assertEqual(enrol.source, Enrollment.Source.COHORT)
        self.assertEqual(cohort.seats_left, 0)
        self.assertFalse(cohort.can_reserve)

    def test_webhook_requires_valid_signature(self):
        self.make_order()
        body = json.dumps({"event": "payment.captured", "payload": {"payment": {"entity": {
            "id": "pay_1", "order_id": "order_1", "amount": 99900}}}}).encode()
        bad = self.client.post(reverse("billing_webhook"), body, content_type="application/json",
                               headers={"X-Razorpay-Signature": "nope"})
        self.assertEqual(bad.status_code, 400)
        self.assertFalse(services.has_pro(self.user))
        ok = self.client.post(reverse("billing_webhook"), body, content_type="application/json",
                              headers={"X-Razorpay-Signature": sign("whsec", body)})
        self.assertEqual(ok.status_code, 200)
        self.assertTrue(services.has_pro(self.user))

    def test_verify_endpoint_only_for_own_orders_with_valid_signature(self):
        self.make_order()
        other = get_user_model().objects.create_user("b", "b@example.com", "pw")
        data = {"razorpay_order_id": "order_1", "razorpay_payment_id": "pay_1",
                "razorpay_signature": sign("secret123", "order_1|pay_1")}
        self.client.force_login(other)
        self.assertEqual(self.client.post(reverse("billing_verify"), data).status_code, 400)
        self.client.force_login(self.user)
        self.assertEqual(self.client.post(reverse("billing_verify"), {**data, "razorpay_signature": "x"}).status_code, 400)
        self.assertEqual(self.client.post(reverse("billing_verify"), data).status_code, 200)
        self.assertTrue(services.has_pro(self.user))

    def test_checkout_creates_order_via_razorpay(self):
        self.client.force_login(self.user)
        fake = mock.Mock(status_code=200)
        fake.json.return_value = {"id": "order_new"}
        with mock.patch("billing.services.requests.post", return_value=fake) as post:
            res = self.client.post(reverse("billing_checkout"), {"kind": "plan", "slug": "pro"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["order_id"], "order_new")
        self.assertEqual(post.call_args.kwargs["json"]["amount"], 99900)  # price comes from the DB, never the browser
        self.assertTrue(Order.objects.filter(razorpay_order_id="order_new", user=self.user).exists())

    @override_settings(RAZORPAY_KEY_ID="", RAZORPAY_KEY_SECRET="")
    def test_checkout_unavailable_without_keys(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.post(reverse("billing_checkout"), {"kind": "plan", "slug": "pro"}).status_code, 503)

    def test_pro_course_needs_active_membership(self):
        Enrollment.objects.create(course=self.course, email="a@example.com")
        self.assertNotIn(self.course, accessible_courses(self.user))
        Membership.objects.create(user=self.user, plan=self.plan, ends_at=timezone.now() + timedelta(days=5))
        self.assertIn(self.course, accessible_courses(self.user))
        Membership.objects.all().update(ends_at=timezone.now() - timedelta(days=1))
        self.assertNotIn(self.course, accessible_courses(self.user))

    def test_enrol_rules_by_access_level(self):
        free = Course.objects.create(slug="f", title="F", access=Course.Access.FREE, is_active=True)
        invite = Course.objects.create(slug="i", title="I", access=Course.Access.INVITE, is_active=True)
        self.assertEqual(enrol_user(self.user, free)[1], "free")
        self.assertEqual(Enrollment.objects.get(course=free).source, Enrollment.Source.SELF)
        self.assertIsNone(enrol_user(self.user, free)[0])  # second time: already enrolled
        self.assertEqual(enrol_user(self.user, invite)[1], "invite")
        self.assertEqual(enrol_user(self.user, self.course)[1], "needs_pro")
        self.assertFalse(Enrollment.objects.filter(course__in=[invite, self.course]).exists())
        Membership.objects.create(user=self.user, plan=self.plan, ends_at=timezone.now() + timedelta(days=5))
        self.assertEqual(enrol_user(self.user, self.course)[1], "pro")


class CatalogViewTests(TestCase):
    def setUp(self):
        self.free = Course.objects.create(slug="f", title="Free One", access="free", is_common=True, is_active=True)
        Course.objects.create(slug="h", title="Hidden", access="free", is_active=True, is_listed=False)

    def test_catalog_is_public_and_hides_unlisted(self):
        res = self.client.get(reverse("course_catalog"))
        self.assertContains(res, "Free One")
        self.assertNotContains(res, "Hidden")
        self.assertContains(res, "Sign in to enrol")

    def test_enrol_post_grants_access_and_requires_login(self):
        anon = self.client.post(reverse("course_enroll", args=["f"]))
        self.assertEqual(anon.status_code, 302)
        self.assertIn("login", anon["Location"])
        user = get_user_model().objects.create_user("u", "u@example.com", "pw")
        self.client.force_login(user)
        self.client.post(reverse("course_enroll", args=["f"]))
        self.assertTrue(Enrollment.objects.filter(course=self.free, email="u@example.com", user=user).exists())

    def test_signed_out_buttons_match_each_access_level(self):
        Course.objects.create(slug="pr", title="Pro One", access="pro", is_active=True)
        Course.objects.create(slug="iv", title="Invite One", access="invite", is_active=True)
        html = self.client.get(reverse("course_catalog")).content.decode()
        self.assertEqual(html.count("Sign in to enrol"), 1)  # only the free course asks you to sign in
        self.assertIn("Unlock with Pro", html)
        self.assertIn("By invitation", html)

    def test_pricing_page_renders_without_keys(self):
        Plan.objects.create(slug="p", name="Pro", price_paise=50000)
        res = self.client.get(reverse("pricing"))
        self.assertContains(res, "Online payments are not open yet")


class DropoffTests(TestCase):
    def test_funnel_counts_readers_and_flags_big_drops(self):
        from unittest import mock

        from courses.models import PageProgress, PageVisit
        from courses.services import dropoff

        course = Course.objects.create(slug="d", title="D", is_active=True)
        users = [get_user_model().objects.create_user(f"u{i}", f"u{i}@x.com", "pw") for i in range(10)]
        for u in users:
            PageVisit.objects.create(user=u, course=course, page="s1")
        for u in users[:4]:
            PageVisit.objects.create(user=u, course=course, page="s2")
        for u in users[:2]:
            PageProgress.objects.create(user=u, course=course, page="s2")
        with mock.patch("courses.services.chapters", return_value=["s1", "s2"]):
            rows = dropoff(course)
        self.assertEqual([r["readers"] for r in rows], [10, 4])
        self.assertEqual(rows[1]["reach"], 40)
        self.assertEqual(rows[1]["lost"], 60)
        self.assertTrue(rows[1]["alarm"])
        self.assertEqual(rows[1]["finish_rate"], 50)

    def test_insights_is_staff_only(self):
        user = get_user_model().objects.create_user("n", "n@x.com", "pw")
        self.client.force_login(user)
        self.assertEqual(self.client.get(reverse("course_insights")).status_code, 302)
        user.is_staff = True
        user.save()
        self.assertEqual(self.client.get(reverse("course_insights")).status_code, 200)


class PathsAndLandingTests(TestCase):
    def setUp(self):
        from courses.models import LearningPath, PathStep

        self.path = LearningPath.objects.create(slug="p1", title="Path One", tagline="Go far", sort_order=1)
        self.course = Course.objects.create(slug="c1", title="Course One", is_active=True, is_common=True)
        PathStep.objects.create(path=self.path, order=1, kind="course", course=self.course)
        PathStep.objects.create(path=self.path, order=2, kind="link", title="Real tool", url="/resume-review/")
        PathStep.objects.create(path=self.path, order=3, kind="link", title="Missing tool", url="/no-such-page/")

    def test_path_skips_links_that_do_not_exist_on_this_site(self):
        res = self.client.get(reverse("path_detail", args=["p1"]))
        self.assertContains(res, "Course One")
        self.assertContains(res, "Real tool")
        self.assertNotContains(res, "Missing tool")

    def test_paths_index_and_landing_show_the_path(self):
        self.assertContains(self.client.get(reverse("paths")), "Path One")
        home = self.client.get("/")
        self.assertContains(home, "Path One")
        self.assertContains(home, "what to do first")

    def test_signed_in_user_sees_enrolled_badge(self):
        user = get_user_model().objects.create_user("e", "e@x.com", "pw")
        Enrollment.objects.create(course=self.course, email="e@x.com")
        self.client.force_login(user)
        self.assertContains(self.client.get(reverse("path_detail", args=["p1"])), "enrolled")


class ManualPaymentTests(TestCase):
    def test_payment_link_replaces_checkout_button(self):
        Plan.objects.create(slug="p", name="Pro", price_paise=99900, payment_url="https://rzp.io/l/pro")
        Cohort.objects.create(slug="b", title="Batch", payment_url="https://rzp.io/l/batch", status="open")
        html = self.client.get(reverse("pricing")).content.decode()
        self.assertIn('href="https://rzp.io/l/pro"', html)
        self.assertIn('href="https://rzp.io/l/batch"', html)
        self.assertNotIn("data-buy=", html)
        self.assertNotIn("Online payments are not open yet", html)  # nothing is left unpayable

    def test_admin_can_grant_pro_by_hand_with_default_length(self):
        staff = get_user_model().objects.create_superuser("root", "root@x.com", "pw")
        student = get_user_model().objects.create_user("s", "s@x.com", "pw")
        plan = Plan.objects.create(slug="p", name="Pro", price_paise=1, duration_days=30)
        self.client.force_login(staff)
        res = self.client.post("/admin/billing/membership/add/", {
            "user": student.pk, "plan": plan.pk, "starts_at_0": "2026-10-17", "starts_at_1": "10:00:00", "ends_at_0": "", "ends_at_1": ""})
        self.assertEqual(res.status_code, 302, getattr(res, "context", None) and res.context["adminform"].form.errors)
        self.assertTrue(services.has_pro(student))
        end = services.membership_end(student)
        self.assertAlmostEqual((end - timezone.now()).days, 30, delta=1)
