from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from courses.builder import build_course
from courses.gitbook import convert_space
from courses.models import Course


class Command(BaseCommand):
    help = (
        "Convert a GitBook space (folder with README.md + SUMMARY.md) into course_content/<slug>/. "
        "With --apply, also create/update the Course and build its docs."
    )

    def add_arguments(self, parser):
        parser.add_argument("source", help="Path to the GitBook space folder")
        parser.add_argument("slug")
        parser.add_argument("--title", required=True)
        parser.add_argument("--description", default="")
        parser.add_argument("--common", action="store_true",
                            help="Make it a common course (open to all students, no enrolment)")
        parser.add_argument("--apply", action="store_true", help="Create/update the course and build it")

    def handle(self, source, slug, title, description, common, apply, **options):
        src = Path(source).expanduser().resolve()
        out = Path(settings.COURSES_SRC_ROOT) / slug
        try:
            report = convert_space(src, out, title=title, description=description)
        except ValueError as exc:
            raise CommandError(str(exc))
        self.stdout.write(f"{slug}: {report['pages']} pages, {report['assets']} images -> {out}")
        for skipped in report["skipped"]:
            self.stdout.write(self.style.WARNING(f"  skipped empty or missing page: {skipped}"))
        if not apply:
            return

        course, created = Course.objects.update_or_create(
            slug=slug, defaults={"title": title, "description": description, "source_dir": slug, "is_common": common}
        )
        self.stdout.write(f"  {'created' if created else 'updated'} course “{course.title}”, building ...")
        if build_course(course.pk):
            self.stdout.write(self.style.SUCCESS("  built ok"))
        else:
            course.refresh_from_db()
            raise CommandError(f"Build failed:\n{course.build_log[-2000:]}")
