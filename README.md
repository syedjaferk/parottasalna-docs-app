# Course Portal

Django (SSR) + Google sign-in (django-allauth) + per-course Sphinx docs built from Markdown (MyST),
served only to users enrolled in that course.

## How it works

- **Login:** Google only. No passwords, no local signup.
- **Allow-list:** an admin adds Gmail addresses to a course (bulk textarea or inline table).
  A brand-new Google account is rejected unless its verified email is on some course.
- **Docs:** `course_content/<slug>/*.md` -> `sphinx-build` -> `docs_build/<slug>/html/`.
  Every request to `/courses/<slug>/docs/...` is authorised by Django first.
- **Common courses** (tick *Common course* in the admin) are public: anyone can read their docs without signing in
  (progress tracking and quizzes are only for students enrolled in that course). They are listed on the landing page and indexed by search engines;
  other courses are only for enrolled students. The dashboard shows the two groups separately.
- **Staff** (`is_staff`) can open every course; everyone else only their enrolled ones plus common ones.

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

### Blog

Public blog at `/blog/` (search, categories, tags, RSS at `/blog/feed.xml`), built from the Obsidian
vault (`second-brain`). Import or refresh posts with:

```bash
python manage.py import_blog /path/to/second-brain          # or set BLOG_SRC_ROOT
python manage.py import_blog --prune                         # also delete posts removed from the vault
```

- Only notes with post frontmatter (`layout: post`, `title`, `date`) are imported; `Templates/` is skipped.
- `[[wikilinks]]` become links between posts; the `## Related Posts` list becomes related-post cards.
- HTML is sanitised (nh3): no scripts or event handlers; only YouTube embeds, on youtube-nocookie.com.
- Local images work like in Obsidian: `<img src="../attachments/x.png">`, `![](pic.png)` or `![[pic.png]]`.
  Only files a published post uses are served (at `/blog/media/...`); the rest of the vault stays private.
- **Independent of WordPress.** The vault now holds everything (images and PDFs in `attachments/`,
  repaired code, internal links). `localize_blog_vault` did that once and is safe to re-run:
  `python manage.py localize_blog_vault /path/to/vault --dry-run` (needs WordPress online).
- While `BLOG_WORDPRESS_URL` is set, each post names its WordPress original as canonical. To make the app
  the only home, set `BLOG_WORDPRESS_URL=` (empty): imports never contact WordPress and posts are canonical
  here. (`import_blog --no-wordpress` skips WordPress for a single run.)
- Docker: the vault folder (`BLOG_SOURCE_DIR`, default `../second-brain`) is mounted read-only; run
  `docker compose exec web python manage.py import_blog` after pulling new posts.
- Hide a post without deleting it: **Admin → Blog → Posts → untick "Is published"**.

### Progress tracking

Every chapter page ends with a **Mark as complete** button, but only for students enrolled in that
course (and staff). Readers who aren't enrolled, e.g. anyone browsing a common course, get no progress
UI and no quizzes, and nothing is stored for them; enrol them on the course to turn it on. Completed chapters get a
✓ in the docs sidebar and a "Completed" badge, the sidebar shows "X of Y chapters", and dashboard
cards show a progress bar and a 🏆 badge when the whole course is done. Records are under
**Admin → Page progress**.

### Importing a GitBook space

A GitBook export (folder with `README.md`, `SUMMARY.md`, `.gitbook/assets/`) can be turned into a course:

```bash
python manage.py import_gitbook path/to/space my-course --title "My Course" --description "..." --common --apply
```

It writes `course_content/my-course/` (SUMMARY.md becomes the sidebar, images move to `_assets/`,
YouTube embeds become players, "Solution" tabs become collapsible blocks) and, with `--apply`,
creates/updates the course and builds it. Re-run it after editing on GitBook; it replaces the folder.

### Quizzes

Add a quiz in **Admin → Quizzes**: pick the course, set **Chapter** to the docs page name
(`lesson-1` for `lesson-1.md`), add questions, tick **Is published**.

- Choices go one per line; start the correct one(s) with `*`. Several `*` = "select all that apply".
- Question text supports Markdown, including code blocks.
- That chapter's docs page shows a "Check your understanding" card automatically (no docs rebuild needed).
- Every attempt is stored. Students see their best score; staff see a per-course scoreboard at
  `/courses/<slug>/quizzes/scores/` (CSV download) and every attempt under **Admin → Attempts**.

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

### Quizzes and flashcards from files

Instead of typing them into the admin, keep them in `course_content/<course>/practice/*.yaml`
(one file per chapter; see `course_content/docker-kubernetes/practice/` and the format at the top
of `quizzes/management/commands/load_practice.py`), then load them:

```bash
python manage.py load_practice docker-kubernetes            # publish; safe to re-run
python manage.py load_practice docker-kubernetes --draft    # staff-only preview
python manage.py load_practice docker-kubernetes --prune    # also delete ones not in the files
```

Reloading updates questions and cards in place, so students' scores and card progress are kept.

Run the tests with `python manage.py test`.

## Production notes

- Set `DEBUG=false`, a real `SECRET_KEY`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `USE_X_ACCEL_REDIRECT=true`.
- `python manage.py collectstatic`, run `gunicorn config.wsgi`, put Nginx in front (`deploy/nginx.conf`).
  The `/protected-docs/` location is `internal`, so files are only reachable through Django's check.
- Use PostgreSQL via `DATABASE_URL` if you expect concurrent admins.
- The admin "Rebuild" button uses a background thread (fine for one server). To rebuild on every
  Git push instead, call `python manage.py build_docs` from a hook or cron job, or move to Celery/RQ.

## Security design

- Course access is checked on **every** docs request, not just at login. Non-enrolled users get 404;
  signed-out visitors are sent to sign-in (except for public common courses).
- Path traversal and dotfiles are blocked; the build directory is never exposed as a static root.
- Sphinx runs with a generated `conf.py` and a stripped environment, so course content can't run code or read secrets.
- Emails are compared case-insensitively. Only Google-verified emails are trusted.
- **API (progress, quizzes):** every endpoint re-checks access server-side; progress and quiz scores are
  only stored for students enrolled in that course (`can_track`). Writes are POST-only with CSRF, reads
  are GET/HEAD-only, signed-out API calls get `401` JSON, unknown and forbidden courses both return `404`,
  input is validated against server-side lists, and per-user JSON is sent with `Cache-Control: private, no-store`.
- Quiz results are visible only to their owner and staff; `max_attempts` is enforced under a row lock.
- CSV exports neutralise cells starting with `= + - @` (formula injection from user-controlled names).
- Nginx rate-limits POSTs per IP (5/s, burst 20) in `deploy/docker/nginx.conf` and `deploy/nginx.conf`.
# parottasalna-docs-app
