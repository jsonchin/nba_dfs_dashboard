"""
Contains functions that map to api_request routes.

- player/{player_id}/profile
- player/{player_id}/logs
- player/{player_id}/averages
"""

from flask import request, url_for
import json
from .. import app
from .. import db_utils
from collections import defaultdict

CURRENT_SEASON = app.config['CURRENT_SEASON']
PROFILE_TEMPLATE = 'https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/{team_id}/{current_season}/260x190/{player_id}.png'


@app.route('/player/<int:player_id>/profile')
def player_profile_endpoint(player_id):
    """
    Returns:
        - a relative url to the player's profile picture
        - name
        - team
        - position
    """
    position = db_utils.execute_sql("""
        SELECT MAX(PLAYER_POSITION)
            FROM PLAYER_POSITIONS
            WHERE PLAYER_ID = (?)
                AND SEASON = (?);""", (player_id, CURRENT_SEASON)).rows[0][0]

    name, team, team_id, player_id = db_utils.execute_sql("""
        SELECT PLAYER_NAME, TEAM_ABBREVIATION, TEAM_ID, PLAYER_ID
            FROM PLAYER_LOGS
            WHERE PLAYER_ID = (?)
                AND SEASON = (?)
            ORDER BY GAME_DATE DESC
            LIMIT 1;""", (player_id, CURRENT_SEASON)).rows[0]
    resp = {}
    resp['position'] = position
    resp['name'] = name
    resp['team'] = team
    resp['pictureUrl'] = PROFILE_TEMPLATE.format(**{
        'player_id': player_id,
        'team_id': team_id,
        'current_season': CURRENT_SEASON[:4]
    })
    return json.dumps(resp)


@app.route('/player/<int:player_id>/logs', methods=['GET'])
def player_logs_endpoint(player_id):
    """
    Returns:
        - a list of logs
    """
    db_query = db_utils.execute_sql("""
        SELECT
                GAME_ID,
                TEAM_ABBREVIATION,
                GAME_DATE,
                MATCHUP,
                ROUND(PTS
                + 0.5 * FG3M
                + 1.25 * REB
                + 1.5 * AST
                + 2 * BLK
                + 2 * STL
                + -0.5 * TOV
                + 1.5 * DD2
                + 3 * TD3, 2) AS DK_FP,
                WL,
                ROUND(MIN, 0) AS MIN,
                PTS,
                REB,
                AST,
                TOV,
                STL,
                BLK,
                DD2,
                TD3,
                FGM,
                FG_PCT,
                FG3M,
                FG3_PCT,
                PLUS_MINUS
            FROM PLAYER_LOGS
            WHERE PLAYER_ID = (?)
                AND SEASON = (?)
            ORDER BY GAME_DATE DESC;""", (player_id, CURRENT_SEASON))
    resp = {}
    resp['logs'] = db_query.rows
    resp['statNames'] = db_query.column_names
    return json.dumps(resp)


@app.route('/player/<int:player_id>/averages')
def player_averages_endpoint(player_id):
    """
    Returns:
        - the player's average stats
    """
    db_query = db_utils.execute_sql("""
        SELECT
                ROUND(PTS
                + 0.5 * FG3M
                + 1.25 * REB
                + 1.5 * AST
                + 2 * BLK
                + 2 * STL
                + -0.5 * TOV
                + COALESCE(1.5 * (CAST(DD2 AS FLOAT) / GP), 0)
                + COALESCE(3 * (CAST(TD3 AS FLOAT) / GP), 0), 2) AS DK_FP,
                MIN,
                PTS,
                REB,
                AST,
                TOV,
                STL,
                BLK,
                COALESCE((CAST(DD2 AS FLOAT) / GP), 0) AS DD2,
                COALESCE((CAST(TD3 AS FLOAT) / GP), 0) AS TD3,
                FGM,
                FG_PCT,
                FG3M,
                FG3_PCT,
                PLUS_MINUS
            FROM GENERAL_TRADITIONAL_PLAYER_STATS
            WHERE PLAYER_ID = (?)
                AND SEASON = (?)
            ORDER BY DATE_TO DESC
            LIMIT 1;""", (player_id, CURRENT_SEASON))
    resp = {}
    resp['averages'] = db_query.rows[0]
    resp['statNames'] = db_query.column_names
    return json.dumps(resp)
