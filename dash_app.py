import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

import flask
import pandas as pd
import datetime
import time
import os

server = flask.Flask('app')
server.secret_key = os.environ.get('secret_key', 'secret')

station_df = pd.read_csv('observations.csv', sep=',', quotechar="|", nrows=2190)
obs_df = pd.read_csv('observations.csv', sep=',', header=2191, quotechar="|")

app = dash.Dash('app', server=server)

app.scripts.config.serve_locally = False
dcc._js_dist[0]['external_url'] = 'https://cdn.plot.ly/plotly-basic-latest.min.js'

app.layout = html.Div([
    html.H1('Temperatures'),
    dcc.Dropdown(
        id='observation-dropdown',
        options=[
            {'label': 'Air Temperature', 'value': 'Air Temperature'},
            {'label': 'Dew Point', 'value': 'Dew Point'},
        ],
        value='Air Temperature'
    ),
    dcc.Dropdown(
        id='station-dropdown',
        options=[
            {'label': station, 'value': station} for station in station_df.ID
        ],
        value='KTOL'
    ),
    dcc.Graph(id='obs-graph')
], className='container')


@app.callback(Output('obs-graph', 'figure'),
              [Input('station-dropdown', 'value'), Input('observation-dropdown', 'value')])
def update_graph(selected_dropdown_value, selected_observation):
    dff = obs_df[obs_df['Station'] == selected_dropdown_value]
    return {
        'data': [{
            'x': [datetime.datetime(int(d[6:10]), int(d[0:2]), int(d[3:5]), int(t[0:2]), int(t[3:5])) for d, t in zip(dff.Date, dff.Time)],
            'y': dff[selected_observation],
            'line': {
                'width': 3,
                'shape': 'spline'
            }
        }],
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
