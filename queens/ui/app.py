"""
Main pygame application for the Queens puzzle game.

Manages the main loop and scene transitions.
"""

import pygame
from queens.ui.scenes import MenuScene, PlayScene, WinScene, SolverScene


class App:
    """
    Main application class for the Queens puzzle game.

    Manages pygame window, scene transitions, and main event loop.
    """

    def __init__(self, width: int = 800, height: int = 700):
        """
        Initialize the application.

        Args:
            width: Window width in pixels.
            height: Window height in pixels.
        """
        pygame.init()
        self.width = width
        self.height = height
        self.surface = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Queens Puzzle")
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        self.current_scene = MenuScene(self)
        self.running = True

    def start_game(self, level):
        """
        Start playing a level.

        Args:
            level: The level to play.
        """
        self.current_scene = PlayScene(self, level)

    def goto_menu(self):
        """Return to the main menu."""
        self.current_scene = MenuScene(self)

    def goto_win(self, elapsed_time: float):
        """
        Show the win screen.

        Args:
            elapsed_time: Time taken to complete the puzzle.
        """
        self.current_scene = WinScene(self, elapsed_time)

    def goto_solver(self, level):
        """
        Show the solver visualization scene.

        Args:
            level: The level to solve.
        """
        self.current_scene = SolverScene(self, level)

    def handle_events(self):
        """Process pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            else:
                self.current_scene.handle_event(event)

    def update(self):
        """Update the current scene."""
        self.current_scene.update()

    def draw(self):
        """Draw the current scene."""
        self.current_scene.draw(self.surface)
        pygame.display.flip()

    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)

        pygame.quit()


def main():
    """Entry point for the game."""
    app = App()
    app.run()


if __name__ == '__main__':
    main()
