import random

WINS = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
    [0, 3, 6], [1, 4, 7], [2, 5, 8],  # cols
    [0, 4, 8], [2, 4, 6],              # diagonals
]


def check_winner(board):
    """Return 'X', 'O', 'draw', or None."""
    for a, b, c in WINS:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    if all(cell is not None for cell in board):
        return 'draw'
    return None


def get_empty(board):
    return [i for i, c in enumerate(board) if c is None]


def minimax(board, is_maximizing):
    result = check_winner(board)
    if result == 'O':
        return 10
    if result == 'X':
        return -10
    if result == 'draw':
        return 0

    if is_maximizing:
        best = -999
        for i in get_empty(board):
            board[i] = 'O'
            best = max(best, minimax(board, False))
            board[i] = None
        return best
    else:
        best = 999
        for i in get_empty(board):
            board[i] = 'X'
            best = min(best, minimax(board, True))
            board[i] = None
        return best


def ai_move_hard(board):
    """Best move using minimax — unbeatable."""
    best_score = -999
    best_move = None
    for i in get_empty(board):
        board[i] = 'O'
        score = minimax(board, False)
        board[i] = None
        if score > best_score:
            best_score = score
            best_move = i
    return best_move


def ai_move_easy(board):
    """Random move — beatable."""
    empties = get_empty(board)
    return random.choice(empties) if empties else None


def get_ai_move(board, difficulty='hard'):
    if difficulty == 'easy':
        return ai_move_easy(board)
    return ai_move_hard(board)
