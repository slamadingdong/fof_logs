"""Schema that represent the outcome of a play."""
from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class PassingOutcome:
    # Whether the pass was complete.
    complete: bool
    # Total number of yards gained or lost on the play.
    yards: int
    # Yards gained after the catch.
    yac: int
    # The targeted route, e.g. Wheel, 9
    target_route: str = ''
    # The priority of the targeted route, either primary, secondary, outlet.
    target_priority: str = ''
    # Whether the QB was sacked.
    sacked: bool = False
    # Whether the QB was hurried.
    hurried: bool = False
    # Whether the QB's pass was blocked at the line.
    blocked: bool = False
    # Whether the pass was intercepted.
    intercepted: bool = False
    # Whether the QB threw into double coverage.
    throw_into_double: bool = False
    # Whether the pass was dropped.
    dropped: bool = False
    # Whether the QB scrambled.
    scramble: bool = False

    def __post_init__(self):
        if sum([self.complete, self.sacked, self.blocked,
                self.intercepted, self.dropped, self.scramble]) > 1:
            raise ValueError(f"Multiple incompatible outcomes were true: "
                             f"{repr(self)}")


@dataclass(frozen=True)
class RunningOutcome:
    yards: int


@dataclass(frozen=True)
class PlayOutcome:
    outcome: Union[PassingOutcome, RunningOutcome]
    # Whether the defense was familiar with the play.
    familiar: bool
