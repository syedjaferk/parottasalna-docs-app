"""Score every course against docs/COURSE_STANDARD.md so weak courses are easy to find."""
import re

import yaml
from django.conf import settings
from django.core.management.base import BaseCommand

from courses.models import Course

REQUIRED_KEYS = ("title", "description", "level", "hours", "audience", "outcomes")
SECTIONS = {
    "big idea": re.compile(r"^#{2,3}\s*(the big idea|big idea|what is|overview)", re.I | re.M),
    "common mistakes": re.compile(r"^#{2,3}\s*(common mistakes|pitfalls|gotchas)", re.I | re.M),
    "exercises": re.compile(r"^#{2,3}\s*(hands-on exercises|exercises|practice|try it)", re.I | re.M),
}
DIAGRAM = re.compile(r"```\{raw\} html|!\[[^\]]*\]\(|```mermaid|<svg", re.I)
PLACEHOLDER = re.compile(r"\bTODO:|\bTBD\b|(?i:lorem ipsum|coming soon)")
MIN_WORDS = 600


def session_files(folder):
    sessions = folder / "sessions"
    if sessions.is_dir():
        return sorted(sessions.rglob("*.md"))
    return sorted(p for p in folder.glob("*.md") if p.name not in {"index.md", "setup.md", "README.md"})


def audit(folder, quiz_count=None):
    """Return a list of (severity, message). severity is 'fail' or 'warn'."""
    issues = []
    meta_file = folder / "course.yaml"
    meta = {}
    if not meta_file.is_file():
        issues.append(("fail", "no course.yaml"))
    else:
        try:
            meta = yaml.safe_load(meta_file.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as error:
            issues.append(("fail", f"course.yaml is not valid YAML: {error}"))
    for key in REQUIRED_KEYS:
        if not meta.get(key):
            issues.append(("fail" if key in ("title", "description") else "warn", f"course.yaml is missing '{key}'"))
    if meta.get("description") and len(str(meta["description"])) < 80:
        issues.append(("warn", "description is shorter than 80 characters"))
    index = folder / "index.md"
    if not index.is_file():
        issues.append(("fail", "no index.md"))
    elif "toctree" not in index.read_text(encoding="utf-8"):
        issues.append(("fail", "index.md has no toctree"))
    files = session_files(folder)
    if len(files) < 6:
        issues.append(("warn", f"only {len(files)} session(s); the standard asks for 6 or more"))
    weak = {"too short": [], "no code": [], "no diagram": [], "placeholder": []}
    missing = {name: [] for name in SECTIONS}
    for path in files:
        text = path.read_text(encoding="utf-8")
        if len(text.split()) < MIN_WORDS:
            weak["too short"].append(path.name)
        if "```" not in text:
            weak["no code"].append(path.name)
        if not DIAGRAM.search(text):
            weak["no diagram"].append(path.name)
        if PLACEHOLDER.search(text):
            weak["placeholder"].append(path.name)
        for name, pattern in SECTIONS.items():
            if not pattern.search(text):
                missing[name].append(path.name)
    for label, names in weak.items():
        if names:
            issues.append(("fail" if label == "placeholder" else "warn", f"{len(names)} session(s) {label}: {', '.join(names[:3])}{'…' if len(names) > 3 else ''}"))
    for name, names in missing.items():
        if names:
            issues.append(("warn", f"{len(names)} session(s) lack a '{name}' section"))
    if quiz_count is not None and quiz_count == 0:
        issues.append(("warn", "no published quiz"))
    return issues


class Command(BaseCommand):
    help = "Audit course_content/* against docs/COURSE_STANDARD.md."

    def add_arguments(self, parser):
        parser.add_argument("slugs", nargs="*")
        parser.add_argument("--strict", action="store_true", help="Exit with an error if any course has a failure.")
        parser.add_argument("--verbose-issues", action="store_true", help="List every issue, not just the counts.")

    def handle(self, *args, **options):
        root = settings.COURSES_SRC_ROOT
        folders = [p for p in sorted(root.iterdir()) if p.is_dir() and not p.name.startswith((".", "_"))]
        if options["slugs"]:
            folders = [p for p in folders if p.name in options["slugs"]]
        quizzes = {c.source_dir or c.slug: c.quizzes.filter(is_published=True).count() for c in Course.objects.all()}
        any_fail = False
        for folder in folders:
            issues = audit(folder, quizzes.get(folder.name))
            fails = sum(1 for s, _ in issues if s == "fail")
            warns = len(issues) - fails
            any_fail |= bool(fails)
            status = self.style.ERROR("FAIL") if fails else (self.style.WARNING("WARN") if warns else self.style.SUCCESS("PASS"))
            self.stdout.write(f"{status}  {folder.name:32} {fails} failure(s), {warns} warning(s)")
            if options["verbose_issues"] or fails:
                for severity, message in issues:
                    self.stdout.write(f"        {'x' if severity == 'fail' else '-'} {message}")
        if options["strict"] and any_fail:
            raise SystemExit(1)
