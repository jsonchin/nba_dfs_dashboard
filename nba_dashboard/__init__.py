import os
import sqlite3
from flask import Flask, request, g, redirect, url_for, render_template


app = Flask(__name__, static_folder="static/dist",
            template_folder="static")

app.config.from_envvar('DASHBOARD_CONFIG')
