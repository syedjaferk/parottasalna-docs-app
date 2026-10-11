from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, TransactionTestCase
from django.urls import reverse

from config.asgi import application

from . import services
from .models import Poll, Vote
from .views import COOKIE

User = get_user_model()


def make_poll(user, show_results=True):
    return services.create_poll("Best tiffin?", "Idly\nDosa\n\nPongal", user, show_results)


class ServiceTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user("teacher", is_staff=True)

    def test_create_cleans_options_and_makes_a_code(self):
        poll = make_poll(self.teacher)
        self.assertRegex(poll.code, r"^[A-Z2-9]{5}$")
        self.assertEqual(poll.option_list(), ["Idly", "Dosa", "Pongal"])

    def test_bad_options_are_rejected(self):
        for options in ("Only one", "A\na", "\n".join(str(i) for i in range(7)), "x" * 81 + "\ny"):
            with self.assertRaises(ValidationError):
                services.create_poll("Q?", options, self.teacher)

    def test_one_vote_per_voter_and_votes_can_change(self):
        poll = make_poll(self.teacher)
        services.cast(poll, "token-a", 0)
        services.cast(poll, "token-b", 0)
        services.cast(poll, "token-a", 2)          # changes, doesn't add
        self.assertEqual(services.counts(poll), [1, 0, 1])
        self.assertEqual(services.my_choice(poll, "token-a"), 2)
        self.assertIsNone(services.my_choice(poll, "nobody"))

    def test_invalid_and_closed(self):
        poll = make_poll(self.teacher)
        for bad in (3, -1, "x", None):
            with self.assertRaises(services.PollError):
                services.cast(poll, "t", bad)
        services.set_open(poll, False)
        with self.assertRaises(services.PollError):
            services.cast(poll, "t", 0)
        self.assertIsNotNone(poll.closed_at)

    def test_voters_are_not_linkable_across_polls(self):
        a, b = make_poll(self.teacher), make_poll(self.teacher)
        self.assertNotEqual(Vote.hash_voter("same", a.code), Vote.hash_voter("same", b.code))


class ViewTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user("teacher", is_staff=True)
        self.poll = make_poll(self.teacher)

    def test_enter_code(self):
        r = self.client.post(reverse("poll_enter"), {"code": self.poll.code.lower()})
        self.assertRedirects(r, reverse("poll_vote", args=[self.poll.code]))
        self.assertContains(self.client.post(reverse("poll_enter"), {"code": "ZZZZZ"}), "No poll with that code")

    def test_vote_sets_cookie_and_changing_does_not_duplicate(self):
        url = reverse("poll_vote", args=[self.poll.code])
        page = self.client.get(url)
        self.assertContains(page, "Best tiffin?")
        self.assertNotContains(page, "Live results")          # results only after voting
        r = self.client.post(url, {"choice": 1})
        self.assertRedirects(r, url)
        self.assertTrue(r.cookies[COOKIE]["httponly"])
        self.client.post(url, {"choice": 2})
        self.assertEqual(self.poll.votes.count(), 1)
        self.assertEqual(self.poll.votes.get().choice, 2)
        page = self.client.get(url)
        self.assertContains(page, "Live results")
        self.assertContains(page, "Tap another option")

    def test_hidden_results_and_closed_poll(self):
        self.poll.show_results = False
        self.poll.save()
        url = reverse("poll_vote", args=[self.poll.code])
        self.client.post(url, {"choice": 0})
        page = self.client.get(url)
        self.assertNotContains(page, "Live results")
        self.assertContains(page, "Watch the teacher")
        services.set_open(self.poll, False)
        self.client.post(url, {"choice": 1})
        self.assertEqual(self.poll.votes.get().choice, 0)       # closed: unchanged
        self.assertContains(self.client.get(url), "Voting is closed")

    def test_teacher_pages_are_staff_only(self):
        present = reverse("poll_present", args=[self.poll.code])
        r = self.client.get(reverse("poll_manage"))
        self.assertEqual(r.status_code, 302)                                  # anonymous → login
        self.assertTrue(r["Location"].startswith(reverse("admin:login")))
        student = User.objects.create_user("student")                        # signed in, not staff
        self.client.force_login(student)
        for url in (reverse("poll_manage"), present, reverse("poll_qr", args=[self.poll.code])):
            self.assertEqual(self.client.get(url).status_code, 404, url)
        self.assertEqual(self.client.post(reverse("poll_manage"),
                                          {"question": "Q", "options": "a\nb"}).status_code, 404)
        self.assertEqual(self.client.post(reverse("poll_action", args=[self.poll.code]),
                                          {"action": "close"}).status_code, 404)
        self.assertEqual(Poll.objects.count(), 1)
        # Students can still vote
        self.client.post(reverse("poll_vote", args=[self.poll.code]), {"choice": 0})
        self.assertEqual(self.poll.votes.count(), 1)
        other_staff = User.objects.create_user("other", is_staff=True)       # staff can create their own…
        self.client.force_login(other_staff)
        self.assertEqual(self.client.get(reverse("poll_manage")).status_code, 200)
        self.assertEqual(self.client.get(present).status_code, 404)          # …but not run someone else's
        admin = User.objects.create_superuser("admin", password=None)         # superusers can run any
        self.client.force_login(admin)
        self.assertEqual(self.client.get(present).status_code, 200)
        self.client.force_login(self.teacher)
        page = self.client.get(present)
        self.assertContains(page, "<svg")                        # the QR code
        self.assertContains(page, self.poll.code)
        qr = self.client.get(reverse("poll_qr", args=[self.poll.code]))
        self.assertEqual(qr["Content-Type"], "image/svg+xml")

    def test_create_and_actions(self):
        self.client.force_login(self.teacher)
        r = self.client.post(reverse("poll_manage"), {"question": "Ready?", "options": "Yes\nNo", "show_results": "on"})
        poll = Poll.objects.get(question="Ready?")
        self.assertRedirects(r, reverse("poll_present", args=[poll.code]))
        self.assertContains(self.client.post(reverse("poll_manage"), {"question": "Q", "options": "one"}), "Give 2")
        services.cast(poll, "t", 0)
        act = reverse("poll_action", args=[poll.code])
        self.client.post(act, {"action": "close"})
        poll.refresh_from_db()
        self.assertFalse(poll.is_open)
        self.client.post(act, {"action": "toggle_results"})
        self.client.post(act, {"action": "reset"})
        poll.refresh_from_db()
        self.assertFalse(poll.show_results)
        self.assertEqual(poll.votes.count(), 0)
        self.client.post(act, {"action": "delete"})
        self.assertFalse(Poll.objects.filter(pk=poll.pk).exists())


class LiveTests(TransactionTestCase):
    """The read-only WebSocket feed, with the in-memory channel layer."""

    def setUp(self):
        self.teacher = User.objects.create_user("teacher", is_staff=True)
        self.client.force_login(self.teacher)
        self.session = self.client.cookies["sessionid"].value

    def socket(self, code, cookie=""):
        return WebsocketCommunicator(application, f"/ws/polls/{code}/",
                                     headers=[(b"origin", b"http://testserver"), (b"host", b"testserver"),
                                              (b"cookie", cookie.encode())])

    def test_votes_reach_teacher_and_students_live(self):
        poll = make_poll(self.teacher)

        async def scenario():
            teacher = self.socket(poll.code, f"sessionid={self.session}")
            student = self.socket(poll.code)
            self.assertTrue((await teacher.connect())[0])
            self.assertTrue((await student.connect())[0])
            self.assertEqual((await teacher.receive_json_from())["state"]["counts"], [0, 0, 0])
            await student.receive_json_from()

            await database_sync_to_async(lambda: (services.cast(poll, "s1", 1), services.broadcast(poll)))()
            self.assertEqual((await teacher.receive_json_from())["state"]["counts"], [0, 1, 0])
            self.assertEqual((await student.receive_json_from())["state"]["total"], 1)
            await teacher.disconnect()
            await student.disconnect()

        async_to_sync(scenario)()

    def test_hidden_results_are_not_sent_to_students(self):
        poll = make_poll(self.teacher, show_results=False)

        async def scenario():
            student = self.socket(poll.code)
            await student.connect()
            state = (await student.receive_json_from())["state"]
            self.assertIsNone(state["counts"])
            self.assertIsNone(state["total"])
            teacher = self.socket(poll.code, f"sessionid={self.session}")
            await teacher.connect()
            self.assertEqual((await teacher.receive_json_from())["state"]["counts"], [0, 0, 0])
            staff = await database_sync_to_async(User.objects.create_user)("other-staff", is_staff=True)
            await database_sync_to_async(self.client.force_login)(staff)
            as_staff = self.socket(poll.code, f"sessionid={self.client.cookies['sessionid'].value}")
            await as_staff.connect()
            self.assertIsNone((await as_staff.receive_json_from())["state"]["counts"])   # not the creator
            missing = self.socket("ZZZZZ")
            ok, code = await missing.connect()
            self.assertFalse(ok)
            self.assertEqual(code, 4404)

        async_to_sync(scenario)()
