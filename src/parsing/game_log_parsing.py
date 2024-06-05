"""Responsible for fully parsing the play by play."""
from typing import Any, List, Tuple

from bs4 import element

from parsing.game_context_parsing import GameContextParser
from parsing.names_parsing import NameParser
from parsing.play_call_parsing import parse_play_call
from parsing.play_summary_parsing import parse_play_outcome
from schema.parsed_play import ParsedPlay


def parse_full_game(raw_log: Any, participation: Any) -> List[ParsedPlay]:
    """Given the raw play-by-play soup object, parse every play.

    :param: raw_log: The beautifulsoup of the play by play for a game.
    :param: participation: The beautifulsoup of the participation table for
    the game.
    :returns: A list of ParsedPlays in order for the given game.
    """
    output = []
    context_parser = GameContextParser(participation)
    summaries_calls = _summaries_and_calls(game_log=raw_log)
    summaries = [summary for summary, _ in summaries_calls]
    name_parser = NameParser(participation, summaries)
    for summary, play_call in summaries_calls:
        if 'Unknown' in summary or play_call is None:
            continue
        outcome = parse_play_outcome(summary, play_call)
        names = name_parser.parse_player_names(summary, play_call)
        playcall = parse_play_call(summary, play_call)
        context = context_parser.parse_context(summary, play_call)
        if playcall and context:
            output.append(ParsedPlay(call=playcall, outcome=outcome,
                                     context=context, names=names))
    return output


def _get_summary(log: Any):
    summary_text = ''
    for child in log.children:
        try:
            texts = child.find_all(text=True, recursive=False)
            score_info = child.find_all('b', recursive=False)
        except AttributeError:
            return None
        if len(score_info) == 0:
            summary_text = ''.join(texts)
        if len(score_info) > 0:
            score_type = score_info[0].string
            summary_text = score_type.join(texts)
        if len(score_info) == 2:
            summary_text += score_info[1].string
        if len(summary_text) == 0:
            return None
        return summary_text


def _get_play_call(log):
    try:
        play_call = log.find_all('tr')
        if play_call:
            return [[ele.text for ele in row] for row in play_call]
    except AttributeError:
        return None


def _summaries_and_calls(game_log) -> List[Tuple[str, Any]]:
    out = []
    for log in game_log:
        if log.text == '\n':
            continue
        if not isinstance(log, element.NavigableString):
            log = log.td
        summary = _get_summary(log)
        if summary is None:
            continue
        call = _get_play_call(log)
        out.append((summary, call))
    return out
