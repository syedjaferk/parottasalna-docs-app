from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from courses.models import Course, Enrollment

from .models import Profile

User = get_user_model()


class ProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("kavya", email="kavya@gmail.com", first_name="Kavya")
        self.client.force_login(self.user)
        self.url = reverse("profile")

    def test_sign_in_required(self):
        self.client.logout()
        self.assertEqual(self.client.get(self.url).status_code, 302)

    def test_shows_own_details(self):
        resp = self.client.get(self.url)
        self.assertContains(resp, "kavya@gmail.com")
        self.assertContains(resp, "Only you and the portal admins can see this")

    def test_save_profile(self):
        resp = self.client.post(self.url, {
            "headline": "  Final-year   CSE student ", "stage": "student", "location": "Chennai",
            "bio": "Learning backend.", "interests": ["python", "ai"],
            "github": "https://github.com/kavya", "linkedin": "", "website": "",
        })
        self.assertRedirects(resp, self.url)
        p = Profile.objects.get(user=self.user)
        self.assertEqual(p.headline, "Final-year CSE student")
        self.assertEqual(p.interests, ["python", "ai"])
        page = self.client.get(self.url)
        self.assertContains(page, "AI engineering &amp; agents")
        self.assertContains(page, "https://github.com/kavya")

    def test_rejects_unsafe_links_and_unknown_interests(self):
        resp = self.client.post(self.url, {"github": "javascript:alert(1)", "interests": ["hacking"]})
        self.assertEqual(resp.status_code, 200)
        form = resp.context["form"]
        self.assertIn("github", form.errors)
        self.assertIn("interests", form.errors)
        self.assertFalse(Profile.objects.filter(user=self.user, github__startswith="javascript").exists())


class StreakMovedTests(TestCase):
    """The reading streak lives on the profile now; the dashboard only links to it."""

    def setUp(self):
        course = Course.objects.create(slug="c1", title="C1")
        Enrollment.objects.create(course=course, email="s@gmail.com")
        self.user = User.objects.create_user("s", email="s@gmail.com")
        self.client.force_login(self.user)

    def test_dashboard_links_to_profile_instead_of_the_card(self):
        resp = self.client.get(reverse("home"))
        self.assertNotContains(resp, 'class="streak-card"')
        self.assertContains(resp, "Start a reading streak")
        self.assertContains(resp, reverse("profile"))

    def test_profile_shows_the_streak_card(self):
        self.assertContains(self.client.get(reverse("profile")), 'class="streak-card"')


class HeaderMenuTests(TestCase):
    def test_signed_in_menu(self):
        user = User.objects.create_user("a", email="a@gmail.com")
        self.client.force_login(user)
        resp = self.client.get(reverse("profile"))
        self.assertContains(resp, 'class="acct"')
        self.assertContains(resp, "My profile")
        self.assertContains(resp, "Sign out")
        self.assertNotContains(resp, "Admin panel")         # staff only

    def test_staff_sees_panel(self):
        staff = User.objects.create_user("b", email="b@gmail.com", is_staff=True)
        self.client.force_login(staff)
        self.assertContains(self.client.get(reverse("profile")), "Admin panel")

    def test_guest_menu(self):
        resp = self.client.get(reverse("login"))
        self.assertContains(resp, 'class="acct guest"')
        self.assertContains(resp, "Sign in")
