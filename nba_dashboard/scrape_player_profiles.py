import requests
from . import app
from .db_utils import execute_sql

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
API_REQUEST_TEMPLATE = 'https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/{team_id}/{current_season}/260x190/{player_id}.png'
CURRENT_SEASON = '2017-18'

def scrape_profile(team_id, player_id):
    """
    Scrapes the player's profile for their picture and
    return the picture's content.
    """
    api_request = API_REQUEST_TEMPLATE.format(**{
        'team_id': team_id,
        'player_id': player_id,
        'current_season': CURRENT_SEASON[:4] # only the season's beginning year
    })
    response = requests.get(url=api_request, headers={'User-agent': USER_AGENT},
        stream=True, allow_redirects=False)
    return response.content

def store_profile(player_id, img):
    """
    Stores the given image data at static/images/profile/{player_id}.png.
    """
    with open('static/images/profile/{}.png'.format(player_id), 'wb') as f:
        f.write(img)

def scrape_all_profiles():
    players = execute_sql("""
        SELECT
                DISTINCT TEAM_ID, PLAYER_ID
            FROM PLAYER_LOGS
            WHERE SEASON = (?);""", (CURRENT_SEASON, )).rows
    for team_id, player_id in players:
        store_profile(player_id, scrape_profile(team_id, player_id))

@app.cli.command()
def update_player_profiles():
    """
    Updates the images stored at static/images/profile.
    """
    scrape_all_profiles()
