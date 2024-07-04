"""Hodls all regexes for parsing the game logs."""

# Clock regex's.
CLOCK_REGEX = r'\(.*\)'
TIME_REGEX = r'\d\d:\d\d'

# Down Distance regex grabs something like '1-10' or '4-2'
DOWN_DISTANCE_REGEX = r'\d-\d{1,2}'

# Field Position regex gets whose yard line the ball is on.
FIELD_POSITION_REGEX = r'[A-Z]{3}\d\d'

# Fumble recovery regex gets team who recovered football.
FUMBLE_RECOVERY_REGEX = r'(?<=recovered by )[A-Z]{3}'

# Kickoff regex determines which team is kicking.
KICKOFF_REGEX = r'(?<=from the )[A-Z]{3}'

# Coin toss regex tells which team will receive.
COIN_TOSS_REGEX = r'(.*)(?= won the toss)'

# Regexes for passing play outcomes. Try to capture the yardage
PASS_COMPLETED_REGEX = r'pass completed'
SIMPLE_INCOMPLETION_REGEX = r'pass (fell|(was thrown)) incomplete'
DROPPED_REGEX = r'pass was dropped'
PASS_BLOCKED_REGEX = r'pass was blocked at the line'
PASS_BLOCKED_PLAYER_REGEX = r'(?<=\. )(.*)(?= blocked the pass\.)'
INTERCEPTION_REGEX = r'intercepted'
SACKED_REGEX = r'sacked by'
HURRIED_REGEX = r'(hurried |hurry |was thrown quickly )'
QB_REGEX = r"\((?:\dQ|OT): \d{2}:\d{2}\)(?: Play-Action\.)? ([A-Za-z.'-]+(?: [A-Za-z.'-]+)*) pass"

# Only applies to sacks
SACK_YARDS_LOST_REGEX = r'(?<=a loss of )\d{1,2}'
SACK_PLAYER_REGEX = r'(?<=sacked by )(.*)(?= for a loss of )'

# Regexes for yardage
YARDAGE_REGEX = r'(?<=for )(|-)\d{1,2}'
YAC_REGEX = r'(|-)\d{1,2}(?:(?= yards after the catch)|(?= yard after the ' \
            r'catch))'

# Regexes for types of plays.
PLAYACTION_REGEX = r'Play-Action'
FINESSE_RUN_REGEX = r' counterplay | trap |draw '
RUN_REGEX = r' ran '
REVERSE_REGEX = r' reverse '
KNEEL_REGEX = r'dropped to one knee'

# Regexes for penalties
PENALTY_TYPE_REGEX = r'(?<=was called for )([^,.]+)'
PENALIZED_TEAM_REGEX = r'(?<= of )(.*)(?= was called for)'
