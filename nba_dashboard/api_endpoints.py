"""
Contains functions that map to api_request routes.

- player/{player_id}/profile
- player/{player_id}/logs
- player/{player_id}/averages
- game_date_games/{game_date}
- game/{game_id}
"""

from flask import request, url_for
import json
from . import app
from . import db_utils
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
                + 1.5 * DD2
                + 3 * TD3, 2) AS DK_FP,
                MIN,
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
                            FROM GENERAL_TRADITIONAL_PLAYER_STATS
                            WHERE PLAYER_ID = (?)
                                AND SEASON = (?);""", (player_id, CURRENT_SEASON))
    resp = {}
    resp['averages'] = db_query.rows[0]
    resp['statNames'] = db_query.column_names
    return json.dumps(resp)


@app.route('/game_date_games/<string:game_date>')
def game_date_games_endpoint(game_date):
    """
    Returns:
        - a list of GAME json
    """
    games = db_utils.execute_sql("""
        SELECT DISTINCT GAME_ID, TEAM_ABBREVIATION
            FROM GAMES
            WHERE GAME_DATE = (?)
                AND SEASON = (?);""", (game_date, CURRENT_SEASON)).rows
    
    games_to_team = defaultdict(list)
    for game_id, team_abbreviation in games:
        games_to_team[game_id].append(team_abbreviation)
    
    resp = {}
    resp['gameIds'] = games_to_team
    return json.dumps(resp)


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
        raise ValueError('GAME_INFO_TRADITIONAL does not have column TEAM_ABBREVIATION')
    players_by_team_abbrev = defaultdict(list)
    for row in db_query.rows:
        team_abbrev = row[team_abbrev_index]
        players_by_team_abbrev[team_abbrev].append(row)

    if len(players_by_team_abbrev.keys()) != 2:
        raise ValueError('Invalid data in the database. Did not find two teams.')
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
        raise ValueError('{} did not play in {}.'.format(team_abbreviation, game_id))

    resp = {}
    resp['players'] = db_query.rows
    resp['statNames'] = db_query.column_names
    return json.dumps(resp)
