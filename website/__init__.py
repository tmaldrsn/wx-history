from flask import Flask, url_for, render_template, request
import sqlite3
import datetime


app = Flask(__name__)

@app.route('/')
def home_page():
    return render_template('hello.html')

@app.route('/stations/')
def show_station_list():
    con = sqlite3.connect("observations.db")
    cur = con.cursor()

    query = "select * from station"
    stations_list = list(cur.execute(query))
    con.close()
    return render_template('stations.html', stations=stations_list)

@app.route('/stations/<s>/<page>')
def show_station(s, page):
    con = sqlite3.connect("observations.db")
    cur = con.cursor()

    station_query = f"select * from station where id='{s}'"
    station_data = list(cur.execute(station_query))
    query = f"select * from {s} order by substr(date, 7, 4) desc, substr(date, 1, 2) desc, substr(date, 4, 2) desc, time desc limit 50 offset {50*(int(page)-1)}"
    observations = list(cur.execute(query))
    con.close()
    return render_template('observations.html', station=station_data, obs=observations, page=int(page))


@app.route('/search/')
def search_page():
    return render_template('search.html')


@app.route('/search/data', methods=['GET'])
def handle_data():
    result = request.args
    date = result['date']
    datetime_object = datetime.date(year=int(date[:4]), month=int(date[5:7]), day=int(date[8:10]))
    formatted_date = datetime.date.strftime(datetime_object,"%m/%d/%Y")

    con = sqlite3.connect("observations.db")
    cur = con.cursor()

    station_query = f"select * from station where id='{result['station']}'"
    data_query = f"select * from {result['station']} where date='{formatted_date}'"

    station_data = list(cur.execute(station_query))
    observation_data = list(cur.execute(data_query))

    return render_template('result.html', obs=observation_data, station=station_data)