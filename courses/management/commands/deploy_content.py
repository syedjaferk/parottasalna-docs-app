from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from courses.builder import build_course
from courses.models import Course


class Command(BaseCommand):
    help = (
        "Rebuild docs and reload practice files (quizzes + flashcards) for the given courses. "
        "Targets can be course slugs or course_content folder names, so a deploy can pass the "
        "folders that changed in a commit."
    )

    def add_arguments(self, parser):
        parser.add_argument("targets", nargs="*", help="Course slugs or course_content folder names.")
        parser.add_argument("--all", action="store_true", help="Every active course.")
        parser.add_argument("--no-build", action="store_true", help="Skip the Sphinx build.")
        parser.add_argument("--no-practice", action="store_true", help="Skip load_practice.")

    def bootstrap_tables(self):
        """First-run content for tables that start empty: prep catalogue, playground problems, learning paths.

        Only runs while a table is empty, so a later edit in the admin is never overwritten by a deploy.
        (Billing plans are not seeded here: prices are a business decision, add them in the admin.)
        """
        from courses.models import LearningPath
        from prep.models import CatalogProblem
        from sysdesign.models import Problem

        for model, command in ((CatalogProblem, "seed_prep"), (Problem, "load_sysdesign"), (LearningPath, "seed_paths")):
            if model.objects.exists():
                continue
            try:
                call_command(command, stdout=self.stdout, stderr=self.stderr)
            except CommandError as exc:
                self.stderr.write(self.style.ERROR(f"{command} failed: {exc}"))

    def handle(self, *args, **options):
        call_command("sync_courses", update=True, stdout=self.stdout, stderr=self.stderr)   # new folders become courses; blank catalogue fields filled
        self.bootstrap_tables()
        courses = list(Course.objects.filter(is_active=True).order_by("slug"))
        if not options["all"]:
            targets = set(options["targets"])
            if not targets:
                self.stdout.write("No courses to update.")
                return
            known = {c.slug for c in courses} | {c.source_dir or c.slug for c in courses}
            for name in sorted(targets - known):
                self.stdout.write(self.style.WARNING(
                    f"{name}: no active course uses this slug or folder. Create it in the admin "
                    f"(source_dir = {name}), then run the build-docs task."
                ))
            courses = [c for c in courses if c.slug in targets or (c.source_dir or c.slug) in targets]

        failures = 0
        for course in courses:
            if not options["no_build"]:
                self.stdout.write(f"{course.slug}: building docs ...")
                if build_course(course.pk):
                    self.stdout.write(self.style.SUCCESS(f"{course.slug}: docs ok"))
                else:
                    failures += 1
                    course.refresh_from_db()
                    self.stderr.write(self.style.ERROR(
                        f"{course.slug}: docs build failed\n{course.build_log[-2000:]}"
                    ))
            if not options["no_practice"] and (course.src_dir / "practice").is_dir():
                try:
                    call_command("load_practice", course.slug, stdout=self.stdout, stderr=self.stderr)
                except CommandError as exc:
                    failures += 1
                    self.stderr.write(self.style.ERROR(f"{course.slug}: practice not loaded: {exc}"))
            if not options["no_practice"] and (course.src_dir / "assessments").is_dir():
                try:
                    call_command("load_assessments", course.slug, stdout=self.stdout, stderr=self.stderr)
                except CommandError as exc:
                    failures += 1
                    self.stderr.write(self.style.ERROR(f"{course.slug}: assessments not loaded: {exc}"))
        if failures:
            raise CommandError(f"{failures} step(s) failed.")
