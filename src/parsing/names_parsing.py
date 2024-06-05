"""Responsible for reading player names from the play log."""
import logging
import re
from typing import Any, Dict, List

from parsing.consts import (QB, RB, FB, TE, X_SE, Z_FL, SLOT, LT, LG, C, RG, RT,
                            LDE, NT, RDE, WLB, SLB, MLB, WILB, SILB, LCB, RCB,
                            NB, DB, SS, FS, PRIMARY, SECONDARY, BALL_CARRIER)
from parsing.name_utils import shorten_name, target_receiver_name
from parsing.regexes import PASS_BLOCKED_PLAYER_REGEX, SACK_PLAYER_REGEX, QB_REGEX
from schema.player_names import PlayerNames

logger = logging.getLogger(__name__)


class NameParser(object):

    def __init__(self, particpation_tbl: Any, summaries: List[Any]):
        self._short_name_to_full_name: Dict[str, str] = {}
        self._init_short_name_dict(particpation_tbl, summaries)

    def _init_short_name_dict(self, participation_tbl: Any, summaries: List[Any]) -> None:
        for table in participation_tbl:
            for row in table.find_all('tr'):
                player = row.contents[0].text
                full_name = ' '.join(player.split(' ')[1:])
                short_name = shorten_name(full_name)
                self._short_name_to_full_name[short_name] = full_name

        # QBs are not in the participation table, so we scan every pass play to find their names.
        for summary in summaries:
            if " pass " in summary:
                match = re.search(QB_REGEX, summary)
                if match:
                    player_name = match.group(1)
                    self._short_name_to_full_name[shorten_name(player_name)] = player_name
                else:
                    logger.warning(f"Failed to find the QB in the play summary: {summary}")
                    continue

    def parse_player_names(self, summary, play_call) -> PlayerNames:
        """Assign the player names to positions according to the log info.
    
        :param: summary: The summary string of the play.
        :param: play_call: The play call table object with full player names,
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
                out.qb_name = self._name_from_play_call(off_player)
            elif off_position == RB:
                out.rb_name = self._name_from_play_call(off_player)
            elif off_position == FB:
                out.fb_name = self._name_from_play_call(off_player)
            elif off_position == TE and out.te_name == '':
                out.te_name = self._name_from_play_call(off_player)
            elif off_position == X_SE:
                out.x_name = self._name_from_play_call(off_player)
            elif off_position == Z_FL:
                out.z_name = self._name_from_play_call(off_player)
            elif off_position == SLOT:
                if out.slot_1_name == '':
                    out.slot_1_name = self._name_from_play_call(off_player)
                elif out.slot_2_name == '':
                    out.slot_2_name = self._name_from_play_call(off_player)
            elif off_position == LT:
                out.lt_name = self._name_from_play_call(off_player)
            elif off_position == LG:
                out.lg_name = self._name_from_play_call(off_player)
            elif off_position == C:
                out.c_name = self._name_from_play_call(off_player)
            elif off_position == RG:
                out.rg_name = self._name_from_play_call(off_player)
            elif off_position == RT:
                out.rt_name = self._name_from_play_call(off_player)

            def_player = off_def_players[3]
            def_position = def_player.split(' ')[0]
            if def_position == LDE:
                out.lde_name = self._name_from_play_call(def_player)
            elif def_position == '3tcDT':
                if 'Over' in def_formation:
                    out.ldt_name = self._name_from_play_call(def_player)
                elif '34' in def_formation:
                    out.nt_name = self._name_from_play_call(def_player)
                else:
                    out.rdt_name = self._name_from_play_call(def_player)
            elif def_position == '1tcDT':
                if 'Under' in def_formation:
                    out.ldt_name = self._name_from_play_call(def_player)
                elif '34' in def_formation:
                    out.nt_name = self._name_from_play_call(def_player)
                else:
                    out.rdt_name = self._name_from_play_call(def_player)
            elif def_position == NT:
                out.nt_name = self._name_from_play_call(def_player)
            elif def_position == RDE:
                out.rde_name = self._name_from_play_call(def_player)
            elif def_position == MLB:
                out.mlb_name = self._name_from_play_call(def_player)
            elif def_position == SLB:
                out.slb_name = self._name_from_play_call(def_player)
            elif def_position == WLB:
                out.wlb_name = self._name_from_play_call(def_player)
            elif def_position == SILB:
                out.silb_name = self._name_from_play_call(def_player)
            elif def_position == WILB:
                out.wilb_name = self._name_from_play_call(def_player)
            elif def_position == RCB:
                out.rcb_name = self._name_from_play_call(def_player)
            elif def_position == LCB:
                out.lcb_name = self._name_from_play_call(def_player)
            elif def_position == NB:
                out.nb_name = self._name_from_play_call(def_player)
            elif def_position == DB:
                out.db_name = self._name_from_play_call(def_player)
            elif def_position == SS:
                out.ss_name = self._name_from_play_call(def_player)
            elif def_position == FS:
                out.fs_name = self._name_from_play_call(def_player)

            out.ball_carrier_name = self._parse_ball_carrier(play_call)
            out.primary_receiver_name = self._parse_receiver_name(play_call, PRIMARY)
            out.secondary_receiver_name = self._parse_receiver_name(play_call,
                                                                    SECONDARY)
            out.targeted_receiver_name = self._parse_targeted_receiver(summary)
        return out

    def _name_from_play_call(self, name_column):
        short_name = ' '.join(name_column.split(' ')[1:])
        try:
            return self._short_name_to_full_name[short_name]
        except KeyError:
            print(f"Issue with this player: {short_name}")

    def _parse_ball_carrier(self, play_call) -> str:
        for player in play_call[1:]:
            action = player[1]
            if action == BALL_CARRIER:
                return ' '.join(player[0].split(' ')[1:])
        return ''

    def _parse_targeted_receiver(self, summary) -> str:
        if ' pass ' in summary:
            return target_receiver_name(summary)
        return ''

    def _parse_receiver_name(self, play_call, priority_type: str) -> str:
        for player in play_call[1:]:
            name = self._name_from_play_call(player[0])
            priority = player[1].split(',')[0]
            if priority == priority_type:
                return name
        return ''

    def _parse_pressure_name(self, summary) -> str:
        if re.search(SACK_PLAYER_REGEX, summary):
            sackers = re.search(SACK_PLAYER_REGEX, summary)[0]
            sackers = sackers.split(' and ')
            first_sacker = sackers[0]
            return first_sacker

        # TODO: Implement hurry
        if re.search(PASS_BLOCKED_PLAYER_REGEX, summary):
            blocker = re.search(PASS_BLOCKED_PLAYER_REGEX, summary)[0]
            return blocker
        return ''
