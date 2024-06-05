"""Utilities for parsing names."""
import re
import logging
from parsing.consts import QB, RB, FB, TE, WR, C, T, G, P, K

logger = logging.getLogger(__name__)

# The possible positions for a targeted receiver.
_TARGET_POSITIONS = [QB, RB, FB, TE, WR, C, T, G, P, K]

# Add if necessary, these names cause annoying problems.
_MIDDLE_NAMES = ['St.', 'Van', 'Von', 'Al', 'El', 'La']

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
        return f'{first[0]}.{middle} {last}'
    else:
        first, last = components
        return f'{first[0]}.{last}'


def full_name(has_name_substr: str) -> str:
    """Extract the full name from a substring that begins with the player's name."""
    name_components = _parse_name_components(has_name_substr)
    return ' '.join(name_components)


def _parse_name_components(has_name_substr: str) -> tuple:
    """From a string that begins with a players name, extract the first, last, and middle names."""
    name_str = has_name_substr.strip(' ')
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
        logger.warning(f"Issue parsing name components for: {has_name_substr}")
        pass
    if middle:
        return first, middle, last
    else:
        return first, last
