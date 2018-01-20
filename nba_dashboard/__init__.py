import os
import sqlite3
from flask import Flask, request, g, redirect, url_for, render_template


app = Flask(__name__)

app.config.from_envvar('DASHBOARD_CONFIG')
