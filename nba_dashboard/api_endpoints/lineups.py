"""
Contains functions that map to api_request routes.

- /lineups
"""

from flask import request
import json
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from .. import app
from .. import db_utils
from .utils import match_name, map_team_abbrevs, get_player_ids, get_team_abbrev_team_id_map


ROTOWIRE_URL = 'https://www.rotowire.com/basketball/nba_lineups.htm'
NBA_LINEUP_URL = 'http://stats.nba.com/stats/teamplayerdashboard?DateFrom=&DateTo=&GameSegment=&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&PlusMinus=N&Rank=N&Season={season}&SeasonSegment=&SeasonType=Regular+Season&TeamId={team_id}&VsConference=&VsDivision='
RESULT_SET_INDEX = 1
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
POSITIONS_ORDER = ['PG', 'SG', 'PF', 'SF', 'C']


def get_starters_injured_by_team_abbrev():
    """
    Returns two dictionaries.
    The first maps team abbreviations to a list of starters (in position order).
    The second maps team abbreviations to a set of injured players.
    This data is scraped from rotowire.
    """
    soup = BeautifulSoup(requests.get(ROTOWIRE_URL).content, 'html.parser')
    game_divs = soup.find_all('div', class_='offset1 span15')

    starters_by_abbreviation = {}
    injured_by_abbreviation = {}
    for game_div in game_divs:
        game_header = game_div.find_all(
            'div', class_='span15 dlineups-topbox')[0]
        team_name_1 = game_header.find_all(
            'div', class_='span5 dlineups-topboxleft')[0].text.strip()
        team_name_2 = game_header.find_all(
            'div', class_='span5 dlineups-topboxright')[0].text.strip()

        players_div = game_div.find_all(
            'div', class_='span15 dlineups-mainbox')[0]

        # find starters
        team_lineup_divs = players_div.find_all('div', recursive=False)[1].find_all('div', class_='dlineups-half')
        for team_name, lineup_div in zip((team_name_1, team_name_2), team_lineup_divs):
            starter_names = [match_name(player_a['title'].strip())
                             for player_a in lineup_div.find_all('a')]
            starters_by_abbreviation[team_name] = starter_names

        # find injured
        team_lineup_divs = players_div.find_all('div', recursive=False)[2].find_all('div', class_='dlineups-half equalheight')
        for team_name, lineup_div in zip((team_name_1, team_name_2), team_lineup_divs):
            injured_names = [match_name(player_a.text.strip())
                             for player_a in lineup_div.find_all('a')]
            injured_by_abbreviation[team_name] = set(injured_names)

    return starters_by_abbreviation, injured_by_abbreviation


def get_nba_lineup(team_id):
    """
    Given a team_id, scrapes from the official NBA website the
    team's roster corresponding to the team_id.
    """
    api_request = NBA_LINEUP_URL.format(
        **{'team_id': team_id, 'season': app.config['CURRENT_SEASON']})
    response = requests.get(url=api_request,
                            headers={'User-agent': USER_AGENT},
                            stream=True,
                            allow_redirects=False).json()['resultSets'][RESULT_SET_INDEX]
    headers = response['headers']
    rows = response['rowSet']
    chosen_columns = ('PLAYER_ID', 'PLAYER_NAME', 'NBA_FANTASY_PTS')
    chosen_indicies = tuple(headers.index(col) for col in chosen_columns)

    lineup = [{col: row[index] for col, index in zip(chosen_columns, chosen_indicies)} for row in rows]
    return sorted(lineup, key=lambda d: d['NBA_FANTASY_PTS'])


def get_game_day_lineup(team_abbrev, team_id, starter_names, injured_names):
    """
    Returns a lineup for a given team (proper json response).
    """
    nba_lineup = get_nba_lineup(team_id)

    game_day_lineup = []
    for player in nba_lineup:
        player_name = player['PLAYER_NAME']
        player_id = player['PLAYER_ID']
        starter_index = starter_names.index(player_name) if player_name in starter_names else -1
        position = POSITIONS_ORDER[starter_index] if starter_index != -1 else ''
        is_injured = player_name in injured_names
        game_day_lineup.append({
            'name': player_name,
            'playerId': player_id,
            'team': team_abbrev,
            'position': position,
            'isInjured': is_injured
        })
    
    return game_day_lineup


@app.route('/lineups', methods=['GET'])
def lineups_endpoint():
    """
    Returns all lineups for today in json format
    specified in the json schema.
    """
    team_abbrev_to_team_id_map = get_team_abbrev_team_id_map()
    starters_by_abbrev, injured_by_abbrev = get_starters_injured_by_team_abbrev()

    lineups = {}
    for team_abbrev in starters_by_abbrev:
        team_id = team_abbrev_to_team_id_map[team_abbrev]
        lineup = get_game_day_lineup(
            team_abbrev, team_id, starters_by_abbrev[team_abbrev], injured_by_abbrev[team_abbrev])
        lineups[team_abbrev] = lineup
    return json.dumps(lineups)
