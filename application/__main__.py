import pandas as pd
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import dash_daq as daq
#
# import numpy as np
from dash.dependencies import Input, Output, State, ALL, MATCH
# import time
import json
# import math
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# data
from application.data.data_loader import DataLoader

# configs
from configparser import ConfigParser
from application.config.config import Config
configuration = Config()
parser = ConfigParser()
parser.read("settings.ini")

state = configuration.state

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
app.scripts.config.serve_locally = False
app.config.suppress_callback_exceptions = True


def timeline():
    from application.timeline import timeline
    return timeline


def controller():
    from application.controller import select_aggregation, select_per_capita, cases_death_switch
    return [cases_death_switch, select_aggregation, select_per_capita]


@app.callback(Output("memory", "data"),
              [Input("daily", "n_clicks"),
               Input("days", "n_clicks"),
               Input("accum", "n_clicks"),
               Input("select_per_capita", "on"),
               Input("cases_death_switch", "value")])
def set_state(daily, days, accum, per_capita, indicator):
    # if daily is None:
    #     raise PreventUpdate
    # if days is None:
    #     raise PreventUpdate
    # if accum is None:
    #     raise PreventUpdate
    # if per_capita is None:
    #     raise PreventUpdate
    # if indicator is None:
    #     raise PreventUpdate
    ctx = dash.callback_context
    if ctx.triggered[0]["prop_id"].split(".")[0] == "daily":
        state["aggregation"] = "daily"
    elif ctx.triggered[0]["prop_id"].split(".")[0] == "days":
        state["aggregation"] = "days"
    elif ctx.triggered[0]["prop_id"].split(".")[0] == "accum":
        state["aggregation"] = "accum"

    state["per capita"] = per_capita
    if indicator:
        state["indicator"] = "cases"
    else:
        state["indicator"] = "deaths"

    print(state)
    return state


@app.callback(
    [Output("daily", "className"),
     Output("days", "className"),
     Output("accum", "className")],
    [Input("memory", "data")],
)
def set_active(data):
    button_conf = ["btn", "btn active", "btn"]
    if data["aggregation"] == "daily":
        button_conf = ["btn active", "btn", "btn"]
    elif data["aggregation"] == "accum":
        button_conf = ["btn", "btn", "btn active"]
    elif data["aggregation"] == "days":
        button_conf = ["btn", "btn active", "btn"]

    return button_conf


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
            children=[timeline()]
        ),
        dcc.Tab(
            label="map",
            value="map_tab",
            className="custom-tab",
            selected_className="custom-tab--selected",
        )

    ],
    parent_className="custom-tabs",
    className="custom-tabs-container",
    style={"width": "100%", "margin": 0, "padding": 0},
)


row_1 = [
    dbc.Col(
        children=[
            tabs_div,
            html.Div(id="update")
        ],
        lg=12,
        md=6,
        xs=12),
    # dbc.Col(table, lg=6, md=6, xs=12)
]
row_2 = controller()


def set_layout():
    return dbc.Container(
        children=[
            dbc.Row(row_1, no_gutters=True, justify="center"),
            dbc.Row(row_2, no_gutters=False, justify="center"),
            dcc.Store(id='memory', data=state, storage_type='session'),
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
