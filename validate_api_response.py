import jsonschema
import json
import os
import pandas as pd

import unittest

from nba_dashboard import app
from nba_dashboard import dashboard


EXAMPLE_PLAYER_IDS = [
    '1717',
    '1626257'
]
EXAMPLE_GAME_IDS = {
    '0021700667': ('SAS', 'TOR'),
    '0021700668': ('MIA', 'BKN'),
    '0021700653': ('WAS', 'CHA')
}
EXAMPLE_GAME_DATES = [
    '2018-01-10',
    '2017-10-30'
]
EXAMPLE_DRAFTKINGS_CSV_STR = b',Position,Name,Salary,GameInfo,AvgPointsPerGame,teamAbbrev\n0,PF/C,DeMarcus Cousins,10900,CHI@NO 01/22/2018 08:00PM ET,54.817,NO\n1,PF/C,Anthony Davis,10800,CHI@NO 01/22/2018 08:00PM ET,49.731,NO\n'

JSON_SCHEMA_ROOT = 'nba_dashboard/json_schemas'
JSON_SCHEMA_GET_FILE_NAME = 'get.resp.schema.json'
JSON_SCHEMA_POST_FILE_NAME = 'post.resp.schema.json'


def validate_api_resp(actual_json_resp, json_schema_path: str, json_schema_file_name):
    """
    Validates a json instance against a json schema file.
    """
    with open(os.path.join(JSON_SCHEMA_ROOT, json_schema_path, json_schema_file_name), 'r') as f:
        json_schema = json.loads(f.read())
        actual_json = json.loads(str(actual_json_resp.data, 'utf-8'))
        jsonschema.validate(actual_json, json_schema)

def validate_api_get_resp(actual_json_resp, json_schema_path: str):
    validate_api_resp(actual_json_resp, json_schema_path,
                      JSON_SCHEMA_GET_FILE_NAME)

def validate_api_post_resp(actual_json_resp, json_schema_path: str):
    validate_api_resp(actual_json_resp, json_schema_path,
                      JSON_SCHEMA_POST_FILE_NAME)


def make_get_request(client, endpoint):
    """
    Makes a get request to the given endpoint from the client.
    """
    return client.get(endpoint)


def make_post_request(client, endpoint, data):
    """
    Makes a post request to the given endpoint with the
    provided data from the client.
    """
    return client.post(endpoint, data=data)


class ValidateAPIResponses(unittest.TestCase):

    def setUp(self):
        app.config['DB_PATH'] = '../nba_stats_scraper_db_storage/nba_ss_db/db/databases'
        self.app = app.test_client()

    def test_validate_player_profiles(self):

        for player_id in EXAMPLE_PLAYER_IDS:
            route = 'player/{player_id}/profile'
            endpoint = '/' + route.format(**{'player_id': player_id})
            api_json_resp = make_get_request(self.app, endpoint)
            validate_api_get_resp(api_json_resp, route)

    def test_validate_player_logs(self):
        for player_id in EXAMPLE_PLAYER_IDS:
            route = 'player/{player_id}/logs'
            endpoint = '/' + route.format(**{'player_id': player_id})
            api_json_resp = make_get_request(self.app, endpoint)
            validate_api_get_resp(api_json_resp, route)

    def test_validate_player_averages(self):
        for player_id in EXAMPLE_PLAYER_IDS:
            route = 'player/{player_id}/averages'
            endpoint = '/' + route.format(**{'player_id': player_id})
            api_json_resp = make_get_request(self.app, endpoint)
            validate_api_get_resp(api_json_resp, route)

    def test_validate_game(self):
        for game_id in EXAMPLE_GAME_IDS:
            route = 'game/{game_id}'
            endpoint = '/' + route.format(**{'game_id': game_id})
            api_json_resp = make_get_request(self.app, endpoint)
            validate_api_get_resp(api_json_resp, route)

    def test_validate_game_team_abbreviation(self):
        for game_id in EXAMPLE_GAME_IDS:
            team_abbreviations = EXAMPLE_GAME_IDS[game_id]
            for team_abbreviation in team_abbreviations:
                route = 'game/{game_id}/{team_abbreviation}'
                endpoint = '/' + route.format(**{
                    'game_id': game_id,
                    'team_abbreviation': team_abbreviation
                    })
                api_json_resp = make_get_request(self.app, endpoint)
                validate_api_get_resp(api_json_resp, route)

    def test_validate_game_date_games(self):
        for game_date in EXAMPLE_GAME_DATES:
            route = 'game_date_games/{game_date}'
            endpoint = '/' + route.format(**{'game_date': game_date})
            api_json_resp = make_get_request(self.app, endpoint)
            validate_api_get_resp(api_json_resp, route)
    
    def test_validate_file_upload_draftkings(self):
        route = 'file_upload/draftkings'
        endpoint = '/' + route
        api_json_resp = make_post_request(
                self.app,
                endpoint, 
                data={
                    'file': (pd.compat.BytesIO(EXAMPLE_DRAFTKINGS_CSV_STR), 'draftkings_csv.csv'),
                }
            )
        validate_api_post_resp(api_json_resp, route)
        

if __name__ == '__main__':
    unittest.main()
