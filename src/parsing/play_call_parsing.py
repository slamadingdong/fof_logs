"""Responsible for parsing the offensive and defensive play calls."""
import logging
import re
from typing import Optional, Any

from parsing.consts import LE, LT, LG, LM, RM, RG, RT, RE, BALL_CARRIER, \
    PRIMARY, \
    SECONDARY, PROTECT, BUZZ, BLITZ, DOUBLE, SPY
from parsing.regexes import *
from schema.play_call import (DefensivePlay,
                                  OffensivePlay,
                                  PlayCall,
                                  PlayType)

logger = logging.getLogger(__name__)

# Strings to help identify things in the tables.
_FORMATION = ' formation'
_PERSONNEL = ' Personnel'

# Play text converted to the run direction.
_RUN_DIRECTION_MAP = {
    'around left end': LE,
    'outside the left tackle': LT,
    'inside the left tackle': LG,
    'inside the left guard': LM,
    'around right end': RE,
    'outside the right tackle': RT,
    'inside the right tackle': RG,
    'inside the right guard': RM,
}


def parse_play_call(summary_text: str, play_call: Any) -> Optional[PlayCall]:
    """Parse the play call from the table and summary.

    :param: play_call: The beautifulsoup table with the playcall.
    :param: summary_text: The string with the summary of the play outcome."""
    offense = _parse_offense(play_call, summary_text)
    defense = _parse_defense(play_call)
    # Offense and defense must both be successfully parsed.
    if offense is None or defense is None:
        return None
    return PlayCall(offns=offense, dfns=defense)


def _parse_offense(play_call: Any, summary_text: str) -> \
        Optional[OffensivePlay]:
    try:
        formations_row = play_call[0]
        off = formations_row[1]
        off = off.split(', ')
        personnel = off[0].replace(_PERSONNEL, '')
        qb_alignment = ''
        formation = ''
        if len(off) >= 2:
            formation = off[1].replace(_FORMATION, '')
        if len(off) >= 3:
            qb_alignment = off[2]
    except IndexError:
        raise IndexError("Failed to parse offensive formation for: " + repr(
            play_call[0]))
    protect = 0
    primary_route = ''
    primary_pos = ''
    secondary_route = ''
    secondary_pos = ''
    ball_carrier = ''
    run_direction = ''
    for player_resp in play_call[1:]:
        position = player_resp[0].split(' ')[0]
        route = player_resp[1]
        if len(route) == 0:
            continue
        if route == BALL_CARRIER:
            ball_carrier = position
            continue
        if route == PROTECT:
            protect += 1
            continue
        priority, route = route.split(',')
        if priority == PRIMARY:
            primary_route = route.strip()
            primary_pos = position
        if priority == SECONDARY:
            secondary_route = route.strip()
            secondary_pos = position
    if ball_carrier:
        for direction in _RUN_DIRECTION_MAP.keys():
            if direction in summary_text:
                run_direction = _RUN_DIRECTION_MAP[direction]
    play_type = _parse_play_type(summary_text)
    return OffensivePlay(off_personnel=personnel,
                         off_formation=formation,
                         qb_alignment=qb_alignment,
                         primary_route=primary_route,
                         primary_receiver=primary_pos,
                         secondary_route=secondary_route,
                         secondary_receiver=secondary_pos,
                         protect=protect,
                         ball_carrier=ball_carrier,
                         run_direction=run_direction,
                         play_type=play_type)


def _parse_defense(play_call: Any) -> Optional[DefensivePlay]:
    try:
        buzz = False
        formations_row = play_call[0]
        dfns = formations_row[3].split(', ')
        formation = dfns[0].replace(_FORMATION, '')
        personnel = dfns[1].replace(_PERSONNEL, '')
        coverage = dfns[2]
        if BUZZ in dfns:
            buzz = True
    except IndexError:
        logger.warning(f'Failed to parse the defensive play call for '
                       f'input text: \n {repr(play_call)}')
        return None
    blitz = 0
    spy = False
    double_target = ''
    for player_resp in play_call[1:]:
        resp = player_resp[4]
        if BLITZ in resp:
            blitz += 1
        elif DOUBLE in resp:
            double_target = resp.split(' ')[1]
        elif SPY in resp:
            spy = True
    return DefensivePlay(def_personnel=personnel,
                         def_formation=formation,
                         coverage=coverage,
                         spy=spy,
                         double_target=double_target,
                         blitz=blitz,
                         buzz=buzz)


def _parse_play_type(summary_text: str) -> PlayType:
    if 'Play-Action' in summary_text:
        return PlayType('pass', playaction=True)
    if 'scrambled' in summary_text:
        return PlayType('pass')
    if (re.search(SACKED_REGEX, summary_text) or
            re.search(PASS_COMPLETED_REGEX, summary_text) or
            re.search(SIMPLE_INCOMPLETION_REGEX, summary_text) or
            re.search(DROPPED_REGEX, summary_text) or
            re.search(PASS_BLOCKED_REGEX, summary_text) or
            re.search(INTERCEPTION_REGEX, summary_text) or
            re.search(HURRIED_REGEX, summary_text)):
        return PlayType('pass')
    if re.search(FINESSE_RUN_REGEX, summary_text):
        return PlayType('run', finesse_run=True)
    if re.search(REVERSE_REGEX, summary_text):
        return PlayType('run', reverse=True)
    if re.search(KNEEL_REGEX, summary_text):
        return PlayType('kneel')
    if re.search(RUN_REGEX, summary_text) or \
            'kept the ball' in summary_text:
        return PlayType('run')
    logger.warning(f'Could not determine play type for: \n {summary_text}')
