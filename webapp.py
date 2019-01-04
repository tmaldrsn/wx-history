from flask import Flask, url_for, render_template
import sqlite3


app = Flask(__name__)

@app.route('/')
def home_page():
    return render_template('hello.html')

@app.route('/station/')
def show_station_list():
    con = sqlite3.connect("observations.db")
    cur = con.cursor()

    query = "select * from station"
    stations_list = cur.execute(query)
    return render_template('stations.html', stations=list(stations_list))

@app.route('/station/<s>')
def show_station(s):
    con = sqlite3.connect("observations.db")
    cur = con.cursor()

    station_query = f"select * from station where id='{s}'"
    station_data = list(cur.execute(station_query))
    query = f"select * from {s} order by substr(date, 7, 4) desc, substr(date, 1, 2) desc, substr(date, 4, 2) desc, time desc"
    observations = list(cur.execute(query))
    return render_template('observations.html', station=station_data, obs=observations[-50:])

