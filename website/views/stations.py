from flask import (
    Blueprint,
    render_template,
    url_for,
    request,
    abort,
    redirect,
    jsonify
)
import website
import website.observations as gobs

import sqlite3
import datetime

import numpy as np
import pandas as pd
import os


forecast_elements = [
    "Datetime",
    "Wind",
    "Visibility",
    "Weather",
    "Sky Condition",
    "Air Temperature",
    "Dew Point",
    "6HR Max",
    "6HR Min",
    "Humidity",
    "Wind Chill",
    "Heat Index",
    "Altimeter Pressure",
    "Sea Level Pressure",
    "1HR Precip",
    "3HR Precip",
    "6HR Precip"
]

DB_PATH = "data/observations.db"

mod = Blueprint('stations', __name__, url_prefix='/stations/')


@mod.route('/')
def show_station_list():
    station_df = pd.read_csv('data/stations.csv', sep=',', quotechar="|")
    vals = station_df.values

    for val in vals:
        val[3] = round(val[3], 3)
        val[4] = round(val[4], 3)
    """
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    query = "select * from station"
    stations_list = list(cur.execute(query))
    con.close()
    """
    return render_template('stations/index.html', stations=vals)


@mod.route('/<s>/')
def show_station_information(s):
    station_df = pd.read_csv('data/stations.csv', sep=',', quotechar="|")
    station_info = station_df[station_df['ID'] == s].values

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    query = f"select * from {s} order by datetime desc limit 1"
    current_info = list(cur.execute(query))
    con.close()

    return render_template('stations/dashboard.html', station_info=station_info, current_info=current_info)


@mod.route('/<s>/<page>')
def show_station_data(s, page=1):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    station_df = pd.read_csv('data/stations.csv', sep=',', quotechar="|")
    station_info = station_df[station_df['ID'] == s].values
    query = f"select * from {s} order by datetime desc limit 50 offset {50*(int(page)-1)}"
    observations = list(cur.execute(query))
    len_query = f"select count(*) from {s}"
    num_observations = list(cur.execute(len_query))[0][0]
    max_page = num_observations // 50 + 1
    con.close()

    if int(page) > max_page or int(page) < 0:
        abort(404)
    return render_template('stations/observations.html', station=station_info, obs=observations, page=int(page),  max_page=int(max_page))


@mod.route('/<s>/_get_observations')
def get_observations(s):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    #station = request.args.get('station', 0, type=str)
    query = f"select * from {s} order by datetime desc limit 100"
    observations = list(cur.execute(query))

    con.close()

    datetimes = [obs[0] for obs in observations]
    temps = [obs[5] for obs in observations]

    return jsonify(datetimes=datetimes, temps=temps)
