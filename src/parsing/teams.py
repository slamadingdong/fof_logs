"""Stores the mapping from cities to their teams' three letter abbreviations.
"""

ABBREV_TO_CITY = {
    'CHI': 'Chicago',
    'PHI': 'Philadelphia',
    'DET': 'Detroit',
    'PIT': 'Pittsburgh',
    'NED': 'New England',
    'MIA': 'Miami',
    'ARI': 'Arizona',
    'ATL': 'Atlanta',
    'BAL': 'Baltimore',
    'BUF': 'Buffalo',
    'CAR': 'Carolina',
    'CIN': 'Cincinnati',
    'CLE': 'Cleveland',
    'DEN': 'Denver',
    'DAL': 'Dallas',
    'GBY': 'Green Bay',
    'HOU': 'Houston',
    'IND': 'Indianapolis',
    'JAX': 'Jacksonville',
    'KCY': 'Kansas City',
    'LVS': 'Las Vegas',
    'LAS': 'Las Vegas',
    'LAR': 'Los Angeles',
    'MIN': 'Minnesota',
    'NOS': 'New Orleans',
    'NYK': 'New York',
    'NJY': 'New Jersey',
    'OAK': 'Oakland',
    'SDO': 'San Diego',
    'SFO': 'San Francisco',
    'SEA': 'Seattle',
    'TBY': 'Tampa Bay',
    'TEN': 'Tennessee',
    'WAS': 'Washington',
    'COL': 'Columbus (OH)'
    }

CITY_TO_ABBREV = {val: key for key, val in ABBREV_TO_CITY.items()}
