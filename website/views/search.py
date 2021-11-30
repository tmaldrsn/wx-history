import pandas as pd
from flask import (
    Blueprint,
    render_template,
    url_for,
    request,
    abort
)
import sqlite3
import datetime

mod = Blueprint('search', __name__, url_prefix='/search/')


@mod.route('/')
def search_page():
    return render_template('search/index.html')


@mod.route('/data', methods=['GET'])
def handle_data():
    result = request.args
    date = result['date']
    datetime_object = datetime.date(
        year=int(date[:4]), month=int(date[5:7]), day=int(date[8:10]))
    #formatted_date = datetime.date.strftime(datetime_object, "%m/%d/%Y")

    con = sqlite3.connect("data/observations.db")
    cur = con.cursor()

    station_df = pd.read_csv('data/stations.csv', sep=',', quotechar="|")
    vals = station_df[station_df['ID'] == result['station']].values

    #station_query = f"select * from station where id='{result['station']}'"
    data_query = f"select * from {result['station']} where datetime LIKE '{date} %'"

    #station_data = list(cur.execute(station_query))
    station_data = list(vals)
    observation_data = list(cur.execute(data_query))

    return render_template(
        'search/result.html',
        obs=observation_data,
        station=station_data,
        curr_date=str(datetime_object),
        prev_date=str(datetime_object-datetime.timedelta(days=1)),
        next_date=str(datetime_object+datetime.timedelta(days=1)),
    )
