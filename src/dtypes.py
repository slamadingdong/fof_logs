"""Responsible for managing dtypes of columns."""
import pandas as pd

from column_names import *

CATEGORICAL_COLS = [
    DEF_FORMATION,
    DEF_PERSONNEL,
    COVERAGE,
    DOUBLE_TARGET,
    OFF_FORMATION,
    OFF_PERSONNEL,
    QB_ALIGN,
    PRIMARY_ROUTE,
    PRIMARY_RECEIVER,
    SECONDARY_ROUTE,
    SECONDARY_RECEIVER,
    RUN_DIRECTION,
    BALL_CARRIER,
    TARGET_ROUTE,
    TARGET_PRIORITY,
    PLAY_TYPE,
    LEAGUE_ID,
    YEAR,
]

INT_8_COLS = [
    PROTECT,
    DOWN,
    DISTANCE,
    YARDS,
    YAC,
    QUARTER,
    YARDLINE,
    BLITZ, ]

BOOL_COLS = [
    HOME_POSSESSION,
    COMPLETE,
    SACKED,
    HURRIED,
    BLOCKED,
    DROPPED,
    INT,
    THROW_TO_DOUBLE,
    SCRAMBLE,
    SPY,
    BUZZ,
    PLAY_ACTION,
    OPP_HALF,
    FINESSE,
    REVERSE,
]


def cast_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Cast columns to efficient memory types."""
    for col in df.columns.tolist():
        if col in CATEGORICAL_COLS:
            df.loc[:, col] = df[col].astype('category')
        elif col in INT_8_COLS:
            df.loc[:, col] = df[col].astype('Int8')
        elif col in BOOL_COLS:
            df.loc[:, col] = df[col].astype('bool')
    return df
