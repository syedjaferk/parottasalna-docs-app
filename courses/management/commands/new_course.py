"""Write a new course skeleton that already follows docs/COURSE_STANDARD.md."""
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

COURSE_YAML = """title: {title}
description: One or two sentences on what the learner can do after this course and who it is for. Make it at least eighty characters long.
level: beginner
hours: 10
audience: Who should take this course, in one or two sentences.
outcomes: |
  First thing you can do afterwards
  Second thing you can do afterwards
  Third thing you can do afterwards
access: free
common: true
"""

INDEX = """# {title}

One paragraph: what this course teaches and why it matters.

## How each session works

1. **The big idea**: the topic in plain words, with an everyday example.
2. **A picture**: a diagram of the idea.
3. **Worked example**: real code or numbers, with the output you actually got.
4. **Common mistakes**: what trips beginners up.
5. **Hands-on exercises**: try first, then reveal the solution.
6. **Practice**: a quiz for the chapter.

```{{toctree}}
:maxdepth: 1
:caption: Sessions

sessions/01-first-session
```
"""

SESSION = """# Session 1 · Title

## The big idea

Explain the idea in plain words, then give an everyday example.

## A picture

```{{raw}} html
:file: ../diagrams/first-idea.html
```

## Worked example

```text
Real code or numbers here, plus the output you actually got.
```

## Common mistakes

- Mistake one, and how to avoid it.

## Hands-on exercises

**Exercise 1.** Describe the task.

<details class="solution"><summary>Solution</summary>

The worked solution.

</details>
"""


class Command(BaseCommand):
    help = "Create course_content/<slug>/ from the course standard."

    def add_arguments(self, parser):
        parser.add_argument("slug")
        parser.add_argument("--title", default="")

    def handle(self, *args, **options):
        slug = options["slug"]
        folder = settings.COURSES_SRC_ROOT / slug
        if folder.exists():
            raise CommandError(f"{folder} already exists.")
        title = options["title"] or slug.replace("-", " ").title()
        (folder / "sessions").mkdir(parents=True)
        (folder / "diagrams").mkdir()
        (folder / "course.yaml").write_text(COURSE_YAML.format(title=title), encoding="utf-8")
        (folder / "index.md").write_text(INDEX.format(title=title), encoding="utf-8")
        (folder / "sessions" / "01-first-session.md").write_text(SESSION, encoding="utf-8")
        self.stdout.write(self.style.SUCCESS(f"Created {folder}. Next: sync_courses --update, build_docs {slug}, check_courses {slug}."))
