"""Responsible for parsing the GameContext."""
import re
from typing import Any

from parsing.name_utils import parse_team_rosters, which_team_offense
from parsing.regexes import *
from schema.game_context import (GameContext,
                                 Clock,
                                 FieldPosition,
                                 DownDistance)


class GameContextParser(object):
    """This class holds the data of each team's players.

    This is to help determine which team possess the ball by comparing the
    players in the play call to the table of home and away players."""

    def __init__(self, participation_tbl: Any):
        home_team, away_team, short_names, _ = parse_team_rosters(participation_tbl)
        self._players = short_names
        self._home_team = home_team
        self._away_team = away_team

    def parse_context(self, summ_text: str, play_call: Any) -> GameContext:
        """Parses the summary text and play call table into a GameContext."""
        home = which_team_offense(play_call, self._players['home'], self._players['away']) == "home"
        return GameContext(clock=_parse_clock(summ_text),
                           field_pos=self._parse_field_pos(summ_text,
                                                           play_call),
                           home_possession=home,
                           down_distance=_parse_down_distance(summ_text))

    def _parse_field_pos(self, summ_text, play_call) -> FieldPosition:
        maybe_field_pos = re.search(FIELD_POSITION_REGEX, summ_text)
        if maybe_field_pos:
            yardline = int(maybe_field_pos[0][3:])
            side = maybe_field_pos[0][:3]
            offense = which_team_offense(play_call, self._players['home'], self._players['away'])
            offense = self._home_team if offense == 'home' else self._away_team
            opponents_half = side != offense
            return FieldPosition(yardline=yardline,
                                 opponents_half=opponents_half)
        if 'two-point' in summ_text:
            return FieldPosition(yardline=2,
                                 opponents_half=True)
        raise AssertionError("The field position could not be parsed: " +
                             summ_text)


def _parse_clock(summ_text) -> Clock:
    maybe_clock_string = re.search(CLOCK_REGEX, summ_text)
    if maybe_clock_string:
        clock_string = maybe_clock_string[0]
        quarter = clock_string[1]
        # Overtime
        if quarter == 'O':
            quarter = 5
        time_string = re.search(TIME_REGEX, clock_string)
        if time_string:
            time = float(time_string[0].replace(':', '.'))
            return Clock(quarter=int(quarter), time_remaining=time)
    raise AssertionError("The clock string could not be parsed: " +
                         summ_text)


def _parse_down_distance(summary_text: str) -> DownDistance:
    maybe_down_distance = re.search(DOWN_DISTANCE_REGEX, summary_text)
    if maybe_down_distance:
        down = int(maybe_down_distance[0][0])
        distance = int(maybe_down_distance[0][2:4])
        return DownDistance(down=down, distance=distance)
    if 'two-point' in summary_text:
        return DownDistance(down=4, distance=2)
    raise AssertionError("The down and distance could not be parsed: " +
                         summary_text)
