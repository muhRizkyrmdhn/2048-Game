"""
board_component.py
Renders the 2048 board as a pure HTML string (no iframe, no inline <style>).

Keyframe animations (tile-slide, tile-pop, tile-spawn) live in style.css and
are loaded once by app.py.  This module only emits <div> elements that carry:
  - class  g-tile-slide | g-tile-merge | g-tile-spawn
  - inline CSS vars  --ox and --oy  (pixel offsets from origin)

Streamlit allows inline style="" attributes and class="" — it only strips
<style>/<script> tags injected via st.markdown.
"""

import numpy as np
from typing import Optional

# ── sizing constants ─────────────────────────────────────────────────────────
CELL  = 82    # px — cell width/height
GAP   = 8     # px — gap between cells
BOARD = 4 * CELL + 3 * GAP   # 352 px

# ── tile colour palette ───────────────────────────────────────────────────────
_BG = {
    0:    "rgba(255,255,255,0.04)",
    2:    "#312e81", 4:    "#3730a3", 8:    "#1d4ed8",
    16:   "#1e40af", 32:   "#0369a1", 64:   "#0891b2",
    128:  "#059669", 256:  "#065f46", 512:  "#854d0e",
    1024: "#92400e",
    2048: "linear-gradient(135deg,#f59e0b,#ef4444)",
}
_FG = {
    0:    "transparent",
    2:    "#e0e7ff", 4:    "#e0e7ff", 8:    "#dbeafe",
    16:   "#dbeafe", 32:   "#e0f2fe", 64:   "#ecfeff",
    128:  "#d1fae5", 256:  "#d1fae5", 512:  "#fef9c3",
    1024: "#fef3c7", 2048: "#ffffff",
}

def _bg(v: int) -> str:
    return _BG.get(v, "linear-gradient(135deg,#7c3aed,#db2777)")

def _fg(v: int) -> str:
    return _FG.get(v, "#ffffff")

def _fs(v: int) -> str:
    if v < 100:   return "1.5rem"
    if v < 1000:  return "1.2rem"
    if v < 10000: return "1.0rem"
    return "0.82rem"


# ── movement tracker ──────────────────────────────────────────────────────────

def _track(prev: np.ndarray, curr: np.ndarray) -> list[dict]:
    """
    For every non-zero cell in `curr`, find where it came from in `prev`.
    Returns a list of tile descriptors with keys:
      value, to_r, to_c, dr, dc, merged, spawned
    """
    available: dict[tuple, int] = {}
    for r in range(4):
        for c in range(4):
            v = int(prev[r, c])
            if v:
                available[(r, c)] = v

    claimed:      set = set()
    matched_curr: set = set()
    tiles: list[dict] = []

    # Pass 1 — exact value match (plain slide, no merge)
    for r in range(4):
        for c in range(4):
            v = int(curr[r, c])
            if not v:
                continue
            best, best_d = None, 9999
            for (pr, pc), pv in available.items():
                if (pr, pc) in claimed:
                    continue
                if pv == v:
                    d = abs(pr - r) + abs(pc - c)
                    if d < best_d:
                        best, best_d = (pr, pc), d
            if best:
                claimed.add(best)
                matched_curr.add((r, c))
                tiles.append(dict(
                    value=v, to_r=r, to_c=c,
                    dr=r - best[0], dc=c - best[1],
                    merged=False, spawned=False,
                ))

    # Pass 2 — half-value match (merge result)
    for r in range(4):
        for c in range(4):
            if (r, c) in matched_curr:
                continue
            v = int(curr[r, c])
            if not v or v < 2:
                continue
            best, best_d = None, 9999
            for (pr, pc), pv in available.items():
                if (pr, pc) in claimed:
                    continue
                if pv == v // 2:
                    d = abs(pr - r) + abs(pc - c)
                    if d < best_d:
                        best, best_d = (pr, pc), d
            if best:
                claimed.add(best)
                matched_curr.add((r, c))
                tiles.append(dict(
                    value=v, to_r=r, to_c=c,
                    dr=r - best[0], dc=c - best[1],
                    merged=True, spawned=False,
                ))

    # Pass 3 — remaining tiles are newly spawned
    for r in range(4):
        for c in range(4):
            if (r, c) in matched_curr:
                continue
            v = int(curr[r, c])
            if v:
                tiles.append(dict(
                    value=v, to_r=r, to_c=c,
                    dr=0, dc=0,
                    merged=False, spawned=True,
                ))

    return tiles


# ── HTML renderer ─────────────────────────────────────────────────────────────

# Base style shared by all tile divs (no animation — animation added via class)
_TILE_BASE = (
    "position:absolute;"
    "width:{sz}px;height:{sz}px;"
    "border-radius:10px;"
    "display:flex;align-items:center;justify-content:center;"
    "font-family:'Segoe UI',system-ui,sans-serif;"
    "font-weight:800;font-size:{fs};"
    "background:{bg};color:{fg};"
    "border:1px solid rgba(255,255,255,0.10);"
    "left:{x}px;top:{y}px;"
    "--ox:{ox}px;--oy:{oy}px;"
    "{glow}"
)


def render_board_html(
    curr_board: np.ndarray,
    prev_board: Optional[np.ndarray],
    run_key: int = 0,
) -> str:
    """
    Return an HTML string safe for st.markdown(..., unsafe_allow_html=True).

    No <style> or <script> tags — keyframes live in style.css.
    `run_key` (= move_count) changes each turn so Streamlit sees new content
    and the browser re-triggers CSS animations.
    """
    if prev_board is None:
        prev_board = curr_board.copy()

    tiles = _track(prev_board, curr_board)

    # ── background cells (static, no animation) ───────────────────────────
    bg_html = ""
    for r in range(4):
        for c in range(4):
            x = c * (CELL + GAP)
            y = r * (CELL + GAP)
            bg_html += (
                f'<div style="position:absolute;'
                f'left:{x}px;top:{y}px;'
                f'width:{CELL}px;height:{CELL}px;'
                f'background:rgba(255,255,255,0.04);'
                f'border-radius:10px;"></div>'
            )

    # ── tile divs ─────────────────────────────────────────────────────────
    tile_html = ""
    for t in tiles:
        v      = t["value"]
        r, c   = t["to_r"], t["to_c"]
        dr, dc = t["dr"],   t["dc"]

        x  = c * (CELL + GAP)
        y  = r * (CELL + GAP)
        ox = dc * (CELL + GAP)   # horizontal pixel offset from source
        oy = dr * (CELL + GAP)   # vertical pixel offset from source

        glow = ""
        if v == 2048:
            glow = "box-shadow:0 0 22px rgba(245,158,11,0.65);"
        elif v > 2048:
            glow = "box-shadow:0 0 26px rgba(124,58,237,0.7);"

        style = _TILE_BASE.format(
            sz=CELL, fs=_fs(v), bg=_bg(v), fg=_fg(v),
            x=x, y=y, ox=ox, oy=oy, glow=glow,
        )

        # Animation class — defined in style.css, not here
        if t["spawned"]:
            anim_cls = "g-tile-spawn"
        elif t["merged"]:
            anim_cls = "g-tile-merge"
        else:
            anim_cls = "g-tile-slide"

        tile_html += f'<div class="{anim_cls}" style="{style}">{v}</div>'

    # ── board wrapper ─────────────────────────────────────────────────────
    # data-run changes every move → Streamlit sees a content change →
    # browser re-parses the element → CSS animations restart cleanly.
    return (
        f'<div data-run="{run_key}" '
        f'style="display:inline-block;'
        f'background:rgba(255,255,255,0.06);'
        f'border:1px solid rgba(255,255,255,0.12);'
        f'border-radius:18px;padding:12px;'
        f'backdrop-filter:blur(16px);'
        f'-webkit-backdrop-filter:blur(16px);">'
        f'<div style="position:relative;width:{BOARD}px;height:{BOARD}px;">'
        f'{bg_html}'
        f'{tile_html}'
        f'</div>'
        f'</div>'
    )
