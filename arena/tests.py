from datetime import timedelta

from asgiref.sync import async_to_sync, sync_to_async
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.utils import timezone

from config.asgi import application

from . import services
from .consumers import COOKIE, make_player_cookie, read_player_cookie
from .models import LiveGame, LiveQuestion, LiveQuiz, Player

User = get_user_model()


def make_quiz(n=2):
    quiz = LiveQuiz.objects.create(title="Docker basics")
    for i in range(n):
        LiveQuestion.objects.create(quiz=quiz, order=i, text=f"Question {i}", time_limit=20, points=1000,
                                    choices="Wrong\n*Right\nAlso wrong")
    return quiz


class ModelTests(TestCase):
    def test_choices_parsing(self):
        q = LiveQuestion(text="?", choices="A\n*B\n\n C ")
        self.assertEqual(q.parsed_choices(), [("A", False), ("B", True), ("C", False)])
        self.assertEqual(q.correct_indexes(), {1})

    def test_clean_rejects_bad_questions(self):
        quiz = LiveQuiz.objects.create(title="t")
        for choices in ("*Only one", "A\nB", "*A\nB\nC\nD\nE"):
            with self.assertRaises(ValidationError):
                LiveQuestion(quiz=quiz, text="?", choices=choices).full_clean()
        LiveQuestion(quiz=quiz, text="?", choices="*A\nB").full_clean()


class ServiceTests(TestCase):
    def setUp(self):
        self.host = User.objects.create_user("host", is_staff=True)
        self.quiz = make_quiz()
        self.game = services.create_game(self.quiz, self.host)

    def test_pin_is_six_digits_and_findable(self):
        self.assertRegex(self.game.pin, r"^\d{6}$")
        self.assertEqual(services.active_game(self.game.pin), self.game)

    def test_empty_quiz_cannot_start(self):
        with self.assertRaises(services.GameError):
            services.create_game(LiveQuiz.objects.create(title="empty"), self.host)

    def test_nicknames(self):
        player, token = services.join(self.game, "  Kumar   S ")
        self.assertEqual(player.nickname, "Kumar S")
        self.assertNotEqual(player.token_hash, token)
        self.assertEqual(services.player_for(self.game.pin, player.pk, token), player)
        self.assertIsNone(services.player_for(self.game.pin, player.pk, "wrong"))
        services.join(self.game, "தமிழ்செல்வி")  # Tamil names are fine
        for bad in ("", "   ", "x" * 21, "bell\x07"):
            with self.assertRaises(services.GameError):
                services.join(self.game, bad)
        with self.assertRaises(services.GameError):
            services.join(self.game, "kumar s")  # taken (case-insensitive)

    def test_full_game_flow_and_scoring(self):
        alice, _ = services.join(self.game, "alice")
        bob, _ = services.join(self.game, "bob")
        with self.assertRaises(services.GameError):
            services.submit_answer(alice.pk, 1)  # still in the lobby
        services.host_action(self.game.pk, "start")
        _, everyone = services.submit_answer(alice.pk, 1)
        self.assertFalse(everyone)
        with self.assertRaises(services.GameError):
            services.submit_answer(alice.pk, 0)  # one answer per question
        with self.assertRaises(services.GameError):
            services.submit_answer(bob.pk, 7)  # no such choice
        _, everyone = services.submit_answer(bob.pk, 0)
        self.assertTrue(everyone)  # last answer reveals straight away
        self.game.refresh_from_db()
        self.assertEqual(self.game.status, LiveGame.Status.REVEAL)
        alice.refresh_from_db()
        bob.refresh_from_db()
        self.assertGreater(alice.score, 900)
        self.assertEqual(bob.score, 0)

        state = services.state(self.game)
        self.assertEqual(state["reveal"], {"correct": [1], "counts": [1, 1, 0]})
        self.assertEqual(services.personal(alice)["rank"], 1)
        self.assertEqual(services.personal(bob)["last"], {"choice": 0, "correct": False, "points": 0})

        services.host_action(self.game.pk, "leaderboard")
        self.assertEqual(services.state(LiveGame.objects.get(pk=self.game.pk))["leaderboard"][0]["nickname"], "alice")
        services.host_action(self.game.pk, "next")
        game = services.host_action(self.game.pk, "reveal")
        game = services.host_action(game.pk, "next")  # past the last question → finished
        self.assertEqual(game.status, LiveGame.Status.FINISHED)
        self.assertIsNone(services.active_game(game.pin))

    def test_wrong_order_actions_are_refused(self):
        for action in ("next", "reveal", "leaderboard", "dance"):
            with self.assertRaises(services.GameError):
                services.host_action(self.game.pk, action)

    def test_score_shrinks_with_time_and_late_answers_fail(self):
        q = self.quiz.questions.first()
        self.assertEqual(services.score_for(q, 0, True), 1000)
        self.assertEqual(services.score_for(q, 20000, True), 500)
        self.assertEqual(services.score_for(q, 999999, True), 500)
        self.assertEqual(services.score_for(q, 0, False), 0)
        player, _ = services.join(self.game, "late")
        services.host_action(self.game.pk, "start")
        LiveGame.objects.filter(pk=self.game.pk).update(question_started_at=timezone.now() - timedelta(seconds=30))
        with self.assertRaises(services.GameError):
            services.submit_answer(player.pk, 1)

    def test_reveal_if_due_only_for_the_open_question(self):
        services.host_action(self.game.pk, "start")
        self.assertIsNone(services.reveal_if_due(self.game.pk, 5))
        self.assertEqual(services.reveal_if_due(self.game.pk, 0).status, LiveGame.Status.REVEAL)
        self.assertIsNone(services.reveal_if_due(self.game.pk, 0))

    def test_finished_pin_can_be_reused(self):
        services.host_action(self.game.pk, "finish")
        LiveGame.objects.create(quiz=self.quiz, host=self.host, pin=self.game.pin)


class ViewTests(TestCase):
    def setUp(self):
        self.host = User.objects.create_user("host", is_staff=True)
        self.quiz = make_quiz()
        self.game = services.create_game(self.quiz, self.host)

    def test_join_flow_sets_signed_cookie(self):
        self.assertContains(self.client.get(reverse("arena_join")), "PIN")
        r = self.client.post(reverse("arena_join"), {"pin": "000000"})
        self.assertContains(r, "find a game with that PIN")
        r = self.client.post(reverse("arena_join"), {"pin": self.game.pin})
        self.assertRedirects(r, reverse("arena_nickname", args=[self.game.pin]))
        r = self.client.post(reverse("arena_nickname", args=[self.game.pin]), {"nickname": "<b>meena</b>"})
        self.assertRedirects(r, reverse("arena_play", args=[self.game.pin]))
        cookie = r.cookies[COOKIE]
        self.assertTrue(cookie["httponly"])
        player_id, token = read_player_cookie(cookie.value)
        self.assertEqual(Player.objects.get(pk=player_id).nickname, "<b>meena</b>")
        page = self.client.get(reverse("arena_play", args=[self.game.pin]))
        self.assertContains(page, "&lt;b&gt;meena&lt;/b&gt;")
        self.assertNotContains(page, "<b>meena</b>")

    def test_play_without_cookie_goes_to_nickname(self):
        r = self.client.get(reverse("arena_play", args=[self.game.pin]))
        self.assertRedirects(r, reverse("arena_nickname", args=[self.game.pin]))

    def test_host_pages_are_staff_only(self):
        student = User.objects.create_user("stu")
        self.client.force_login(student)
        self.assertEqual(self.client.get(reverse("arena_host_home")).status_code, 302)
        other = User.objects.create_user("other", is_staff=True)
        self.client.force_login(other)
        self.assertEqual(self.client.get(reverse("arena_host", args=[self.game.pin])).status_code, 404)
        self.assertEqual(self.client.get(reverse("arena_results_csv", args=[self.game.pk])).status_code, 404)
        self.client.force_login(self.host)
        self.assertContains(self.client.get(reverse("arena_host_home")), "Docker basics")
        self.assertContains(self.client.get(reverse("arena_host", args=[self.game.pin])), self.game.pin)
        r = self.client.post(reverse("arena_host_start", args=[self.quiz.pk]))
        self.assertEqual(r.status_code, 302)
        self.assertEqual(LiveGame.objects.count(), 2)

    def test_results_csv_neutralises_formulas(self):
        services.join(self.game, "=HYPERLINK(1)")
        self.client.force_login(self.host)
        body = self.client.get(reverse("arena_results_csv", args=[self.game.pk])).content.decode()
        self.assertIn("'=HYPERLINK(1)", body)


class ConsumerTests(TransactionTestCase):
    """End-to-end over WebSockets with the in-memory channel layer."""

    def setUp(self):
        self.host = User.objects.create_user("host", is_staff=True)
        self.quiz = make_quiz(n=1)
        self.game = services.create_game(self.quiz, self.host)
        self.client.force_login(self.host)
        self.session = self.client.cookies["sessionid"].value

    def communicator(self, role, cookie=""):
        return WebsocketCommunicator(application, f"/ws/arena/{self.game.pin}/{role}/",
                                     headers=[(b"origin", b"http://testserver"), (b"host", b"testserver"),
                                              (b"cookie", cookie.encode())])

    def test_player_and_host_play_a_round(self):
        player, token = services.join(self.game, "alice")
        player_cookie = f"{COOKIE}={make_player_cookie(player.pk, token)}"

        async def scenario():
            host = self.communicator("host", f"sessionid={self.session}")
            ok, _ = await host.connect()
            self.assertTrue(ok)
            first = await host.receive_json_from()
            self.assertEqual(first["state"]["status"], "lobby")
            self.assertEqual(first["extras"]["nicknames"], ["alice"])

            phone = self.communicator("play", player_cookie)
            ok, _ = await phone.connect()
            self.assertTrue(ok)
            hello = await phone.receive_json_from()
            self.assertEqual((hello["state"]["status"], hello["you"]["nickname"]), ("lobby", "alice"))

            await host.send_json_to({"action": "start"})
            q = await phone.receive_json_from()
            self.assertEqual(q["state"]["question"]["choices"], ["Wrong", "Right", "Also wrong"])
            self.assertNotIn("reveal", q["state"])  # the answer isn't leaked before the reveal
            self.assertEqual((await host.receive_json_from())["state"]["status"], "question")

            await phone.send_json_to({"action": "answer", "choice": 1})
            self.assertEqual(await phone.receive_json_from(), {"type": "answered", "choice": 1})
            counts = await host.receive_json_from()
            self.assertEqual((counts["type"], counts["answered"]), ("counts", 1))
            reveal = await phone.receive_json_from()  # everyone answered → automatic reveal
            self.assertEqual(reveal["state"]["status"], "reveal")
            self.assertTrue(reveal["you"]["last"]["correct"])
            self.assertEqual((await host.receive_json_from())["state"]["status"], "reveal")

            await host.send_json_to({"action": "next"})  # only one question → finished
            done = await phone.receive_json_from()
            self.assertEqual(done["state"]["status"], "finished")
            self.assertEqual(done["state"]["leaderboard"][0]["nickname"], "alice")
            await phone.disconnect()
            await host.disconnect()

        async_to_sync(scenario)()

    def test_strangers_are_rejected(self):
        async def scenario():
            for role, cookie in (("play", ""), ("play", f"{COOKIE}=forged"), ("host", "")):
                comm = self.communicator(role, cookie)
                ok, code = await comm.connect()
                self.assertFalse(ok)
                self.assertEqual(code, 4403)

            student = await sync_to_async(User.objects.create_user)("stu")
            await sync_to_async(self.client.force_login)(student)
            comm = self.communicator("host", f"sessionid={self.client.cookies['sessionid'].value}")
            ok, code = await comm.connect()
            self.assertFalse(ok)

        async_to_sync(scenario)()

    def test_flooding_closes_the_socket(self):
        player, token = services.join(self.game, "spam")

        async def scenario():
            phone = self.communicator("play", f"{COOKIE}={make_player_cookie(player.pk, token)}")
            await phone.connect()
            await phone.receive_json_from()
            for _ in range(10):
                await phone.send_json_to({"action": "noop"})
            out = await phone.receive_output(timeout=2)
            self.assertEqual(out, {"type": "websocket.close", "code": 4029})

        async_to_sync(scenario)()
