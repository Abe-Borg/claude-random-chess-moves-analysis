"""
K+R vs K Random Move Simulation

Simulates chess endgames where White has King + Rook vs Black's lone King.
Both sides make completely random legal moves.

Tracks outcomes: checkmate, stalemate, rook captured, and move limits.
"""

import random
from dataclasses import dataclass
from typing import List, Tuple, Optional, Set
from collections import defaultdict
import time


@dataclass(frozen=True)
class Square:
    """Represents a chess square (0-7 for both file and rank)."""
    file: int  # 0-7 (a-h)
    rank: int  # 0-7 (1-8)
    
    def is_valid(self) -> bool:
        return 0 <= self.file <= 7 and 0 <= self.rank <= 7
    
    def __str__(self) -> str:
        return f"{'abcdefgh'[self.file]}{self.rank + 1}"
    
    def distance(self, other: 'Square') -> int:
        """Chebyshev distance (king distance)."""
        return max(abs(self.file - other.file), abs(self.rank - other.rank))


@dataclass
class Position:
    """
    Represents a K+R vs K position.
    White: King + Rook
    Black: King only
    """
    white_king: Square
    white_rook: Optional[Square]  # None if captured
    black_king: Square
    white_to_move: bool = True
    
    def copy(self) -> 'Position':
        return Position(
            white_king=self.white_king,
            white_rook=self.white_rook,
            black_king=self.black_king,
            white_to_move=self.white_to_move
        )


def squares_between(sq1: Square, sq2: Square) -> List[Square]:
    """Returns squares strictly between sq1 and sq2 (for rook moves)."""
    squares = []
    
    if sq1.file == sq2.file:  # Same file (vertical)
        step = 1 if sq2.rank > sq1.rank else -1
        for r in range(sq1.rank + step, sq2.rank, step):
            squares.append(Square(sq1.file, r))
    elif sq1.rank == sq2.rank:  # Same rank (horizontal)
        step = 1 if sq2.file > sq1.file else -1
        for f in range(sq1.file + step, sq2.file, step):
            squares.append(Square(f, sq1.rank))
    
    return squares


def is_attacked_by_rook(square: Square, rook: Optional[Square], blocking_squares: Set[Square]) -> bool:
    """Check if a square is attacked by the rook."""
    if rook is None:
        return False
    
    if square.file != rook.file and square.rank != rook.rank:
        return False  # Not on same file or rank
    
    if square == rook:
        return False
    
    # Check for blockers
    for between in squares_between(rook, square):
        if between in blocking_squares:
            return False
    
    return True


def is_attacked_by_king(square: Square, king: Square) -> bool:
    """Check if a square is attacked by a king."""
    return square.distance(king) == 1


def is_square_attacked_by_white(pos: Position, square: Square) -> bool:
    """Check if a square is attacked by white pieces."""
    # Attacked by white king?
    if is_attacked_by_king(square, pos.white_king):
        return True
    
    # Attacked by rook?
    blocking = {pos.white_king, pos.black_king}
    if is_attacked_by_rook(square, pos.white_rook, blocking):
        return True
    
    return False


def is_black_king_in_check(pos: Position) -> bool:
    """Is the black king in check?"""
    return is_square_attacked_by_white(pos, pos.black_king)


def get_king_moves(king_pos: Square) -> List[Square]:
    """Get all potential king destination squares (not checking legality)."""
    moves = []
    for df in [-1, 0, 1]:
        for dr in [-1, 0, 1]:
            if df == 0 and dr == 0:
                continue
            new_sq = Square(king_pos.file + df, king_pos.rank + dr)
            if new_sq.is_valid():
                moves.append(new_sq)
    return moves


def get_rook_moves(rook_pos: Square, occupied: Set[Square]) -> List[Square]:
    """Get all potential rook destination squares."""
    moves = []
    
    # Four directions: up, down, left, right
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    
    for df, dr in directions:
        for dist in range(1, 8):
            new_sq = Square(rook_pos.file + df * dist, rook_pos.rank + dr * dist)
            if not new_sq.is_valid():
                break
            if new_sq in occupied:
                moves.append(new_sq)  # Can capture
                break
            moves.append(new_sq)
    
    return moves


def get_white_legal_moves(pos: Position) -> List[Tuple[str, Square, Square]]:
    """
    Get all legal moves for White.
    Returns list of (piece, from_square, to_square).
    """
    moves = []
    occupied = {pos.white_king, pos.black_king}
    if pos.white_rook:
        occupied.add(pos.white_rook)
    
    # White King moves
    for dest in get_king_moves(pos.white_king):
        # Can't move onto own rook
        if dest == pos.white_rook:
            continue
        # Can't move adjacent to black king
        if dest.distance(pos.black_king) <= 1:
            continue
        # Can't move onto black king (would be adjacent anyway)
        if dest == pos.black_king:
            continue
        
        # After moving, is white king attacked? (Only by black king, which we checked)
        moves.append(('K', pos.white_king, dest))
    
    # White Rook moves
    if pos.white_rook:
        for dest in get_rook_moves(pos.white_rook, {pos.white_king, pos.black_king}):
            # Can't capture own king
            if dest == pos.white_king:
                continue
            # Can capture black king? Actually no - that's not a legal position to reach
            # The black king can't be in check at start of white's turn... wait, this is white's turn
            # Actually we need to check: after rook moves, is white king in check? 
            # Black has no rook, so white king can never be in check. Skip this check.
            moves.append(('R', pos.white_rook, dest))
    
    return moves


def get_black_legal_moves(pos: Position) -> List[Tuple[str, Square, Square]]:
    """
    Get all legal moves for Black (lone king).
    Returns list of (piece, from_square, to_square).
    """
    moves = []
    
    for dest in get_king_moves(pos.black_king):
        # Can't move adjacent to white king
        if dest.distance(pos.white_king) <= 1:
            continue
        
        # Can capture the rook?
        captures_rook = (dest == pos.white_rook)
        
        # If not capturing rook, check if destination is attacked
        if not captures_rook:
            # Check if dest is attacked by white
            # After black king moves, check attack status
            temp_pos = pos.copy()
            temp_pos.black_king = dest
            if is_square_attacked_by_white(temp_pos, dest):
                continue  # Can't move into check
        else:
            # Capturing rook - is the rook defended by white king?
            if dest.distance(pos.white_king) <= 1:
                continue  # Rook is defended, can't capture
        
        moves.append(('k', pos.black_king, dest))
    
    return moves


def apply_move(pos: Position, move: Tuple[str, Square, Square]) -> Position:
    """Apply a move and return new position."""
    piece, from_sq, to_sq = move
    new_pos = pos.copy()
    
    if piece == 'K':
        new_pos.white_king = to_sq
    elif piece == 'R':
        new_pos.white_rook = to_sq
    elif piece == 'k':
        new_pos.black_king = to_sq
        # Check if capturing rook
        if to_sq == pos.white_rook:
            new_pos.white_rook = None
    
    new_pos.white_to_move = not pos.white_to_move
    return new_pos


def get_game_status(pos: Position) -> str:
    """
    Determine game status.
    Returns: 'ongoing', 'checkmate', 'stalemate', 'insufficient_material'
    """
    # Rook captured?
    if pos.white_rook is None:
        return 'insufficient_material'
    
    # Check for checkmate/stalemate (only relevant on black's turn)
    if not pos.white_to_move:
        black_moves = get_black_legal_moves(pos)
        if len(black_moves) == 0:
            if is_black_king_in_check(pos):
                return 'checkmate'
            else:
                return 'stalemate'
    
    return 'ongoing'


def random_starting_position() -> Position:
    """Generate a random legal starting position."""
    while True:
        # Place three pieces randomly
        squares = random.sample(range(64), 3)
        
        wk = Square(squares[0] % 8, squares[0] // 8)
        wr = Square(squares[1] % 8, squares[1] // 8)
        bk = Square(squares[2] % 8, squares[2] // 8)
        
        # Kings can't be adjacent
        if wk.distance(bk) <= 1:
            continue
        
        pos = Position(white_king=wk, white_rook=wr, black_king=bk, white_to_move=True)
        
        # Black king can't be in check initially (it's white's turn, so this is fine)
        # Actually, we want positions where it's not immediately checkmate
        status = get_game_status(pos)
        if status == 'ongoing':
            return pos


def play_random_game(max_moves: int = 5000) -> Tuple[str, int, Position]:
    """
    Play a random game from a random starting position.
    Returns (result, num_moves, final_position).
    """
    pos = random_starting_position()
    
    for move_num in range(max_moves):
        # Get legal moves for current side
        if pos.white_to_move:
            moves = get_white_legal_moves(pos)
        else:
            moves = get_black_legal_moves(pos)
        
        if len(moves) == 0:
            # This shouldn't happen for white (always has king moves)
            # For black, this is checkmate or stalemate
            status = get_game_status(pos)
            return (status, move_num, pos)
        
        # Make random move
        move = random.choice(moves)
        pos = apply_move(pos, move)
        
        # Check game status after move
        status = get_game_status(pos)
        if status != 'ongoing':
            return (status, move_num + 1, pos)
    
    return ('max_moves', max_moves, pos)


def run_simulation(num_games: int = 10000, max_moves: int = 5000, verbose: bool = True) -> dict:
    """Run multiple random games and collect statistics."""
    
    results = defaultdict(int)
    move_counts = defaultdict(list)
    
    start_time = time.time()
    
    for i in range(num_games):
        if verbose and (i + 1) % 1000 == 0:
            elapsed = time.time() - start_time
            rate = (i + 1) / elapsed
            print(f"  Completed {i + 1:,} games ({rate:.0f} games/sec)...")
        
        result, moves, final_pos = play_random_game(max_moves)
        results[result] += 1
        move_counts[result].append(moves)
    
    elapsed = time.time() - start_time
    
    # Compile statistics
    stats = {
        'num_games': num_games,
        'max_moves': max_moves,
        'elapsed_seconds': elapsed,
        'results': dict(results),
        'percentages': {k: v / num_games * 100 for k, v in results.items()},
        'avg_moves': {k: sum(v) / len(v) if v else 0 for k, v in move_counts.items()},
        'min_moves': {k: min(v) if v else 0 for k, v in move_counts.items()},
        'max_moves_seen': {k: max(v) if v else 0 for k, v in move_counts.items()},
    }
    
    return stats


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
        pct = stats['percentages'].get(outcome, 0)
        avg = stats['avg_moves'].get(outcome, 0)
        min_m = stats['min_moves'].get(outcome, 0)
        max_m = stats['max_moves_seen'].get(outcome, 0)
        
        if count > 0:
            print(f"\n{outcome_labels.get(outcome, outcome)}:")
            print(f"  Count: {count:,} ({pct:.2f}%)")
            print(f"  Moves: avg={avg:.1f}, min={min_m}, max={max_m}")
    
    print("\n" + "=" * 60)
    
    # Summary
    draws = stats['results'].get('stalemate', 0) + stats['results'].get('insufficient_material', 0)
    wins = stats['results'].get('checkmate', 0)
    inconclusive = stats['results'].get('max_moves', 0)
    
    print("\nSUMMARY:")
    print(f"  White wins (checkmate): {wins / stats['num_games'] * 100:.2f}%")
    print(f"  Draws (stalemate + rook captured): {draws / stats['num_games'] * 100:.2f}%")
    if inconclusive > 0:
        print(f"  Inconclusive (hit move limit): {inconclusive / stats['num_games'] * 100:.2f}%")
    print("=" * 60)


if __name__ == "__main__":
    print("Starting K+R vs K Random Move Simulation...")
    print("Both sides make completely random legal moves.\n")
    
    # Run simulation
    stats = run_simulation(num_games=100000, max_moves=10000, verbose=True)
    
    # Print results
    print_results(stats)