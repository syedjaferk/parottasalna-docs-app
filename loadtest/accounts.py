"""Create or remove temporary student accounts for load testing. Run inside the web container:

    docker compose exec -T -e LT_ACTION=create -e LT_COUNT=60 web python manage.py shell < loadtest/accounts.py > sessions.json
    docker compose exec -T -e LT_ACTION=cleanup web python manage.py shell < loadtest/accounts.py

"create" prints a JSON list of session keys (one signed-in student each, enrolled in LT_COURSE).
"cleanup" deletes the accounts, their enrolments and sessions, and everything they created
(progress, quiz attempts, flashcard reviews, notes) through the user foreign keys.
Accounts are recognisable by the reserved .invalid email domain, so real users are never touched.
"""
import json
import os

from django.contrib.auth import BACKEND_SESSION_KEY, HASH_SESSION_KEY, SESSION_KEY, get_user_model
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session

from courses.models import Course, Enrollment

User = get_user_model()
DOMAIN = "loadtest.invalid"
action = os.environ.get("LT_ACTION", "")

if action == "create":
    course = Course.objects.get(slug=os.environ.get("LT_COURSE", "docker-kubernetes"))
    keys = []
    for i in range(int(os.environ.get("LT_COUNT", "50"))):
        email = f"loadtest-{i:03d}@{DOMAIN}"
        user, _ = User.objects.get_or_create(username=f"loadtest-{i:03d}", defaults={"email": email})
        user.set_unusable_password()
        user.save()
        Enrollment.objects.get_or_create(course=course, email=email)
        session = SessionStore()
        session[SESSION_KEY] = str(user.pk)
        session[BACKEND_SESSION_KEY] = "django.contrib.auth.backends.ModelBackend"
        session[HASH_SESSION_KEY] = user.get_session_auth_hash()
        session.create()
        keys.append(session.session_key)
    print(json.dumps({"course": course.slug, "sessions": keys}))

elif action == "cleanup":
    users = User.objects.filter(email__endswith="@" + DOMAIN)
    ids = {str(pk) for pk in users.values_list("pk", flat=True)}
    stale = [s.session_key for s in Session.objects.all() if s.get_decoded().get(SESSION_KEY) in ids]
    sessions = Session.objects.filter(session_key__in=stale).delete()[0]
    enrolments = Enrollment.objects.filter(email__endswith="@" + DOMAIN).delete()[0]
    deleted = users.delete()[1]
    print(json.dumps({"sessions": sessions, "enrolments": enrolments, "deleted": deleted}))

else:
    raise SystemExit("Set LT_ACTION=create or LT_ACTION=cleanup")
