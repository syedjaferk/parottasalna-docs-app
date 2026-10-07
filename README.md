# Course Portal

Django (SSR) + Google sign-in (django-allauth) + per-course Sphinx docs built from Markdown (MyST),
served only to users enrolled in that course.

## How it works

- **Login:** Google only. No passwords, no local signup.
- **Allow-list:** an admin adds Gmail addresses to a course (bulk textarea or inline table).
  A brand-new Google account is rejected unless its verified email is on some course.
- **Docs:** `course_content/<slug>/*.md` -> `sphinx-build` -> `docs_build/<slug>/html/`.
  Every request to `/courses/<slug>/docs/...` is authorised by Django first.
- **Staff** (`is_staff`) can open every course; everyone else only their enrolled ones.

## Local setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # set SECRET_KEY, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

python manage.py makemigrations courses
python manage.py migrate
python manage.py createsuperuser   # use YOUR GOOGLE EMAIL so Google login attaches to it
python manage.py runserver
```

## Docker Compose

```bash
cp .env.example .env               # set SECRET_KEY, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, POSTGRES_PASSWORD
docker compose up -d --build       # Postgres + Django (gunicorn) + Nginx on http://localhost:8000
docker compose exec web python manage.py createsuperuser
```

- `./course_content` is mounted into the app, so new session `.md` files appear without a rebuild of
  the image; then click **Rebuild documentation** in the admin (or `docker compose exec web python manage.py build_docs`).
- All courses are rebuilt whenever the `web` container starts (`BUILD_DOCS_ON_START=false` to skip).
- Built docs live in the `docs_build` volume and are streamed by Nginx via `X-Accel-Redirect`.
- With `DEBUG=false` and no HTTPS in front, also set `SECURE_SSL_REDIRECT=false` and `SECURE_COOKIES=false`.
  In production put a TLS terminator in front (it should send `X-Forwarded-Proto: https`).

### Branding & SEO

Brand name, description, topics and social links live in `courses/branding.py` and are used by
every portal page (meta tags, Open Graph, JSON-LD, footer) and by the generated Sphinx docs.
Images are in `static/brand/`. Only the landing page `/` is indexable; `/robots.txt` and
`/sitemap.xml` are generated.

### Google OAuth client

Google Cloud Console -> APIs & Services -> Credentials -> *Create OAuth client ID* -> Web application.
Authorised redirect URIs:

- `http://localhost:8000/accounts/google/login/callback/`
- `https://YOUR-DOMAIN/accounts/google/login/callback/`

### First course

1. Go to `/admin/`, add a Course with slug `python-101` (sample content is in `course_content/python-101`).
2. Paste Gmail addresses into **Add users (bulk)** and save.
3. Select the course in the list, choose action **Rebuild documentation**
   (or run `python manage.py build_docs python-101`).
4. Sign in with an enrolled Google account at `/` and open the docs.

Run the tests with `python manage.py test`.

## Production notes

- Set `DEBUG=false`, a real `SECRET_KEY`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `USE_X_ACCEL_REDIRECT=true`.
- `python manage.py collectstatic`, run `gunicorn config.wsgi`, put Nginx in front (`deploy/nginx.conf`).
  The `/protected-docs/` location is `internal`, so files are only reachable through Django's check.
- Use PostgreSQL via `DATABASE_URL` if you expect concurrent admins.
- The admin "Rebuild" button uses a background thread (fine for one server). To rebuild on every
  Git push instead, call `python manage.py build_docs` from a hook or cron job, or move to Celery/RQ.

## Security design

- Course access is checked on **every** docs request, not just at login. Non-enrolled users get 404.
- Path traversal and dotfiles are blocked; the build directory is never exposed as a static root.
- Sphinx runs with a generated `conf.py` and a stripped environment, so course content can't run code or read secrets.
- Emails are compared case-insensitively. Only Google-verified emails are trusted.
# parottasalna-docs-app
