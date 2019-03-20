from website.views import (
    general,
    search,
    stations,
)
from website import observations as gobs
from flask import (
    Flask,
    url_for,
    render_template,
    request,
    abort,
    redirect
)

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

server = Flask(__name__)
server.secret_key = os.environ.get('secret_key', 'secret')
server.config.from_object('websiteconfig')


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
        observations = gobs.get_raw_data(station)
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


@server.errorhandler(400)
def bad_request(error):
    return render_template('400.html', error=error), 400


@server.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@server.route('/dashboard')
def render_dashboard():
    return redirect('/stations/KTOL/1')


app = DispatcherMiddleware(server, {
    '/stations/current/': dash_app.server
})

server.register_blueprint(general.mod)
server.register_blueprint(search.mod)
server.register_blueprint(stations.mod)
