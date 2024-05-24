"""Responsible for parsing the GameContext."""
import re
from typing import Dict, Any

from name_utils import shorten_name
from regexes import *
from src.schema.game_context import (GameContext,
                                     Clock,
                                     FieldPosition,
                                     DownDistance)
from teams import CITY_TO_ABBREV


class GameContextParser(object):
    """This class holds the data of each team's players.

    This is to help determine which team possess the ball by comparing the
    players in the play call to the table of home and away players."""

    def __init__(self, participation_tbl: Any):
        self._players: Dict
        self._home_team: str
        self._away_team: str
        self._init_teams(participation_tbl)

    def parse_context(self, summ_text: str, play_call: Any) -> GameContext:
        """Parses the summary text and play call table into a GameContext."""
        home = self._which_team_offense(
            play_call) == self._home_team
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
            offense = self._which_team_offense(play_call)
            opponents_half = side != offense
            return FieldPosition(yardline=yardline,
                                 opponents_half=opponents_half)
        if 'two-point' in summ_text:
            return FieldPosition(yardline=2,
                                 opponents_half=True)
        raise AssertionError("The field position could not be parsed: " +
                             summ_text)

    def _which_team_offense(self, play_call: Any):
        home_matches, away_matches = 0, 0
        for player_row in play_call[1:]:
            stripped_position = player_row[0].split(' ')[1:]
            player_name = ' '.join(stripped_position)
            if player_name in self._players['home']:
                home_matches += 1
            if player_name in self._players['away']:
                away_matches += 1
            if home_matches > 3 or away_matches > 3:
                break
        if home_matches > away_matches:
            return self._home_team
        else:
            return self._away_team

    def _init_teams(self, participation) -> None:
        away_table, home_table = participation[0], participation[1]
        away_city, home_city = away_table.th.text, home_table.th.text
        self._home_team = CITY_TO_ABBREV[home_city]
        self._away_team = CITY_TO_ABBREV[away_city]
        self._players = {'home': [], 'away': []}
        for home_player_row in home_table.find_all('tr'):
            player = home_player_row.contents[0].text
            player = player.split(' ')
            name = shorten_name(' '.join(player[1:]))
            self._players['home'].append(name)
        for away_player_row in away_table.find_all('tr'):
            player = away_player_row.contents[0].text
            player = player.split(' ')
            name = shorten_name(' '.join(player[1:]))
            self._players['away'].append(name)


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
