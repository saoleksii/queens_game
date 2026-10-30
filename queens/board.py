"""
Board state and level representation for Queens puzzle.

This module defines Level (the puzzle definition) and BoardState (the mutable
game state), along with validation and conflict detection.
"""

from enum import Enum
from typing import List, Tuple, Dict


class CellState(Enum):
    """Possible states of a cell in the board."""
    EMPTY = 0
    QUEEN = 1
    MARK = 2


class Level:
    def __init__(self, size: int, regions: List[List[int]]):
        self.size = size
        self.regions = [row[:] for row in regions]
        # region: coordinates of its cells
        self.region_cells: Dict[int, List[Tuple[int, int]]] = {}
        for r in range(size):
            for c in range(size):
                reg_id = self.regions[r][c]
                if reg_id not in self.region_cells:
                    self.region_cells[reg_id] = []
                self.region_cells[reg_id].append((r, c))
                
        self._validate()

    def _validate(self):
        # Check grid dimensions
        if len(self.regions) != self.size:
            raise ValueError(f"Expected {self.size} rows, got {len(self.regions)}")

        for i, row in enumerate(self.regions):
            if len(row) != self.size:
                raise ValueError(f"Row {i} has length {len(row)}, expected {self.size}")

        # Check that all N regions are present
        used_regions = set(self.region_cells.keys())
        if len(used_regions) != self.size:
            raise ValueError(f"Expected {self.size} regions, found {len(used_regions)}")
            
        for region_id in used_regions:
            if not isinstance(region_id, int) or region_id < 0 or region_id >= self.size:
                raise ValueError(f"Invalid region ID: {region_id}")

        # Check that each region is connected
        for region_id in range(self.size):
            if not self._is_region_connected(region_id):
                raise ValueError(f"Region {region_id} is not connected")

    def _is_region_connected(self, region_id: int) -> bool:
        cells = self.region_cells.get(region_id, [])
        if not cells:
            return False

        # BFS
        visited = {cells[0]}
        queue = [cells[0]]

        while queue:
            i, j = queue.pop(0)
            for di, dj in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                ni, nj = i + di, j + dj
                if (0 <= ni < self.size and 0 <= nj < self.size
                    and self.regions[ni][nj] == region_id
                    and (ni, nj) not in visited):
                        visited.add((ni, nj))
                        queue.append((ni, nj))

        return len(visited) == len(cells)

    def get_region_cells(self, region_id: int) -> List[Tuple[int, int]]:
        return self.region_cells.get(region_id, [])

class BoardState:
    def __init__(self, level: Level):
        self.level = level
        self.size = level.size
        self.cells: List[List[CellState]] = [
            [CellState.EMPTY for _ in range(self.size)]
            for _ in range(self.size)
        ]

    def place_queen(self, row: int, col: int) -> bool:
        if self.cells[row][col] != CellState.EMPTY:
            return False

        self.cells[row][col] = CellState.QUEEN
        return True

    def remove_queen(self, row: int, col: int) -> bool:
        if self.cells[row][col] != CellState.QUEEN:
            return False

        self.cells[row][col] = CellState.EMPTY
        return True

    def toggle_mark(self, row: int, col: int) -> CellState:
        if self.cells[row][col] == CellState.QUEEN:
            return CellState.QUEEN

        if self.cells[row][col] == CellState.MARK:
            self.cells[row][col] = CellState.EMPTY
        else:
            self.cells[row][col] = CellState.MARK

        return self.cells[row][col]

    def set_cell(self, row: int, col: int, state: CellState) -> None:
        """Explicit command setter added for history playback without checking rules"""
        self.cells[row][col] = state

    def get_cell(self, row: int, col: int) -> CellState:
        return self.cells[row][col]

    def find_conflicts(self) -> List[Tuple[int, int]]:
        conflicts = set()
        queens = self.get_queen_cells()

        # Check row and column conflicts quickly via dictionary counts
        rows_with_queens = {}
        cols_with_queens = {}
        regions_with_queens = {}

        for row, col in queens:
            rows_with_queens.setdefault(row, []).append((row, col))
            cols_with_queens.setdefault(col, []).append((row, col))
            
            region_id = self.level.regions[row][col]
            regions_with_queens.setdefault(region_id, []).append((row, col))

        for cells in rows_with_queens.values():
            if len(cells) > 1:
                conflicts.update(cells)

        for cells in cols_with_queens.values():
            if len(cells) > 1:
                conflicts.update(cells)

        for cells in regions_with_queens.values():
            if len(cells) > 1:
                conflicts.update(cells)

        for row, col in queens:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = row + dr, col + dc
                    if (0 <= nr < self.size and 0 <= nc < self.size and self.cells[nr][nc] == CellState.QUEEN):
                        conflicts.add((row, col))
                        conflicts.add((nr, nc))

        return sorted(list(conflicts))

    def get_queen_cells(self) -> List[Tuple[int, int]]:
        queens = []
        for i in range(self.size):
            for j in range(self.size):
                if self.cells[i][j] == CellState.QUEEN:
                    queens.append((i, j))
        return queens

    def get_marked_cells(self) -> List[Tuple[int, int]]:
        marked = []
        for i in range(self.size):
            for j in range(self.size):
                if self.cells[i][j] == CellState.MARK:
                    marked.append((i, j))
        return marked

    def is_solved(self) -> bool:
        queens = self.get_queen_cells()

        if len(queens) != self.size:
            return False

        return len(self.find_conflicts()) == 0