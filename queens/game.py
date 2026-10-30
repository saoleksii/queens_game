"""
Game session logic for Queens puzzle.

This module handles player interactions, game state, undo functionality,
and timer.
"""

import time
from typing import Tuple, List
from queens.board import Level, BoardState, CellState


class GameSession:
    def __init__(self, level: Level):
        self.level = level
        self.board = BoardState(level)
        self.start_time = time.time()

        # Undo history implemented as a Command Pattern: (row, col, old_state, new_state)
        self.history: List[Tuple[int, int, CellState, CellState]] = []
        self.history_index = -1

    def click_cell(self, row: int, col: int, right_click: bool = False) -> bool:
        if right_click:
            # Right click toggles mark
            return self.toggle_mark(row, col)
        else:
            # Left click cycles state
            current = self.board.get_cell(row, col)

            if current == CellState.EMPTY:
                return self.place_queen(row, col)
            elif current == CellState.QUEEN:
                return self.remove_queen(row, col)
            return False

    def place_queen(self, row: int, col: int) -> bool:
        old_state = self.board.get_cell(row, col)
        if not self.board.place_queen(row, col):
            return False

        self._save_state(row, col, old_state, CellState.QUEEN)
        return True

    def remove_queen(self, row: int, col: int) -> bool:
        old_state = self.board.get_cell(row, col)
        if not self.board.remove_queen(row, col):
            return False

        self._save_state(row, col, old_state, CellState.EMPTY)
        return True

    def toggle_mark(self, row: int, col: int) -> bool:
        old_state = self.board.get_cell(row, col)
        new_state = self.board.toggle_mark(row, col)
        
        # If the cell remained unaffected (e.g. was a QUEEN), don't log a command
        if old_state == new_state:
            return False

        self._save_state(row, col, old_state, new_state)
        return True

    def undo(self) -> bool:
        if self.history_index >= 0:
            row, col, old_state, _ = self.history[self.history_index]
            self.board.set_cell(row, col, old_state)
            self.history_index -= 1
            return True

        return False

    def redo(self) -> bool:
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            row, col, _, new_state = self.history[self.history_index]
            self.board.set_cell(row, col, new_state)
            return True

        return False

    def is_won(self) -> bool:
        return self.board.is_solved()

    def get_conflicts(self) -> List[Tuple[int, int]]:
        return self.board.find_conflicts()

    def elapsed_time(self) -> float:
        return time.time() - self.start_time

    def can_undo(self) -> bool:
        return self.history_index >= 0

    def can_redo(self) -> bool:
        return self.history_index < len(self.history) - 1

    def _save_state(self, row: int, col: int, old_state: CellState, new_state: CellState):
        # Truncate forward-history (redo states) if we mutate the timeline
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]

        self.history.append((row, col, old_state, new_state))
        self.history_index += 1