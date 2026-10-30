"""
ai_solver.py
Expectimax search with heuristic evaluation for 2048.
"""

import time
import numpy as np 
from game_logic import move, get_empty_cells, DIRECTIONS, get_valid_moves

# ---------------------------------------------------------------------------
# Heuristic weights (tunable)
# ---------------------------------------------------------------------------
W_MONOTONICITY = 1.0
W_EMPTY        = 2.7
W_CORNER       = 3.5
W_SMOOTHNESS   = 0.1

# Snake-pattern weight matrix: highest weight at top-left corner,
# spiralling inward to reward corner-anchored max tile.
_SNAKE_WEIGHTS = np.array(
    [
        [2**15, 2**14, 2**13, 2**12],
        [2**8,  2**9,  2**10, 2**11],
        [2**7,  2**6,  2**5,  2**4],
        [2**0,  2**1,  2**2,  2**3],
    ],
    dtype=np.float64,
)


# ---------------------------------------------------------------------------
# Heuristic evaluation
# ---------------------------------------------------------------------------

def _monotonicity(board: np.ndarray) -> float:
    """Score rows and columns for monotonic (consistently increasing/decreasing) ordering."""
    score = 0.0
    # rows
    for r in range(4):
        row = board[r]
        inc = dec = 0.0
        for c in range(3):
            a, b = float(row[c]), float(row[c + 1])
            if a > b:
                dec += a - b
            elif b > a:
                inc += b - a
        score -= min(inc, dec)
    # columns
    for c in range(4):
        col = board[:, c]
        inc = dec = 0.0
        for r in range(3):
            a, b = float(col[r]), float(col[r + 1])
            if a > b:
                dec += a - b
            elif b > a:
                inc += b - a
        score -= min(inc, dec)
    return score


def _smoothness(board: np.ndarray) -> float:
    """Penalise large differences between adjacent tiles (log2 space)."""
    score = 0.0
    log_board = np.where(board > 0, np.log2(board.astype(np.float64) + 1), 0.0)
    for r in range(4):
        for c in range(4):
            if board[r, c] == 0:
                continue
            val = log_board[r, c]
            if c + 1 < 4 and board[r, c + 1] != 0:
                score -= abs(val - log_board[r, c + 1])
            if r + 1 < 4 and board[r + 1, c] != 0:
                score -= abs(val - log_board[r + 1, c])
    return score


def _corner_bonus(board: np.ndarray) -> float:
    """Reward keeping the max tile in any corner using the snake pattern."""
    return float(np.sum(board * _SNAKE_WEIGHTS))


def _empty_cells(board: np.ndarray) -> float:
    return float(len(get_empty_cells(board)))


def evaluate(board: np.ndarray) -> float:
    """Combine heuristics into a single scalar score."""
    return (
        W_MONOTONICITY * _monotonicity(board)
        + W_EMPTY      * _empty_cells(board)
        + W_CORNER     * _corner_bonus(board)
        + W_SMOOTHNESS * _smoothness(board)
    )


# ---------------------------------------------------------------------------
# Expectimax search
# ---------------------------------------------------------------------------

def _expectimax(board: np.ndarray, depth: int, is_max: bool) -> float:
    """
    Recursive Expectimax.
    - MAX node  → player chooses the best direction.
    - CHANCE node → weighted average over random tile placements.
    """
    if depth == 0:
        return evaluate(board)

    if is_max:
        best = float("-inf")
        for direction in DIRECTIONS:
            new_b, _, changed = move(board, direction)
            if changed:
                val = _expectimax(new_b, depth - 1, False)
                if val > best:
                    best = val
        return best if best != float("-inf") else evaluate(board)

    # Chance node
    empty = get_empty_cells(board)
    if not empty:
        return evaluate(board)

    total = 0.0
    n = len(empty)
    for (r, c) in empty:
        for tile_val, prob in ((2, 0.9), (4, 0.1)):
            child = board.copy()
            child[r, c] = tile_val
            total += prob * _expectimax(child, depth - 1, True)
    return total / n


def get_best_move(board: np.ndarray, depth: int = 3) -> tuple[str | None, float, float]:
    """
    Return (best_direction, best_score, elapsed_ms).
    depth is adjusted dynamically: 4 when ≤ 6 empty cells, else 3.
    """
    empty_count = len(get_empty_cells(board))
    effective_depth = 4 if empty_count <= 6 else depth

    t0 = time.perf_counter()
    best_dir: str | None = None
    best_val = float("-inf")

    for direction in DIRECTIONS:
        new_b, _, changed = move(board, direction)
        if changed:
            val = _expectimax(new_b, effective_depth - 1, False)
            if val > best_val:
                best_val = val
                best_dir = direction

    elapsed_ms = (time.perf_counter() - t0) * 1000
    return best_dir, best_val, elapsed_ms


def get_board_eval(board: np.ndarray) -> dict:
    """Return a breakdown of heuristic sub-scores for the AI Metrics panel."""
    return {
        "monotonicity": round(W_MONOTONICITY * _monotonicity(board), 2),
        "empty_cells":  round(W_EMPTY        * _empty_cells(board),  2),
        "corner_bonus": round(W_CORNER       * _corner_bonus(board), 2),
        "smoothness":   round(W_SMOOTHNESS   * _smoothness(board),   2),
        "total":        round(evaluate(board), 2),
    }
