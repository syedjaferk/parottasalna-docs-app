"""Builds a course's markdown into static HTML with Sphinx (+ MyST), safely and atomically."""
import contextlib
import os
import shutil
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

from django.conf import settings
from django.db import close_old_connections, connections
from django.utils import timezone

from .models import Course

try:  # POSIX only; on other platforms builds simply aren't locked.
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None

LOG_LIMIT = 20_000


def _conf_py(course: Course) -> str:
    # Generated config: we never execute a conf.py from course content.
    return f"""
project = {course.title!r}
root_doc = "index"
extensions = ["myst_parser"]
source_suffix = {{".md": "markdown", ".rst": "restructuredtext"}}
myst_enable_extensions = ["colon_fence", "deflist", "tasklist"]
html_theme = {settings.SPHINX_THEME!r}
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "**/.git", "**/.*"]
"""


@contextlib.contextmanager
def _course_lock(directory: Path):
    if fcntl is None:
        yield True
        return
    with open(directory / ".build.lock", "w") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            yield False
            return
        try:
            yield True
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def _finish(course_id, status, log):
    fields = {"build_status": status, "build_log": log[-LOG_LIMIT:]}
    if status == Course.BuildStatus.OK:
        fields["last_built_at"] = timezone.now()
    Course.objects.filter(pk=course_id).update(**fields)


def _swap(new_dir: Path, live_dir: Path, old_dir: Path):
    shutil.rmtree(old_dir, ignore_errors=True)
    if live_dir.exists():
        live_dir.rename(old_dir)
    new_dir.rename(live_dir)
    shutil.rmtree(old_dir, ignore_errors=True)


def build_course(course_id: int) -> bool:
    """Build one course. Returns True on success. The previous good build stays live on failure."""
    course = Course.objects.get(pk=course_id)
    out_root = Path(settings.DOCS_BUILD_ROOT) / course.slug
    out_root.mkdir(parents=True, exist_ok=True)

    with _course_lock(out_root) as acquired:
        if not acquired:
            return False  # another build of this course is already running

        Course.objects.filter(pk=course_id).update(build_status=Course.BuildStatus.BUILDING)

        try:
            src = course.src_dir
        except Exception as exc:  # unsafe source_dir
            _finish(course_id, Course.BuildStatus.FAILED, f"Invalid source_dir: {exc}")
            return False
        if not src.is_dir():
            _finish(course_id, Course.BuildStatus.FAILED, f"Source folder not found: {src}")
            return False
        if not (src / "index.md").exists() and not (src / "index.rst").exists():
            _finish(course_id, Course.BuildStatus.FAILED, "The source folder needs an index.md.")
            return False

        new_dir = out_root / "html.new"
        shutil.rmtree(new_dir, ignore_errors=True)

        with tempfile.TemporaryDirectory() as conf_dir:
            (Path(conf_dir) / "conf.py").write_text(_conf_py(course), encoding="utf-8")
            cmd = [
                sys.executable, "-m", "sphinx",
                "-b", "html",
                "-c", conf_dir,
                "-d", str(out_root / "doctrees"),
                "--keep-going",
                str(src), str(new_dir),
            ]
            # Minimal environment: don't leak SECRET_KEY / OAuth secrets to the build process.
            env = {k: os.environ[k] for k in ("PATH", "HOME", "LANG", "LC_ALL", "VIRTUAL_ENV")
                   if k in os.environ}
            try:
                proc = subprocess.run(
                    cmd, capture_output=True, text=True, env=env,
                    timeout=settings.SPHINX_BUILD_TIMEOUT,
                )
            except subprocess.TimeoutExpired:
                shutil.rmtree(new_dir, ignore_errors=True)
                _finish(course_id, Course.BuildStatus.FAILED, "Build timed out.")
                return False
            except OSError as exc:
                _finish(course_id, Course.BuildStatus.FAILED, f"Could not start Sphinx: {exc}")
                return False

        log = (proc.stdout or "") + (proc.stderr or "")
        if proc.returncode != 0 or not (new_dir / "index.html").exists():
            shutil.rmtree(new_dir, ignore_errors=True)
            _finish(course_id, Course.BuildStatus.FAILED, log or "Sphinx failed with no output.")
            return False

        _swap(new_dir, out_root / "html", out_root / "html.old")
        _finish(course_id, Course.BuildStatus.OK, log)
        return True


def build_in_background(course_ids):
    """Fire-and-forget builds from a request. Swap for Celery/RQ if you scale out."""
    ids = list(course_ids)
    Course.objects.filter(pk__in=ids).update(build_status=Course.BuildStatus.BUILDING)

    def run():
        close_old_connections()
        try:
            for course_id in ids:
                try:
                    build_course(course_id)
                except Exception as exc:  # never leave a course stuck on "building"
                    _finish(course_id, Course.BuildStatus.FAILED, f"Unexpected error: {exc}")
        finally:
            connections.close_all()

    threading.Thread(target=run, daemon=True).start()
