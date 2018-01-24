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

NBA_LINEUPS_SNAPSHOT = {
    1610612747: [{'NBA_FANTASY_PTS': 33.9, 'PLAYER_ID': 1628366, 'PLAYER_NAME': 'Lonzo Ball'}, {'NBA_FANTASY_PTS': 28.9, 'PLAYER_ID': 1627742, 'PLAYER_NAME': 'Brandon Ingram'}, {'NBA_FANTASY_PTS': 27.6, 'PLAYER_ID': 1628398, 'PLAYER_NAME': 'Kyle Kuzma'}, {'NBA_FANTASY_PTS': 27.0, 'PLAYER_ID': 203484, 'PLAYER_NAME': 'Kentavious Caldwell-Pope'}, {'NBA_FANTASY_PTS': 26.3, 'PLAYER_ID': 203944, 'PLAYER_NAME': 'Julius Randle'}, {'NBA_FANTASY_PTS': 24.2, 'PLAYER_ID': 1626204, 'PLAYER_NAME': 'Larry Nance Jr.'}, {'NBA_FANTASY_PTS': 23.2, 'PLAYER_ID': 203903, 'PLAYER_NAME': 'Jordan Clarkson'}, {'NBA_FANTASY_PTS': 22.7, 'PLAYER_ID': 201572, 'PLAYER_NAME': 'Brook Lopez'}, {'NBA_FANTASY_PTS': 12.9, 'PLAYER_ID': 1628404, 'PLAYER_NAME': 'Josh Hart'}, {'NBA_FANTASY_PTS': 10.2, 'PLAYER_ID': 1627780, 'PLAYER_NAME': 'Gary Payton II'}, {'NBA_FANTASY_PTS': 9.4, 'PLAYER_ID': 203898, 'PLAYER_NAME': 'Tyler Ennis'}, {'NBA_FANTASY_PTS': 8.7, 'PLAYER_ID': 201147, 'PLAYER_NAME': 'Corey Brewer'}, {'NBA_FANTASY_PTS': 8.0, 'PLAYER_ID': 101106, 'PLAYER_NAME': 'Andrew Bogut'}, {'NBA_FANTASY_PTS': 7.1, 'PLAYER_ID': 1627936, 'PLAYER_NAME': 'Alex Caruso'}, {'NBA_FANTASY_PTS': 5.5, 'PLAYER_ID': 2736, 'PLAYER_NAME': 'Luol Deng'}, {'NBA_FANTASY_PTS': 1.7, 'PLAYER_ID': 203505, 'PLAYER_NAME': 'Vander Blue'}, {'NBA_FANTASY_PTS': 1.6, 'PLAYER_ID': 1627826, 'PLAYER_NAME': 'Ivica Zubac'}, {'NBA_FANTASY_PTS': 1.3, 'PLAYER_ID': 1628418, 'PLAYER_NAME': 'Thomas Bryant'}, {'NBA_FANTASY_PTS': 0.0, 'PLAYER_ID': 1628502, 'PLAYER_NAME': 'Nigel Hayes'}],
1610612752: [{'NBA_FANTASY_PTS': 40.4, 'PLAYER_ID': 204001, 'PLAYER_NAME': 'Kristaps Porzingis'}, {'NBA_FANTASY_PTS': 30.4, 'PLAYER_ID': 203501, 'PLAYER_NAME': 'Tim Hardaway Jr.'}, {'NBA_FANTASY_PTS': 29.1,'PLAYER_ID': 202683, 'PLAYER_NAME': 'Enes Kanter'}, {'NBA_FANTASY_PTS': 24.7, 'PLAYER_ID': 201584, 'PLAYER_NAME': 'Courtney Lee'}, {'NBA_FANTASY_PTS': 21.5, 'PLAYER_ID': 201563, 'PLAYER_NAME': 'Michael Beasley'}, {'NBA_FANTASY_PTS': 21.4, 'PLAYER_ID': 101127, 'PLAYER_NAME': 'Jarrett Jack'}, {'NBA_FANTASY_PTS': 19.9, 'PLAYER_ID': 203124, 'PLAYER_NAME': "Kyle O'Quinn"}, {'NBA_FANTASY_PTS': 15.3, 'PLAYER_ID': 1628373, 'PLAYER_NAME': 'Frank Ntilikina'}, {'NBA_FANTASY_PTS': 12.9, 'PLAYER_ID': 203926, 'PLAYER_NAME': 'Doug McDermott'}, {'NBA_FANTASY_PTS': 10.9, 'PLAYER_ID': 203504, 'PLAYER_NAME': 'Trey Burke'}, {'NBA_FANTASY_PTS': 9.8, 'PLAYER_ID': 1626195, 'PLAYER_NAME': 'Willy Hernangomez'}, {'NBA_FANTASY_PTS': 9.7, 'PLAYER_ID': 1627758, 'PLAYER_NAME': 'Ron Baker'}, {'NBA_FANTASY_PTS': 9.2, 'PLAYER_ID': 201196, 'PLAYER_NAME': 'Ramon Sessions'}, {'NBA_FANTASY_PTS': 9.0, 'PLAYER_ID': 202498, 'PLAYER_NAME': 'Lance Thomas'}, {'NBA_FANTASY_PTS': 6.8, 'PLAYER_ID': 201149, 'PLAYER_NAME': 'Joakim Noah'}, {'NBA_FANTASY_PTS': 5.4, 'PLAYER_ID': 1628422, 'PLAYER_NAME': 'Damyean Dotson'}, {'NBA_FANTASY_PTS': 0.0, 'PLAYER_ID': 1627851, 'PLAYER_NAME': 'Mindaugas Kuzminskas'}],
1610612753: [{'NBA_FANTASY_PTS': 38.0, 'PLAYER_ID': 202696, 'PLAYER_NAME': 'Nikola Vucevic'}, {'NBA_FANTASY_PTS': 34.2, 'PLAYER_ID': 203932, 'PLAYER_NAME': 'Aaron Gordon'}, {'NBA_FANTASY_PTS': 30.2, 'PLAYER_ID': 203901, 'PLAYER_NAME': 'Elfrid Payton'}, {'NBA_FANTASY_PTS': 28.2, 'PLAYER_ID': 203095, 'PLAYER_NAME': 'Evan Fournier'}, {'NBA_FANTASY_PTS': 22.5, 'PLAYER_ID': 203613, 'PLAYER_NAME': 'Jonathon Simmons'}, {'NBA_FANTASY_PTS': 19.1, 'PLAYER_ID': 203082, 'PLAYER_NAME': 'Terrence Ross'}, {'NBA_FANTASY_PTS': 17.1, 'PLAYER_ID': 202687, 'PLAYER_NAME': 'Bismack Biyombo'}, {'NBA_FANTASY_PTS': 15.9, 'PLAYER_ID': 201571, 'PLAYER_NAME': 'D.J. Augustin'}, {'NBA_FANTASY_PTS': 14.8, 'PLAYER_ID': 1628371, 'PLAYER_NAME': 'Jonathan Isaac'}, {'NBA_FANTASY_PTS': 13.5, 'PLAYER_ID': 1626209, 'PLAYER_NAME': 'Mario Hezonja'}, {'NBA_FANTASY_PTS': 12.9, 'PLAYER_ID': 202714, 'PLAYER_NAME': 'Shelvin Mack'}, {'NBA_FANTASY_PTS': 11.9, 'PLAYER_ID': 201578, 'PLAYER_NAME': 'Marreese Speights'}, {'NBA_FANTASY_PTS': 9.3, 'PLAYER_ID': 203920, 'PLAYER_NAME': 'Khem Birch'}, {'NBA_FANTASY_PTS': 8.3, 'PLAYER_ID': 1628411, 'PLAYER_NAME': 'Wes Iwundu'}, {'NBA_FANTASY_PTS': 7.2, 'PLAYER_ID': 203940, 'PLAYER_NAME': 'Adreian Payne'}, {'NBA_FANTASY_PTS': 5.5, 'PLAYER_ID': 201167, 'PLAYER_NAME': 'Arron Afflalo'}, {'NBA_FANTASY_PTS': 4.7, 'PLAYER_ID': 1628503, 'PLAYER_NAME': 'Jamel Artis'}],
1610612739: [{'NBA_FANTASY_PTS': 53.1, 'PLAYER_ID': 2544, 'PLAYER_NAME': 'LeBron James'}, {'NBA_FANTASY_PTS': 34.0, 'PLAYER_ID': 201567, 'PLAYER_NAME': 'Kevin Love'}, {'NBA_FANTASY_PTS': 24.2, 'PLAYER_ID': 2548, 'PLAYER_NAME': 'Dwyane Wade'}, {'NBA_FANTASY_PTS': 21.8, 'PLAYER_ID': 202738, 'PLAYER_NAME': 'Isaiah Thomas'}, {'NBA_FANTASY_PTS': 19.0, 'PLAYER_ID': 201145, 'PLAYER_NAME': 'Jeff Green'}, {'NBA_FANTASY_PTS': 16.9, 'PLAYER_ID': 201565, 'PLAYER_NAME': 'Derrick Rose'}, {'NBA_FANTASY_PTS': 16.6, 'PLAYER_ID': 203109, 'PLAYER_NAME': 'Jae Crowder'}, {'NBA_FANTASY_PTS': 16.2, 'PLAYER_ID': 2747, 'PLAYER_NAME': 'JR Smith'}, {'NBA_FANTASY_PTS': 14.8, 'PLAYER_ID': 2594, 'PLAYER_NAME': 'Kyle Korver'}, {'NBA_FANTASY_PTS': 14.4, 'PLAYER_ID': 202684, 'PLAYER_NAME': 'Tristan Thompson'}, {'NBA_FANTASY_PTS': 11.3, 'PLAYER_ID': 202697, 'PLAYER_NAME': 'Iman Shumpert'}, {'NBA_FANTASY_PTS': 10.0, 'PLAYER_ID': 101181, 'PLAYER_NAME': 'Jose Calderon'}, {'NBA_FANTASY_PTS': 9.0, 'PLAYER_ID':101112, 'PLAYER_NAME': 'Channing Frye'}, {'NBA_FANTASY_PTS': 5.3, 'PLAYER_ID': 1626224, 'PLAYER_NAME': 'Cedi Osman'}, {'NBA_FANTASY_PTS': 3.5, 'PLAYER_ID': 1627790, 'PLAYER_NAME': 'Ante Zizic'},{'NBA_FANTASY_PTS': 1.1, 'PLAYER_ID': 204066, 'PLAYER_NAME': 'John Holland'}, {'NBA_FANTASY_PTS': 0.0, 'PLAYER_ID': 1628506, 'PLAYER_NAME': 'London Perrantes'}],
1610612751: [{'NBA_FANTASY_PTS': 28.9, 'PLAYER_ID': 1626178, 'PLAYER_NAME': 'Rondae Hollis-Jefferson'}, {'NBA_FANTASY_PTS': 28.8, 'PLAYER_ID': 1626156, 'PLAYER_NAME': "D'Angelo Russell"}, {'NBA_FANTASY_PTS': 28.8, 'PLAYER_ID': 203915, 'PLAYER_NAME': 'Spencer Dinwiddie'}, {'NBA_FANTASY_PTS': 26.2, 'PLAYER_ID': 201960, 'PLAYER_NAME': 'DeMarre Carroll'}, {'NBA_FANTASY_PTS': 25.0, 'PLAYER_ID': 1627747,'PLAYER_NAME': 'Caris LeVert'}, {'NBA_FANTASY_PTS': 21.7, 'PLAYER_ID': 202344, 'PLAYER_NAME': 'Trevor Booker'}, {'NBA_FANTASY_PTS': 21.5, 'PLAYER_ID': 203459, 'PLAYER_NAME': 'Allen Crabbe'}, {'NBA_FANTASY_PTS': 21.0, 'PLAYER_ID': 202391, 'PLAYER_NAME': 'Jeremy Lin'}, {'NBA_FANTASY_PTS': 17.2, 'PLAYER_ID': 203925, 'PLAYER_NAME': 'Joe Harris'}, {'NBA_FANTASY_PTS': 15.5, 'PLAYER_ID': 203092, 'PLAYER_NAME': 'Tyler Zeller'}, {'NBA_FANTASY_PTS': 15.2, 'PLAYER_ID': 1628386, 'PLAYER_NAME': 'Jarrett Allen'}, {'NBA_FANTASY_PTS': 13.2, 'PLAYER_ID': 1627785, 'PLAYER_NAME': 'Isaiah Whitehead'}, {'NBA_FANTASY_PTS': 12.6, 'PLAYER_ID': 203112, 'PLAYER_NAME': 'Quincy Acy'}, {'NBA_FANTASY_PTS': 9.4, 'PLAYER_ID': 203917, 'PLAYER_NAME': 'Nik Stauskas'}, {'NBA_FANTASY_PTS': 9.4, 'PLAYER_ID': 202389, 'PLAYER_NAME': 'Timofey Mozgov'}, {'NBA_FANTASY_PTS': 8.9, 'PLAYER_ID': 1626143, 'PLAYER_NAME': 'Jahlil Okafor'}, {'NBA_FANTASY_PTS': 8.5, 'PLAYER_ID': 203930, 'PLAYER_NAME': 'Sean Kilpatrick'}, {'NBA_FANTASY_PTS': 7.0, 'PLAYER_ID': 1628495, 'PLAYER_NAME': 'Milton Doyle'}, {'NBA_FANTASY_PTS': 4.6, 'PLAYER_ID': 1628451, 'PLAYER_NAME': 'Jacob Wiley'}],
1610612758: [{'NBA_FANTASY_PTS': 28.2, 'PLAYER_ID': 1626161, 'PLAYER_NAME': 'Willie Cauley-Stein'}, {'NBA_FANTASY_PTS': 26.4, 'PLAYER_ID': 2216, 'PLAYER_NAME': 'Zach Randolph'}, {'NBA_FANTASY_PTS': 21.5, 'PLAYER_ID': 1627741, 'PLAYER_NAME': 'Buddy Hield'}, {'NBA_FANTASY_PTS': 21.1, 'PLAYER_ID': 1628368, 'PLAYER_NAME': "De'Aaron Fox"}, {'NBA_FANTASY_PTS': 20.9, 'PLAYER_ID': 203992, 'PLAYER_NAME': 'Bogdan Bogdanovic'}, {'NBA_FANTASY_PTS': 20.3, 'PLAYER_ID': 201588, 'PLAYER_NAME': 'George Hill'}, {'NBA_FANTASY_PTS': 17.2, 'PLAYER_ID': 202066, 'PLAYER_NAME': 'Garrett Temple'}, {'NBA_FANTASY_PTS': 17.1, 'PLAYER_ID': 201585, 'PLAYER_NAME': 'Kosta Koufos'}, {'NBA_FANTASY_PTS': 17.1, 'PLAYER_ID': 1627746, 'PLAYER_NAME': 'Skal Labissiere'}, {'NBA_FANTASY_PTS': 15.2, 'PLAYER_ID': 1628412, 'PLAYER_NAME': 'Frank Mason'}, {'NBA_FANTASY_PTS': 14.2, 'PLAYER_ID': 203960, 'PLAYER_NAME': 'JaKarr Sampson'}, {'NBA_FANTASY_PTS': 12.7, 'PLAYER_ID': 1713, 'PLAYER_NAME': 'Vince Carter'}, {'NBA_FANTASY_PTS': 9.1, 'PLAYER_ID': 1628382, 'PLAYER_NAME': 'Justin Jackson'}, {'NBA_FANTASY_PTS': 7.0, 'PLAYER_ID': 1627781, 'PLAYER_NAME': 'Malachi Richardson'}, {'NBA_FANTASY_PTS': 6.7, 'PLAYER_ID': 1627834, 'PLAYER_NAME': 'Georgios Papagiannis'}, {'NBA_FANTASY_PTS': 4.7, 'PLAYER_ID': 204022, 'PLAYER_NAME': 'Jack Cooley'}],
1610612744: [{'NBA_FANTASY_PTS': 48.0, 'PLAYER_ID': 201142, 'PLAYER_NAME': 'Kevin Durant'}, {'NBA_FANTASY_PTS': 45.7, 'PLAYER_ID': 201939, 'PLAYER_NAME': 'Stephen Curry'}, {'NBA_FANTASY_PTS': 37.2, 'PLAYER_ID': 203110, 'PLAYER_NAME': 'Draymond Green'}, {'NBA_FANTASY_PTS': 31.4, 'PLAYER_ID': 202691, 'PLAYER_NAME': 'Klay Thompson'}, {'NBA_FANTASY_PTS': 18.6, 'PLAYER_ID': 2738, 'PLAYER_NAME': 'Andre Iguodala'}, {'NBA_FANTASY_PTS': 17.9, 'PLAYER_ID': 2561, 'PLAYER_NAME': 'David West'}, {'NBA_FANTASY_PTS': 16.7, 'PLAYER_ID': 1628395, 'PLAYER_NAME': 'Jordan Bell'}, {'NBA_FANTASY_PTS': 15.8, 'PLAYER_ID': 201956, 'PLAYER_NAME': 'Omri Casspi'}, {'NBA_FANTASY_PTS': 15.0, 'PLAYER_ID': 2585, 'PLAYER_NAME': 'Zaza Pachulia'}, {'NBA_FANTASY_PTS': 11.8, 'PLAYER_ID': 2733, 'PLAYER_NAME': 'Shaun Livingston'}, {'NBA_FANTASY_PTS': 10.2, 'PLAYER_ID': 1627775, 'PLAYER_NAME': 'Patrick McCaw'}, {'NBA_FANTASY_PTS': 10.1, 'PLAYER_ID': 201156, 'PLAYER_NAME': 'Nick Young'}, {'NBA_FANTASY_PTS': 9.3, 'PLAYER_ID': 201580, 'PLAYER_NAME': 'JaVale McGee'}, {'NBA_FANTASY_PTS': 9.2, 'PLAYER_ID': 1626172, 'PLAYER_NAME': 'Kevon Looney'}, {'NBA_FANTASY_PTS': 6.6, 'PLAYER_ID': 1626188, 'PLAYER_NAME': 'Quinn Cook'}, {'NBA_FANTASY_PTS': 1.2, 'PLAYER_ID': 1627745, 'PLAYER_NAME': 'Damian Jones'}],
1610612759: [{'NBA_FANTASY_PTS': 39.3, 'PLAYER_ID': 200746, 'PLAYER_NAME': 'LaMarcus Aldridge'}, {'NBA_FANTASY_PTS': 32.5, 'PLAYER_ID': 202695, 'PLAYER_NAME': 'Kawhi Leonard'}, {'NBA_FANTASY_PTS': 28.0, 'PLAYER_ID': 2200, 'PLAYER_NAME': 'Pau Gasol'}, {'NBA_FANTASY_PTS': 24.7, 'PLAYER_ID': 203937, 'PLAYER_NAME': 'Kyle Anderson'}, {'NBA_FANTASY_PTS': 22.7, 'PLAYER_ID': 200752, 'PLAYER_NAME': 'Rudy Gay'}, {'NBA_FANTASY_PTS': 20.5, 'PLAYER_ID': 201980, 'PLAYER_NAME': 'Danny Green'}, {'NBA_FANTASY_PTS': 18.3, 'PLAYER_ID': 1627749, 'PLAYER_NAME': 'Dejounte Murray'}, {'NBA_FANTASY_PTS': 17.8, 'PLAYER_ID': 2225, 'PLAYER_NAME': 'Tony Parker'}, {'NBA_FANTASY_PTS': 17.1, 'PLAYER_ID': 201988, 'PLAYER_NAME': 'Patty Mills'}, {'NBA_FANTASY_PTS': 16.6, 'PLAYER_ID': 1938, 'PLAYER_NAME': 'Manu Ginobili'}, {'NBA_FANTASY_PTS': 11.4, 'PLAYER_ID': 1627854, 'PLAYER_NAME': 'Bryn Forbes'}, {'NBA_FANTASY_PTS': 10.6, 'PLAYER_ID': 202722, 'PLAYER_NAME': 'Davis Bertans'}, {'NBA_FANTASY_PTS': 8.6, 'PLAYER_ID': 203530, 'PLAYER_NAME': 'Joffrey Lauvergne'}, {'NBA_FANTASY_PTS': 6.9, 'PLAYER_ID': 203464, 'PLAYER_NAME': 'Brandon Paul'}, {'NBA_FANTASY_PTS': 5.1, 'PLAYER_ID': 1627856, 'PLAYER_NAME': 'Matt Costello'}, {'NBA_FANTASY_PTS': 4.0, 'PLAYER_ID': 1628401, 'PLAYER_NAME': 'Derrick White'}, {'NBA_FANTASY_PTS': 2.4, 'PLAYER_ID': 1626199, 'PLAYER_NAME': 'Darrun Hilliard'}],
1610612738 :[{'NBA_FANTASY_PTS': 38.5, 'PLAYER_ID': 202681, 'PLAYER_NAME': 'Kyrie Irving'}, {'NBA_FANTASY_PTS': 33.6, 'PLAYER_ID': 201143, 'PLAYER_NAME': 'Al Horford'}, {'NBA_FANTASY_PTS': 26.4, 'PLAYER_ID': 1628369, 'PLAYER_NAME': 'Jayson Tatum'}, {'NBA_FANTASY_PTS': 26.1, 'PLAYER_ID': 1627759, 'PLAYER_NAME': 'Jaylen Brown'}, {'NBA_FANTASY_PTS': 23.8, 'PLAYER_ID': 203935, 'PLAYER_NAME': 'Marcus Smart'}, {'NBA_FANTASY_PTS': 21.3, 'PLAYER_ID': 202694, 'PLAYER_NAME': 'Marcus Morris'}, {'NBA_FANTASY_PTS': 19.9, 'PLAYER_ID': 1626179, 'PLAYER_NAME': 'Terry Rozier'}, {'NBA_FANTASY_PTS': 15.1, 'PLAYER_ID': 203382, 'PLAYER_NAME': 'Aron Baynes'}, {'NBA_FANTASY_PTS': 13.2, 'PLAYER_ID': 1628464, 'PLAYER_NAME': 'Daniel Theis'}, {'NBA_FANTASY_PTS': 7.2, 'PLAYER_ID': 203499, 'PLAYER_NAME': 'Shane Larkin'}, {'NBA_FANTASY_PTS': 5.4, 'PLAYER_ID': 1628400, 'PLAYER_NAME': 'Semi Ojeleye'}, {'NBA_FANTASY_PTS': 4.3, 'PLAYER_ID': 1627846, 'PLAYER_NAME': 'Abdel Nader'}, {'NBA_FANTASY_PTS': 3.7, 'PLAYER_ID': 1627824, 'PLAYER_NAME': 'Guerschon Yabusele'}, {'NBA_FANTASY_PTS': 3.2, 'PLAYER_ID': 202330, 'PLAYER_NAME': 'Gordon Hayward'}, {'NBA_FANTASY_PTS': 3.0, 'PLAYER_ID': 1628444, 'PLAYER_NAME': 'Jabari Bird'}, {'NBA_FANTASY_PTS': 1.5, 'PLAYER_ID': 1628443, 'PLAYER_NAME': 'Kadeem Allen'}],
1610612760: [{'NBA_FANTASY_PTS': 53.5, 'PLAYER_ID': 201566, 'PLAYER_NAME': 'Russell Westbrook'}, {'NBA_FANTASY_PTS': 37.5, 'PLAYER_ID': 202331, 'PLAYER_NAME': 'Paul George'}, {'NBA_FANTASY_PTS': 30.9, 'PLAYER_ID': 203500, 'PLAYER_NAME': 'Steven Adams'}, {'NBA_FANTASY_PTS': 29.5, 'PLAYER_ID': 2546, 'PLAYER_NAME': 'Carmelo Anthony'}, {'NBA_FANTASY_PTS': 17.7, 'PLAYER_ID': 203460, 'PLAYER_NAME': 'Andre Roberson'}, {'NBA_FANTASY_PTS': 15.9, 'PLAYER_ID': 203924, 'PLAYER_NAME': 'Jerami Grant'}, {'NBA_FANTASY_PTS': 14.9, 'PLAYER_ID': 101109, 'PLAYER_NAME': 'Raymond Felton'}, {'NBA_FANTASY_PTS': 8.6, 'PLAYER_ID': 1627772, 'PLAYER_NAME': 'Daniel Hamilton'}, {'NBA_FANTASY_PTS': 8.5, 'PLAYER_ID': 202335, 'PLAYER_NAME': 'Patrick Patterson'}, {'NBA_FANTASY_PTS': 8.2, 'PLAYER_ID': 203518, 'PLAYER_NAME': 'Alex Abrines'}, {'NBA_FANTASY_PTS': 8.2, 'PLAYER_ID': 203962, 'PLAYER_NAME': 'Josh Huestis'}, {'NBA_FANTASY_PTS': 5.7, 'PLAYER_ID': 1628390, 'PLAYER_NAME': 'Terrance Ferguson'}, {'NBA_FANTASY_PTS': 5.6, 'PLAYER_ID': 1626177, 'PLAYER_NAME': 'Dakari Johnson'}, {'NBA_FANTASY_PTS': 3.6, 'PLAYER_ID': 2555, 'PLAYER_NAME': 'Nick Collison'}, {'NBA_FANTASY_PTS': 3.3, 'PLAYER_ID': 202713, 'PLAYER_NAME': 'Kyle Singler'}]
}


def get_starters_by_team(soup):
    """
    Returns a dictionary from team abbreviations to
    a list of player names who are starting today.

    soup: BeautifulSoup scraped from ROTOWIRE_URL.
    """
    game_divs = soup.find_all('div', class_='offset1 span15')

    starters_by_abbreviation = {}
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
        team_lineup_divs = players_div.find_all('div', recursive=False)[
            1].find_all('div', class_='dlineups-half')
        for team_name, lineup_div in zip((team_name_1, team_name_2), team_lineup_divs):
            starter_names = [match_name(player_a['title'].strip())
                             for player_a in lineup_div.find_all('a')]
            starters_by_abbreviation[team_name] = starter_names

    return starters_by_abbreviation

def get_injured_by_team(soup):
    """
    Returns a dictionary from team abbreviations to
    a list of player names who are injured today.

    soup: BeautifulSoup scraped from ROTOWIRE_URL.
    """
    game_divs = soup.find_all('div', class_='offset1 span15')

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

        # find injured
        team_lineup_divs = players_div.find_all('div', recursive=False)[
            2].find_all('div', class_='dlineups-half equalheight')
        for team_name, lineup_div in zip((team_name_1, team_name_2), team_lineup_divs):
            injured_names = [match_name(player_a.text.strip())
                             for player_a in lineup_div.find_all('a')]
            injured_by_abbreviation[team_name] = set(injured_names)

    return injured_by_abbreviation

def get_matchups(soup):
    """
    Returns a list of matchups.
    A matchup is a tuple of two team abbreviations.
    The game is located at the second team's home.

    soup: BeautifulSoup scraped from ROTOWIRE_URL.
    """
    game_divs = soup.find_all('div', class_='offset1 span15')

    matchups = []
    for game_div in game_divs:
        game_header = game_div.find_all(
            'div', class_='span15 dlineups-topbox')[0]
        team_name_1 = game_header.find_all(
            'div', class_='span5 dlineups-topboxleft')[0].text.strip()
        team_name_2 = game_header.find_all(
            'div', class_='span5 dlineups-topboxright')[0].text.strip()
        matchups.append((team_name_1, team_name_2))

    return matchups


def get_nba_lineup(team_id):
    """
    Given a team_id, scrapes from the official NBA website the
    team's roster corresponding to the team_id.
    """
    if team_id in NBA_LINEUPS_SNAPSHOT:
        return NBA_LINEUPS_SNAPSHOT[team_id]

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
    return sorted(lineup, key=lambda d: -d['NBA_FANTASY_PTS'])


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
    soup = BeautifulSoup(requests.get(ROTOWIRE_URL).content, 'html.parser')
    starters_by_abbrev = get_starters_by_team(soup)
    injured_by_abbrev = get_injured_by_team(soup)
    matchups = get_matchups(soup)

    lineups = {}
    for team_abbrev in starters_by_abbrev:
        team_id = team_abbrev_to_team_id_map[team_abbrev]
        lineup = get_game_day_lineup(
            team_abbrev, team_id, starters_by_abbrev[team_abbrev], injured_by_abbrev[team_abbrev])
        lineups[team_abbrev] = lineup
    
    resp = {}
    resp['lineups'] = lineups
    resp['matchups'] = matchups
    return json.dumps(resp)
