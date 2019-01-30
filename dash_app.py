import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

import flask
import pandas as pd
import datetime
import time
import os

from src.get_new_observations import main as gno

line_obs = ['Air Temperature', 'Dew Point', 'Humidity',
            'Altimeter Pressure', 'Sea Level Pressure']
scatter_obs = ['Wind Chill', 'Heat Index']
bar_obs = ['1HR Precip', '3HR Precip', '6HR Precip']

forecast_elements = [
    "Date",
    "Time",
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


server = flask.Flask('app')
server.secret_key = os.environ.get('secret_key', 'secret')

station_df = pd.read_csv('observations.csv', sep=',',
                         quotechar="|", nrows=2190)
# obs_df = pd.read_csv('observations.csv', sep=',', header=2191, quotechar="|")

app = dash.Dash('app', server=server)

app.scripts.config.serve_locally = False
dcc._js_dist[0]['external_url'] = 'https://cdn.plot.ly/plotly-basic-latest.min.js'

app.layout = html.Div([
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


@app.callback(Output('obs-graph', 'figure'),
              [Input('station-dropdown', 'value'), Input('observation-dropdown', 'value')])
def update_graph(selected_dropdown_value, selected_observation):
    data = []
    for station in selected_dropdown_value:
        dff = pd.DataFrame(gno(station)[0])
        dff.columns = forecast_elements
        dff.dropna()
        data.append({
            'x': [datetime.datetime(int(d[6:10]), int(d[0:2]), int(d[3:5]), int(t[0:2]), int(t[3:5])) for d, t in zip(dff.Date, dff.Time)],
            'y': list(map(float, dff[selected_observation])),
            'name': station,
            'line': {
                'width': 3,
                'shape': 'spline'
            }
        })

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


if __name__ == '__main__':
    app.run_server()
