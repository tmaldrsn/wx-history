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

mod = Blueprint('api', __name__, url_prefix='/api/')
DB_PATH = 'data/observations.db'


@mod.route('/get_extremes')
def extremes():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    station_df = pd.read_csv('data/stations.csv', sep=',', quotechar="|")
    station_list = station_df.ID.values

    min_temp, max_temp = np.inf, -np.inf
    min_station, max_station = "", ""
    dt = datetime.date.today() - datetime.timedelta(days=2)
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


@mod.route('/search_zipcode', methods=['GET'])
def zipcode_to_station():
    zipcode = request.args['zip']
    return jsonify(get_closest_station(int(zipcode)))


def get_zip_coords(zipcode):
    df = pd.read_csv('data/zipcodes.csv')
    entry = df[df.Zipcode == zipcode].values
    return entry.item(5), entry.item(6)


def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # radius of earth

    def rad(x):
        return np.radians(x)
    d_phi = rad(lat2) - rad(lat1)
    d_lam = rad(lon2) - rad(lon1)

    a = (np.sin(d_phi/2)**2) + np.cos(rad(lat1)) * \
        np.cos(rad(lat2)) * np.sin(d_lam/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return R * c


def get_closest_station(zipcode):
    zip_lat, zip_lon = get_zip_coords(zipcode)
    stations = pd.read_csv('data/stations.csv', sep=',',
                           quotechar='|').values
    closest_distance, closest_station = np.inf, ""

    for station in stations:
        station_lat, station_lon = station[3], station[4]
        distance = haversine(zip_lat, zip_lon, station_lat, station_lon)
        if distance < closest_distance:
            closest_distance = distance
            closest_station = station[0]

    return closest_station, closest_distance


@mod.route('/get_observations', methods=['GET'])
def get_observations():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    station = request.args['station']
    nobs = 100
    if request.args['nobs']:
        nobs = request.args['nobs']
    query = f"select * from {station} order by datetime desc limit {nobs}"
    observations = list(cur.execute(query))

    con.close()

    datetimes = [obs[0] for obs in observations]
    temps = [obs[5] for obs in observations]

    return jsonify(datetimes=datetimes, temps=temps)
