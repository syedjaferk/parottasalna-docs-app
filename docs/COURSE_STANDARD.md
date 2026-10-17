# Course standard

Every course on the portal follows the same pattern, so a learner who liked one course gets the same
quality in the next. `python manage.py check_courses` scores each course against this page.

## A course folder

```text
course_content/<slug>/
  course.yaml        title, description, level, hours, audience, outcomes, access
  index.md           what the course is, how each session works, the table of contents
  setup.md           what to install before session 1 (tool courses)
  sessions/NN-name.md
  diagrams/*.html    one picture per idea (inline SVG, raw-included)
  code/              runnable examples, with real output saved next to them
  practice/          quiz and flashcard source files (loaded through the admin)
```

## course.yaml

| Key | Required | Meaning |
|---|---|---|
| `title` | yes | Short and specific |
| `description` | yes | 2 to 3 sentences: what you learn, who it is for (80+ characters) |
| `level` | yes | `beginner`, `intermediate` or `advanced` |
| `hours` | yes | Honest study time in hours |
| `audience` | yes | One or two sentences: who should take this |
| `outcomes` | yes | List of 3 to 6 things you can do afterwards |
| `access` | no | `free` (default), `pro` or `invite` |
| `common` | no | `true` = anyone can read without signing in |

## A session page

Each `sessions/NN-name.md` has these sections, in this order:

1. **The big idea**: the topic in plain words plus an everyday example.
2. **A picture**: a diagram of the idea (`{raw} html` include).
3. **Worked example**: real code or real numbers, with the output you actually got.
4. **Common mistakes**: what trips beginners up.
5. **Hands-on exercises**: try first, then a collapsible solution.
6. **Practice**: a quiz in the admin for this chapter.

A session is 600 words or more, has at least one code block and one diagram.

## Course level checks

- 6 or more sessions, or a clearly stated reason for fewer.
- An `index.md` with a table of contents and a "how each session works" section.
- At least one published quiz per course (ideally one per session).
- No placeholder text (`TODO`, `Lorem`, `coming soon`).

## Adding a new course

```bash
python manage.py new_course my-course --title "My Course"   # writes the skeleton above
python manage.py sync_courses --update                       # creates or refreshes the Course row
python manage.py build_docs my-course
python manage.py check_courses my-course
```
