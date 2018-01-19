import sqlite3
from flask import g
from . import app
import os


def initial_connect_db():
    """
    Connects to the database specified in config.py
    by its path and its name.
    """
    con = sqlite3.connect(os.path.join(
        app.config['DB_PATH'], app.config['DB_NAME']))
    return con


def get_db_con():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = initial_connect_db()
    return g.sqlite_db


def exec_sql(sql, params=()):
    """
    Executes sql with provided params (no sql injection) and
    returns a list of rows.
    """
    con = get_db_con()
    cur = con.execute(sql, params)
    rows = cur.fetchall()
    return rows


@app.teardown_appcontext
def close_db(error):
    """
    Closes the database again at the end of the request.
    """
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
