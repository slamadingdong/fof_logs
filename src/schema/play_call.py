"""Schema for offensive and defensive play calls."""
from dataclasses import dataclass


@dataclass(frozen=True)
class DefensivePlay:
    # Eg. nickel, dime
    def_personnel: str
    # 4-3 over/under, 3-4
    def_formation: str
    # E.g. man-to-man, cover-2
    coverage: str
    # Whether there is a QB spy
    spy: bool
    # The receiver being doubled, or empty if no double
    double_target: str
    # The number of blitzers
    blitz: int
    # Whether there is a buzz safety
    buzz: bool


@dataclass(frozen=True, eq=True)
class PlayType:
    # Either 'pass' or 'run'
    type: str
    # Whether there was playaction.
    playaction: bool = False
    # Whether it was a finesse run
    finesse_run: bool = False
    # Whether it was a reverse.
    reverse: bool = False


@dataclass(frozen=True, eq=True)
class OffensivePlay:
    # E.g. 113, 122
    off_personnel: str
    # E.g. I, strong, trips
    off_formation: str
    # Pistol, shotgun, normal
    qb_alignment: str
    play_type: PlayType
    # E.g. Wheel, 9
    primary_route: str = ''
    # E.g. X, Y, A
    primary_receiver: str = ''
    # Same as primary
    secondary_route: str = ''
    # Same as primary
    secondary_receiver: str = ''
    run_direction: str = ''
    # E.g. RB, FB, QB
    ball_carrier: str = ''
    # For pass plays, the number of extra blockers
    protect: int = 0


@dataclass
class PlayCall(frozen=True):
    offns: OffensivePlay
    dfns: DefensivePlay
