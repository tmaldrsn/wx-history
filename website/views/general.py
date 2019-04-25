from flask import (
    Blueprint,
    render_template,
    url_for,
    request,
    abort,
    jsonify
)
import sqlite3
import datetime
import numpy as np
import pandas as pd

mod = Blueprint('general', __name__)


@mod.route('/')
def home_page():
    station_df = pd.read_csv('data/stations.csv', sep=',', quotechar='|')
    ids = list(station_df["ID"].values)
    lats = list(station_df["Latitude"].values)
    lons = list(station_df["Longitude"].values)
    return render_template('general/index.html', ids=ids, lats=lats, lons=lons)
