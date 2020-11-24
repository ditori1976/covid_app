from application.config.config import Config
from application.data.data_loader import DataLoader
from configparser import ConfigParser
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from datetime import datetime
import math
import json
import time
from dash.dependencies import Input, Output, State, ALL, MATCH
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import dash_table
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash


configuration = Config()
layout = dict(margin=dict(l=0, r=0, b=0, t=0, pad=0), dragmode="select")
style_todo = {"display": "inline", "margin": "10px"}

parser = ConfigParser()
parser.read("settings.ini")

background_color_grey = "#b0c6eb"

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[
        {
            "name": "viewport",
            "content": "width=device-width, initial-scale=1.0"
        }
    ]
)
app.title = "COVID-19"

navbar = dbc.NavbarSimple(
    children=[
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Page 2", href="#"),
                dbc.DropdownMenuItem("Page 3", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        )
    ],
    brand_href="#",
    color="#b0c6eb",
    dark=True,
)


def set_layout():
    return dbc.Container(
        children=[
            navbar,
            #dbc.Row(row_1, no_gutters=True, justify="center"),
            #dbc.Row(row_2, no_gutters=True, justify="left"),
            #dbc.Row(row_3, no_gutters=True, justify="center"),
            #dcc.Store(id='memory', data=state),
        ],
        fluid=True
    )


app.layout = set_layout


application = app.server


if __name__ == "__main__":

    # start_multi()
    app.run_server(
        debug=True,
        port=configuration.port,
        host=configuration.host)
