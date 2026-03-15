from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass
from typing import Iterator, List, Optional, Tuple

from cell import Cell, MARK_FLAG, MARK_NONE, MARK_QUESTION


@dataclass
class RevealResult:
    """Stores the outcome of a reveal action."""
    exploded: bool = False
    exploded_cell: Optional[Tuple[int, int]] = None
    changed: int = 0


class Board:
    """Manages board state and core Minesweeper rules."""
    def __init__(self, rows: int, cols: int, mines: int, playable_mask: Optional[List[List[bool]]] = None) -> None:
        """Creates a board with optional playable-cell mask."""
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.playable_mask = playable_mask
        self.grid: List[List[Cell]] = []
        self.first_move_done = False
        self.game_over = False
        self.won = False
        self.exploded_cell: Optional[Tuple[int, int]] = None
        self.revealed_safe_cells = 0
        self.placed_mines = mines
        self.playable_cells = rows * cols
        self.reset()

    def reset(self) -> None:
        """Resets cells and game state for a new match."""
        self.grid = []
        self.playable_cells = 0
        for r in range(self.rows):
            row_cells: List[Cell] = []
            for c in range(self.cols):
                playable = True
                if self.playable_mask is not None:
                    playable = bool(self.playable_mask[r][c])
                row_cells.append(Cell(playable=playable))
                if playable:
                    self.playable_cells += 1
            self.grid.append(row_cells)
        self.first_move_done = False
        self.game_over = False
        self.won = False
        self.exploded_cell = None
        self.revealed_safe_cells = 0
        self.placed_mines = min(self.mines, max(0, self.playable_cells - 1))

    def in_bounds(self, row: int, col: int) -> bool:
        """Returns True if coordinates are inside the board."""
        return 0 <= row < self.rows and 0 <= col < self.cols

    def neighbors(self, row: int, col: int) -> Iterator[Tuple[int, int]]:
        """Yields valid neighbor coordinates around a cell."""
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr = row + dr
                nc = col + dc
                if self.in_bounds(nr, nc):
                    yield nr, nc

    def _place_mines(self, first_row: int, first_col: int) -> None:
        """Places mines, excluding the first-click safe area."""
        exclusion = {
            (r, c)
            for r in range(first_row - 1, first_row + 2)
            for c in range(first_col - 1, first_col + 2)
            if self.in_bounds(r, c) and self.grid[r][c].playable
        }
        candidates = [
            (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
            if self.grid[r][c].playable and (r, c) not in exclusion
        ]
        random.shuffle(candidates)
        self.placed_mines = min(self.mines, len(candidates))
        for r, c in candidates[: self.placed_mines]:
            self.grid[r][c].has_mine = True

        for r in range(self.rows):
            for c in range(self.cols):
                if not self.grid[r][c].playable or self.grid[r][c].has_mine:
                    continue
                self.grid[r][c].adjacent_mines = sum(
                    1
                    for nr, nc in self.neighbors(r, c)
                    if self.grid[nr][nc].playable and self.grid[nr][nc].has_mine
                )

    def reveal(self, row: int, col: int) -> RevealResult:
        """Reveals a cell and applies flood-fill when needed."""
        result = RevealResult()
        if self.game_over or not self.in_bounds(row, col):
            return result

        cell = self.grid[row][col]
        if not cell.playable:
            return result
        if cell.revealed or cell.mark == MARK_FLAG:
            return result

        if not self.first_move_done:
            self._place_mines(row, col)
            self.first_move_done = True

        if cell.has_mine:
            cell.revealed = True
            self.game_over = True
            self.won = False
            self.exploded_cell = (row, col)
            result.exploded = True
            result.exploded_cell = (row, col)
            result.changed = 1
            return result

        queue = deque([(row, col)])
        while queue:
            cr, cc = queue.popleft()
            current = self.grid[cr][cc]
            if current.revealed or current.mark == MARK_FLAG:
                continue
            if not current.playable:
                continue
            if current.has_mine:
                continue
            current.revealed = True
            current.mark = MARK_NONE
            self.revealed_safe_cells += 1
            result.changed += 1

            if current.adjacent_mines == 0:
                for nr, nc in self.neighbors(cr, cc):
                    neighbor = self.grid[nr][nc]
                    if (
                        neighbor.playable
                        and not neighbor.revealed
                        and not neighbor.has_mine
                        and neighbor.mark != MARK_FLAG
                    ):
                        queue.append((nr, nc))

        self._check_win()
        return result

    def _check_win(self) -> None:
        """Marks the game as won when all safe cells are revealed."""
        safe_total = self.playable_cells - self.placed_mines
        if self.revealed_safe_cells == safe_total:
            self.game_over = True
            self.won = True

    def cycle_mark(self, row: int, col: int, enable_question: bool = True) -> None:
        """Cycles cell mark state: none -> flag -> question -> none."""
        if self.game_over or not self.in_bounds(row, col):
            return
        cell = self.grid[row][col]
        if not cell.playable:
            return
        if cell.revealed:
            return

        if cell.mark == MARK_NONE:
            cell.mark = MARK_FLAG
            return
        if cell.mark == MARK_FLAG:
            cell.mark = MARK_QUESTION if enable_question else MARK_NONE
            return
        cell.mark = MARK_NONE

    def count_flags(self) -> int:
        """Counts currently flagged cells."""
        return sum(1 for row in self.grid for cell in row if cell.mark == MARK_FLAG)

    def score_points(self) -> int:
        """Returns score based on revealed safe cells."""
        return max(0, min(999, self.revealed_safe_cells))

    def should_show_mine(self, row: int, col: int) -> bool:
        """Returns True when a mine should be rendered after loss."""
        cell = self.grid[row][col]
        if not self.game_over:
            return False
        if self.won:
            return False
        return cell.has_mine

    def is_wrong_flag(self, row: int, col: int) -> bool:
        """Returns True for incorrect flags after loss."""
        if not self.game_over or self.won:
            return False
        cell = self.grid[row][col]
        return cell.mark == MARK_FLAG and not cell.has_mine
