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

Legal-move generation, turn tracking, and check/checkmate/stalemate
detection are delegated to [`python-chess`](https://python-chess.readthedocs.io/)
(installed from PyPI as the `chess` package). Each random game just
samples uniformly from `board.legal_moves`, pushes the choice, and asks
the library whether the position is terminal.

The 50-move rule and threefold repetition are **deliberately not consulted**,
even though `python-chess` can detect them. Games that would otherwise be
drawn by those rules continue until checkmate, stalemate, the rook(s) being
captured, or the `max_moves` cap is hit. This preserves the original
"random play to material draw or accidental mate" experiment.

## Requirements

Python 3.8+ and `python-chess`.

```bash
pip install -r requirements.txt
```

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
├── requirements.txt         # python-chess
└── README.md
```
