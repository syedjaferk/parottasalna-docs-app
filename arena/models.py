"""Live quiz games (Kahoot/Menti style): a host runs a quiz on a big screen, players join with a PIN."""
import hashlib

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

NICKNAME_MAX = 20
MAX_PLAYERS = 500


class LiveQuiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=300, blank=True, help_text="Shown in the lobby.")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                   related_name="live_quizzes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name_plural = "live quizzes"

    def __str__(self):
        return self.title


class LiveQuestion(models.Model):
    quiz = models.ForeignKey(LiveQuiz, on_delete=models.CASCADE, related_name="questions")
    text = models.CharField(max_length=300)
    choices = models.TextField(
        help_text="2–4 choices, one per line. Start the correct one(s) with <code>*</code>.",
    )
    time_limit = models.PositiveSmallIntegerField(default=20, help_text="Seconds to answer (5–120).")
    points = models.PositiveSmallIntegerField(
        default=1000, help_text="Points for an instant correct answer; answering at the last second gives half.",
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.text[:80]

    def parsed_choices(self):
        """[(text, is_correct), ...]"""
        result = []
        for line in self.choices.splitlines():
            line = line.strip()
            if line:
                correct = line.startswith("*")
                result.append((line[1:].strip() if correct else line, correct))
        return result

    def correct_indexes(self):
        return {i for i, (_, correct) in enumerate(self.parsed_choices()) if correct}

    def clean(self):
        super().clean()
        choices = self.parsed_choices()
        if not 2 <= len(choices) <= 4:
            raise ValidationError({"choices": "Give 2 to 4 choices, one per line."})
        if not any(correct for _, correct in choices):
            raise ValidationError({"choices": "Mark at least one correct choice with *."})
        if any(len(text) > 120 for text, _ in choices):
            raise ValidationError({"choices": "Keep each choice under 120 characters (it must fit on a phone)."})
        if not 5 <= self.time_limit <= 120:
            raise ValidationError({"time_limit": "Use 5 to 120 seconds."})


class LiveGame(models.Model):
    class Status(models.TextChoices):
        LOBBY = "lobby", "Waiting for players"
        QUESTION = "question", "Question open"
        REVEAL = "reveal", "Showing the answer"
        LEADERBOARD = "leaderboard", "Leaderboard"
        FINISHED = "finished", "Finished"

    quiz = models.ForeignKey(LiveQuiz, on_delete=models.CASCADE, related_name="games")
    host = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="hosted_games")
    pin = models.CharField(max_length=6, db_index=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.LOBBY)
    current_index = models.IntegerField(default=-1, help_text="Index into the quiz's questions; -1 before the first.")
    question_started_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["pin"], condition=~models.Q(status="finished"), name="uniq_active_pin"),
        ]

    def __str__(self):
        return f"{self.quiz.title} · PIN {self.pin} · {self.get_status_display()}"


class Player(models.Model):
    game = models.ForeignKey(LiveGame, on_delete=models.CASCADE, related_name="players")
    nickname = models.CharField(max_length=NICKNAME_MAX)
    token_hash = models.CharField(max_length=64, help_text="SHA-256 of the player's secret token.")
    score = models.IntegerField(default=0)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-score", "joined_at"]
        constraints = [models.UniqueConstraint(fields=["game", "nickname"], name="uniq_game_nickname")]

    def __str__(self):
        return f"{self.nickname} ({self.score})"

    @staticmethod
    def hash_token(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()


class PlayerAnswer(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(LiveQuestion, on_delete=models.CASCADE, related_name="player_answers")
    choice = models.PositiveSmallIntegerField()
    correct = models.BooleanField(default=False)
    points = models.IntegerField(default=0)
    elapsed_ms = models.PositiveIntegerField(default=0)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["player", "question"], name="uniq_player_question")]
