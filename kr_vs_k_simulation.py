"""
K+R vs K Random Move Simulation

Simulates chess endgames where White has King + Rook vs Black's lone King.
Both sides make completely random legal moves.

Tracks outcomes: checkmate, stalemate, rook captured, and move limits.

Legal-move generation, turn tracking, and check/checkmate detection are
delegated to python-chess. The 50-move rule and threefold repetition are
deliberately not consulted, so games that would otherwise be drawn by
those rules continue until checkmate, stalemate, the rook is captured,
or `max_moves` is hit.
"""

import random
import time
from collections import defaultdict
from typing import Tuple

import chess


def random_starting_position() -> chess.Board:
    """Generate a random legal starting position with WK, WR, BK."""
    while True:
        wk_sq, wr_sq, bk_sq = random.sample(chess.SQUARES, 3)

        board = chess.Board.empty()
        board.set_piece_at(wk_sq, chess.Piece(chess.KING, chess.WHITE))
        board.set_piece_at(wr_sq, chess.Piece(chess.ROOK, chess.WHITE))
        board.set_piece_at(bk_sq, chess.Piece(chess.KING, chess.BLACK))
        board.turn = chess.WHITE

        if not board.is_valid():
            continue
        if board.is_checkmate() or board.is_stalemate():
            continue
        return board


def get_game_status(board: chess.Board) -> str:
    """
    'ongoing', 'checkmate', 'stalemate', or 'insufficient_material'.

    Note: we check for the white rook directly rather than using
    board.is_insufficient_material(), because K+R vs K is not insufficient
    material in chess (the rook can mate). This simulation treats the rook
    being captured as a draw, matching the original behavior.
    """
    if not board.pieces(chess.ROOK, chess.WHITE):
        return 'insufficient_material'
    if board.is_checkmate():
        return 'checkmate'
    if board.is_stalemate():
        return 'stalemate'
    return 'ongoing'


def play_random_game(max_moves: int = 5000) -> Tuple[str, int, chess.Board]:
    """Play a random game from a random starting position."""
    board = random_starting_position()

    for ply in range(max_moves):
        moves = list(board.legal_moves)
        if not moves:
            return (get_game_status(board), ply, board)

        board.push(random.choice(moves))

        status = get_game_status(board)
        if status != 'ongoing':
            return (status, ply + 1, board)

    return ('max_moves', max_moves, board)


def run_simulation(num_games: int = 10000, max_moves: int = 5000,
                   verbose: bool = True) -> dict:
    """Run multiple random games and collect statistics."""
    results = defaultdict(int)
    move_counts = defaultdict(list)

    start_time = time.time()

    for i in range(num_games):
        if verbose and (i + 1) % 1000 == 0:
            elapsed = time.time() - start_time
            rate = (i + 1) / elapsed
            print(f"  Completed {i + 1:,} games ({rate:.0f} games/sec)...")

        result, moves, _ = play_random_game(max_moves)
        results[result] += 1
        move_counts[result].append(moves)

    elapsed = time.time() - start_time

    return {
        'num_games': num_games,
        'max_moves': max_moves,
        'elapsed_seconds': elapsed,
        'results': dict(results),
        'percentages': {k: v / num_games * 100 for k, v in results.items()},
        'avg_moves': {k: sum(v) / len(v) if v else 0 for k, v in move_counts.items()},
        'min_moves': {k: min(v) if v else 0 for k, v in move_counts.items()},
        'max_moves_seen': {k: max(v) if v else 0 for k, v in move_counts.items()},
    }


def print_results(stats: dict):
    """Pretty print simulation results."""
    print("\n" + "=" * 60)
    print("K+R vs K RANDOM MOVE SIMULATION RESULTS")
    print("=" * 60)
    print(f"\nGames simulated: {stats['num_games']:,}")
    print(f"Max moves per game: {stats['max_moves']:,}")
    print(f"Time elapsed: {stats['elapsed_seconds']:.1f} seconds")
    print(f"Speed: {stats['num_games'] / stats['elapsed_seconds']:.0f} games/second")

    print("\n" + "-" * 40)
    print("OUTCOMES:")
    print("-" * 40)

    outcome_labels = {
        'checkmate': 'Checkmate (White wins)',
        'stalemate': 'Stalemate (Draw)',
        'insufficient_material': 'Rook captured (Draw)',
        'max_moves': f'Max moves reached ({stats["max_moves"]:,})',
    }

    for outcome in ['checkmate', 'stalemate', 'insufficient_material', 'max_moves']:
        count = stats['results'].get(outcome, 0)
        if count == 0:
            continue
        pct = stats['percentages'].get(outcome, 0)
        avg = stats['avg_moves'].get(outcome, 0)
        min_m = stats['min_moves'].get(outcome, 0)
        max_m = stats['max_moves_seen'].get(outcome, 0)
        print(f"\n{outcome_labels.get(outcome, outcome)}:")
        print(f"  Count: {count:,} ({pct:.2f}%)")
        print(f"  Moves: avg={avg:.1f}, min={min_m}, max={max_m}")

    print("\n" + "=" * 60)

    n = stats['num_games']
    draws = (stats['results'].get('stalemate', 0)
             + stats['results'].get('insufficient_material', 0))
    wins = stats['results'].get('checkmate', 0)
    inconclusive = stats['results'].get('max_moves', 0)

    print("\nSUMMARY:")
    print(f"  White wins (checkmate): {wins / n * 100:.2f}%")
    print(f"  Draws (stalemate + rook captured): {draws / n * 100:.2f}%")
    if inconclusive > 0:
        print(f"  Inconclusive (hit move limit): {inconclusive / n * 100:.2f}%")
    print("=" * 60)


if __name__ == "__main__":
    print("Starting K+R vs K Random Move Simulation...")
    print("Both sides make completely random legal moves.\n")

    stats = run_simulation(num_games=10000, max_moves=200, verbose=True)
    print_results(stats)
