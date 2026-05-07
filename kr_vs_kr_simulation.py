"""
K+R vs K+R Random Move Simulation

Simulates chess endgames where each side has King + Rook.
Both sides make completely random legal moves.

Tracks outcomes: white checkmate, black checkmate, stalemate,
insufficient material (both rooks captured), and move limits.
"""

import random
from dataclasses import dataclass
from typing import List, Tuple, Optional, Set
from collections import defaultdict
import time


@dataclass(frozen=True)
class Square:
    file: int
    rank: int

    def is_valid(self) -> bool:
        return 0 <= self.file <= 7 and 0 <= self.rank <= 7

    def __str__(self) -> str:
        return f"{'abcdefgh'[self.file]}{self.rank + 1}"

    def distance(self, other: 'Square') -> int:
        return max(abs(self.file - other.file), abs(self.rank - other.rank))


@dataclass
class Position:
    white_king: Square
    white_rook: Optional[Square]
    black_king: Square
    black_rook: Optional[Square]
    white_to_move: bool = True

    def copy(self) -> 'Position':
        return Position(
            white_king=self.white_king,
            white_rook=self.white_rook,
            black_king=self.black_king,
            black_rook=self.black_rook,
            white_to_move=self.white_to_move,
        )


Move = Tuple[str, Square, Square]


def squares_between(sq1: Square, sq2: Square) -> List[Square]:
    squares = []
    if sq1.file == sq2.file:
        step = 1 if sq2.rank > sq1.rank else -1
        for r in range(sq1.rank + step, sq2.rank, step):
            squares.append(Square(sq1.file, r))
    elif sq1.rank == sq2.rank:
        step = 1 if sq2.file > sq1.file else -1
        for f in range(sq1.file + step, sq2.file, step):
            squares.append(Square(f, sq1.rank))
    return squares


def rook_attacks(square: Square, rook: Optional[Square], blockers: Set[Square]) -> bool:
    if rook is None:
        return False
    if square == rook:
        return False
    if square.file != rook.file and square.rank != rook.rank:
        return False
    for between in squares_between(rook, square):
        if between in blockers:
            return False
    return True


def king_attacks(square: Square, king: Square) -> bool:
    return square.distance(king) == 1 and square != king


def is_square_attacked(pos: Position, square: Square, by_white: bool,
                       ignore: Optional[Square] = None) -> bool:
    """
    Is `square` attacked by the given side?
    `ignore`: a square that should NOT count as a blocker (e.g. the moving
    king's old square when checking whether its destination is safe).
    """
    if by_white:
        attacker_king = pos.white_king
        attacker_rook = pos.white_rook
        other_king = pos.black_king
        other_rook = pos.black_rook
    else:
        attacker_king = pos.black_king
        attacker_rook = pos.black_rook
        other_king = pos.white_king
        other_rook = pos.white_rook

    if king_attacks(square, attacker_king):
        return True

    blockers: Set[Square] = {attacker_king, other_king}
    if other_rook is not None:
        blockers.add(other_rook)
    if ignore is not None:
        blockers.discard(ignore)

    return rook_attacks(square, attacker_rook, blockers)


def is_in_check(pos: Position, white: bool) -> bool:
    king = pos.white_king if white else pos.black_king
    return is_square_attacked(pos, king, by_white=not white)


def king_destinations(king_pos: Square) -> List[Square]:
    moves = []
    for df in (-1, 0, 1):
        for dr in (-1, 0, 1):
            if df == 0 and dr == 0:
                continue
            sq = Square(king_pos.file + df, king_pos.rank + dr)
            if sq.is_valid():
                moves.append(sq)
    return moves


def rook_destinations(rook_pos: Square, occupied: Set[Square]) -> List[Square]:
    moves = []
    for df, dr in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        for dist in range(1, 8):
            sq = Square(rook_pos.file + df * dist, rook_pos.rank + dr * dist)
            if not sq.is_valid():
                break
            if sq in occupied:
                moves.append(sq)
                break
            moves.append(sq)
    return moves


def get_legal_moves(pos: Position) -> List[Move]:
    if pos.white_to_move:
        own_king, own_rook = pos.white_king, pos.white_rook
        enemy_king, enemy_rook = pos.black_king, pos.black_rook
    else:
        own_king, own_rook = pos.black_king, pos.black_rook
        enemy_king, enemy_rook = pos.white_king, pos.white_rook

    moves: List[Move] = []

    # King moves
    for dest in king_destinations(own_king):
        if own_rook is not None and dest == own_rook:
            continue
        if dest == enemy_king:
            continue
        if dest.distance(enemy_king) <= 1:
            continue
        # If destination is the enemy rook, capturing removes it as attacker.
        captures_rook = (enemy_rook is not None and dest == enemy_rook)
        # Check if dest is attacked by enemy, treating own king's old square
        # as empty (it moved away) and ignoring a captured rook.
        temp = pos.copy()
        if pos.white_to_move:
            temp.white_king = dest
            if captures_rook:
                temp.black_rook = None
        else:
            temp.black_king = dest
            if captures_rook:
                temp.white_rook = None
        if is_in_check(temp, pos.white_to_move):
            continue
        moves.append(('K', own_king, dest))

    # Rook moves
    if own_rook is not None:
        occupied: Set[Square] = {own_king, enemy_king}
        if enemy_rook is not None:
            occupied.add(enemy_rook)
        for dest in rook_destinations(own_rook, occupied):
            if dest == own_king:
                continue
            if dest == enemy_king:
                continue  # cannot capture a king
            temp = pos.copy()
            captures_rook = (enemy_rook is not None and dest == enemy_rook)
            if pos.white_to_move:
                temp.white_rook = dest
                if captures_rook:
                    temp.black_rook = None
            else:
                temp.black_rook = dest
                if captures_rook:
                    temp.white_rook = None
            if is_in_check(temp, pos.white_to_move):
                continue
            moves.append(('R', own_rook, dest))

    return moves


def apply_move(pos: Position, move: Move) -> Position:
    piece, _from, to = move
    new_pos = pos.copy()

    if pos.white_to_move:
        if piece == 'K':
            new_pos.white_king = to
        else:  # 'R'
            new_pos.white_rook = to
        if pos.black_rook is not None and to == pos.black_rook:
            new_pos.black_rook = None
    else:
        if piece == 'K':
            new_pos.black_king = to
        else:
            new_pos.black_rook = to
        if pos.white_rook is not None and to == pos.white_rook:
            new_pos.white_rook = None

    new_pos.white_to_move = not pos.white_to_move
    return new_pos


def get_game_status(pos: Position) -> str:
    """
    'ongoing', 'white_checkmate', 'black_checkmate', 'stalemate',
    'insufficient_material'.
    """
    if pos.white_rook is None and pos.black_rook is None:
        return 'insufficient_material'

    moves = get_legal_moves(pos)
    if moves:
        return 'ongoing'

    if pos.white_to_move:
        # White has no legal moves
        return 'black_checkmate' if is_in_check(pos, white=True) else 'stalemate'
    else:
        return 'white_checkmate' if is_in_check(pos, white=False) else 'stalemate'


def random_starting_position() -> Position:
    while True:
        squares = random.sample(range(64), 4)
        wk = Square(squares[0] % 8, squares[0] // 8)
        wr = Square(squares[1] % 8, squares[1] // 8)
        bk = Square(squares[2] % 8, squares[2] // 8)
        br = Square(squares[3] % 8, squares[3] // 8)

        if wk.distance(bk) <= 1:
            continue

        pos = Position(white_king=wk, white_rook=wr,
                       black_king=bk, black_rook=br,
                       white_to_move=True)

        # Black can't already be in check when it's White's turn.
        if is_in_check(pos, white=False):
            continue
        if get_game_status(pos) != 'ongoing':
            continue
        return pos


def play_random_game(max_moves: int = 1000) -> Tuple[str, int, Position]:
    pos = random_starting_position()

    for move_num in range(max_moves):
        moves = get_legal_moves(pos)
        if not moves:
            return (get_game_status(pos), move_num, pos)

        pos = apply_move(pos, random.choice(moves))

        status = get_game_status(pos)
        if status != 'ongoing':
            return (status, move_num + 1, pos)

    return ('max_moves', max_moves, pos)


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
