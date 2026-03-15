from __future__ import annotations

from typing import Tuple

import pygame

import settings
from board import Board
from cell import MARK_FLAG, MARK_QUESTION


FACE_NORMAL = "normal"
FACE_SURPRISED = "surprised"
FACE_DEAD = "dead"
FACE_WIN = "win"
FACE_PRESSED = "pressed"


class UI:
    """Draws HUD, board, cells, and popup elements."""
    def __init__(self, board_width: int, board_height: int) -> None:
        """Builds layout rects and fonts."""
        self.board_width = board_width
        self.board_height = board_height

        self.window_width = settings.BORDER * 2 + board_width
        self.window_height = settings.BORDER * 2 + settings.HUD_HEIGHT + board_height

        self.hud_rect = pygame.Rect(
            settings.BORDER,
            settings.BORDER,
            board_width,
            settings.HUD_HEIGHT,
        )
        self.board_rect = pygame.Rect(
            settings.BORDER,
            settings.BORDER + settings.HUD_HEIGHT,
            board_width,
            board_height,
        )

        self.face_rect = pygame.Rect(0, 0, 42, 42)
        self.face_rect.center = self.hud_rect.center

        self.number_font = pygame.font.SysFont("arial", max(14, int(settings.CELL_SIZE * 0.62)), bold=True)
        self.popup_title_font = pygame.font.SysFont("arial", 28, bold=True)
        self.popup_text_font = pygame.font.SysFont("arial", 20, bold=False)
        self.popup_btn_font = pygame.font.SysFont("arial", 20, bold=True)

    def draw_window_frame(self, screen: pygame.Surface) -> None:
        """Draws the outer window frame."""
        screen.fill(settings.WINDOW_BG)
        outer = pygame.Rect(0, 0, self.window_width, self.window_height)
        pygame.draw.rect(screen, settings.FRAME_DARK, outer, 2)
        inner = outer.inflate(-2, -2)
        pygame.draw.rect(screen, settings.FRAME_LIGHT, inner, 2)

    def draw_hud(self, screen: pygame.Surface, score: int, seconds: int, face_state: str) -> None:
        """Draws score, timer, and face on the top HUD."""
        pygame.draw.rect(screen, settings.HUD_BG, self.hud_rect)
        inner = self.hud_rect.inflate(-8, -8)
        pygame.draw.rect(screen, settings.HUD_INNER, inner)

        left_counter_rect = pygame.Rect(inner.left + 8, inner.centery - 22, 86, 44)
        right_counter_rect = pygame.Rect(inner.right - 8 - 86, inner.centery - 22, 86, 44)
        self._draw_counter(screen, left_counter_rect, score)
        self._draw_counter(screen, right_counter_rect, min(999, seconds))
        self._draw_face(screen, face_state)

    def _draw_counter(self, screen: pygame.Surface, rect: pygame.Rect, value: int) -> None:
        """Draws a 3-digit seven-segment-style counter."""
        pygame.draw.rect(screen, settings.COUNTER_BG, rect)
        pygame.draw.rect(screen, (74, 48, 48), rect, 2)
        value = max(-99, min(999, value))
        s = f"{value:03d}" if value >= 0 else f"-{abs(value):02d}"

        digit_w = rect.width // 3
        for i, ch in enumerate(s):
            drect = pygame.Rect(rect.left + i * digit_w + 3, rect.top + 4, digit_w - 6, rect.height - 8)
            self._draw_7seg_digit(screen, drect, ch)

    def _draw_7seg_digit(self, screen: pygame.Surface, rect: pygame.Rect, ch: str) -> None:
        """Draws one seven-segment digit character."""
        # If you're an electronics engineer, you'll understand this better.
        segments_for = {
            "0": "abcedf",
            "1": "bc",
            "2": "abged",
            "3": "abgcd",
            "4": "fgbc",
            "5": "afgcd",
            "6": "afgecd",
            "7": "abc",
            "8": "abcdefg",
            "9": "abfgcd",
            "-": "g",
        }
        active = set(segments_for.get(ch, ""))
        x, y, w, h = rect
        t = max(2, w // 6)

        seg_rects = {
            "a": pygame.Rect(x + t, y, w - 2 * t, t),
            "b": pygame.Rect(x + w - t, y + t, t, h // 2 - t),
            "c": pygame.Rect(x + w - t, y + h // 2, t, h // 2 - t),
            "d": pygame.Rect(x + t, y + h - t, w - 2 * t, t),
            "e": pygame.Rect(x, y + h // 2, t, h // 2 - t),
            "f": pygame.Rect(x, y + t, t, h // 2 - t),
            "g": pygame.Rect(x + t, y + h // 2 - t // 2, w - 2 * t, t),
        }

        for seg, srect in seg_rects.items():
            color = settings.COUNTER_RED if seg in active else (64, 22, 22)
            pygame.draw.rect(screen, color, srect)

    def _draw_face(self, screen: pygame.Surface, state: str) -> None:
        """Draws the center face according to game state."""
        fill = (197, 209, 118)
        if state == FACE_PRESSED:
            fill = (171, 186, 102)
        pygame.draw.rect(screen, fill, self.face_rect)
        pygame.draw.rect(screen, (47, 57, 31), self.face_rect, 2)

        cx, cy = self.face_rect.center
        pygame.draw.circle(screen, (38, 45, 30), (cx - 8, cy - 6), 2)
        pygame.draw.circle(screen, (38, 45, 30), (cx + 8, cy - 6), 2)

        if state == FACE_DEAD:
            pygame.draw.line(screen, (38, 45, 30), (cx - 12, cy - 10), (cx - 4, cy - 2), 2)
            pygame.draw.line(screen, (38, 45, 30), (cx - 12, cy - 2), (cx - 4, cy - 10), 2)
            pygame.draw.line(screen, (38, 45, 30), (cx + 4, cy - 10), (cx + 12, cy - 2), 2)
            pygame.draw.line(screen, (38, 45, 30), (cx + 4, cy - 2), (cx + 12, cy - 10), 2)
            pygame.draw.arc(screen, (38, 45, 30), (cx - 10, cy + 2, 20, 12), 3.2, 6.2, 2)
            return

        if state == FACE_SURPRISED:
            pygame.draw.circle(screen, (38, 45, 30), (cx, cy + 8), 4, 2)
            return

        if state == FACE_WIN:
            pygame.draw.rect(screen, (31, 39, 29), (cx - 12, cy - 10, 9, 4))
            pygame.draw.rect(screen, (31, 39, 29), (cx + 3, cy - 10, 9, 4))
            pygame.draw.arc(screen, (38, 45, 30), (cx - 10, cy + 1, 20, 14), 0.15, 2.95, 2)
            return

        pygame.draw.arc(screen, (38, 45, 30), (cx - 10, cy + 1, 20, 12), 0.2, 2.9, 2)

    def draw_board(self, screen: pygame.Surface, board: Board, map_surface: pygame.Surface) -> None:
        """Draws map background and all board cells."""
        screen.blit(map_surface, self.board_rect.topleft)

        reveal_tint = pygame.Surface((settings.CELL_SIZE, settings.CELL_SIZE), pygame.SRCALPHA)
        reveal_tint.fill(settings.REVEALED_OVERLAY)
        covered_tint = pygame.Surface((settings.CELL_SIZE, settings.CELL_SIZE), pygame.SRCALPHA)
        covered_tint.fill((*settings.COVERED_BASE, settings.COVERED_ALPHA))

        for r in range(board.rows):
            for c in range(board.cols):
                self._draw_cell(screen, board, r, c, reveal_tint, covered_tint)

        pygame.draw.rect(screen, settings.REVEALED_BORDER, self.board_rect, 1)

    def _draw_cell(
        self,
        screen: pygame.Surface,
        board: Board,
        row: int,
        col: int,
        reveal_tint: pygame.Surface,
        covered_tint: pygame.Surface,
    ) -> None:
        """Draws one board cell with overlays and symbols."""
        x = self.board_rect.x + col * settings.CELL_SIZE
        y = self.board_rect.y + row * settings.CELL_SIZE
        rect = pygame.Rect(x, y, settings.CELL_SIZE, settings.CELL_SIZE)
        cell = board.grid[row][col]
        if not cell.playable:
            return

        if cell.revealed:
            if board.exploded_cell == (row, col):
                pygame.draw.rect(screen, settings.MINE_EXPLODED_BG, rect)
            else:
                screen.blit(reveal_tint, rect.topleft)
            pygame.draw.rect(screen, settings.REVEALED_BORDER, rect, 1)
        else:
            screen.blit(covered_tint, rect.topleft)
            pygame.draw.line(screen, settings.COVERED_LIGHT, rect.topleft, rect.topright, 2)
            pygame.draw.line(screen, settings.COVERED_LIGHT, rect.topleft, rect.bottomleft, 2)
            pygame.draw.line(screen, settings.COVERED_DARK, (rect.left, rect.bottom - 1), rect.bottomright, 2)
            pygame.draw.line(screen, settings.COVERED_DARK, (rect.right - 1, rect.top), rect.bottomright, 2)

        if board.should_show_mine(row, col):
            self._draw_mine(screen, rect)

        if cell.mark == MARK_FLAG and not cell.revealed:
            self._draw_flag(screen, rect)
        elif cell.mark == MARK_QUESTION and not cell.revealed:
            self._draw_question(screen, rect)

        if board.is_wrong_flag(row, col):
            pygame.draw.rect(screen, settings.WRONG_FLAG_BG, rect, 0)
            self._draw_flag(screen, rect)
            pygame.draw.line(screen, (120, 36, 36), rect.topleft, rect.bottomright, 2)
            pygame.draw.line(screen, (120, 36, 36), rect.topright, rect.bottomleft, 2)

        if cell.revealed and not cell.has_mine and cell.adjacent_mines > 0:
            color = settings.NUMBER_COLORS.get(cell.adjacent_mines, (25, 25, 25))
            text = self.number_font.render(str(cell.adjacent_mines), True, color)
            trect = text.get_rect(center=rect.center)
            screen.blit(text, trect)

        # Thin grid for readability.
        g = pygame.Surface((settings.CELL_SIZE, settings.CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.line(g, settings.GRID_LINE, (0, 0), (settings.CELL_SIZE, 0), 1)
        pygame.draw.line(g, settings.GRID_LINE, (0, 0), (0, settings.CELL_SIZE), 1)
        screen.blit(g, rect.topleft)

    def _draw_flag(self, screen: pygame.Surface, rect: pygame.Rect) -> None:
        """Draws a flag symbol."""
        mast_x = rect.left + rect.width // 2 - 4
        pygame.draw.line(screen, settings.FLAG_DARK, (mast_x, rect.top + 6), (mast_x, rect.bottom - 7), 2)
        pygame.draw.polygon(
            screen,
            settings.FLAG_RED,
            [
                (mast_x, rect.top + 6),
                (rect.left + rect.width - 7, rect.top + 11),
                (mast_x, rect.top + 17),
            ],
        )
        pygame.draw.rect(screen, settings.FLAG_DARK, (mast_x - 4, rect.bottom - 8, 10, 3))

    def _draw_question(self, screen: pygame.Surface, rect: pygame.Rect) -> None:
        """Draws a question mark symbol."""
        glyph = self.number_font.render("?", True, settings.QUESTION_COLOR)
        g_rect = glyph.get_rect(center=rect.center)
        screen.blit(glyph, g_rect)

    def _draw_mine(self, screen: pygame.Surface, rect: pygame.Rect) -> None:
        """Draws a mine symbol."""
        cx, cy = rect.center
        r = max(4, settings.CELL_SIZE // 6)
        pygame.draw.circle(screen, settings.MINE_COLOR, (cx, cy), r)
        pygame.draw.circle(screen, settings.MINE_RING, (cx, cy), r, 1)
        for dx, dy in ((0, -8), (0, 8), (-8, 0), (8, 0), (-6, -6), (6, -6), (-6, 6), (6, 6)):
            pygame.draw.line(screen, settings.MINE_COLOR, (cx, cy), (cx + dx, cy + dy), 2)

    def board_cell_at_pixel(self, pos: Tuple[int, int]) -> Tuple[int, int] | None:
        """Maps a pixel position to board row/col."""
        x, y = pos
        if not self.board_rect.collidepoint(x, y):
            return None
        col = (x - self.board_rect.x) // settings.CELL_SIZE
        row = (y - self.board_rect.y) // settings.CELL_SIZE
        return int(row), int(col)

    def popup_buttons(self) -> tuple[pygame.Rect, pygame.Rect]:
        """Returns popup button rectangles."""
        popup_w = min(460, self.window_width - 40)
        popup_h = 210
        popup = pygame.Rect(0, 0, popup_w, popup_h)
        popup.center = (self.window_width // 2, self.window_height // 2)

        btn_w = 150
        btn_h = 44
        gap = 20
        total_w = btn_w * 2 + gap
        start_x = popup.centerx - total_w // 2
        y = popup.bottom - 64
        restart_rect = pygame.Rect(start_x, y, btn_w, btn_h)
        exit_rect = pygame.Rect(start_x + btn_w + gap, y, btn_w, btn_h)
        return restart_rect, exit_rect

    def draw_game_over_popup(self, screen: pygame.Surface) -> None:
        """Draws the modal popup shown after losing."""
        dim = pygame.Surface((self.window_width, self.window_height), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 140))
        screen.blit(dim, (0, 0))

        popup_w = min(460, self.window_width - 40)
        popup_h = 210
        popup = pygame.Rect(0, 0, popup_w, popup_h)
        popup.center = (self.window_width // 2, self.window_height // 2)

        pygame.draw.rect(screen, (219, 223, 229), popup, border_radius=8)
        pygame.draw.rect(screen, (78, 88, 100), popup, 2, border_radius=8)

        title = self.popup_title_font.render("You Lost", True, (40, 46, 56))
        title_rect = title.get_rect(center=(popup.centerx, popup.top + 45))
        screen.blit(title, title_rect)

        text = self.popup_text_font.render("Do you want to restart or quit?", True, (58, 66, 76))
        text_rect = text.get_rect(center=(popup.centerx, popup.top + 88))
        screen.blit(text, text_rect)

        restart_rect, exit_rect = self.popup_buttons()
        pygame.draw.rect(screen, (161, 180, 104), restart_rect, border_radius=6)
        pygame.draw.rect(screen, (58, 68, 43), restart_rect, 2, border_radius=6)
        pygame.draw.rect(screen, (205, 111, 101), exit_rect, border_radius=6)
        pygame.draw.rect(screen, (89, 44, 40), exit_rect, 2, border_radius=6)

        restart_lbl = self.popup_btn_font.render("Restart", True, (31, 40, 26))
        exit_lbl = self.popup_btn_font.render("Quit", True, (62, 28, 26))
        screen.blit(restart_lbl, restart_lbl.get_rect(center=restart_rect.center))
        screen.blit(exit_lbl, exit_lbl.get_rect(center=exit_rect.center))
