"""
Displays index.html. Leaves the routing to react.
"""

from flask import render_template
from . import app


@app.route('/')
@app.route('/gameDateGames')
@app.route('/gameDayAnalysis')
def show_index():
    return render_template('index.html')
