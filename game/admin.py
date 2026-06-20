from django.contrib import admin
from .models import GameSession, PlayerProfile

@admin.register(PlayerProfile)
class PlayerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'wins', 'losses', 'draws', 'win_rate']

@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ['pk', 'player', 'result', 'difficulty', 'created_at']
    list_filter = ['result', 'difficulty']
