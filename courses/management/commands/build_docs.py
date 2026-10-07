from django.core.management.base import BaseCommand

from courses.builder import build_course
from courses.models import Course


class Command(BaseCommand):
    help = "Build Sphinx docs for the given course slugs (default: all active courses)."

    def add_arguments(self, parser):
        parser.add_argument("slugs", nargs="*")

    def handle(self, *args, **options):
        courses = Course.objects.filter(is_active=True)
        if options["slugs"]:
            courses = courses.filter(slug__in=options["slugs"])
        failures = 0
        for course in courses:
            self.stdout.write(f"Building {course.slug} ...")
            if build_course(course.pk):
                self.stdout.write(self.style.SUCCESS("  ok"))
            else:
                failures += 1
                course.refresh_from_db()
                self.stderr.write(self.style.ERROR(f"  failed\n{course.build_log[-2000:]}"))
        if failures:
            raise SystemExit(1)
