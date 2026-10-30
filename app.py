"""
app.py
2048 Game with Expectimax AI Solver – Streamlit UI
"""

import time
import pathlib
import numpy as np
import streamlit as st

from game_logic      import new_board, move, add_random_tile, is_game_over, max_tile, get_valid_moves
from ai_solver       import get_best_move, get_board_eval
from board_component import render_board_html

# ─────────────────────────────────────────────
# Page config (MUST be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title  = "2048 × AI",
    page_icon   = "🎮",
    layout      = "centered",
    initial_sidebar_state = "collapsed",
)

# ─────────────────────────────────────────────
# Inject CSS
# ─────────────────────────────────────────────
_CSS_PATH = pathlib.Path(__file__).parent / "style.css"
with open(_CSS_PATH) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Session-state initialisation
# ─────────────────────────────────────────────
def _init_state():
    if "board" not in st.session_state:
        st.session_state.board      = new_board()
        st.session_state.score      = 0
        st.session_state.best       = 0
        st.session_state.game_over  = False
        st.session_state.autoplay   = False
        st.session_state.hint_dir   = None
        st.session_state.ai_metrics = {}
        st.session_state.ai_ms      = 0.0
        st.session_state.move_count = 0
        st.session_state.last_move  = None   # tracks last direction for animation
        st.session_state.prev_board = None   # board before last move (to detect merges)

_init_state()
ss = st.session_state          # shorthand

# ─────────────────────────────────────────────
# Helper: apply a direction
# ─────────────────────────────────────────────
def _apply_move(direction: str):
    if ss.game_over:
        return
    new_b, gained, changed = move(ss.board, direction)
    if changed:
        ss.prev_board  = ss.board.copy()     # snapshot before new tile spawns
        ss.board       = add_random_tile(new_b)
        ss.score      += gained
        ss.best        = max(ss.best, ss.score)
        ss.move_count += 1
        ss.hint_dir    = None
        ss.last_move   = direction           # store for animation
        if is_game_over(ss.board):
            ss.game_over = True
            ss.autoplay  = False

# ─────────────────────────────────────────────
# DIRECTION ARROW MAP
# ─────────────────────────────────────────────
_ARROW = {"left": "⬅️", "right": "➡️", "up": "⬆️", "down": "⬇️"}

# ─────────────────────────────────────────────
# Auto-play: take one step if autoplay is on
# ─────────────────────────────────────────────
if ss.autoplay and not ss.game_over:
    direction, score_val, elapsed = get_best_move(ss.board, depth=3)
    ss.ai_metrics = get_board_eval(ss.board)
    ss.ai_ms      = elapsed
    if direction:
        ss.hint_dir = direction
        _apply_move(direction)
    else:
        ss.autoplay = False

# ─────────────────────────────────────────────
# ── HEADER ──
# ─────────────────────────────────────────────
st.markdown("<h1>2048 × AI</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;color:#94a3b8;font-size:0.85rem;"
    "margin-top:-6px;margin-bottom:14px;'>"
    "Expectimax Search · Glassmorphism UI</p>",
    unsafe_allow_html=True,
)

# Score row
c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    st.markdown(
        f'<div class="score-card">'
        f'<div class="label">Score</div>'
        f'<div class="value">{ss.score:,}</div>'
        f'</div>', unsafe_allow_html=True
    )
with c2:
    st.markdown(
        f'<div class="score-card">'
        f'<div class="label">Best</div>'
        f'<div class="value">{ss.best:,}</div>'
        f'</div>', unsafe_allow_html=True
    )
with c3:
    mt = max_tile(ss.board)
    tile_lbl = f"{mt:,}"
    st.markdown(
        f'<div class="score-card">'
        f'<div class="label">Max Tile</div>'
        f'<div class="value">{tile_lbl}</div>'
        f'</div>', unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ── MAIN LAYOUT: board  +  controls ──
# ─────────────────────────────────────────────
board_col, ctrl_col = st.columns([3, 2], gap="large")

with board_col:
    # Status badge
    if ss.game_over:
        badge = '<span class="status-badge status-gameover">Game Over</span>'
    elif ss.autoplay:
        badge = '<span class="status-badge status-ai">🤖 AI Playing</span>'
    else:
        badge = '<span class="status-badge status-playing">Playing</span>'
    st.markdown(
        f"<div style='text-align:center;margin-bottom:10px;'>{badge}</div>",
        unsafe_allow_html=True,
    )

    # Board — pure st.markdown, no iframe, no flicker
    st.markdown(
        render_board_html(ss.board, prev_board=ss.prev_board, run_key=ss.move_count),
        unsafe_allow_html=True,
    )

    # Move counter
    st.markdown(
        f"<p style='text-align:center;color:#64748b;font-size:0.78rem;"
        f"margin-top:8px;'>Moves: {ss.move_count}</p>",
        unsafe_allow_html=True,
    )

with ctrl_col:
    st.markdown("#### 🕹️ Controls")

    # ── Directional pad ──
    _, up_col, _ = st.columns([1, 1, 1])
    with up_col:
        if st.button("⬆️", key="btn_up", use_container_width=True):
            _apply_move("up")
            st.rerun()

    l_col, _, r_col = st.columns([1, 1, 1])
    with l_col:
        if st.button("⬅️", key="btn_left", use_container_width=True):
            _apply_move("left")
            st.rerun()
    with r_col:
        if st.button("➡️", key="btn_right", use_container_width=True):
            _apply_move("right")
            st.rerun()

    _, dn_col, _ = st.columns([1, 1, 1])
    with dn_col:
        if st.button("⬇️", key="btn_down", use_container_width=True):
            _apply_move("down")
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── AI buttons ──
    st.markdown("#### 🤖 AI")

    hint_col, auto_col = st.columns(2)
    with hint_col:
        if st.button("💡 Hint", key="btn_hint", use_container_width=True, disabled=ss.game_over):
            direction, score_val, elapsed = get_best_move(ss.board, depth=3)
            ss.hint_dir   = direction
            ss.ai_metrics = get_board_eval(ss.board)
            ss.ai_ms      = elapsed
            st.rerun()

    with auto_col:
        if ss.autoplay:
            if st.button("⏹ Stop", key="btn_stop", use_container_width=True):
                ss.autoplay = False
                st.rerun()
        else:
            if st.button("▶ Auto", key="btn_auto", use_container_width=True, disabled=ss.game_over):
                ss.autoplay = True
                st.rerun()

    # Hint display
    if ss.hint_dir:
        arrow = _ARROW.get(ss.hint_dir, "?")
        st.markdown(
            f'<div class="hint-box">{arrow}</div>'
            f'<p style="text-align:center;font-size:0.78rem;color:#a78bfa;">'
            f'Best move: <b>{ss.hint_dir.upper()}</b></p>',
            unsafe_allow_html=True,
        )

    st.markdown("<hr>", unsafe_allow_html=True)

    # Reset button
    if st.button("🔄 New Game", key="btn_reset", use_container_width=True):
        ss.board      = new_board()
        ss.score      = 0
        ss.game_over  = False
        ss.autoplay   = False
        ss.hint_dir   = None
        ss.ai_metrics = {}
        ss.ai_ms      = 0.0
        ss.move_count = 0
        ss.last_move  = None
        ss.prev_board = None
        st.rerun()

# ─────────────────────────────────────────────
# ── AI METRICS PANEL ──
# ─────────────────────────────────────────────
if ss.ai_metrics:
    m = ss.ai_metrics
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="ai-panel">
          <div class="panel-title">🧠 AI Evaluation Metrics</div>
          <div class="ai-metric-row">
            <span>Monotonicity</span>
            <span class="metric-val">{m.get('monotonicity', 0):,.1f}</span>
          </div>
          <div class="ai-metric-row">
            <span>Empty Cells</span>
            <span class="metric-val">{m.get('empty_cells', 0):,.1f}</span>
          </div>
          <div class="ai-metric-row">
            <span>Corner Bonus</span>
            <span class="metric-val">{m.get('corner_bonus', 0):,.0f}</span>
          </div>
          <div class="ai-metric-row">
            <span>Smoothness</span>
            <span class="metric-val">{m.get('smoothness', 0):,.2f}</span>
          </div>
          <hr style="margin:8px 0;">
          <div class="ai-metric-row">
            <span><b>Total Score</b></span>
            <span class="metric-val">{m.get('total', 0):,.0f}</span>
          </div>
          <div class="ai-metric-row" style="margin-top:6px;">
            <span>⏱ AI Think Time</span>
            <span class="metric-val">{ss.ai_ms:.1f} ms</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────
# Auto-play loop: schedule next rerun
# ─────────────────────────────────────────────
if ss.autoplay and not ss.game_over:
    time.sleep(0.05)   # ~50 ms between moves for smooth animation feel
    st.rerun()

# ─────────────────────────────────────────────
# Game-over banner
# ─────────────────────────────────────────────
if ss.game_over:
    st.markdown(
        f"""
        <div style="
            text-align:center;
            padding: 24px;
            margin-top: 16px;
            background: rgba(239,68,68,0.12);
            border: 1px solid rgba(239,68,68,0.4);
            border-radius: 16px;
        ">
            <div style="font-size:2.2rem;font-weight:800;color:#ef4444;">
                Game Over
            </div>
            <div style="color:#94a3b8;margin-top:6px;">
                Final Score: <b style='color:#f8fafc'>{ss.score:,}</b>
                &nbsp;·&nbsp; Max Tile: <b style='color:#f8fafc'>{max_tile(ss.board):,}</b>
                &nbsp;·&nbsp; Moves: <b style='color:#f8fafc'>{ss.move_count}</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
