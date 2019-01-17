from flask import (
    Blueprint,
    render_template,
    url_for,
    request,
    abort
)
import sqlite3
import datetime

mod = Blueprint('stations', __name__, url_prefix='/stations/')


@mod.route('/')
def show_station_list():
    con = sqlite3.connect("observations.db")
    cur = con.cursor()

    query = "select * from station"
    stations_list = list(cur.execute(query))
    con.close()
    return render_template('stations/index.html', stations=stations_list)


@mod.route('/<s>/<page>')
def show_station(s, page):
    con = sqlite3.connect("observations.db")
    cur = con.cursor()

    station_query = f"select * from station where id='{s}'"
    station_data = list(cur.execute(station_query))
    query = f"select * from {s} order by substr(date, 7, 4) desc, substr(date, 1, 2) desc, substr(date, 4, 2) desc, time desc limit 50 offset {50*(int(page)-1)}"
    observations = list(cur.execute(query))
    len_query = f"select count(*) from {s}"
    num_observations = list(cur.execute(len_query))[0][0]
    max_page = num_observations // 50 + 1
    con.close()

    if int(page) > max_page or int(page) < 0:
        abort(404)
    return render_template('stations/observations.html', station=station_data, obs=observations, page=int(page),  max_page=int(max_page))
