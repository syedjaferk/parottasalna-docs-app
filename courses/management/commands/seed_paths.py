"""Create the three flagship learning paths. Safe to re-run: existing paths are left alone."""
from django.core.management.base import BaseCommand

from courses.models import Course, LearningPath, PathStep

PATHS = [
    dict(slug="interview-prep", title="Crack the interview", icon="🎯", sort_order=1,
         tagline="Patterns, system design and a resume that gets past the ATS.",
         audience="Students and engineers preparing for product-company interviews.",
         outcome="Solve new coding problems by pattern, design a system on a whiteboard, and apply with a strong resume.",
         steps=[("course", "dsa-patterns", "", "Learn the 23 patterns behind most coding questions."),
                ("link", "", "Practice tracker", "Log problems and re-solve them on a schedule.", "/prep/practice/"),
                ("course", "system-design", "", "Learn the interview framework, estimation and the building blocks."),
                ("link", "", "System design playground", "Design TinyURL and nine more systems step by step with instant feedback.", "/system-design/"),
                ("link", "", "Resume review", "Get an ATS score before you apply.", "/resume-review/"),
                ("link", "", "Placement quiz", "Check which patterns you recognise.", "/prep/placement/")]),
    dict(slug="backend-cloud", title="Backend and cloud engineer", icon="☁️", sort_order=2,
         tagline="From first Python line to deploying containers on AWS.",
         audience="Beginners and developers who want a backend or DevOps career.",
         outcome="Build an API with a database, ship it in a container and run it in the cloud.",
         steps=[("course", "python-fundamentals", "", "Start here if you are new to programming."),
                ("course", "git-basics-to-intermediate", "", "Work with a team on GitHub."),
                ("course", "database-engineering", "", "SQL and PostgreSQL."),
                ("course", "docker-mastery", "", "Containers in plain words."),
                ("course", "locust", "", "Find out how much traffic your service can take."),
                ("course", "aws-solutions-architect", "", "Design secure, highly available systems on AWS.")]),
    dict(slug="ai-engineer", title="AI engineer", icon="🤖", sort_order=3,
         tagline="Build agents that use tools, memory and your own data.",
         audience="Developers who know basic Python and want to build with LLMs.",
         outcome="Build, evaluate and deploy a working AI agent.",
         steps=[("course", "python-fundamentals", "", "Skip if you already write Python."),
                ("course", "agentic-ai", "", "Prompting, tool calling, RAG and memory."),
                ("course", "ai-agent-bootcamp", "", "Build, secure and ship your own agent.")]),
]


class Command(BaseCommand):
    help = "Create the flagship learning paths."

    def handle(self, *args, **options):
        for original in PATHS:
            spec = dict(original)   # do not modify PATHS: this command may run twice in one process
            steps = spec.pop("steps")
            path, made = LearningPath.objects.get_or_create(slug=spec["slug"], defaults=spec)
            if made:
                for i, step in enumerate(steps, 1):
                    kind, slug, title, note = step[:4]
                    PathStep.objects.create(
                        path=path, order=i, kind=kind, title=title, note=note,
                        course=Course.objects.filter(slug=slug).first() if kind == "course" else None,
                        url=step[4] if len(step) > 4 else "")
            self.stdout.write(f"{path.slug}: {'created' if made else 'exists'}")
