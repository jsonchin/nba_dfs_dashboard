"""
Contains functions that display views.

- index
"""

from flask import request, redirect, url_for, abort, render_template
from . import app
from . import db_utils

@app.route('/')
def show_index():
    rows = db_utils.exec_sql("""SELECT * FROM PLAYER_LOGS LIMIT 10;""")
    return render_template('index.html', rows=rows)
