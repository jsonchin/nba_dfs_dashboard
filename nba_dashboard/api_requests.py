"""
Contains functions that map to api_request routes.

- player
"""

from . import app
from . import db_utils


@app.route('/player')
def show_player():
    rows = db_utils.exec_sql("""SELECT * FROM PLAYER_LOGS LIMIT 10;""")
    return rows
