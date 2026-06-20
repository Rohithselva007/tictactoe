from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count, Q


class PlayerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    wins = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)
    draws = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_games(self):
        return self.wins + self.losses + self.draws

    @property
    def win_rate(self):
        if self.total_games == 0:
            return 0
        return round((self.wins / self.total_games) * 100, 1)

    def __str__(self):
        return f"{self.user.username} — W:{self.wins} L:{self.losses} D:{self.draws}"


class GameSession(models.Model):
    RESULT_CHOICES = [
        ('player_win', 'Player Win'),
        ('ai_win', 'AI Win'),
        ('draw', 'Draw'),
        ('in_progress', 'In Progress'),
    ]

    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('hard', 'Hard'),
    ]

    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games')
    board = models.CharField(max_length=9, default='---------')  # 9 chars: X, O, or -
    current_turn = models.CharField(max_length=1, default='X')   # X = player, O = AI
    result = models.CharField(max_length=20, choices=RESULT_CHOICES, default='in_progress')
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='hard')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def board_list(self):
        """Return board as a 9-element list."""
        return [c if c != '-' else None for c in self.board]

    def set_board(self, board_list):
        """Accept a 9-element list and save to char field."""
        self.board = ''.join(c if c else '-' for c in board_list)

    def __str__(self):
        return f"Game #{self.pk} — {self.player.username} ({self.result})"

    class Meta:
        ordering = ['-created_at']
