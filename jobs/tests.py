from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from . import services
from .models import Job

User = get_user_model()
BACKEND = "django.contrib.auth.backends.ModelBackend"


def job_data(**overrides):
    data = {
        "title": "Backend Developer", "company": "Acme", "location": "Chennai", "job_type": "full_time",
        "work_mode": "hybrid", "experience": "0–2 years", "salary": "", "skills": "Python, Django",
        "description": "Build APIs.\n\nWork with the team.", "apply_url": "https://acme.example/jobs/1",
        "apply_email": "", "last_date": "",
    }
    data.update(overrides)
    return data


def make_job(user, status=Job.Status.APPROVED, **kw):
    job = Job.objects.create(title=kw.pop("title", "Backend Developer"), company="Acme", location="Chennai",
                             description="Build APIs.", apply_url="https://acme.example", posted_by=user,
                             status=status, **kw)
    if status == Job.Status.APPROVED:
        job.published_at = timezone.now()
        job.save()
    return job


class PostingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("stu", email="stu@example.com")
        self.staff = User.objects.create_user("admin", is_staff=True)

    def test_must_sign_in_to_post(self):
        r = self.client.get(reverse("job_new"))
        self.assertEqual(r.status_code, 302)
        self.assertIn(reverse("login"), r["Location"])

    def test_user_post_waits_for_review(self):
        self.client.force_login(self.user, backend=BACKEND)
        r = self.client.post(reverse("job_new"), job_data())
        job = Job.objects.get()
        self.assertRedirects(r, job.get_absolute_url())
        self.assertEqual((job.status, job.posted_by), (Job.Status.PENDING, self.user))
        self.assertNotContains(self.client.get(reverse("job_list")), "Backend Developer")   # not public yet
        self.assertContains(self.client.get(job.get_absolute_url()), "Waiting for review")   # poster sees it
        self.client.logout()
        self.assertEqual(self.client.get(job.get_absolute_url()).status_code, 404)          # public doesn't

    def test_staff_post_is_live_at_once(self):
        self.client.force_login(self.staff, backend=BACKEND)
        self.client.post(reverse("job_new"), job_data())
        job = Job.objects.get()
        self.assertEqual(job.status, Job.Status.APPROVED)
        self.assertIsNotNone(job.published_at)
        self.client.logout()
        self.assertContains(self.client.get(reverse("job_list")), "Backend Developer")

    def test_validation(self):
        self.client.force_login(self.user, backend=BACKEND)
        r = self.client.post(reverse("job_new"), job_data(apply_url="", apply_email=""))
        self.assertContains(r, "Add an application link or an email address")
        r = self.client.post(reverse("job_new"), job_data(apply_url="javascript:alert(1)"))
        self.assertContains(r, "Enter a valid URL")
        yesterday = (timezone.localdate() - timedelta(days=1)).isoformat()
        r = self.client.post(reverse("job_new"), job_data(last_date=yesterday))
        self.assertContains(r, "already in the past")
        self.assertEqual(Job.objects.count(), 0)

    def test_daily_limit(self):
        self.client.force_login(self.user, backend=BACKEND)
        for _ in range(services.DAILY_POST_LIMIT):
            self.client.post(reverse("job_new"), job_data())
        r = self.client.post(reverse("job_new"), job_data(), follow=True)
        self.assertContains(r, "up to 5 jobs a day")
        self.assertEqual(Job.objects.count(), services.DAILY_POST_LIMIT)


class ManageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("stu")
        self.other = User.objects.create_user("other")
        self.staff = User.objects.create_user("admin", is_staff=True)

    def test_only_poster_or_staff_can_edit_and_delete(self):
        job = make_job(self.user)
        self.client.force_login(self.other, backend=BACKEND)
        self.assertEqual(self.client.get(reverse("job_edit", args=[job.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse("job_delete", args=[job.pk])).status_code, 404)
        self.client.force_login(self.user, backend=BACKEND)
        self.client.post(reverse("job_edit", args=[job.pk]), job_data(title="Senior Backend Developer"))
        job.refresh_from_db()
        self.assertEqual(job.title, "Senior Backend Developer")
        self.assertEqual(job.status, Job.Status.PENDING)            # edits are reviewed again
        self.client.post(reverse("job_delete", args=[job.pk]))
        self.assertFalse(Job.objects.filter(pk=job.pk).exists())

    def test_review_flow(self):
        job = make_job(self.user, status=Job.Status.PENDING)
        self.client.force_login(self.user, backend=BACKEND)
        self.assertEqual(self.client.get(reverse("job_review")).status_code, 302)    # not staff
        self.assertEqual(self.client.post(reverse("job_moderate", args=[job.pk]), {"action": "approve"}).status_code, 302)
        job.refresh_from_db()
        self.assertEqual(job.status, Job.Status.PENDING)            # bounced to the admin login, nothing changed
        self.client.force_login(self.staff, backend=BACKEND)
        self.assertContains(self.client.get(reverse("job_list")), "Review (1)")
        self.assertContains(self.client.get(reverse("job_review")), job.title)
        self.client.post(reverse("job_moderate", args=[job.pk]), {"action": "reject", "note": "Missing salary"})
        job.refresh_from_db()
        self.assertEqual((job.status, job.review_note), (Job.Status.REJECTED, "Missing salary"))
        self.client.force_login(self.user, backend=BACKEND)
        self.assertContains(self.client.get(reverse("job_mine")), "Missing salary")
        self.client.force_login(self.staff, backend=BACKEND)
        self.client.post(reverse("job_moderate", args=[job.pk]), {"action": "approve"})
        job.refresh_from_db()
        self.assertEqual((job.status, job.reviewed_by), (Job.Status.APPROVED, self.staff))


class PublicTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("stu", email="poster@example.com")

    def test_list_filters_and_search(self):
        make_job(self.user, title="Python Developer", skills="Python", job_type="full_time")
        make_job(self.user, title="Data Intern", job_type="internship", work_mode="remote")
        make_job(self.user, title="Hidden", status=Job.Status.PENDING)
        make_job(self.user, title="Expired", last_date=timezone.localdate() - timedelta(days=1))
        page = self.client.get(reverse("job_list")).content.decode()
        self.assertIn("Python Developer", page)
        self.assertIn("Data Intern", page)
        self.assertNotIn("Hidden", page)
        self.assertNotIn("Expired", page)
        self.assertContains(self.client.get(reverse("job_list"), {"type": "internship"}), "Data Intern")
        self.assertNotContains(self.client.get(reverse("job_list"), {"type": "internship"}), "Python Developer")
        self.assertNotContains(self.client.get(reverse("job_list"), {"q": "python", "mode": "remote"}), "Data Intern")

    def test_detail_is_public_safe_and_canonical(self):
        job = make_job(self.user, title="<script>alert(1)</script> Dev")
        r = self.client.get(reverse("job_detail_short", args=[job.pk]))
        self.assertRedirects(r, job.get_absolute_url(), status_code=301)
        page = self.client.get(job.get_absolute_url())
        self.assertContains(page, "&lt;script&gt;")
        self.assertNotContains(page, "<script>alert(1)</script>")
        self.assertNotContains(page, "poster@example.com")            # the poster isn't shown publicly
        self.assertContains(page, 'rel="nofollow noopener noreferrer"')

    def test_expired_job_shows_as_closed(self):
        job = make_job(self.user, last_date=timezone.localdate() - timedelta(days=2))
        page = self.client.get(job.get_absolute_url())
        self.assertContains(page, "Applications for this job closed")
        self.assertNotContains(page, "Apply on company site")

    def test_sitemap_lists_live_jobs_only(self):
        live = make_job(self.user, title="Live Job")
        hidden = make_job(self.user, title="Pending Job", status=Job.Status.PENDING)
        xml = self.client.get(reverse("sitemap")).content.decode()
        self.assertIn(live.get_absolute_url(), xml)
        self.assertNotIn(hidden.get_absolute_url(), xml)
