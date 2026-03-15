from __future__ import annotations

import logging

import pygame

import settings
from board import Board
from osm_map import OSMMapBuilder
from ui import FACE_DEAD, FACE_NORMAL, FACE_PRESSED, FACE_SURPRISED, FACE_WIN, UI


class MinesweeperGame:
    """Runs the game loop, input handling, and rendering."""
    def __init__(self) -> None:
        """Initializes pygame, board, map, and runtime state."""
        self.logger = logging.getLogger(__name__)
        pygame.init()
        pygame.display.set_caption("Minesweeper OSM - Strait of Hormuz")
        self.logger.info("Game initialization")

        self.board_px_w = settings.BOARD_COLS * settings.CELL_SIZE
        self.board_px_h = settings.BOARD_ROWS * settings.CELL_SIZE
        self.ui = UI(self.board_px_w, self.board_px_h)
        self.screen = pygame.display.set_mode((self.ui.window_width, self.ui.window_height))
        self.clock = pygame.time.Clock()

        self.map_builder = OSMMapBuilder()
        self.map_surface = self.map_builder.get_or_build_map(self.board_px_w, self.board_px_h, settings.OSM_ZOOM)
        playable_mask = self.map_builder.build_water_playable_mask(
            self.map_surface, settings.BOARD_ROWS, settings.BOARD_COLS
        )
        self.board = Board(settings.BOARD_ROWS, settings.BOARD_COLS, settings.MINE_COUNT, playable_mask=playable_mask)
        self.logger.info(
            "Board ready: rows=%s cols=%s mines=%s playable_cells=%s",
            settings.BOARD_ROWS,
            settings.BOARD_COLS,
            settings.MINE_COUNT,
            self.board.playable_cells,
        )

        self.running = True
        self.face_state = FACE_NORMAL
        self.left_down_on_board = False
        self.left_down_on_face = False
        self.start_tick_ms: int | None = None
        self.elapsed_seconds = 0
        self.show_game_over_popup = False

    def reset_game(self) -> None:
        """Resets the current game state."""
        self.board.reset()
        self.face_state = FACE_NORMAL
        self.left_down_on_board = False
        self.left_down_on_face = False
        self.start_tick_ms = None
        self.elapsed_seconds = 0
        self.show_game_over_popup = False
        self.logger.info("Game reset")

    def _update_timer(self) -> None:
        """Updates elapsed seconds while the game is active."""
        if self.start_tick_ms is None or self.board.game_over:
            return
        delta_ms = pygame.time.get_ticks() - self.start_tick_ms
        self.elapsed_seconds = min(999, delta_ms // 1000)

    def _begin_timer_if_needed(self) -> None:
        """Starts timer on first reveal action."""
        if self.start_tick_ms is None:
            self.start_tick_ms = pygame.time.get_ticks()

    def _current_face(self) -> str:
        """Returns the current face icon state."""
        if self.left_down_on_face:
            return FACE_PRESSED
        if self.board.game_over and self.board.won:
            return FACE_WIN
        if self.board.game_over and not self.board.won:
            return FACE_DEAD
        if self.left_down_on_board:
            return FACE_SURPRISED
        return FACE_NORMAL

    def _handle_left_down(self, pos: tuple[int, int]) -> None:
        """Handles left mouse button press."""
        if self.show_game_over_popup:
            return
        if self.ui.face_rect.collidepoint(pos):
            self.left_down_on_face = True
            return
        if self.board.game_over:
            return
        if self.ui.board_rect.collidepoint(pos):
            self.left_down_on_board = True

    def _handle_left_up(self, pos: tuple[int, int]) -> None:
        """Handles left mouse button release."""
        if self.show_game_over_popup:
            return
        if self.left_down_on_face:
            self.left_down_on_face = False
            if self.ui.face_rect.collidepoint(pos):
                self.reset_game()
            return

        if not self.left_down_on_board:
            return
        self.left_down_on_board = False

        if self.board.game_over:
            return

        cell_pos = self.ui.board_cell_at_pixel(pos)
        if cell_pos is None:
            return
        row, col = cell_pos
        self._begin_timer_if_needed()
        result = self.board.reveal(row, col)
        if result.exploded:
            self.show_game_over_popup = True
            self.logger.info("Game over: mine at r=%s c=%s", row, col)
        elif self.board.game_over and self.board.won:
            self.logger.info("Victory: score=%s time=%ss", self.board.score_points(), self.elapsed_seconds)

    def _handle_right_click(self, pos: tuple[int, int]) -> None:
        """Handles right click on board cells."""
        if self.show_game_over_popup:
            return
        if self.board.game_over:
            return
        cell_pos = self.ui.board_cell_at_pixel(pos)
        if cell_pos is None:
            return
        row, col = cell_pos
        self.board.cycle_mark(row, col, enable_question=True)

    def _handle_popup_click(self, pos: tuple[int, int]) -> None:
        """Handles clicks on game-over popup buttons."""
        if not self.show_game_over_popup:
            return
        restart_rect, exit_rect = self.ui.popup_buttons()
        if restart_rect.collidepoint(pos):
            self.reset_game()
            self.logger.info("Game over popup: restart")
        elif exit_rect.collidepoint(pos):
            self.running = False
            self.logger.info("Game over popup: exit")

    def run(self) -> None:
        """Runs the main event/render loop."""
        while self.running:
            self.clock.tick(settings.FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.logger.info("Quit event received")
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._handle_left_down(event.pos)
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if self.show_game_over_popup:
                        self._handle_popup_click(event.pos)
                    else:
                        self._handle_left_up(event.pos)
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                    self._handle_right_click(event.pos)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self.reset_game()

            self._update_timer()
            self.face_state = self._current_face()
            self.render()

        self.logger.info("Application shutdown")
        pygame.quit()

    def render(self) -> None:
        """Draws one complete frame."""
        self.ui.draw_window_frame(self.screen)
        self.ui.draw_hud(
            self.screen,
            score=self.board.score_points(),
            seconds=self.elapsed_seconds,
            face_state=self.face_state,
        )
        self.ui.draw_board(self.screen, self.board, self.map_surface)
        if self.show_game_over_popup:
            self.ui.draw_game_over_popup(self.screen)
        pygame.display.flip()
