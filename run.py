"""
Entry point for selecting which random-move experiment to run.

Usage:
    python3 run.py kr_vs_k       [--num-games N] [--max-moves M] [--quiet]
    python3 run.py kr_vs_kr      [--num-games N] [--max-moves M] [--quiet]
    python3 run.py standard      [--num-games N] [--max-moves M] [--quiet]
"""

import argparse

import kr_vs_k_simulation
import kr_vs_kr_simulation
import standard_simulation


EXPERIMENTS = {
    'kr_vs_k':  (kr_vs_k_simulation,  10_000, 200),
    'kr_vs_kr': (kr_vs_kr_simulation, 10_000, 200),
    'standard': (standard_simulation, 10_000, 1_000),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('experiment', choices=sorted(EXPERIMENTS.keys()),
                        help='Which experiment to run')
    parser.add_argument('--num-games', type=int, default=None,
                        help='Number of games to simulate')
    parser.add_argument('--max-moves', type=int, default=None,
                        help='Move cap per game (in plies)')
    parser.add_argument('--quiet', action='store_true',
                        help='Suppress progress output')
    args = parser.parse_args()

    module, default_games, default_moves = EXPERIMENTS[args.experiment]
    num_games = args.num_games if args.num_games is not None else default_games
    max_moves = args.max_moves if args.max_moves is not None else default_moves

    stats = module.run_simulation(
        num_games=num_games, max_moves=max_moves, verbose=not args.quiet,
    )
    module.print_results(stats)


if __name__ == "__main__":
    main()
