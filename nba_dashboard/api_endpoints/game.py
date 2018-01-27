"""
Contains functions that map to api_request routes.

- /game/{game_id}
- /game/{game_id}/{team_abbreviation}
"""

from flask import request, url_for
import json
from .. import app
from .. import db_utils
from .utils import map_rows_to_cols
from collections import defaultdict


CURRENT_SEASON = app.config['CURRENT_SEASON']


@app.route('/game/<string:game_id>')
def game_endpoint(game_id):
    """
    Returns:
        - the two teams
        - box score stats for each of the players
        - injury data
    """
    db_query = db_utils.execute_sql("""
         SELECT
                PLAYER_NAME,
                TEAM_ABBREVIATION,
                START_POSITION,
                ROUND(PTS
                + 0.5 * FG3M
                + 1.25 * REB
                + 1.5 * AST
                + 2 * BLK
                + 2 * STL
                + -0.5 * NBA_TO, 2) AS DK_FP,
                MIN,
                PTS,
                REB,
                AST,
                STL,
                BLK,
                NBA_TO,
                PLUS_MINUS,
                FGM,
                FG_PCT,
                FG3M,
                FG3_PCT,
                OREB,
                DREB,
                COMMENT,
                PLAYER_ID
            FROM GAME_INFO_TRADITIONAL
            WHERE GAME_ID = (?)
                AND SEASON = (?)
            ORDER BY DK_FP DESC;""", (game_id, CURRENT_SEASON))

    mapped_rows = map_rows_to_cols(db_query.rows, db_query.column_names)

    players_by_team_abbrev = defaultdict(list)
    for player in mapped_rows:
        team_abbrev = player['TEAM_ABBREVIATION']
        players_by_team_abbrev[team_abbrev].append(player)

    if len(players_by_team_abbrev.keys()) != 2:
        raise ValueError(
            'Invalid data in the database. Did not find two teams.')

    resp = {}
    resp['playersByTeam'] = dict(players_by_team_abbrev)
    return json.dumps(resp)


@app.route('/game/<string:game_id>/<string:team_abbreviation>')
def game_team_specific_endpoint(game_id, team_abbreviation):
    """
    Returns:
        - the two teams
        - box score stats for each of the players
        - injury data
    """
    db_query = db_utils.execute_sql("""
        SELECT
                PLAYER_NAME,
                TEAM_ABBREVIATION,
                START_POSITION,
                ROUND(PTS
                + 0.5 * FG3M
                + 1.25 * REB
                + 1.5 * AST
                + 2 * BLK
                + 2 * STL
                + -0.5 * NBA_TO, 2) AS DK_FP,
                MIN,
                PTS,
                REB,
                AST,
                STL,
                BLK,
                NBA_TO,
                PLUS_MINUS,
                FGM,
                FG_PCT,
                FG3M,
                FG3_PCT,
                OREB,
                DREB,
                COMMENT,
                PLAYER_ID
            FROM GAME_INFO_TRADITIONAL
            WHERE GAME_ID = (?)
                AND TEAM_ABBREVIATION = (?)
                AND SEASON = (?)
            ORDER BY DK_FP DESC;""", (game_id, team_abbreviation, CURRENT_SEASON))

    if len(db_query.rows) == 0:
        raise ValueError('{} did not play in {}.'.format(
            team_abbreviation, game_id))

    resp = {}
    resp['players'] = map_rows_to_cols(db_query.rows, db_query.column_names)
    return json.dumps(resp)
