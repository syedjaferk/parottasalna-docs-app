"""Instant classroom polls: a teacher asks one question, students scan a QR code and vote, results update live."""
import hashlib

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

MIN_OPTIONS = 2
MAX_OPTIONS = 6
OPTION_MAX = 80
# Short codes students can type: no 0/O, 1/I/L lookalikes.
CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
CODE_LENGTH = 5


def parse_options(text):
    """One option per line; blank lines ignored."""
    return [line.strip() for line in (text or "").splitlines() if line.strip()]


class Poll(models.Model):
    code = models.CharField(max_length=CODE_LENGTH, unique=True, editable=False)
    question = models.CharField(max_length=300)
    options = models.TextField(help_text=f"One option per line ({MIN_OPTIONS}–{MAX_OPTIONS}).")
    show_results = models.BooleanField(default=True, help_text="Voters see the live results after voting.")
    is_open = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                   related_name="polls")
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.code} · {self.question}"

    def option_list(self):
        return parse_options(self.options)

    def clean(self):
        options = self.option_list()
        if not MIN_OPTIONS <= len(options) <= MAX_OPTIONS:
            raise ValidationError({"options": f"Give {MIN_OPTIONS}–{MAX_OPTIONS} options, one per line."})
        if any(len(o) > OPTION_MAX for o in options):
            raise ValidationError({"options": f"Keep each option under {OPTION_MAX} characters."})
        if len({o.lower() for o in options}) != len(options):
            raise ValidationError({"options": "Options must be different from each other."})


class Vote(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="votes")
    choice = models.PositiveSmallIntegerField()
    # Hash of the voter's cookie token + poll code: one vote per browser, not linkable across polls.
    voter_hash = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["poll", "voter_hash"], name="uniq_poll_voter")]

    @staticmethod
    def hash_voter(token, code):
        return hashlib.sha256(f"{code}:{token}".encode()).hexdigest()
