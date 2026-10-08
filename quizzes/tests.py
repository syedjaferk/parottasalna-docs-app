import tempfile
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from courses.models import Course, Enrollment

from .models import Attempt, Question, Quiz

User = get_user_model()
MODEL_BACKEND = "django.contrib.auth.backends.ModelBackend"


class QuizTestCase(TestCase):
    def setUp(self):
        self.course = Course.objects.create(slug="c1", title="C1", build_status="ok")
        Enrollment.objects.create(course=self.course, email="stu@gmail.com")
        self.student = User.objects.create_user("stu", email="stu@gmail.com")
        self.outsider = User.objects.create_user("out", email="out@gmail.com")
        self.staff = User.objects.create_user("adm", email="adm@gmail.com", is_staff=True)
        self.quiz = Quiz.objects.create(course=self.course, title="Lesson 1 quiz", chapter="lesson-1",
                                        is_published=True)
        self.q1 = Question.objects.create(quiz=self.quiz, text="Pick `tuple`", choices="list\n*tuple\ndict", order=1)
        self.q2 = Question.objects.create(quiz=self.quiz, text="Mutable?", choices="*list\ntuple\n*dict",
                                          points=2, order=2)

    def login(self, user):
        self.client.force_login(user, backend=MODEL_BACKEND)

    def take_url(self, quiz=None):
        return f"/courses/c1/quizzes/{(quiz or self.quiz).pk}/"


class QuestionTests(QuizTestCase):
    def test_parsing_and_multiple(self):
        self.assertEqual(self.q1.parsed_choices(), [("list", False), ("tuple", True), ("dict", False)])
        self.assertFalse(self.q1.is_multiple)
        self.assertTrue(self.q2.is_multiple)

    def test_validation_needs_a_correct_choice(self):
        with self.assertRaises(ValidationError):
            Question(quiz=self.quiz, text="x", choices="a\nb").full_clean()
        with self.assertRaises(ValidationError):
            Question(quiz=self.quiz, text="x", choices="*a").full_clean()

    def test_chapter_must_exist_in_course_content(self):
        with tempfile.TemporaryDirectory() as root:
            (Path(root) / "c1").mkdir()
            (Path(root) / "c1" / "lesson-1.md").write_text("# L1")
            with override_settings(COURSES_SRC_ROOT=Path(root)):
                Quiz(course=self.course, title="ok", chapter="lesson-1.md").full_clean()
                with self.assertRaises(ValidationError):
                    Quiz(course=self.course, title="bad", chapter="lesson-9").full_clean()


class TakingTests(QuizTestCase):
    def test_full_marks(self):
        self.login(self.student)
        response = self.client.post(self.take_url(), {f"q{self.q1.pk}": "1", f"q{self.q2.pk}": ["0", "2"]})
        attempt = Attempt.objects.get()
        self.assertRedirects(response, f"/courses/c1/quizzes/attempts/{attempt.pk}/")
        self.assertEqual((attempt.score, attempt.max_score), (3, 3))
        self.assertTrue(attempt.passed)

    def test_partial_multi_select_scores_zero_for_that_question(self):
        self.login(self.student)
        self.client.post(self.take_url(), {f"q{self.q1.pk}": "1", f"q{self.q2.pk}": "0"})
        self.assertEqual(Attempt.objects.get().score, 1)

    def test_unanswered_asks_for_confirmation_first(self):
        self.login(self.student)
        response = self.client.post(self.take_url(), {f"q{self.q1.pk}": "1"})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Attempt.objects.exists())
        self.client.post(self.take_url(), {f"q{self.q1.pk}": "1", "confirm_unanswered": "1"})
        self.assertEqual(Attempt.objects.get().score, 1)

    def test_bogus_choice_values_are_ignored(self):
        self.login(self.student)
        self.client.post(self.take_url(), {f"q{self.q1.pk}": ["9", "x", "1"], f"q{self.q2.pk}": ["0", "2"],
                                           "confirm_unanswered": "1"})
        self.assertEqual(Attempt.objects.get().answers[str(self.q1.pk)], [1])

    def test_answers_are_not_in_the_quiz_page(self):
        self.login(self.student)
        response = self.client.get(self.take_url())
        self.assertContains(response, "tuple")
        self.assertNotContains(response, "*tuple")

    def test_max_attempts_is_enforced(self):
        Quiz.objects.filter(pk=self.quiz.pk).update(max_attempts=1)
        self.login(self.student)
        data = {f"q{self.q1.pk}": "1", f"q{self.q2.pk}": "0"}
        self.client.post(self.take_url(), data)
        response = self.client.post(self.take_url(), data)
        self.assertRedirects(response, "/courses/c1/quizzes/")
        self.assertEqual(Attempt.objects.count(), 1)


class AccessTests(QuizTestCase):
    def test_outsider_and_anonymous_are_blocked(self):
        self.assertEqual(self.client.get(self.take_url()).status_code, 302)
        self.login(self.outsider)
        for url in (self.take_url(), "/courses/c1/quizzes/", "/courses/c1/quizzes.json"):
            self.assertEqual(self.client.get(url).status_code, 404)

    def test_drafts_hidden_from_students_but_staff_can_preview(self):
        draft = Quiz.objects.create(course=self.course, title="Draft")
        Question.objects.create(quiz=draft, text="?", choices="*a\nb")
        self.login(self.student)
        self.assertEqual(self.client.get(self.take_url(draft)).status_code, 404)
        self.login(self.staff)
        self.assertEqual(self.client.get(self.take_url(draft)).status_code, 200)

    def test_students_cannot_see_each_others_results(self):
        attempt = Attempt.objects.create(quiz=self.quiz, user=self.staff, score=1, max_score=3)
        Enrollment.objects.create(course=self.course, email="out@gmail.com")
        self.login(self.outsider)
        self.assertEqual(self.client.get(f"/courses/c1/quizzes/attempts/{attempt.pk}/").status_code, 404)

    def test_scoreboard_is_staff_only(self):
        self.login(self.student)
        self.assertEqual(self.client.get("/courses/c1/quizzes/scores/").status_code, 302)


class FeedAndScoresTests(QuizTestCase):
    def test_feed_lists_published_quizzes_with_best_score(self):
        Attempt.objects.create(quiz=self.quiz, user=self.student, score=1, max_score=3)
        Attempt.objects.create(quiz=self.quiz, user=self.student, score=3, max_score=3)
        self.login(self.student)
        data = self.client.get("/courses/c1/quizzes.json").json()
        self.assertEqual(len(data["quizzes"]), 1)
        item = data["quizzes"][0]
        self.assertEqual(item["chapter"], "lesson-1")
        self.assertEqual(item["questions"], 2)
        self.assertEqual(item["best"]["score"], 3)

    def test_scoreboard_and_csv(self):
        Attempt.objects.create(quiz=self.quiz, user=self.student, score=2, max_score=3)
        self.login(self.staff)
        response = self.client.get("/courses/c1/quizzes/scores/")
        self.assertContains(response, "stu@gmail.com")
        self.assertContains(response, "2/3")
        csv = self.client.get("/courses/c1/quizzes/scores.csv").content.decode()
        self.assertIn("Email,Name,Lesson 1 quiz,Quizzes taken,Total,Out of", csv)
        self.assertIn("stu@gmail.com,,2/3,1,2,3", csv)

    def test_scoreboard_handles_users_without_email(self):
        nomail = User.objects.create_user("teacher", is_staff=True)
        Attempt.objects.create(quiz=self.quiz, user=nomail, score=1, max_score=3)
        self.login(self.staff)
        self.assertIn("teacher,,1/3", self.client.get("/courses/c1/quizzes/scores.csv").content.decode())


class CommonCourseQuizTests(QuizTestCase):
    def setUp(self):
        super().setUp()
        self.common = Course.objects.create(slug="open", title="Open", is_common=True, build_status="ok")
        self.open_quiz = Quiz.objects.create(course=self.common, title="Open quiz", is_published=True)
        Question.objects.create(quiz=self.open_quiz, text="?", choices="*a\nb")

    def test_not_enrolled_readers_get_no_quizzes(self):
        self.assertEqual(self.client.get("/courses/open/quizzes.json").json()["quizzes"], [])
        self.login(self.student)  # enrolled in c1 only
        self.assertEqual(self.client.get("/courses/open/quizzes.json").json()["quizzes"], [])
        self.assertEqual(self.client.get(f"/courses/open/quizzes/{self.open_quiz.pk}/").status_code, 404)
        self.client.post(f"/courses/open/quizzes/{self.open_quiz.pk}/", {"confirm_unanswered": "1"})
        self.assertFalse(Attempt.objects.filter(quiz=self.open_quiz).exists())

    def test_enrolled_students_and_staff_can_take_common_quizzes(self):
        Enrollment.objects.create(course=self.common, email="stu@gmail.com")
        self.login(self.student)
        self.assertEqual(len(self.client.get("/courses/open/quizzes.json").json()["quizzes"]), 1)
        self.login(self.staff)
        self.assertEqual(self.client.get(f"/courses/open/quizzes/{self.open_quiz.pk}/").status_code, 200)


class QuizSecurityTests(QuizTestCase):
    def test_scoreboard_csv_neutralises_formulas_in_student_names(self):
        self.student.first_name = '=HYPERLINK("http://evil.example","click")'
        self.student.save()
        Attempt.objects.create(quiz=self.quiz, user=self.student, score=1, max_score=3)
        self.login(self.staff)
        csv = self.client.get("/courses/c1/quizzes/scores.csv").content.decode()
        self.assertIn("'=HYPERLINK", csv)
        self.assertNotIn(',=HYPERLINK', csv)

    def test_quiz_submission_requires_csrf_token(self):
        client = self.client_class(enforce_csrf_checks=True)
        client.force_login(self.student, backend=MODEL_BACKEND)
        response = client.post(self.take_url(), {f"q{self.q1.pk}": "1", "confirm_unanswered": "1"})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Attempt.objects.exists())

    def test_attempt_ids_cannot_be_guessed_across_users(self):
        other = User.objects.create_user("o2", email="o2@gmail.com")
        Enrollment.objects.create(course=self.course, email="o2@gmail.com")
        attempt = Attempt.objects.create(quiz=self.quiz, user=self.student, score=3, max_score=3)
        self.login(other)
        self.assertEqual(self.client.get(f"/courses/c1/quizzes/attempts/{attempt.pk}/").status_code, 404)


class FlashcardTests(QuizTestCase):
    def setUp(self):
        super().setUp()
        from .models import Deck, Flashcard

        self.deck = Deck.objects.create(course=self.course, title="Terms", chapter="lesson-1", is_published=True)
        self.c1 = Flashcard.objects.create(deck=self.deck, front="What is an **LLM**?", back="A large language model", order=1)
        self.c2 = Flashcard.objects.create(deck=self.deck, front="Low temperature?", back="Predictable answers", order=2)
        self.study = f"/courses/c1/flashcards/{self.deck.pk}/"
        self.review = f"/courses/c1/flashcards/{self.deck.pk}/review/"

    def post_review(self, card_id, known="true", client=None):
        client = client or self.client
        token = client.get(self.study).cookies.get("csrftoken")
        return client.post(self.review, {"card": str(card_id), "known": known},
                           HTTP_X_CSRFTOKEN=token.value if token else "")

    def test_bulk_card_parsing(self):
        from .services import parse_bulk_cards

        cards, bad = parse_bulk_cards("A :: B\n\nno separator\nC::D :: E\n :: missing front")
        self.assertEqual(cards, [("A", "B"), ("C", "D :: E")])
        self.assertEqual(bad, [3, 5])

    def test_study_page_renders_markdown_and_known_state(self):
        from .models import CardReview

        CardReview.objects.create(user=self.student, card=self.c1, known=True)
        self.login(self.student)
        response = self.client.get(self.study)
        self.assertEqual(response.status_code, 200)
        data = response.context["data"]
        self.assertEqual(data["cards"][0]["front"].strip(), "<p>What is an <strong>LLM</strong>?</p>")
        self.assertEqual([c["known"] for c in data["cards"]], [True, False])

    def test_access_rules(self):
        self.assertEqual(self.client.get(self.study).status_code, 302)          # anonymous → sign in
        self.login(self.outsider)
        self.assertEqual(self.client.get(self.study).status_code, 404)          # not enrolled
        from .models import Deck
        Deck.objects.filter(pk=self.deck.pk).update(is_published=False)
        self.login(self.student)
        self.assertEqual(self.client.get(self.study).status_code, 404)          # draft hidden
        self.login(self.staff)
        self.assertEqual(self.client.get(self.study).status_code, 200)          # staff preview

    def test_review_saves_and_counts(self):
        from .models import CardReview

        client = self.client_class(enforce_csrf_checks=True)
        client.force_login(self.student, backend=MODEL_BACKEND)
        r = self.post_review(self.c1.pk, "true", client)
        self.assertEqual(r.json(), {"card": self.c1.pk, "known": True, "known_total": 1, "total": 2})
        self.post_review(self.c1.pk, "false", client)
        review = CardReview.objects.get(user=self.student, card=self.c1)
        self.assertEqual((review.known, review.times_seen), (False, 2))

    def test_review_rejects_bad_input_and_other_decks(self):
        from .models import Deck, Flashcard

        other = Deck.objects.create(course=self.course, title="Other", is_published=True)
        foreign = Flashcard.objects.create(deck=other, front="x", back="y")
        self.login(self.student)
        self.assertEqual(self.post_review(foreign.pk).status_code, 400)
        self.assertEqual(self.post_review("abc").status_code, 400)
        self.assertEqual(self.post_review(self.c1.pk, "maybe").status_code, 400)
        self.assertEqual(self.client.get(self.review).status_code, 405)

    def test_review_requires_csrf_auth_and_enrolment(self):
        anon = self.client_class()
        self.assertEqual(anon.post(self.review, {"card": self.c1.pk, "known": "true"}).status_code, 401)
        strict = self.client_class(enforce_csrf_checks=True)
        strict.force_login(self.student, backend=MODEL_BACKEND)
        self.assertEqual(strict.post(self.review, {"card": self.c1.pk, "known": "true"}).status_code, 403)
        self.login(self.outsider)
        self.assertEqual(self.client.post(self.review, {"card": self.c1.pk, "known": "true"}).status_code, 404)

    def test_common_course_decks_hidden_from_non_enrolled(self):
        from .models import Deck, Flashcard

        common = Course.objects.create(slug="open", title="Open", is_common=True, build_status="ok")
        deck = Deck.objects.create(course=common, title="Open deck", is_published=True)
        Flashcard.objects.create(deck=deck, front="a", back="b")
        self.assertEqual(self.client.get("/courses/open/quizzes.json").json()["decks"], [])
        self.login(self.student)
        self.assertEqual(self.client.get(f"/courses/open/flashcards/{deck.pk}/").status_code, 404)

    def test_feed_practice_page_and_scoreboard(self):
        from .models import CardReview

        CardReview.objects.create(user=self.student, card=self.c1, known=True)
        self.login(self.student)
        deck = self.client.get("/courses/c1/quizzes.json").json()["decks"][0]
        self.assertEqual((deck["chapter"], deck["cards"], deck["known"]), ("lesson-1", 2, 1))
        self.assertContains(self.client.get("/courses/c1/quizzes/"), "1 of 2 known")
        self.login(self.staff)
        self.assertContains(self.client.get("/courses/c1/quizzes/scores/"), "1/2")
        csv = self.client.get("/courses/c1/quizzes/scores.csv").content.decode()
        self.assertIn("Flashcards: Terms (known of 2)", csv)

    def test_deck_chapter_must_exist(self):
        from .models import Deck

        with tempfile.TemporaryDirectory() as root:
            (Path(root) / "c1").mkdir()
            (Path(root) / "c1" / "lesson-1.md").write_text("# L1")
            with override_settings(COURSES_SRC_ROOT=Path(root)):
                Deck(course=self.course, title="ok", chapter="lesson-1").full_clean()
                with self.assertRaises(ValidationError):
                    Deck(course=self.course, title="bad", chapter="nope").full_clean()
