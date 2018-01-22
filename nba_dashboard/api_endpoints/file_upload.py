"""
Contains functions that map to api_request routes.

- /file_upload/draftkings
"""

from flask import request
import json
import pandas as pd
import numpy as np
from .. import app
from .. import db_utils


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


def get_team_to_matchups(matchups):
    team_to_matchups = {}
    for matchup in matchups:
        t1, t2 = map(map_team_abbrevs, matchup.split('@'))
        team_to_matchups[t1] = '{} @ {}'.format(t1, t2)
        team_to_matchups[t2] = '{} vs. {}'.format(t2, t1)
    return team_to_matchups


@app.route('/file_upload/draftkings', methods=['POST'])
def file_upload_draftkings():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            raise ValueError()
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            raise ValueError()

        file_str = file.read()

        # read in the csv
        dk_df = pd.read_csv(pd.compat.BytesIO(file_str))
        dk_df['matched_name'] = dk_df['Name'].apply(match_name)
        dk_df['player_id'] = get_player_ids(dk_df['matched_name'].values)

        # map the dk team abbrev to NBA team abbrev
        dk_df['team'] = list(map(map_team_abbrevs, dk_df['teamAbbrev']))
        dk_df['opponent_team'] = dk_df['team'].apply(lambda s: s.split(' ')[-1])

        # map the dk matchup to NBA team matchup with NBA team abbrevs
        dk_df['DK_Matchup'] = dk_df['GameInfo'].apply(lambda s: s.split(' ')[0])
        matchups = set(dk_df['DK_Matchup'])
        team_to_matchups = get_team_to_matchups(matchups)
        dk_df['matchup'] = list(map(lambda team: team_to_matchups[team], dk_df['team']))

        # separate the players by matched and unmatched
        matched_players = []
        unmatched_player_names = []

        for index, row in dk_df.iterrows():
            if np.isnan(row['player_id']):
                unmatched_player_names.append(row['Name'])
            else:
                player = {
                    'matchedName': row['matched_name'],
                    'matchedPlayerId': row['player_id'],
                    'salary': row['Salary'],
                    'formattedNBAMatchup': row['matchup'],
                    'team': row['team'],
                    'opponentTeam': row['opponent_team'],
                    'position': row['Position']
                }
                matched_players.append(player)
        resp = {}
        resp['matchedPlayers'] = matched_players
        resp['unmatchedPlayerNames'] = unmatched_player_names
        return json.dumps(resp)

    raise ValueError('Not a POST request')
