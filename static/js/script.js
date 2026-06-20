document.addEventListener('DOMContentLoaded', () => {
  const boardEl = document.getElementById('board');
  if (!boardEl) return;

  const sessionId = window.SESSION_ID;
  const csrfToken = window.CSRF_TOKEN;

  let board = Array(9).fill(null);
  let gameOver = false;
  let waitingForAI = false;

  const WINS = [
    [0,1,2],[3,4,5],[6,7,8],
    [0,3,6],[1,4,7],[2,5,8],
    [0,4,8],[2,4,6]
  ];

  function findWinLine(board) {
    for (const [a,b,c] of WINS) {
      if (board[a] && board[a] === board[b] && board[b] === board[c]) {
        return [a,b,c];
      }
    }
    return [];
  }

  function renderBoard(winLine = []) {
    const cells = boardEl.querySelectorAll('.cell');
    cells.forEach((cell, i) => {
      cell.className = 'cell';
      cell.innerHTML = '';
      if (board[i]) {
        cell.classList.add('taken');
        if (winLine.includes(i)) {
          cell.classList.add('winning-cell', `has-${board[i].toLowerCase()}`);
        }
        const mark = document.createElement('span');
        mark.className = `mark mark-${board[i].toLowerCase()}`;
        mark.textContent = board[i];
        cell.appendChild(mark);
      }
    });
  }

  function setPips(activePlayer) {
    const pipX = document.getElementById('pip-x');
    const pipO = document.getElementById('pip-o');
    const turnText = document.getElementById('turn-text');
    if (!pipX) return;
    pipX.className = 'pip' + (activePlayer === 'X' ? ' active-x' : '');
    pipO.className = 'pip' + (activePlayer === 'O' ? ' active-o' : '');
    turnText.textContent = activePlayer === 'X' ? 'Your turn' : 'AI thinking…';
  }

  function setStatus(result) {
    const el = document.getElementById('status');
    if (!el) return;
    if (!result || result === 'in_progress') { el.textContent = ''; el.style.color = ''; return; }
    const map = {
      player_win: { text: 'You win! 🎉', color: 'var(--x-color)' },
      ai_win:     { text: 'AI wins.',    color: 'var(--o-color)' },
      draw:       { text: "It's a draw.", color: '' },
    };
    const s = map[result] || {};
    el.textContent = s.text || '';
    el.style.color = s.color || '';
  }

  async function handleCellClick(idx) {
    if (gameOver || waitingForAI || board[idx]) return;

    board[idx] = 'X';
    renderBoard();
    setPips('O');
    waitingForAI = true;

    try {
      const res = await fetch(`/api/move/${sessionId}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({ index: idx }),
      });

      const data = await res.json();
      if (!res.ok) { console.error(data.error); waitingForAI = false; return; }

      board = data.board;

      if (data.result !== 'in_progress') {
        gameOver = true;
        const winLine = findWinLine(board);
        renderBoard(winLine);
        setStatus(data.result);
        setPips(null);
      } else {
        renderBoard();
        setPips('X');
        setStatus(null);
      }
    } catch (err) {
      console.error('Network error:', err);
    } finally {
      waitingForAI = false;
    }
  }

  boardEl.addEventListener('click', e => {
    const cell = e.target.closest('.cell');
    if (!cell) return;
    const idx = parseInt(cell.dataset.index, 10);
    handleCellClick(idx);
  });

  setPips('X');
});
