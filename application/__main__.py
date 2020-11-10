from application.timeline import timeline
from application.controller import controller
from application.data.data_loader import DataLoader

# import pandas as pd
from dash import Dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
#import dash_table
#from dash.exceptions import PreventUpdate
#import plotly.graph_objects as go
#import dash_daq as daq
#import time
#import numpy as np
from dash.dependencies import Input, Output, State, ALL, MATCH, ClientsideFunction
# import time
#import json
# import math
#from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# configs
from configparser import ConfigParser
from application.config.config import Config
configuration = Config()
parser = ConfigParser()
parser.read("settings.ini")

state = configuration.state


app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[
        {
            "name": "viewport",
            "content": "width=device-width, initial-scale=1.0"
        }
    ]
)
app.scripts.config.serve_locally = False
app.config.suppress_callback_exceptions = True


def get_new_data():

    global data
    global latest_update

    data = DataLoader(parser)

    # data.load_data()
    latest_update = data.latest_load.strftime("%m/%d/%Y, %H:%M:%S")

    print("Data updated at " + latest_update)


get_new_data()


def graph_template(id, parser):
    return dcc.Graph(
        id=id,
        config={
            "displayModeBar": False},
        style={"height": parser.get(
            "layout", "height_first_row") + "vh", "width": "100%"})


controller = controller()

map_graph = graph_template("map", parser)

timeline_tab = graph_template("timeline", parser)

continent_div = dcc.Tabs(
    id="select-continent",
    value=parser.get("data", "continent"),
    vertical=True,
    children=[
        dcc.Tab(
            label=information["name"],
            value=region,
            className="custom-tab",
            selected_className="custom-tab--selected",
        )
        for region, information in data.regions.items()
    ],
    parent_className="custom-tabs",
    className="custom-tabs-container",
    style={"width": "100%", "margin": 0, "padding": 0},
)

map_tab = dbc.Row(
    children=[
        dbc.Col(continent_div, width=3),
        dbc.Col(map_graph, width=9)
    ],
    no_gutters=True
)

tabs_div = dcc.Tabs(
    id="timeline_map_tab",
    value="timeline_tab",
    vertical=False,
    children=[
        dcc.Tab(
            label="timeline",
            value="timeline_tab",
            className="custom-tab",
            selected_className="custom-tab--selected",
            children=[timeline_tab]
        ),
        dcc.Tab(
            label="map",
            value="map_tab",
            className="custom-tab",
            selected_className="custom-tab--selected",
            children=[map_tab]
        )
    ],
    parent_className="custom-tabs",
    className="custom-tabs-container",
    style={"width": "100%", "margin": 0, "padding": 0},
)


row_1 = dbc.Col(
    children=[
        tabs_div
    ],
    lg=12,
    md=6,
    xs=12,
    style={'margin-bottom': '7px'})

row_2 = dbc.Col(
    children=[
        controller,
        html.Div(id="update")
    ],
    lg=12,
    md=6,
    xs=12,
    style={'margin-bottom': '7px'})


def set_layout():
    return dbc.Container(
        children=[
            dbc.Row(row_1, no_gutters=True, justify="center"),
            dbc.Row(row_2, no_gutters=False, justify="center"),
            #dbc.Row(comparsion, no_gutters=False, justify="center"),

            dcc.Store(id='memory'),
        ],
        fluid=True
    )


app.layout = set_layout

app.title = "COVID-19"

application = app.server

if __name__ == "__main__":

    app.run_server(
        debug=True,
        port=configuration.port,
        host=configuration.host)
