"""
game_logic.py
Core 2048 board operations using NumPy.
"""

import numpy as np
import random


# ---------------------------------------------------------------------------
# Board initialisation
# ---------------------------------------------------------------------------

def new_board() -> np.ndarray:
    """Return an empty 4×4 board with two starting tiles."""
    board = np.zeros((4, 4), dtype=np.int64)
    board = add_random_tile(board)
    board = add_random_tile(board)
    return board


def add_random_tile(board: np.ndarray) -> np.ndarray:
    """Place a 2 (90 %) or 4 (10 %) on a random empty cell."""
    empty = list(zip(*np.where(board == 0)))
    if not empty:
        return board
    r, c = random.choice(empty)
    board[r, c] = 4 if random.random() < 0.1 else 2
    return board


# ---------------------------------------------------------------------------
# Row-level slide helpers (operate on a single row)
# ---------------------------------------------------------------------------

def _slide_row_left(row: np.ndarray) -> tuple[np.ndarray, int]:
    """Slide and merge a single row to the left; return (new_row, score_gained)."""
    tiles = row[row != 0]           # strip zeros
    merged = []
    score = 0
    skip = False
    for i in range(len(tiles)):
        if skip:
            skip = False
            continue
        if i + 1 < len(tiles) and tiles[i] == tiles[i + 1]:
            val = tiles[i] * 2
            merged.append(val)
            score += val
            skip = True
        else:
            merged.append(tiles[i])
    # pad with zeros on the right
    result = np.zeros(4, dtype=np.int64)
    result[: len(merged)] = merged
    return result, score


# ---------------------------------------------------------------------------
# Board-level moves
# ---------------------------------------------------------------------------

def _move_left(board: np.ndarray) -> tuple[np.ndarray, int]:
    new_board = np.zeros_like(board)
    score = 0
    for r in range(4):
        new_board[r], gained = _slide_row_left(board[r])
        score += gained
    return new_board, score


def _move_right(board: np.ndarray) -> tuple[np.ndarray, int]:
    flipped, score = _move_left(np.fliplr(board))
    return np.fliplr(flipped), score


def _move_up(board: np.ndarray) -> tuple[np.ndarray, int]:
    rotated, score = _move_left(np.rot90(board, 1))
    return np.rot90(rotated, -1), score


def _move_down(board: np.ndarray) -> tuple[np.ndarray, int]:
    rotated, score = _move_left(np.rot90(board, -1))
    return np.rot90(rotated, 1), score


_MOVE_FN = {
    "left":  _move_left,
    "right": _move_right,
    "up":    _move_up,
    "down":  _move_down,
}

DIRECTIONS = ["left", "right", "up", "down"]


def move(board: np.ndarray, direction: str) -> tuple[np.ndarray, int, bool]:
    """
    Apply *direction* to *board*.
    Returns (new_board, score_gained, changed).
    `changed` is False when the move produced no effect.
    """
    fn = _MOVE_FN[direction]
    new_b, score = fn(board)
    changed = not np.array_equal(board, new_b)
    return new_b, score, changed


# ---------------------------------------------------------------------------
# Game-state queries
# ---------------------------------------------------------------------------

def get_empty_cells(board: np.ndarray) -> list[tuple[int, int]]:
    return list(zip(*np.where(board == 0))) if np.any(board == 0) else []


def is_game_over(board: np.ndarray) -> bool:
    """Return True when no valid move remains."""
    if get_empty_cells(board):
        return False
    for direction in DIRECTIONS:
        _, _, changed = move(board, direction)
        if changed:
            return False
    return True


def get_valid_moves(board: np.ndarray) -> list[str]:
    return [d for d in DIRECTIONS if move(board, d)[2]]


def max_tile(board: np.ndarray) -> int:
    return int(board.max())
