"""Responsible for parsing all data in the play summary text."""
import re
import logging
from typing import Tuple, Any

from parsing.consts import PROTECT
from parsing.name_utils import target_receiver_name
from parsing.play_call_parsing import parse_play_type
from parsing.regexes import *
from schema.play_outcome import PassingOutcome, RunningOutcome, PlayOutcome

logger = logging.getLogger(__name__)

# Defines the yardage for each type of penalty. Not implemented yet.
_PENALTY_YARDAGE_MAP = {
    'Offensive Holding': 10,
    'False Start': 5,
    'Defensive Holding': 5,
    'Defensive Pass Interference': 15,  # an estimate, this one varies.
    'Unnecessary Roughness': 15,
    'Illegal Contact': 5,
    'Offsides': 5,
    'Encroachment': 5,
    'Intentional Face Mask': 15,
    'Illegal Use of the Hands': 10,
    'Delay of Game': 5,
    'Roughing the Passer': 15,
    'Offensive Pass Interference': 10,
    'Illegal Formation': 5,
    'Unsportsmanlike Conduct': 15,
    'Illegal Motion': 5,
    'Illegal Use of the Hands by the Defense': 5,
    'Tripping': 10
}


def parse_play_outcome(summary_text: str, play_call: Any) -> PlayOutcome:
    """Parses the text of the play summary into a PlayOutcome and down/distance.
    """

    if _should_parse(summary_text):
        # TODO: Parse penalties.
        familiar = ' familiar ' in summary_text
        if parse_play_type(summary_text).type == "pass":
            try:
                outcome = _parse_passing_outcome(summary_text, play_call)
            except ValueError as e:
                raise ValueError(
                    repr(e) + f"Regexes failed for: {summary_text}")
        else:
            outcome = _parse_running_outcome(summary_text)
        play_outcome = PlayOutcome(outcome=outcome, familiar=familiar)
        return play_outcome


def _parse_running_outcome(summary_text: str) -> RunningOutcome:
    try:
        yards = int(re.search(YARDAGE_REGEX, summary_text)[0])
    except TypeError:
        logger.warning(f"Couldn't find yardage for: {summary_text}")
        return RunningOutcome(yards=0)
    return RunningOutcome(yards=int(yards))


def _parse_passing_outcome(summary_text: str, play_call: Any) -> PassingOutcome:
    complete = (re.search(PASS_COMPLETED_REGEX, summary_text) is not None)
    yards = 0
    yac = 0
    hurried = False
    blocked = False
    intercepted = False
    throw_into_double = False
    dropped = False

    if ' scrambled ' in summary_text:
        yards = int(re.search(YARDAGE_REGEX, summary_text)[0])
        return PassingOutcome(complete=False,
                              yards=yards,
                              yac=0,
                              scramble=True)

    if re.search(SACKED_REGEX, summary_text):
        yards = -1 * int(re.search(SACK_YARDS_LOST_REGEX, summary_text)[0])
        return PassingOutcome(complete=False,
                              yards=yards,
                              yac=0,
                              sacked=True)

    if complete:
        yards = int(re.search(YARDAGE_REGEX, summary_text)[0])
        yac = re.search(YAC_REGEX, summary_text)
        if yac:
            yac = int(yac[0])
        else:
            yac = 0

    if re.search(HURRIED_REGEX, summary_text):
        hurried = True
    if re.search(PASS_BLOCKED_REGEX, summary_text):
        blocked = True
    if re.search(DROPPED_REGEX, summary_text):
        dropped = True
    if re.search(INTERCEPTION_REGEX, summary_text):
        intercepted = True
    if 'threw away from the double coverage' in summary_text:
        throw_into_double = False
    if 'threw into double coverage' in summary_text:
        throw_into_double = True

    target_receiver = target_receiver_name(summary_text)
    target_route, target_priority = _parse_targeted_route(
        play_call, target_receiver)

    return PassingOutcome(complete=complete,
                          yards=yards,
                          yac=yac,
                          sacked=False,
                          hurried=hurried,
                          blocked=blocked,
                          intercepted=intercepted,
                          throw_into_double=throw_into_double,
                          dropped=dropped,
                          target_route=target_route,
                          target_priority=target_priority)


def _parse_targeted_route(play_call, target_receiver: str) -> Tuple[str, str]:
    for player_resp in play_call[1:]:
        try:
            values = player_resp[0].split(' ')
            name = ' '.join(values[1:])
            if name == target_receiver:
                priority, route = player_resp[1].split(',')
                return route.strip(), priority
        except ValueError:
            # Occurs for 'Protect' responsibility.
            return PROTECT, PROTECT
    return '', ''


def _is_two_pt_conversion(summary_text):
    return 'two-point conversion' in summary_text or \
        'conversion attempt' in summary_text


def _is_punt(summary_text):
    return 'punted ' in summary_text


def _is_field_goal(summary_text):
    return "field goal" in summary_text


def _is_final_score(summary_text):
    return "Final Score:" in summary_text


def _is_coin_toss(summary_text):
    return "won the toss" in summary_text or 'won the coin toss' in summary_text


def _is_two_min_warning(summary_text):
    return "Official time out for the two-minute warning" in summary_text


def _is_extra_point(summary_text):
    return "Extra point" in summary_text


def _is_kickoff(summary_text):
    return "kicked off" in summary_text


def _is_start_of_quarter(summary_text):
    return "Start of " in summary_text


def _is_timeout(summary_text):
    return "called a time out" in summary_text


def _should_parse(summary_text):
    return not any([_is_timeout(summary_text),
                    _is_extra_point(summary_text)
                       , _is_kickoff(summary_text)
                       , _is_start_of_quarter(summary_text)
                       , _is_two_min_warning(summary_text)
                       , _is_coin_toss(summary_text)
                       , _is_final_score(summary_text)
                       , _is_field_goal(summary_text)
                       , _is_punt(summary_text)
                       , _is_two_pt_conversion(summary_text)])
