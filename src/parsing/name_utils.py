"""Utilities for parsing names."""
import re

from consts import QB, RB, FB, TE, WR, C, T, G, P, K

# The possible positions for a targeted receiver.
_TARGET_POSITIONS = [QB, RB, FB, TE, WR, C, T, G, P, K]

# Add if necessary, these names cause annoying problems.
_MIDDLE_NAMES = ['St.', 'Van', 'Von', 'Al', 'El', 'La']

# Regex for finding the next name element of a string.
_NEXT_NAME_REGEX = r'[A-Z]\.'


def target_receiver_name(text: str) -> str:
    """Extract the name of the target receiver from the text of the play."""
    words = text.split(' ')
    for i in range(len(words)):
        if words[i] in _TARGET_POSITIONS:
            name = ' '.join(words[i + 1:])
            return shorten_name(name)
    # Return an empty string if no target position was found.
    return ''


def shorten_name(name_str: str) -> str:
    """Shorten the name to first initial and last name."""
    name_str = name_str.strip(' ')
    names = name_str.split(' ')
    middle = None
    first = names[0]
    if len(names) < 2:
        return name_str
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
        pass
    if middle:
        return f'{first[0]}.{middle} {last}'
    else:
        return f'{first[0]}.{last}'
