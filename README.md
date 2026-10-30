# 🎮 2048 × AI — Streamlit + Expectimax Solver

> Classic 2048 with a built-in **Expectimax AI** solver and a **Glassmorphism** dark-theme UI,
> deployable for free on [Streamlit Community Cloud](https://streamlit.io/cloud).
> Try it [https://2048-game-kelompok-3.streamlit.app/]
---

## ✨ Features

| Feature | Detail |
|---|---|
| **Manual Play** | Arrow-button D-pad in the browser — works on desktop & mobile |
| **AI Hint** | Single-click suggestion of the best next move |
| **AI Auto-Play** | Fully autonomous play loop until Game Over |
| **Expectimax Search** | Depth 3–4 with dynamic depth selection |
| **Heuristics** | Monotonicity · Corner Bonus · Empty Cells · Smoothness |
| **AI Metrics Panel** | Real-time heuristic sub-scores + think-time (ms) |
| **Score Tracking** | Current Score · Best Score · Max Tile · Move Counter |
| **Glassmorphism UI** | Dark slate gradient, frosted-glass board, neon tile colours |

---

## 🗂 Project Structure

```
2048-streamlit-ai/
├── app.py            # Streamlit UI + session state + game loop
├── ai_solver.py      # Expectimax algorithm & heuristic evaluation
├── game_logic.py     # Pure NumPy 2048 board operations
├── style.css         # Custom CSS (glassmorphism, tile colours)
├── requirements.txt  # streamlit, numpy
└── README.md
```

---

## 🚀 Running Locally

```bash
# 1. Clone / enter the project directory
cd 2048-streamlit-ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## ☁️ Deploy to Streamlit Community Cloud (Free)

1. Push this repository to **GitHub** (public or private).
2. Go to <https://share.streamlit.io> → **New app**.
3. Select your repo, branch `main`, and set **Main file path** to `app.py`.
4. Click **Deploy** — your public URL will be `https://<app>.streamlit.app`.

> No extra configuration file is required; Streamlit Cloud reads `requirements.txt` automatically.

---

## 🤖 AI Algorithm

### Expectimax Search

```
MAX node  (player turn)  → pick direction with highest expected value
CHANCE node (tile spawn) → weighted average: P(2)=0.9, P(4)=0.1
Leaf node                → heuristic evaluation
```

### Heuristic Function

| Component | Weight | Purpose |
|---|---|---|
| **Monotonicity** | 1.0 | Reward rows/cols that are consistently increasing or decreasing |
| **Empty Cells** | 2.7 | Keep the board open to maximise future options |
| **Corner Bonus** | 3.5 | Snake-pattern weight matrix anchors the max tile to the top-left corner |
| **Smoothness** | 0.1 | Penalise large value differences between adjacent tiles |

Dynamic depth: depth = **4** when ≤ 6 empty cells remain, **3** otherwise — keeps every move under ~100 ms.

---

## 📋 Requirements

- Python 3.11+
- `streamlit >= 1.32.0`
- `numpy >= 1.26.0`

---

## 📄 License

MIT — free to use, modify, and distribute.
