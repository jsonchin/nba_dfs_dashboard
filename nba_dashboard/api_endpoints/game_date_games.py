"""
Contains functions that map to api_request routes.

- game_date_games/{game_date}
"""

from flask import request, url_for
import json
from .. import app
from .. import db_utils
from collections import defaultdict

CURRENT_SEASON = app.config['CURRENT_SEASON']


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
