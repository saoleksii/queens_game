"""
Backtracking solver for Queens puzzle.

This module implements a step-by-step backtracking algorithm that solves
Queens puzzles and can be visualized as it progresses.
"""

from enum import Enum
from typing import Iterator, Optional, Tuple, List
from queens.board import Level, BoardState


class StepKind(Enum):
    """Types of steps the solver can take."""
    PLACE = 'place'
    REMOVE = 'remove'
    SOLVED = 'solved'
    PRUNE = 'prune'


class Step:
    def __init__(self, kind: StepKind, cell: Optional[Tuple[int, int]], board_state: BoardState):
        self.kind = kind
        self.cell = cell
        self.board_state = board_state


class Solver:
    def __init__(self, level: Level):
        self.level = level
        self.size = level.size
        self._step_count = 0
        self._backtrack_count = 0
        self._solution_found = False
        self._conflict_counts = [[0] * self.size for _ in range(self.size)]

    def solve(self) -> Iterator[Step]:
        self._step_count = 0
        self._backtrack_count = 0
        self._solution_found = False
        self._conflict_counts = [[0] * self.size for _ in range(self.size)]

        board = BoardState(self.level)
        # Pass a list of all unassigned rows to start
        yield from self._backtrack(board, list(range(self.size)))

    def _update_conflicts(self, row: int, col: int, delta: int):
        """Update domain constraints using reference counting (delta is +1 or -1)."""
        # Column
        for r in range(self.size):
            self._conflict_counts[r][col] += delta
            
        # Region
        region_id = self.level.regions[row][col]
        for r, c in self.level.get_region_cells(region_id):
            self._conflict_counts[r][c] += delta
            
        # Adjacency
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.size and 0 <= nc < self.size:
                    self._conflict_counts[nr][nc] += delta

    def _backtrack(self, board: BoardState, unassigned_rows: List[int]) -> Iterator[Step]:
        # Base case: all rows have been assigned a queen
        if not unassigned_rows:
            self._solution_found = True
            yield Step(StepKind.SOLVED, None, board)
            return

        # Find the row with the fewest available safe cells
        best_row = -1
        min_safe_cells = float('inf')

        for r in unassigned_rows:
            safe_count = 0
            for c in range(self.size):
                if self._conflict_counts[r][c] == 0:
                    safe_count += 1
            
            # Pruning if 0 safe cell
            if safe_count == 0:
                yield Step(StepKind.PRUNE, (r, -1), board)
                return
            
            # Track the most constrained row
            if safe_count < min_safe_cells:
                min_safe_cells = safe_count
                best_row = r

        # Create the next list of rows, removing the one we are about to process
        next_unassigned = unassigned_rows.copy()
        next_unassigned.remove(best_row)

        # Try placing a queen in each valid column of the highly-constrained row
        for col in range(self.size):
            if self._conflict_counts[best_row][col] == 0:
                # Place the queen
                board.place_queen(best_row, col)
                self._update_conflicts(best_row, col, 1)
                self._step_count += 1

                # Yield reference so UI can process delta
                yield Step(StepKind.PLACE, (best_row, col), board)

                # Recurse with the remaining unassigned rows
                yield from self._backtrack(board, next_unassigned)
                
                # Stop processing if deep recursion found the solution
                if self._solution_found:
                    return

                # Backtrack: remove the queen
                self._update_conflicts(best_row, col, -1)
                board.remove_queen(best_row, col)
                self._backtrack_count += 1

                yield Step(StepKind.REMOVE, (best_row, col), board)


def solve(level: Level) -> Iterator[Step]:
    solver = Solver(level)
    yield from solver.solve()