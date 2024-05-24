"""Responsible for reading player names from the play log."""
import re

from consts import (QB, RB, FB, TE, SLOT, LT, LG, C, RG, RT,
                    LDE, NT, RDE, WLB, SLB, MLB, WILB, SILB, LCB, RCB, NB, DB,
                    SS, FS, PRIMARY, SECONDARY, BALL_CARRIER)
from name_utils import shorten_name, target_receiver_name
from regexes import PASS_BLOCKED_PLAYER_REGEX
from regexes import SACK_PLAYER_REGEX
from src.schema.player_names import PlayerNames


def parse_player_names(summary, play_call) -> PlayerNames:
    """Assign the player names to positions according to the log info.

    :param: summary: The summary string of the play.
    :param: play_call: The play call table object with player names,
    positions, and actions (e.g. ball carrier, blitz, or a route).
    """
    out = PlayerNames()
    formations_row = play_call[0]
    dfns = formations_row[3].split(', ')
    def_formation = dfns[0]

    for off_def_players in play_call[1:]:
        off_player = off_def_players[0]
        off_position = off_player.split(' ')[0]
        if off_position == QB:
            out.qb_name = _name_from_play_call(off_player)
        elif off_position == RB:
            out.rb_name = _name_from_play_call(off_player)
        elif off_position == FB:
            out.fb_name = _name_from_play_call(off_player)
        elif off_position == TE and out.te_name == '':
            out.te_name = _name_from_play_call(off_player)
        elif off_position == X:
            out.x_name = _name_from_play_call(off_player)
        elif off_position == Z:
            out.z_name = _name_from_play_call(off_player)
        elif off_position == SLOT:
            if out.slot_1_name == '':
                out.slot_1_name = _name_from_play_call(off_player)
            elif out.slot_2_name == '':
                out.slot_2_name = _name_from_play_call(off_player)
        elif off_position == LT:
            out.lt_name = _name_from_play_call(off_player)
        elif off_position == LG:
            out.lg_name = _name_from_play_call(off_player)
        elif off_position == C:
            out.c_name = _name_from_play_call(off_player)
        elif off_position == RG:
            out.rg_name = _name_from_play_call(off_player)
        elif off_position == RT:
            out.rt_name = _name_from_play_call(off_player)

        def_player = off_def_players[3]
        def_position = def_player.split(' ')[0]
        if def_position == LDE:
            out.lde_name = _name_from_play_call(def_player)
        elif def_position == '3tcDT':
            if 'Over' in def_formation:
                out.ldt_name = _name_from_play_call(def_player)
            else:
                out.rdt_name = _name_from_play_call(def_player)
        elif def_position == '1tcDT':
            if 'Under' in def_formation:
                out.ldt_name = _name_from_play_call(def_player)
            else:
                out.rdt_name = _name_from_play_call(def_player)
        elif def_position == NT:
            out.nt_name = _name_from_play_call(def_player)
        elif def_position == RDE:
            out.rde_name = _name_from_play_call(def_player)
        elif def_position == MLB:
            out.mlb_name = _name_from_play_call(def_player)
        elif def_position == SLB:
            out.slb_name = _name_from_play_call(def_player)
        elif def_position == WLB:
            out.wlb_name = _name_from_play_call(def_player)
        elif def_position == SILB:
            out.silb_name = _name_from_play_call(def_player)
        elif def_position == WILB:
            out.wilb_name = _name_from_play_call(def_player)
        elif def_position == RCB:
            out.rcb_name = _name_from_play_call(def_player)
        elif def_position == LCB:
            out.lcb_name = _name_from_play_call(def_player)
        elif def_position == NB:
            out.nb_name = _name_from_play_call(def_player)
        elif def_position == DB:
            out.db_name = _name_from_play_call(def_player)
        elif def_position == SS:
            out.ss_name = _name_from_play_call(def_player)
        elif def_position == FS:
            out.fs_name = _name_from_play_call(def_player)

        out.ball_carrier_name = _parse_ball_carrier(play_call)
        out.primary_receiver_name = _parse_receiver_name(play_call, PRIMARY)
        out.secondary_receiver_name = _parse_receiver_name(play_call,
                                                           SECONDARY)
        out.targeted_receiver_name = _parse_targeted_receiver(summary)
    return out


def _name_from_play_call(name_column):
    return ' '.join(name_column.split(' ')[1:])


def _parse_ball_carrier(play_call) -> str:
    for player in play_call[1:]:
        action = player[1]
        if action == BALL_CARRIER:
            return ' '.join(player[0].split(' ')[1:])
    return ''


def _parse_targeted_receiver(summary) -> str:
    if ' pass ' in summary:
        return target_receiver_name(summary)
    return ''


def _parse_receiver_name(play_call, priority_type: str) -> str:
    for player in play_call[1:]:
        name = _name_from_play_call(player[0])
        priority = player[1].split(',')[0]
        if priority == priority_type:
            return name
    return ''


def _parse_pressure_name(summary) -> str:
    if re.search(SACK_PLAYER_REGEX, summary):
        sackers = re.search(SACK_PLAYER_REGEX, summary)[0]
        sackers = sackers.split(' and ')
        first_sacker = sackers[0]
        first_sacker = first_sacker.split(' ')[1:]
        return shorten_name(' '.join(first_sacker))

    # TODO: Implement hurry
    if re.search(PASS_BLOCKED_PLAYER_REGEX, summary):
        blocker = re.search(PASS_BLOCKED_PLAYER_REGEX, summary)[0]
        return shorten_name(' '.join(blocker.split(' ')[1:]))
    return ''
