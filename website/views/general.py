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
import pandas as pd

mod = Blueprint('general', __name__)


@mod.route('/')
def home_page():
    station_df = pd.read_csv('data/stations.csv', sep=',', quotechar='|')
    ids = list(station_df["ID"].values)
    lats = list(station_df["Latitude"].values)
    lons = list(station_df["Longitude"].values)
    print(ids)
    return render_template('general/index.html', ids=ids, lats=lats, lons=lons)


@mod.route('/_get_extremes')
def extremes():
    con = sqlite3.connect('data/observations.db')
    cur = con.cursor()

    station_df = pd.read_csv('data/stations.csv', sep=',', quotechar="|")
    station_list = station_df.ID.values

    min_temp, max_temp = 100, 0
    min_station, max_station = "", ""
    dt = datetime.date.today()
    for station in station_list:
        query = f"""select * from {station} where substr(datetime, 0, 11)='{str(dt)}' order by "%s" %s limit 1"""
        try:
            min_query = query % ("Air Temperature", "asc")
            min_station_temp = list(cur.execute(min_query))[0][5]
            max_query = query % ("Air Temperature", "desc")
            max_station_temp = list(cur.execute(max_query))[0][5]

            if min_station_temp < min_temp:
                min_temp = min_station_temp
                min_station = station
            if max_station_temp > max_temp:
                max_temp = max_station_temp
                max_station = station
        except (IndexError, TypeError):
            pass
    return jsonify(date=str(dt), low=min_temp, low_station=min_station, high=max_temp, high_station=max_station)
