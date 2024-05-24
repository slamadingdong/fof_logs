"""Responsible for loading game logs from a directory."""
import glob
import logging
import re
from typing import List, Tuple, Any

# noinspection PyUnresolvedReferences
import cchardet
from bs4 import BeautifulSoup as bs

logger = logging.getLogger(__name__)

# Regex gets the season year of the given game log.
_YEAR_REGEX = r'(?<=log)\d{4}'


def game_log_paths(log_dir: str) -> List[str]:
    """Get all game log paths in the given directory.

    :param: log_dir: The directory path containing the game logs."""
    game_log_path_regex = f"{log_dir}\\log*.html"
    all_paths = glob.glob(pathname=game_log_path_regex)
    logger.info(f"Found {len(all_paths)} game logs.")
    return all_paths


def get_log_participation_year(game_log_path: str) -> Tuple[Any, Any, int]:
    """Parses a single game log path as a tuple with beautifulSoup objects."""
    with open(game_log_path, 'r') as game_log_file:
        year = int(re.search(_YEAR_REGEX, game_log_path)[0])
        contents = game_log_file.read()
    game_log_soup = bs(contents, 'lxml')
    play_by_play = game_log_soup.table
    plays = play_by_play.children
    # Used to identify who was the home team or away team.
    participation_table = game_log_soup.find_all('table')[-2:]
    return plays, participation_table, year
