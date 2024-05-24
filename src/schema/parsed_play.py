"""Schema for a fully parsed play."""
from dataclasses import dataclass

from schema.game_context import GameContext
from schema.play_call import PlayCall
from schema.play_outcome import PlayOutcome
from schema.player_names import PlayerNames


@dataclass(frozen=True)
class ParsedPlay:
    call: PlayCall
    outcome: PlayOutcome
    names: PlayerNames
    context: GameContext
