from flask import (
    Blueprint,
    render_template,
    url_for,
    request,
    abort,
    redirect
)
import website
import website.observations as gobs

import sqlite3
import datetime

from werkzeug.wsgi import DispatcherMiddleware

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

import numpy as np
import pandas as pd
import os

line_obs = ['Air Temperature', 'Dew Point', 'Humidity',
            'Altimeter Pressure', 'Sea Level Pressure']
scatter_obs = ['Wind Chill', 'Heat Index']
bar_obs = ['1HR Precip', '3HR Precip', '6HR Precip']

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

dash_app = dash.Dash('app', url_base_pathname='/current/')
dash_app.scripts.config.serve_locally = False
dcc._js_dist[0]['external_url'] = 'https://cdn.plot.ly/plotly-basic-latest.min.js'

station_df = pd.read_csv('data/stations.csv', sep=',', quotechar='|')

dash_app.layout = html.Div([
    html.H1('Observations'),
    dcc.Dropdown(
        id='observation-dropdown',
        options=[
            {'label': obs, 'value': obs} for obs in line_obs + scatter_obs + bar_obs
        ],
        value='Air Temperature'
    ),
    dcc.Dropdown(
        id='station-dropdown',
        options=[
            {'label': f'{station} - {name}', 'value': station} for station, name in zip(station_df.ID, station_df.Name)
        ],
        value=['KTOL'],
        multi=True
    ),
    dcc.Graph(id='obs-graph')
], className='container')


@dash_app.callback(Output('obs-graph', 'figure'),
                   [Input('station-dropdown', 'value'), Input('observation-dropdown', 'value')])
def update_graph(selected_dropdown_value, selected_observation):
    data = []
    for station in selected_dropdown_value:
        observations = gobs.get_raw_data(station)[0]
        observations = gobs.format_rows(observations)
        dff = pd.DataFrame(observations)
        dff.columns = forecast_elements
        dff.dropna()
        data.append(
            go.Scatter(
                x=list(dff.Datetime),
                y=list(dff[selected_observation]),
                name=station,
                mode='markers',
                opacity=0.7
            ))

    return {
        'data': data,
        'layout': {
            'margin': {
                'l': 30,
                'r': 20,
                'b': 30,
                't': 20
            }
        }
    }


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


@mod.route('/<s>/current')
def render_dashboard(s):
    return
