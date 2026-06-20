import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import GameSession, PlayerProfile
from .ai import get_ai_move, check_winner


# ── Auth ──────────────────────────────────────────────────────────────────────

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            PlayerProfile.objects.create(user=user)
            login(request, user)
            return redirect('game')
    else:
        form = UserCreationForm()
    return render(request, 'game/register.html', {'form': form})


# ── Game ──────────────────────────────────────────────────────────────────────

@login_required
def game_view(request):
    difficulty = request.GET.get('difficulty', 'hard')
    session = GameSession.objects.create(
        player=request.user,
        difficulty=difficulty,
    )
    return render(request, 'game/game.html', {
        'session_id': session.pk,
        'difficulty': difficulty,
    })


@login_required
@require_POST
def make_move(request, session_id):
    """Player makes a move → server validates, checks winner, fires AI move."""
    session = get_object_or_404(GameSession, pk=session_id, player=request.user)

    if session.result != 'in_progress':
        return JsonResponse({'error': 'Game already over.'}, status=400)

    data = json.loads(request.body)
    idx = data.get('index')

    if idx is None or not (0 <= idx <= 8):
        return JsonResponse({'error': 'Invalid index.'}, status=400)

    board = session.board_list()

    if board[idx] is not None:
        return JsonResponse({'error': 'Cell already taken.'}, status=400)

    # Player move (X)
    board[idx] = 'X'
    winner = check_winner(board)

    if winner:
        session.set_board(board)
        session.result = 'player_win' if winner == 'X' else 'draw'
        session.save()
        _update_profile(request.user, session.result)
        return JsonResponse({'board': board, 'result': session.result, 'ai_move': None})

    # AI move (O)
    ai_idx = get_ai_move(board, session.difficulty)
    if ai_idx is not None:
        board[ai_idx] = 'O'

    winner = check_winner(board)
    if winner:
        session.result = 'ai_win' if winner == 'O' else 'draw'
    
    session.set_board(board)
    session.save()

    if session.result != 'in_progress':
        _update_profile(request.user, session.result)

    return JsonResponse({
        'board': board,
        'result': session.result,
        'ai_move': ai_idx,
    })


def _update_profile(user, result):
    profile, _ = PlayerProfile.objects.get_or_create(user=user)
    if result == 'player_win':
        profile.wins += 1
    elif result == 'ai_win':
        profile.losses += 1
    elif result == 'draw':
        profile.draws += 1
    profile.save()


# ── Leaderboard ───────────────────────────────────────────────────────────────

@login_required
def leaderboard(request):
    profiles = PlayerProfile.objects.select_related('user').order_by('-wins', '-draws')[:20]
    return render(request, 'game/leaderboard.html', {'profiles': profiles})


# ── History ───────────────────────────────────────────────────────────────────

@login_required
def history(request):
    games = GameSession.objects.filter(
        player=request.user
    ).exclude(result='in_progress').order_by('-created_at')[:30]
    return render(request, 'game/history.html', {'games': games})
