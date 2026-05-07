# Random Chess Moves Analysis

Monte-Carlo simulations of simple chess endgames where **both sides choose
uniformly at random from their legal moves**. The goal is to measure how often
each outcome (checkmate, stalemate, material-draw, move-limit) occurs under
purely random play.

## Simulations

| Script | Setup |
| --- | --- |
| `kr_vs_k_simulation.py` | White: King + Rook. Black: lone King. |
| `kr_vs_kr_simulation.py` | Each side: King + Rook (symmetric). |

Both scripts use a hand-rolled move generator (no `python-chess` dependency)
that enforces all rules relevant to king-and-rook endgames: kings can't stand
adjacent or move into check, rook moves are filtered for self-pins, the rook
can be captured if undefended, and starting positions are rejected if they are
already terminal.

Rules that don't apply to these piece sets (castling, en passant, promotion)
are omitted. The 50-move rule and threefold repetition are **not** enforced;
games that would otherwise be drawn by repetition are instead capped by a
`max_moves` limit and reported as `max_moves`.

## Requirements

Python 3.8+ (uses `dataclasses` and `typing`). No third-party packages.

```bash
python3 --version
```

`requirements.txt` is intentionally empty.

## Running

From the project root:

```bash
python3 kr_vs_k_simulation.py
python3 kr_vs_kr_simulation.py
```

Each script runs 10,000 games with a 200-move cap and prints a summary.

To customize, import and call `run_simulation` directly:

```python
from kr_vs_kr_simulation import run_simulation, print_results

stats = run_simulation(num_games=50_000, max_moves=500, verbose=True)
print_results(stats)
```

## Output

Each run prints counts, percentages, and move-count statistics
(`avg`, `min`, `max`) per outcome:

- `checkmate` / `white_checkmate` / `black_checkmate`
- `stalemate`
- `insufficient_material` (rook(s) captured, leaving K vs K)
- `max_moves` (move cap hit before a terminal state)

## Repository layout

```
.
├── kr_vs_k_simulation.py    # K+R vs K
├── kr_vs_kr_simulation.py   # K+R vs K+R
├── requirements.txt         # empty (stdlib only)
└── README.md
```
