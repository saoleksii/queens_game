"""
Rendering system for the Queens puzzle UI.

Handles drawing the board, queens, marks, regions, conflicts, and UI elements.
"""

import pygame
from queens.board import CellState


class Renderer:
    """
    Renders Queens puzzle board and UI elements using pygame.

    Handles board layout, cell rendering, region coloring, conflict highlighting.
    """

    def __init__(
        self, board_size: int, width: int = 800, height: int = 800,
        top_reserved: int = 90, bottom_reserved: int = 20
    ):
        """
        Initialize the renderer.

        Args:
            board_size: Number of rows/columns in the board.
            width: Window width in pixels.
            height: Window height in pixels.
            top_reserved: Space reserved above the board for controls.
            bottom_reserved: Space reserved below the board.
        """
        self.board_size = board_size
        self.width = width
        self.height = height
        self.margin = 40
        self.button_height = 30
        self.timer_height = 30
        
        # Calculate board dimensions
        board_area = height - top_reserved - bottom_reserved
        self.cell_size = int(board_area / board_size)
        self.board_left = self.margin
        self.board_top = top_reserved

        # Colors
        self.COLOR_BG = (240, 240, 240)
        self.COLOR_EMPTY = (255, 255, 255)
        self.COLOR_QUEEN = (0, 0, 0)
        self.COLOR_MARK = (150, 150, 150)
        self.COLOR_CONFLICT = (255, 100, 100)
        self.COLOR_BORDER = (0, 0, 0)
        self.COLOR_TEXT = (0, 0, 0)
        
        # Region colors (pastel palette)
        self.REGION_COLORS = [
            (200, 220, 255),  # Light blue
            (200, 255, 220),  # Light green
            (255, 220, 200),  # Light orange
            (255, 200, 220),  # Light pink
            (220, 255, 200),  # Light lime
            (255, 255, 200),  # Light yellow
            (220, 200, 255),  # Light purple
            (200, 255, 255),  # Light cyan
            (255, 200, 150),  # Light salmon
        ]

    def draw_board(self, surface: pygame.Surface, board_state, level, conflicts: set = None):
        """
        Draw the complete board with regions, queens, marks, and conflicts.

        Args:
            surface: Pygame surface to draw on.
            board_state: Current board state with queens and marks.
            level: Level definition with region assignments.
            conflicts: Set of (row, col) cells in conflict (highlighted in red).
        """
        if conflicts is None:
            conflicts = set()

        # Draw cells with regions
        for row in range(self.board_size):
            for col in range(self.board_size):
                region_id = level.regions[row][col]
                color = self.REGION_COLORS[region_id % len(self.REGION_COLORS)]
                
                x = self.board_left + col * self.cell_size
                y = self.board_top + row * self.cell_size
                
                pygame.draw.rect(surface, color, (x, y, self.cell_size, self.cell_size))
                pygame.draw.rect(surface, self.COLOR_BORDER, (x, y, self.cell_size, self.cell_size), 1)
                
                # Highlight conflicts
                if (row, col) in conflicts:
                    pygame.draw.rect(surface, self.COLOR_CONFLICT, (x, y, self.cell_size, self.cell_size), 3)
                
                # Draw queen or mark
                cell_state = board_state.get_cell(row, col)
                if cell_state == CellState.QUEEN:
                    self._draw_queen(surface, x, y)
                elif cell_state == CellState.MARK:
                    self._draw_mark(surface, x, y)

    def _draw_queen(self, surface: pygame.Surface, x: int, y: int):
        """Draw a queen symbol at the given cell."""
        center_x = x + self.cell_size // 2
        center_y = y + self.cell_size // 2
        radius = self.cell_size // 3
        pygame.draw.circle(surface, self.COLOR_QUEEN, (center_x, center_y), radius)

    def _draw_mark(self, surface: pygame.Surface, x: int, y: int):
        """Draw an X mark at the given cell."""
        margin = self.cell_size // 4
        x1, y1 = x + margin, y + margin
        x2, y2 = x + self.cell_size - margin, y + self.cell_size - margin
        pygame.draw.line(surface, self.COLOR_MARK, (x1, y1), (x2, y2), 2)
        pygame.draw.line(surface, self.COLOR_MARK, (x1, y2), (x2, y1), 2)

    def draw_timer(self, surface: pygame.Surface, elapsed_time: float, font: pygame.font.Font):
        """Draw the elapsed time."""
        minutes = int(elapsed_time) // 60
        seconds = int(elapsed_time) % 60
        time_str = f"Time: {minutes:02d}:{seconds:02d}"
        text = font.render(time_str, True, self.COLOR_TEXT)
        surface.blit(text, (self.margin, 8))

    def draw_button(self, surface: pygame.Surface, text: str, x: int, y: int, width: int, 
                   height: int, font: pygame.font.Font, is_hovered: bool = False) -> pygame.Rect:
        """
        Draw a button and return its rect.

        Args:
            surface: Pygame surface to draw on.
            text: Button label.
            x, y: Button position.
            width, height: Button dimensions.
            font: Font for button text.
            is_hovered: Whether button is currently hovered.

        Returns:
            Rect of the button for click detection.
        """
        color = (200, 200, 200) if is_hovered else (220, 220, 220)
        rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, self.COLOR_BORDER, rect, 1)
        
        text_surface = font.render(text, True, self.COLOR_TEXT)
        text_rect = text_surface.get_rect(center=rect.center)
        surface.blit(text_surface, text_rect)
        
        return rect

    def get_cell_at(self, pos: tuple) -> tuple:
        """
        Get the board cell at the given screen position.

        Args:
            pos: (x, y) screen coordinates.

        Returns:
            (row, col) or None if click is outside the board.
        """
        x, y = pos
        
        if x < self.board_left or x >= self.board_left + self.board_size * self.cell_size:
            return None
        if y < self.board_top or y >= self.board_top + self.board_size * self.cell_size:
            return None
        
        col = (x - self.board_left) // self.cell_size
        row = (y - self.board_top) // self.cell_size
        
        return (row, col)

    def get_board_dimensions(self) -> tuple:
        """Get board area dimensions (left, top, width, height)."""
        width = self.board_size * self.cell_size
        height = self.board_size * self.cell_size
        return (self.board_left, self.board_top, width, height)

    def draw_text(self, surface: pygame.Surface, text: str, x: int, y: int,
                 font: pygame.font.Font, color: tuple = None):
        """
        Draw text on the surface.

        Args:
            surface: Pygame surface to draw on.
            text: Text to display.
            x, y: Text position.
            font: Font for the text.
            color: Text color (default: black).
        """
        if color is None:
            color = self.COLOR_TEXT
        text_surface = font.render(text, True, color)
        surface.blit(text_surface, (x, y))
