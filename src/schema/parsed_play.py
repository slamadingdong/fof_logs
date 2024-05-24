"""Schema for a fully parsed play."""
from dataclasses import dataclass

from game_context import GameContext
from play_call import PlayCall
from play_outcome import PlayOutcome
from player_names import PlayerNames


@dataclass(frozen=True)
class ParsedPlay:
    call: PlayCall
    outcome: PlayOutcome
    names: PlayerNames
    context: GameContext
