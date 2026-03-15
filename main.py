import logging

from game import MinesweeperGame
from logging_setup import configure_logging


def main() -> None:
    """Starts logging and runs the game."""
    configure_logging()
    logging.getLogger(__name__).info("Application startup")
    game = MinesweeperGame()
    game.run()


if __name__ == "__main__":
    main()
