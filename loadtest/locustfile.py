"""Load test for learn.parottasalna.com.

    locust -f loadtest/locustfile.py --host https://learn.parottasalna.com --headless \
        --csv out/run --html out/report.html            # stepped ramp, stops itself (see StepRamp)

Two kinds of users:
  PublicVisitor   home page, blog, free (common) course docs, sitemap: no login.
  EnrolledStudent docs of an enrolled course and everything the docs page calls (progress, quizzes,
                  notes), plus the occasional write: mark complete, add/delete a note, submit a quiz.
                  Needs LT_SESSIONS=<file> from loadtest/accounts.py (temporary test accounts).

Writes are rare on purpose: nginx limits POSTs to 5 per second per client IP, and every simulated
user here shares one IP, so 429 "rate limited" answers are counted separately, not as failures.
"""
import itertools
import json
import os
import random
import re
import threading

from locust import HttpUser, LoadTestShape, between, events, task

COMMON_COURSES = ["git", "docker-mastery", "database-engineering", "locust"]
STUDENT_PAGES = [
    "index", "sessions/01-why-docker", "sessions/02-linux-prerequisites",
    "sessions/03-permissions-bind-mounts-architecture", "sessions/04-docker-commands",
    "sessions/05-ip-addressing-subnets", "sessions/06-docker-networking", "sessions/07-dockerfile",
]

_sessions = []
_session_cycle = None
_lock = threading.Lock()
_blog_posts = []


@events.init.add_listener
def _load(environment, **_):
    global _sessions, _session_cycle
    path = os.environ.get("LT_SESSIONS")
    if path:
        with open(path) as handle:
            data = json.load(handle)
        _sessions = data["sessions"]
        _session_cycle = itertools.cycle(_sessions)


def _next_session():
    with _lock:
        return next(_session_cycle)


def _ok(response, allow=(200,)):
    """Mark 429 (our own nginx rate limit) as success-with-a-label instead of a failure."""
    if response.status_code == 429:
        response.success()
        response.request_meta["name"] = response.request_meta["name"] + " [429 rate-limited]"
    elif response.status_code not in allow:
        response.failure(f"HTTP {response.status_code}")
    else:
        response.success()


class PublicVisitor(HttpUser):
    weight = 3
    wait_time = between(1, 4)

    def on_start(self):
        if not _blog_posts:
            with self.client.get("/sitemap.xml", name="/sitemap.xml", catch_response=True) as r:
                _ok(r)
                _blog_posts.extend(re.findall(r"<loc>[^<]*?(/blog/[^<]+/)</loc>", r.text)[:200])

    @task(3)
    def home(self):
        with self.client.get("/", name="/ (home)", catch_response=True) as r:
            _ok(r)

    @task(2)
    def blog_index(self):
        with self.client.get("/blog/", name="/blog/", catch_response=True) as r:
            _ok(r)

    @task(4)
    def blog_post(self):
        if _blog_posts:
            with self.client.get(random.choice(_blog_posts), name="/blog/<post>/", catch_response=True) as r:
                _ok(r)

    @task(5)
    def common_docs(self):
        course = random.choice(COMMON_COURSES)
        with self.client.get(f"/courses/{course}/docs/", name="/courses/<common>/docs/", catch_response=True) as r:
            _ok(r)
        # What the docs page itself calls (nothing stored for readers who aren't enrolled).
        with self.client.get(f"/courses/{course}/progress.json", name="/courses/<common>/progress.json",
                             catch_response=True) as r:
            _ok(r)

    @task(1)
    def docs_asset(self):
        course = random.choice(COMMON_COURSES)
        with self.client.get(f"/courses/{course}/docs/_static/portal.css", name="/courses/<common>/docs/_static/*",
                             catch_response=True) as r:
            _ok(r)


class EnrolledStudent(HttpUser):
    weight = 1
    wait_time = between(1, 4)

    def on_start(self):
        if not _sessions:
            raise RuntimeError("Set LT_SESSIONS to the file made by loadtest/accounts.py")
        self.client.cookies.set("sessionid", _next_session())
        self.course = "docker-kubernetes"
        self.quiz_urls = []
        # Like a real page load: the first JSON call also sets the csrftoken cookie writes need.
        with self.client.get(f"/courses/{self.course}/progress.json", name="progress.json", catch_response=True) as r:
            _ok(r)

    def _csrf_headers(self):
        token = self.client.cookies.get("csrftoken")
        return {"X-CSRFToken": token or "", "Referer": self.host + "/"}

    @task(6)
    def read_chapter(self):
        page = random.choice(STUDENT_PAGES)
        with self.client.get(f"/courses/{self.course}/docs/{page}.html", name="/courses/<enrolled>/docs/<page>",
                             catch_response=True) as r:
            _ok(r)
        # The three JSON calls every docs page makes.
        with self.client.get(f"/courses/{self.course}/progress.json", name="progress.json", catch_response=True) as r:
            _ok(r)
        with self.client.get(f"/courses/{self.course}/quizzes.json", name="quizzes.json", catch_response=True) as r:
            _ok(r)
            if r.ok and not self.quiz_urls:
                self.quiz_urls = [q["url"] for q in r.json().get("quizzes", [])]
        with self.client.get(f"/courses/{self.course}/notes.json?page={page}", name="notes.json",
                             catch_response=True) as r:
            _ok(r)

    @task(2)
    def dashboard(self):
        with self.client.get("/", name="/ (dashboard, signed in)", catch_response=True) as r:
            _ok(r)

    @task(1)
    def my_notes(self):
        with self.client.get(f"/courses/{self.course}/notes/", name="/courses/<enrolled>/notes/",
                             catch_response=True) as r:
            _ok(r)

    @task(1)
    def mark_complete(self):
        page = random.choice(STUDENT_PAGES[1:])
        with self.client.post(f"/courses/{self.course}/progress/", data={"page": page, "completed": "true"},
                              headers=self._csrf_headers(), name="POST progress", catch_response=True) as r:
            _ok(r)

    @task(1)
    def add_and_delete_note(self):
        page = random.choice(STUDENT_PAGES)
        with self.client.post(f"/courses/{self.course}/notes/new/", headers=self._csrf_headers(),
                              data={"page": page, "anchor": "", "quote": "", "body": "load test note"},
                              name="POST note", catch_response=True) as r:
            _ok(r, allow=(201,))
            note_id = r.json().get("id") if r.status_code == 201 else None
        if note_id:
            with self.client.post(f"/courses/{self.course}/notes/{note_id}/delete/", headers=self._csrf_headers(),
                                  name="POST note delete", catch_response=True) as r:
                _ok(r)

    @task(1)
    def take_quiz(self):
        if not self.quiz_urls:
            return
        url = random.choice(self.quiz_urls)
        with self.client.get(url, name="/quizzes/<id>/ (GET)", catch_response=True) as r:
            _ok(r)
        with self.client.post(url, data={"confirm_unanswered": "1"}, headers=self._csrf_headers(),
                              name="/quizzes/<id>/ (submit)", catch_response=True, allow_redirects=False) as r:
            _ok(r, allow=(302, 303))


class StepRamp(LoadTestShape):
    """Add users in steps of STEP_SECONDS; stop early once the site is clearly struggling.

    Stop rule (checked from the second step on): 95th percentile over 3 s, or over 5 % failures.
    """
    STEPS = [int(n) for n in os.environ.get("LT_STEPS", "10,25,50,75,100,150,200,300").split(",")]
    STEP_SECONDS = int(os.environ.get("LT_STEP_SECONDS", "60"))
    P95_LIMIT_MS = 3000
    FAIL_LIMIT = 0.05

    def tick(self):
        elapsed = self.get_run_time()
        step = int(elapsed // self.STEP_SECONDS)
        if step >= len(self.STEPS):
            return None
        if step >= 1 and elapsed % self.STEP_SECONDS < 1:
            total = self.runner.stats.total
            p95 = total.get_current_response_time_percentile(0.95) or 0
            if p95 > self.P95_LIMIT_MS or total.fail_ratio > self.FAIL_LIMIT:
                print(f"[StepRamp] stopping at {self.STEPS[step - 1]} users: p95={p95} ms, "
                      f"failures={total.fail_ratio:.1%}")
                return None
        users = self.STEPS[step]
        return users, max(2, users // 10)
