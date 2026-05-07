"""
K+R vs K+R Random Move Simulation

Simulates chess endgames where each side has King + Rook.
Both sides make completely random legal moves.

Tracks outcomes: white checkmate, black checkmate, stalemate,
insufficient material (both rooks captured), and move limits.

Legal-move generation, turn tracking, and check/checkmate detection are
delegated to python-chess. The 50-move rule and threefold repetition are
deliberately not consulted.
"""

import random
import time
from collections import defaultdict
from typing import Tuple

import chess


def random_starting_position() -> chess.Board:
    """Generate a random legal starting position with WK, WR, BK, BR."""
    while True:
        wk_sq, wr_sq, bk_sq, br_sq = random.sample(chess.SQUARES, 4)

        board = chess.Board.empty()
        board.set_piece_at(wk_sq, chess.Piece(chess.KING, chess.WHITE))
        board.set_piece_at(wr_sq, chess.Piece(chess.ROOK, chess.WHITE))
        board.set_piece_at(bk_sq, chess.Piece(chess.KING, chess.BLACK))
        board.set_piece_at(br_sq, chess.Piece(chess.ROOK, chess.BLACK))
        board.turn = chess.WHITE

        if not board.is_valid():
            continue
        if board.is_checkmate() or board.is_stalemate():
            continue
        return board


def get_game_status(board: chess.Board) -> str:
    """
    'ongoing', 'white_checkmate', 'black_checkmate', 'stalemate',
    or 'insufficient_material'.

    After board.push(move), board.turn is the side that has just been
    handed the move (i.e. the side that was potentially mated).
    """
    white_rook_gone = not board.pieces(chess.ROOK, chess.WHITE)
    black_rook_gone = not board.pieces(chess.ROOK, chess.BLACK)
    if white_rook_gone and black_rook_gone:
        return 'insufficient_material'

    if board.is_checkmate():
        return 'white_checkmate' if board.turn == chess.WHITE else 'black_checkmate'
    if board.is_stalemate():
        return 'stalemate'
    return 'ongoing'


def play_random_game(max_moves: int = 1000) -> Tuple[str, int, chess.Board]:
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


def run_simulation(num_games: int = 10000, max_moves: int = 1000,
                   verbose: bool = True) -> dict:
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
    print("\n" + "=" * 60)
    print("K+R vs K+R RANDOM MOVE SIMULATION RESULTS")
    print("=" * 60)
    print(f"\nGames simulated: {stats['num_games']:,}")
    print(f"Max moves per game: {stats['max_moves']:,}")
    print(f"Time elapsed: {stats['elapsed_seconds']:.1f} seconds")
    print(f"Speed: {stats['num_games'] / stats['elapsed_seconds']:.0f} games/second")

    print("\n" + "-" * 40)
    print("OUTCOMES:")
    print("-" * 40)

    outcome_labels = {
        'white_checkmate': 'White checkmated (Black wins)',
        'black_checkmate': 'Black checkmated (White wins)',
        'stalemate': 'Stalemate (Draw)',
        'insufficient_material': 'Both rooks captured (Draw)',
        'max_moves': f'Max moves reached ({stats["max_moves"]:,})',
    }

    for outcome in ['black_checkmate', 'white_checkmate', 'stalemate',
                    'insufficient_material', 'max_moves']:
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
    white_wins = stats['results'].get('black_checkmate', 0)
    black_wins = stats['results'].get('white_checkmate', 0)
    draws = (stats['results'].get('stalemate', 0)
             + stats['results'].get('insufficient_material', 0))
    inconclusive = stats['results'].get('max_moves', 0)

    print("\nSUMMARY:")
    print(f"  White wins: {white_wins / n * 100:.2f}%")
    print(f"  Black wins: {black_wins / n * 100:.2f}%")
    print(f"  Draws (stalemate + both rooks captured): {draws / n * 100:.2f}%")
    if inconclusive > 0:
        print(f"  Inconclusive (hit move limit): {inconclusive / n * 100:.2f}%")
    print("=" * 60)


if __name__ == "__main__":
    print("Starting K+R vs K+R Random Move Simulation...")
    print("Both sides make completely random legal moves.\n")

    stats = run_simulation(num_games=10000, max_moves=200, verbose=True)
    print_results(stats)
