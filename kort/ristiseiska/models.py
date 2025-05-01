from django.utils import timezone  # Import timezone
from django.db import models
from django.forms import ValidationError

class Player(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"

class Season(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField(blank=False, null=False)
    end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} {self.start_date}"

class Game(models.Model):
    winner = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='game_winner')
    loser = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='game_loser')
    datetime = models.DateTimeField(default=timezone.now)  # Use timezone.now
    season = models.ForeignKey(Season, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.id}: Voittaja: {self.winner} - Häviäjä: {self.loser}"


def clean(self):
    if self.winner == self.loser:
        raise ValidationError("Winner and loser cannot be the same player.")
