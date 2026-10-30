"""
Game scenes for the Queens puzzle UI.

Manages scene transitions: menu, play mode, and win screen.
"""

import pygame
from queens.game import GameSession
from queens.solver import Solver, StepKind
from queens.ui.renderer import Renderer
from queens.load_levels import load_levels


class Scene:
    """Base class for UI scenes."""

    def __init__(self, app):
        """
        Initialize a scene.

        Args:
            app: The main app instance.
        """
        self.app = app

    def handle_event(self, event: pygame.event.Event):
        """Handle a pygame event."""
        pass

    def update(self):
        """Update scene state."""
        pass

    def draw(self, surface: pygame.Surface):
        """Draw the scene."""
        pass

class MenuScene(Scene):
    """
    Main menu for level selection.

    Displays dynamically loaded puzzles from a JSON file.
    """

    def __init__(self, app):
        """
        Initialize the menu scene.

        Args:
            app: The main app instance.
        """
        super().__init__(app)
        
        # Load and validate all levels instantly on startup
        try:
            self.levels = load_levels('levels.json')
        except Exception as e:
            print(f"Error loading levels: {e}")
            self.levels = []
            
        self.buttons = []
        self._update_buttons()

    def _update_buttons(self):
        """Create button rects for all loaded levels."""
        self.buttons = []
        button_width = 300
        button_height = 40
        start_y = 120
        spacing = 20

        x = (self.app.width - button_width) // 2
        current_y = start_y

        for name, level_obj in self.levels:
            self.buttons.append((
                pygame.Rect(x, current_y, button_width, button_height),
                name,
                level_obj
            ))
            current_y += button_height + spacing

    def handle_event(self, event: pygame.event.Event):
        """Handle menu interactions."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            # Unpack rect, name, and the validated level object
            for rect, name, level_obj in self.buttons:
                if rect.collidepoint(pos):
                    self.app.start_game(level_obj)
                    return

    def draw(self, surface: pygame.Surface):
        """Draw the menu."""
        surface.fill((240, 240, 240))
        
        font_title = pygame.font.Font(None, 48)
        font_button = pygame.font.Font(None, 32)
        font_error = pygame.font.Font(None, 24)
        
        title = font_title.render("Queens Puzzle", True, (0, 0, 0))
        title_rect = title.get_rect(center=(self.app.width // 2, 60))
        surface.blit(title, title_rect)
        
        if not self.levels:
            error_msg = font_error.render("No valid levels found in levels.json", True, (200, 0, 0))
            error_rect = error_msg.get_rect(center=(self.app.width // 2, 150))
            surface.blit(error_msg, error_rect)
            return

        mouse_pos = pygame.mouse.get_pos()
        for rect, name, level_obj in self.buttons:
            is_hovered = rect.collidepoint(mouse_pos)
            color = (200, 200, 200) if is_hovered else (220, 220, 220)
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (0, 0, 0), rect, 2)
            
            text = font_button.render(name, True, (0, 0, 0))
            text_rect = text.get_rect(center=rect.center)
            surface.blit(text, text_rect)


class PlayScene(Scene):
    """
    Play mode for solving a puzzle manually.

    Handles board rendering, click interactions, undo, and timer.
    """

    WIN_SCREEN_DELAY_MS = 2000

    def __init__(self, app, level):
        """
        Initialize play scene.

        Args:
            app: The main app instance.
            level: The level to play.
        """
        super().__init__(app)
        self.level = level
        self.session = GameSession(level)
        self.renderer = Renderer(level.size, app.width, app.height)
        self.button_rects = {}
        self.won = False
        self.win_started_at = None
        self.completed_time = None

    def handle_event(self, event: pygame.event.Event):
        """Handle play mode interactions."""
        if self.won:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos

            # Check buttons
            if self.button_rects.get('solve') and self.button_rects['solve'].collidepoint(pos):
                self.app.goto_solver(self.level)
                return
            if self.button_rects.get('undo') and self.button_rects['undo'].collidepoint(pos):
                self.session.undo()
                return
            if self.button_rects.get('redo') and self.button_rects['redo'].collidepoint(pos):
                self.session.redo()
                return
            if self.button_rects.get('menu') and self.button_rects['menu'].collidepoint(pos):
                self.app.goto_menu()
                return

            # Check board
            cell = self.renderer.get_cell_at(pos)
            if cell:
                is_right_click = event.button == 3
                self.session.click_cell(cell[0], cell[1], right_click=is_right_click)

    def update(self):
        """Update play state."""
        if not self.won and self.session.is_won():
            self.won = True
            self.win_started_at = pygame.time.get_ticks()
            self.completed_time = self.session.elapsed_time()
        elif (
            self.won
            and self.win_started_at is not None
            and pygame.time.get_ticks() - self.win_started_at
            >= self.WIN_SCREEN_DELAY_MS
        ):
            self.app.goto_win(self.completed_time)

    def draw(self, surface: pygame.Surface):
        """Draw the play scene."""
        surface.fill((240, 240, 240))
        
        font_text = pygame.font.Font(None, 24)
        font_button = pygame.font.Font(None, 20)
        
        # Draw timer
        self.renderer.draw_timer(surface, self.session.elapsed_time(), font_text)
        
        # Draw board
        conflicts = set(self.session.get_conflicts())
        self.renderer.draw_board(surface, self.session.board, self.level, conflicts)
        
        # Draw buttons
        button_y = 35
        button_width = 65
        button_height = 30
        button_spacing = 70

        button_x = self.renderer.margin
        self.button_rects['solve'] = self.renderer.draw_button(
            surface, "Solve", button_x, button_y, button_width, button_height, font_button
        )

        button_x += button_spacing
        self.button_rects['undo'] = self.renderer.draw_button(
            surface, "Undo", button_x, button_y, button_width, button_height, font_button,
            self.session.can_undo()
        )

        button_x += button_spacing
        self.button_rects['redo'] = self.renderer.draw_button(
            surface, "Redo", button_x, button_y, button_width, button_height, font_button,
            self.session.can_redo()
        )

        button_x += button_spacing
        self.button_rects['menu'] = self.renderer.draw_button(
            surface, "Menu", button_x, button_y, button_width, button_height, font_button
        )


class WinScene(Scene):
    """
    Win screen shown when a puzzle is solved.

    Displays completion message and options to play again or return to menu.
    """

    def __init__(self, app, elapsed_time: float):
        """
        Initialize win scene.

        Args:
            app: The main app instance.
            elapsed_time: Time taken to solve the puzzle.
        """
        super().__init__(app)
        self.elapsed_time = elapsed_time
        self.button_rects = {}

    def handle_event(self, event: pygame.event.Event):
        """Handle win screen interactions."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.button_rects.get('menu', pygame.Rect(0, 0, 0, 0)).collidepoint(pos):
                self.app.goto_menu()

    def draw(self, surface: pygame.Surface):
        """Draw the win screen."""
        surface.fill((240, 240, 240))
        
        font_title = pygame.font.Font(None, 64)
        font_text = pygame.font.Font(None, 32)
        font_button = pygame.font.Font(None, 24)
        
        # Win message
        title = font_title.render("Puzzle Solved!", True, (0, 150, 0))
        title_rect = title.get_rect(center=(self.app.width // 2, 200))
        surface.blit(title, title_rect)
        
        # Time
        minutes = int(self.elapsed_time) // 60
        seconds = int(self.elapsed_time) % 60
        time_text = font_text.render(f"Time: {minutes:02d}:{seconds:02d}", True, (0, 0, 0))
        time_rect = time_text.get_rect(center=(self.app.width // 2, 300))
        surface.blit(time_text, time_rect)
        
        # Menu button
        button_width = 200
        button_height = 50
        button_x = (self.app.width - button_width) // 2
        button_y = 35
        
        self.button_rects['menu'] = pygame.Rect(button_x, button_y, button_width, button_height)
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.button_rects['menu'].collidepoint(mouse_pos)
        color = (200, 200, 200) if is_hovered else (220, 220, 220)
        pygame.draw.rect(surface, color, self.button_rects['menu'])
        pygame.draw.rect(surface, (0, 0, 0), self.button_rects['menu'], 2)
        
        button_text = font_button.render("Return to Menu", True, (0, 0, 0))
        button_text_rect = button_text.get_rect(center=self.button_rects['menu'].center)
        surface.blit(button_text, button_text_rect)


class SolverScene(Scene):
    """
    Solver visualization scene.

    Shows step-by-step solving with controls: Next, Auto-play/Pause, Reset.
    """

    def __init__(self, app, level):
        """
        Initialize solver scene.

        Args:
            app: The main app instance.
            level: The level to solve.
        """
        super().__init__(app)
        self.level = level
        self.renderer = Renderer(level.size, app.width, app.height)
        self.solver = Solver(level)
        self.button_rects = {}
        self._reset()

    def handle_event(self, event: pygame.event.Event):
        """Handle solver scene interactions."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos

            # Check buttons
            if self.button_rects.get('next') and self.button_rects['next'].collidepoint(pos):
                self._step_forward()
                return
            if self.button_rects.get('play') and self.button_rects['play'].collidepoint(pos):
                self.auto_playing = not self.auto_playing
                self.last_step_time = 0
                return
            if self.button_rects.get('reset') and self.button_rects['reset'].collidepoint(pos):
                self._reset()
                return
            if self.button_rects.get('back') and self.button_rects['back'].collidepoint(pos):
                self.app.goto_menu()
                return

    def update(self):
        """Update solver state."""
        import time
        current_time = time.time()

        if self.auto_playing:
            step_delay = 0.15
            if current_time - self.last_step_time >= step_delay:
                self._step_forward()
                self.last_step_time = current_time

    def _step_forward(self):
        """Move to the next solving step by pulling from the generator."""
        if self.finished:
            self.auto_playing = False
            return
            
        try:
            self.current_step = next(self.solver_gen)
            self.step_count += 1
            self.current_board = self.current_step.board_state

            if self.current_step.kind == StepKind.SOLVED:
                self.finished = True
                self.auto_playing = False
        except StopIteration:
            self.finished = True
            self.auto_playing = False

    def _reset(self):
        """Reset to the beginning and re-initialize the generator."""
        from queens.board import BoardState
        self.current_board = BoardState(self.level)
        self.solver_gen = self.solver.solve()
        self.current_step = None
        self.step_count = 0
        self.auto_playing = False
        self.last_step_time = 0
        self.finished = False

    def draw(self, surface: pygame.Surface):
        """Draw the solver scene."""
        surface.fill((240, 240, 240))

        font_text = pygame.font.Font(None, 18)
        font_button = pygame.font.Font(None, 18)

        # Draw board
        self.renderer.draw_board(surface, self.current_board, self.level)

        # Draw current step info to the right of the board so it does not
        # overlap the solver controls at the top.
        info_x = (
            self.renderer.board_left
            + self.renderer.board_size * self.renderer.cell_size
            + 12
        )
        info_y = self.renderer.board_top

        if self.current_step is not None:
            step_text = f"Step {self.step_count}"

            if self.current_step.kind == StepKind.PLACE:
                action_text = f"Place queen at ({self.current_step.cell[0]}, {self.current_step.cell[1]})"
            elif self.current_step.kind == StepKind.REMOVE:
                action_text = f"Backtrack from ({self.current_step.cell[0]}, {self.current_step.cell[1]})"
            elif hasattr(StepKind, 'PRUNE') and self.current_step.kind == StepKind.PRUNE:
                action_text = f"Prune branch: Row {self.current_step.cell[0]} doomed"
            elif self.current_step.kind == StepKind.SOLVED:
                action_text = "Puzzle solved!"
            else:
                action_text = "Failed to solve"

            self.renderer.draw_text(surface, step_text, info_x, info_y, font_text)
            self.renderer.draw_text(surface, action_text, info_x, info_y + 24, font_text)
        else:
            self.renderer.draw_text(surface, "Ready to solve", info_x, info_y, font_text)

        # Draw control buttons
        button_y = 35
        button_width = 80
        button_height = 30
        button_spacing = 90

        button_x = self.renderer.margin
        play_text = "Pause" if self.auto_playing else "Play"
        self.button_rects['next'] = self.renderer.draw_button(
            surface, "Next", button_x, button_y, button_width, button_height, font_button
        )

        button_x += button_spacing
        self.button_rects['play'] = self.renderer.draw_button(
            surface, play_text, button_x, button_y, button_width, button_height, font_button
        )

        button_x += button_spacing
        self.button_rects['reset'] = self.renderer.draw_button(
            surface, "Reset", button_x, button_y, button_width, button_height, font_button
        )

        button_x += button_spacing
        self.button_rects['back'] = self.renderer.draw_button(
            surface, "Back", button_x, button_y, button_width, button_height, font_button
        )