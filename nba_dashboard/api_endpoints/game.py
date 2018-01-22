"""
Contains functions that map to api_request routes.

- game/{game_id}
"""

from flask import request, url_for
import json
from .. import app
from .. import db_utils
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
                OREB,
                DREB,
                AST,
                STL,
                BLK,
                NBA_TO,
                PLUS_MINUS,
                PF,
                FGM,
                FGA,
                FG_PCT,
                FG3M,
                FG3A,
                FG3_PCT,
                FTM,
                FTA,
                FT_PCT,
                COMMENT,
                PLAYER_ID
            FROM GAME_INFO_TRADITIONAL
            WHERE GAME_ID = (?)
                AND SEASON = (?)
            ORDER BY DK_FP DESC;""", (game_id, CURRENT_SEASON))

    stat_names = db_query.column_names
    try:
        team_abbrev_index = stat_names.index('TEAM_ABBREVIATION')
    except:
        raise ValueError(
            'GAME_INFO_TRADITIONAL does not have column TEAM_ABBREVIATION')
    players_by_team_abbrev = defaultdict(list)
    for row in db_query.rows:
        team_abbrev = row[team_abbrev_index]
        players_by_team_abbrev[team_abbrev].append(row)

    if len(players_by_team_abbrev.keys()) != 2:
        raise ValueError(
            'Invalid data in the database. Did not find two teams.')
    resp = {}
    resp['playersByTeam'] = dict(players_by_team_abbrev)
    resp['statNames'] = db_query.column_names
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
                PF,
                FGM,
                FGA,
                FG_PCT,
                FG3M,
                FG3A,
                FG3_PCT,
                OREB,
                DREB,
                FTM,
                FTA,
                FT_PCT,
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
    resp['players'] = db_query.rows
    resp['statNames'] = db_query.column_names
    return json.dumps(resp)
