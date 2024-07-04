"""Responsible for reading player names from the play log."""
import logging
import re
from typing import Any, List

from parsing.consts import (QB, RB, FB, TE, X_SE, Z_FL, SLOT, LT, LG, C, RG, RT,
                            LDE, NT, RDE, WLB, SLB, MLB, WILB, SILB, LCB, RCB,
                            NB, DB, SS, FS, PRIMARY, SECONDARY, BALL_CARRIER)
from parsing.name_utils import shorten_name, target_receiver_name, parse_team_rosters, \
    which_team_offense
from parsing.regexes import PASS_BLOCKED_PLAYER_REGEX, SACK_PLAYER_REGEX, QB_REGEX
from schema.player_names import PlayerNames

logger = logging.getLogger(__name__)


class NameParser(object):

    def __init__(self, particpation_tbl: Any, summaries_and_calls: List[Any]):
        home_team, away_team, short_names, full_names = parse_team_rosters(particpation_tbl)
        self._home_team = home_team
        self._away_team = away_team
        self._full_names = full_names
        self._short_names = short_names
        self._short_name_to_full_name = {'home': {}, 'away': {}}
        self._init_short_name_dict(particpation_tbl, summaries_and_calls)

    def _init_short_name_dict(self, participation_tbl: Any, summaries_and_calls) -> None:
        away_table, home_table = participation_tbl[0], participation_tbl[1]
        for row in home_table.find_all('tr'):
            team_table = self._short_name_to_full_name['home']
            player = row.contents[0].text
            if player == "Unknown":
                continue
            full_name = ' '.join(player.split(' ')[1:])
            short_name = shorten_name(full_name)
            team_table[short_name] = full_name
        for row in away_table.find_all('tr'):
            team_table = self._short_name_to_full_name['away']
            player = row.contents[0].text
            if player == "Unknown":
                continue
            full_name = ' '.join(player.split(' ')[1:])
            short_name = shorten_name(full_name)
            team_table[short_name] = full_name

        # QBs are not in the participation table, so we scan every pass play to find their names.
        for summary, call in summaries_and_calls:
            if 'Unknown' in summary or call is None:
                continue
            offense = which_team_offense(call, self._short_names['home'], self._short_names['away'])
            team_table = self._short_name_to_full_name[offense]
            if " pass " in summary:
                match = re.search(QB_REGEX, summary)
                if match:
                    player_name = match.group(1)
                    team_table[shorten_name(player_name)] = player_name
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
        offense = which_team_offense(play_call, self._short_names['home'],
                                     self._short_names['away'])
        defense = 'home' if offense == 'away' else 'away'

        for off_def_players in play_call[1:]:
            off_player = off_def_players[0]
            off_position = off_player.split(' ')[0]
            if off_position == QB:
                out.qb_name = self._name_from_play_call(off_player, offense)
            elif off_position == RB:
                out.rb_name = self._name_from_play_call(off_player, offense)
            elif off_position == FB:
                out.fb_name = self._name_from_play_call(off_player, offense)
            elif off_position == TE and out.te_name == '':
                out.te_name = self._name_from_play_call(off_player, offense)
            elif off_position == X_SE:
                out.x_name = self._name_from_play_call(off_player, offense)
            elif off_position == Z_FL:
                out.z_name = self._name_from_play_call(off_player, offense)
            elif off_position == SLOT:
                if out.slot_1_name == '':
                    out.slot_1_name = self._name_from_play_call(off_player, offense)
                elif out.slot_2_name == '':
                    out.slot_2_name = self._name_from_play_call(off_player, offense)
            elif off_position == LT:
                out.lt_name = self._name_from_play_call(off_player, offense)
            elif off_position == LG:
                out.lg_name = self._name_from_play_call(off_player, offense)
            elif off_position == C:
                out.c_name = self._name_from_play_call(off_player, offense)
            elif off_position == RG:
                out.rg_name = self._name_from_play_call(off_player, offense)
            elif off_position == RT:
                out.rt_name = self._name_from_play_call(off_player, offense)

            def_player = off_def_players[3]
            def_position = def_player.split(' ')[0]
            if def_position == LDE:
                out.lde_name = self._name_from_play_call(def_player, defense)
            elif def_position == '3tcDT':
                if 'Over' in def_formation:
                    out.ldt_name = self._name_from_play_call(def_player, defense)
                elif '34' in def_formation:
                    out.nt_name = self._name_from_play_call(def_player, defense)
                else:
                    out.rdt_name = self._name_from_play_call(def_player, defense)
            elif def_position == '1tcDT':
                if 'Under' in def_formation:
                    out.ldt_name = self._name_from_play_call(def_player, defense)
                elif '34' in def_formation:
                    out.nt_name = self._name_from_play_call(def_player, defense)
                else:
                    out.rdt_name = self._name_from_play_call(def_player, defense)
            elif def_position == NT:
                out.nt_name = self._name_from_play_call(def_player, defense)
            elif def_position == RDE:
                out.rde_name = self._name_from_play_call(def_player, defense)
            elif def_position == MLB:
                out.mlb_name = self._name_from_play_call(def_player, defense)
            elif def_position == SLB:
                out.slb_name = self._name_from_play_call(def_player, defense)
            elif def_position == WLB:
                out.wlb_name = self._name_from_play_call(def_player, defense)
            elif def_position == SILB:
                out.silb_name = self._name_from_play_call(def_player, defense)
            elif def_position == WILB:
                out.wilb_name = self._name_from_play_call(def_player, defense)
            elif def_position == RCB:
                out.rcb_name = self._name_from_play_call(def_player, defense)
            elif def_position == LCB:
                out.lcb_name = self._name_from_play_call(def_player, defense)
            elif def_position == NB:
                out.nb_name = self._name_from_play_call(def_player, defense)
            elif def_position == DB:
                out.db_name = self._name_from_play_call(def_player, defense)
            elif def_position == SS:
                out.ss_name = self._name_from_play_call(def_player, defense)
            elif def_position == FS:
                out.fs_name = self._name_from_play_call(def_player, defense)

            out.ball_carrier_name = self._parse_ball_carrier(play_call, offense)
            out.primary_receiver_name = self._parse_receiver_name(play_call, PRIMARY, offense)
            out.secondary_receiver_name = self._parse_receiver_name(play_call,
                                                                    SECONDARY, offense)
            out.targeted_receiver_name = self._parse_targeted_receiver(summary)
        return out

    def _name_from_play_call(self, name_column, which_team):
        team_table = self._short_name_to_full_name[which_team]
        short_name = ' '.join(name_column.split(' ')[1:])
        if short_name == "Unknown":
            return ''
        try:
            return team_table[short_name]
        except KeyError:
            return ''

    def _parse_ball_carrier(self, play_call, which_team) -> str:
        team_table = self._short_name_to_full_name[which_team]
        for player in play_call[1:]:
            action = player[1]
            if action == BALL_CARRIER:
                short_name = ' '.join(player[0].split(' ')[1:])
                try:
                    return team_table[short_name]
                except KeyError:
                    return ''
        return ''

    def _parse_targeted_receiver(self, summary) -> str:
        if ' pass ' in summary:
            return target_receiver_name(summary)
        return ''

    def _parse_receiver_name(self, play_call, priority_type: str, offense: str) -> str:
        for player in play_call[1:]:
            name = self._name_from_play_call(player[0], offense)
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
