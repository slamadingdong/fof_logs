# Parse Front Office Football 8 Logs

This repo has a script that will parse FOF8 game logs into tabular data 
containing all sorts of play-by-play information.

## Quickstart
This assumes you have a python 3.10 environment with the requirements 
installed. It also assumes you have exported the game logs to html from 
within the FOF8 game.

First cd to the script directory:
`cd ~/fof_logs/src`

Then run the script:

`python -m parse --logs_dir "C:\Front Office Football Eight\leaguehtml" --league_num "LG000021" --export_dir "D:\SavedLogs"
`

* `--logs_dir` is the directory with the FOF 8 logs, usually it looks like the 
above example.
* `--league_num` is the 8 character id of the league whose logs youd like to 
parse.
* `--export_dir` is a directory youd like to save the parsed data to. It 
  will create this dir for you if it doesn't already exist.

## Output Data

The parsed logs are stored in Feather format which is a very memory/space 
efficient format for tabular data.

Each row represents one play, and has columns representing:
* The player names for each position on the field.
* The play call information for offense and defense, e.g. the primary and 
  secondary receivers and routes, how many players blitzed, the coverage etc.
* The game context: Quarter, time remaining, field position, down, distance etc.
* The play outcome: Yards gained, whether it was a run or pass, sack, hurry, 
  pressure etc.
