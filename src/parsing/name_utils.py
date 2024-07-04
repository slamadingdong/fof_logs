"""Utilities for parsing names."""
import logging
import re
from typing import Any, List, Dict, Tuple

from parsing.consts import QB, RB, FB, TE, WR, C, T, G, P, K
from parsing.teams import CITY_TO_ABBREV

logger = logging.getLogger(__name__)

# The possible positions for a targeted receiver.
_TARGET_POSITIONS = [QB, RB, FB, TE, WR, C, T, G, P, K]

# Add if necessary, these names cause annoying problems.
_MIDDLE_NAMES = ['St.', 'Van', 'Von', 'Al', 'El', 'La', 'Bob', 'Dar', 'De', 'de la']
_COMPOUND_FIRST_NAMES = ['Bob Bob']

# Regex for finding the next name element of a string.
_NEXT_NAME_REGEX = r'[A-Z]\.'


def target_receiver_name(text: str) -> str:
    """Extract the full name of the target receiver from the text of the play."""
    words = text.split(' ')
    for i in range(len(words)):
        if words[i] in _TARGET_POSITIONS:
            has_name = ' '.join(words[i + 1:])
            return full_name(has_name_substr=has_name)
    # Return an empty string if no target position was found.
    return ''


def shorten_name(name_str: str) -> str:
    """Shorten the name to first initial and last name."""
    components = _parse_name_components(name_str)
    if len(components) == 3:
        first, middle, last = components
        if ' '.join([first, middle]) in _COMPOUND_FIRST_NAMES:
            return f'{first[0]}.{last}'
        return f'{first[0]}.{middle} {last}'
    elif len(components) == 2:
        first, last = components
        return f'{first[0]}.{last}'
    else:
        return ''


def full_name(has_name_substr: str) -> str:
    """Extract the full name from a substring that begins with the player's name."""
    name_components = _parse_name_components(has_name_substr)
    return ' '.join(name_components)


def _parse_name_components(has_name_substr: str) -> tuple:
    """From a string that begins with a players name, extract the first, last, and middle names."""
    name_str = has_name_substr.strip(' ').rstrip('.')
    names = name_str.split(' ')
    middle = None
    first = names[0]
    if len(names) < 2:
        return name_str,
    next_name = names[1]
    appendage_index = 2
    if next_name in _MIDDLE_NAMES:
        try:
            middle = next_name
            last = names[2]
            appendage_index = 3
        except IndexError:
            last = next_name
    elif len(names) >= 4 and ' '.join([names[1], names[2]]) in _MIDDLE_NAMES:
        try:
            middle = ' '.join([names[1], names[2]])
            last = names[3]
            appendage_index = 4
        except IndexError:
            last = next_name
    elif re.search(_NEXT_NAME_REGEX, next_name):
        last = names[2]
        appendage_index = 3
    else:
        last = next_name
    last = last.strip('.')
    try:
        third = names[appendage_index]
        if third == 'Jr.' or third == 'Jr..':
            last += ' ' + 'Jr.'
        elif third == 'III' or third == 'III.':
            last += ' ' + 'III'
    except IndexError:
        # There was no middle name
        pass
    if middle:
        return first, middle, last
    else:
        return first, last


def which_team_offense(play_call: Any, home_players: List[str], away_players: List[str]):
    home_matches, away_matches = 0, 0
    for player_row in play_call[1:]:
        stripped_position = player_row[0].split(' ')[1:]
        player_name = ' '.join(stripped_position)
        if player_name in home_players:
            home_matches += 1
        if player_name in away_players:
            away_matches += 1
        if home_matches > 3 or away_matches > 3:
            break
    if home_matches > away_matches:
        return "home"
    else:
        return "away"


def parse_team_rosters(participation) -> Tuple[str, str, Dict, Dict]:
    away_table, home_table = participation[0], participation[1]
    away_city, home_city = away_table.th.text, home_table.th.text
    home_team = CITY_TO_ABBREV[home_city]
    away_team = CITY_TO_ABBREV[away_city]
    short_names = {'home': [], 'away': []}
    full_names = {'home': [], 'away': []}
    for home_player_row in home_table.find_all('tr'):
        player = home_player_row.contents[0].text
        player = player.split(' ')
        full_name = ' '.join(player[1:])
        short_name = shorten_name(full_name)
        short_names['home'].append(short_name)
        full_names['home'].append(full_name)
    for away_player_row in away_table.find_all('tr'):
        player = away_player_row.contents[0].text
        player = player.split(' ')
        full_name = ' '.join(player[1:])
        short_name = shorten_name(full_name)
        short_names['away'].append(short_name)
        full_names['away'].append(full_name)
    return home_team, away_team, short_names, full_names
