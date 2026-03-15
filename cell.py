from dataclasses import dataclass


MARK_NONE = 0
MARK_FLAG = 1
MARK_QUESTION = 2


@dataclass
class Cell:
    playable: bool = True
    has_mine: bool = False
    revealed: bool = False
    mark: int = MARK_NONE
    adjacent_mines: int = 0
