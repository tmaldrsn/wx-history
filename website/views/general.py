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
    return render_template('general/index.html')


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
            min_query = query % ("Air Temperature", "desc")
            min_station_temp = list(cur.execute(min_query))[0][5]
            max_query = query % ("Air Temperature", "asc")
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


@mod.route('/_add_numbers')
def add_numbers():
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    return jsonify(result=a+b)


@mod.route('/add')
def index():
    return render_template('index.html')
