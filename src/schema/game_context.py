"""Dataclasses representing the game state."""
from dataclasses import dataclass


@dataclass(frozen=True)
class FieldPosition:
    # The yardline, between 1 and 50.
    yardline: int
    # Whether the play was in the opponents half
    opponents_half: bool    
    down: int
    distance: int


@dataclass(frozen=True)
class Clock:
    quarter: int
    time_remaining: float


@dataclass(frozen=True)
class GameContext:
    clock: Clock
    field_pos: FieldPosition
    # Whether the home team has the ball.
    home_possession: bool
