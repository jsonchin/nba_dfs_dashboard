import numpy as np
from .. import db_utils
from .. import app

PLAYER_CORRECTION_MAP = {
    'C.J. McCollum': 'CJ McCollum',
    'Dennis Smith': 'Dennis Smith Jr.',
    'P.J. Dozier': 'PJ Dozier',
    'M. Miller': 'Malcolm Miller',
    'D. Hamilton': 'Daniel Hamilton',
    'A. McKinnie': 'Alfonzo McKinnie',
    'L. Brown': 'Lorenzo Brown',
    'C.J. Wilcox': 'CJ Wilcox',
    'J. Sampson': 'JaKarr Sampson',
    'D. Finney-Smith': 'Dorian Finney-Smith',
    'R. Vaughn': 'Rashad Vaughn',
    'M. Dellavedova': 'Matthew Dellavedova',
    'Nene Hilario': 'Nene',
    'Glenn Robinson': 'Glenn Robinson III',
    'C. Swanigan': 'Caleb Swanigan',
    'A. Brown': 'Anthony Brown',
    'P.J. Tucker': 'PJ Tucker',
    'Luc Richard Mbah a Moute': 'Luc Mbah a Moute',
    'Otto Porter': 'Otto Porter Jr.',
    'T.J. Warren': 'TJ Warren',
    'D. Dotson': 'Damyean Dotson',
    'Derrick Jones': 'Derrick Jones Jr.',
    'J.J. Redick': 'JJ Redick',
    'J.R. Smith': 'JR Smith',
    'C.J. Miles': 'CJ Miles',
    'A.J. Hammons': 'AJ Hammons',
    'J. McAdoo': 'James McAdoo',
    'T. Williams': 'Troy Williams',
    'Larry Nance': 'Larry Nance Jr.',
    'K. Caldwell-Pope': 'Kentavious Caldwell-Pope',
    'James Ennis': 'James Ennis III',
    'G. Antetokounmpo': 'Giannis Antetokounmpo',
    'Tim Hardaway': 'Tim Hardaway Jr.',
    'M. Kidd-Gilchrist': 'Michael Kidd-Gilchrist'
}

TEAM_ABBREV_MAPPING = {
    'SA': 'SAS',
    'NO': 'NOP',
    'NY': 'NYK',
    'GS': 'GSW',
    'PHO': 'PHX'
}


def match_name(name):
    return PLAYER_CORRECTION_MAP[name] if name in PLAYER_CORRECTION_MAP else name


def get_player_ids(names):
    player_ids = []
    for name in names:
        result = db_utils.execute_sql("""
            SELECT PLAYER_ID
                FROM PLAYER_IDS
                WHERE PLAYER_NAME = (?)
                    AND SEASON = "2017-18"
            UNION
            SELECT PLAYER_ID
                FROM PLAYER_IDS
                WHERE PLAYER_NAME = (?)
                AND SEASON = "2016-17"
                            LIMIT 1;""",
                                      (name, name)).rows
        if len(result) > 0:
            player_ids.append(result[0][0])
        else:
            player_ids.append(np.nan)
    return player_ids


def map_team_abbrevs(team_abbrev):
    return TEAM_ABBREV_MAPPING[team_abbrev] if team_abbrev in TEAM_ABBREV_MAPPING else team_abbrev


def get_team_abbrev_team_id_map():
    rows = db_utils.execute_sql("""
        SELECT TEAM_ID, TEAM_ABBREVIATION
            FROM games
            WHERE SEASON = (?)
            GROUP BY TEAM_ID;""", (app.config['CURRENT_SEASON'], )).rows
    team_abbrev_to_team_id_map = {}
    for row in rows:
        team_abbrev_to_team_id_map[row[1]] = row[0]
    return team_abbrev_to_team_id_map


def map_rows_to_cols(rows, cols):
    """
    Returns a list of dictionaries.
    Each dictionary is the column name to its corresponding row value.
    """
    mapped_rows = []
    for row in rows:
        mapped_rows.append({cols[i]: row[i] for i in range(len(cols))})
    return mapped_rows
