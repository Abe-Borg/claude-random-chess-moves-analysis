# Random Chess Moves Analysis

Monte-Carlo simulations of simple chess endgames where **both sides choose
uniformly at random from their legal moves**. The goal is to measure how often
each outcome (checkmate, stalemate, material-draw, move-limit) occurs under
purely random play.

## Simulations

| Experiment | Script | Setup |
| --- | --- | --- |
| `kr_vs_k`  | `kr_vs_k_simulation.py`  | White: King + Rook. Black: lone King. Random board placement. |
| `kr_vs_kr` | `kr_vs_kr_simulation.py` | Each side: King + Rook (symmetric). Random board placement. |
| `standard` | `standard_simulation.py` | Standard chess starting position; full rules (castling, en passant, promotion). |

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

Use the `run.py` dispatcher to pick which experiment to run:

```bash
python3 run.py kr_vs_k
python3 run.py kr_vs_kr
python3 run.py standard
```

Optional flags: `--num-games N`, `--max-moves M`, `--quiet`. Defaults are
10,000 games with a 200-ply cap for the K+R sims and a 1,000-ply cap for
`standard`.

Each simulation module is also runnable standalone (`python3
standard_simulation.py`) and exposes a programmatic API:

```python
from standard_simulation import run_simulation, print_results

stats = run_simulation(num_games=50_000, max_moves=1_000, verbose=True)
print_results(stats)
```

## Output

Each run prints counts, percentages, and move-count statistics
(`avg`, `min`, `max`) per outcome:

- `checkmate` / `white_checkmate` / `black_checkmate`
- `stalemate`
- `insufficient_material` — rook(s) captured for the K+R sims, real FIDE
  insufficient-material rule (K vs K, K+B vs K, K+N vs K, etc.) for `standard`
- `max_moves` (move cap hit before a terminal state)

## Repository layout

```
.
├── run.py                   # CLI dispatcher
├── kr_vs_k_simulation.py    # K+R vs K, random placement
├── kr_vs_kr_simulation.py   # K+R vs K+R, random placement
├── standard_simulation.py   # full chess from the standard start
├── requirements.txt         # python-chess
└── README.md
```
