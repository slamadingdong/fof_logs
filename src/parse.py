"""Script for efficiently parsing multiple game log files."""

import argparse
import itertools
import logging
import os
import time
# Ignore annoying pandas warnings
import warnings
from dataclasses import asdict
from multiprocessing import Pool, cpu_count
from pathlib import Path
from typing import List, Dict

warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd

from column_names import LEAGUE_ID
from dtypes import cast_dtypes
from loader import get_log_participation_year, game_log_paths
from parsing.game_log_parsing import parse_full_game, ParsedPlay

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_NUM_PROCESSES = cpu_count()

logger.info(f"Using {_NUM_PROCESSES} processes to parse logs.")


def parse_one_log(path: str, idx: int) -> List[Dict]:
    """Worker task to parse the game log at the given path."""
    raw_log, participation, year = get_log_participation_year(path)
    parsed: List[ParsedPlay] = parse_full_game(raw_log, participation)
    parsed_dicts = [asdict(parsed_play) for parsed_play in parsed]
    for parsed_dict in parsed_dicts:
        parsed_dict.update({"year": year})

    if idx % 100 == 0:
        logger.info(f'Successfully parsed game log {idx}.')
    return parsed_dicts


def load_and_parse(league_log_dir: str, max_to_parse=None) -> List[List[dict]]:
    """Load all the game logs in the given directory and parse them.
    :param: league_log_dir: The directory with league game logs.
    :param: max_to_parse: Optional parameter to limit how many game logs to
    parse.
    """
    start_time = time.perf_counter()
    paths = game_log_paths(league_log_dir)
    paths = paths[:max_to_parse] if max_to_parse else paths
    logging.info(f'About to parse {len(paths)} game logs.')

    with Pool(_NUM_PROCESSES) as pool:
        results = [pool.apply_async(parse_one_log, (path, idx)) for idx, path in
                   enumerate(paths)]
        parsed_data = [res.get() for res in results]
        end_time = time.perf_counter()
        logger.info(f'Took {end_time - start_time} seconds to parse '
                    f'{len(results)}  logs.')
    return parsed_data


def to_df_and_save(parsed_games: List[List[dict]],
                   league_num: str,
                   export_dir: str) -> None:
    """Convert the parsed data to a dataframe and save it in feather format.

    :param: parsed_games: Each item represents a parsed game, and each game
    is a list of dictionaries, one dictionary per play.
    :param: league_num: The league number from which these games were parsed.
    :param: export_dir: The directory to save the dataframe to.
    """
    start_time = time.perf_counter()

    all_rows: List[dict] = list(itertools.chain.from_iterable(parsed_games))
    df: pd.DataFrame = pd.json_normalize(all_rows)
    df.rename(columns=lambda x: x.split('.')[-1], inplace=True)
    df[LEAGUE_ID] = league_num
    df = cast_dtypes(df)
    df.reset_index(inplace=True)

    export_dir = os.path.join(export_dir, league_num)
    Path(export_dir).mkdir(parents=True, exist_ok=True)
    export_path = os.path.join(export_dir, "parsed_logs.fe")
    df.to_feather(export_path)
    end_time = time.perf_counter()
    logger.info(f'Took {end_time - start_time} seconds to make the dataframe '
                f'and save it.')
    return


def main(args):
    """Parse games and save them as a feather file."""
    leagues = args.leag_num.split(",")
    for league in leagues:
        league_log_dir = os.path.join(args.logs_dir, league)
        parsed = load_and_parse(league_log_dir, args.max_to_parse)
        to_df_and_save(parsed, league, args.export_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--logs_dir", help="The directory of the game logs for "
                                           "Front Office Football, usually in "
                                           "'~/Front Office "
                                           "Football/leaguehtml/'", type=str)
    parser.add_argument("--league_ids", help="A comma separated list of the 8 character league "
                                             "numbers or "
                                             "identifiers to parse logs for, "
                                             "e.g. 'LG000010,LG000021'.", type=str)
    parser.add_argument("--max_to_parse", help="Optional: How many logs to "
                                               "parse. If not set, it will "
                                               "parse all logs found in the "
                                               "provided league.", type=int)
    parser.add_argument("--export_dir", help="The directory to export parsed "
                                             "logs to.", type=str)

    main(parser.parse_args())
