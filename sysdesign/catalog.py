"""Playground problems come from the database (``Problem``). ``sysdesign/data/<slug>.json`` are only seed files:
load them with ``manage.py load_sysdesign``."""
from .models import Problem


def get_problem(slug):
    """The published problem as a dict, or None for an unknown or unpublished slug."""
    p = Problem.objects.filter(slug=slug, is_published=True).first()
    return p.as_dict() if p else None


def list_problems():
    return [p.as_dict() for p in Problem.objects.filter(is_published=True)]
