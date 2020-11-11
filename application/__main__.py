from application.timeline import timeline
from application.map import map_fig
from application.controller import controller
from application.data.data_loader import DataLoader
from application.layout import graph_template, continents
from application.config.config import Config


from dash import Dash, callback_context
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ALL, MATCH, ClientsideFunction
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from configparser import ConfigParser
import logging


# import pandas as pd
# import dash_table
# from dash.exceptions import PreventUpdate
# import plotly.graph_objects as go
# import dash_daq as daq
# import time
import numpy as np
# import time
# import json
# import math
# from datetime import datetime

"""
logging
"""
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger()


# configs
configuration = Config()
parser = ConfigParser()
parser.read("settings.ini")

state = configuration.state


"""
create Dash app
load stylesheets
"""
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
app.title = "COVID-19"
app.scripts.config.serve_locally = False
app.config.suppress_callback_exceptions = True


"""
load data
initialize DataLoader
"""


def get_new_data():

    global data
    global latest_update

    data = DataLoader(parser)

    data.load_data()
    latest_update = data.latest_load.strftime("%m/%d/%Y, %H:%M:%S")

    logger.info("Data updated at " + latest_update)


get_new_data()


"""
layout elements
"""
controller = controller()

map_figure = map_fig(parser, data)
map_graph = graph_template("map", parser)
map_graph.figure = map_figure
continent_div = continents(parser, data)


timeline_tab = graph_template("timeline", parser)

add_compare = dbc.Row("add Europe to comparsion")

info = dbc.Row("2342342 cases in Europe on 2020-01-10")


"""
layout
"""
map_tab = dbc.Row(
    children=[
        dbc.Col(
            children=[
                continent_div,
                info,
                add_compare
            ],
            lg=2,
            md=3,
            xs=12,),
        dbc.Col(map_graph, lg=10,
                md=9,
                xs=12,)
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
            # dbc.Row(comparsion, no_gutters=False, justify="center"),

            dcc.Store(id='memory', storage_type='local')
        ],
        fluid=True
    )


app.layout = set_layout


"""
callbacks
"""


@app.callback(Output("memory", "data"),
              [Input("select-continent", "value"),
               Input("map", "clickData"),
               Input("cases_death_switch", "value"),
               ],
              [State("map", "figure")])
def update_state(continent, country, indicator, map_fig):
    if map_fig:
        print("test")
        # lat = map_fig["layout"]["mapbox"]["center"]["lat"]
        # lon = map_fig["layout"]["mapbox"]["center"]["lon"]
        # zoom = map_fig["layout"]["mapbox"]["zoom"]
        # state["bbox"]["center"]["lat"] = lat
        # state["bbox"]["center"]["lon"] = lon
        # state["bbox"]["zoom"] = zoom
    else:
        state["bbox"]["center"] = data.regions[continent]["center"]
        state["bbox"]["zoom"] = data.regions[continent]["zoom"]

    if callback_context.triggered[0]["prop_id"] == "select-continent.value":
        state["active"] = data.regions[continent]["name"]
        state["bbox"]["center"] = data.regions[continent]["center"]
        state["bbox"]["zoom"] = data.regions[continent]["zoom"]
    elif callback_context.triggered[0]["prop_id"] == "map.clickData":
        state["active"] = country["points"][0]["text"]

    if indicator:
        state["indicator"] = "cases"
    else:
        state["indicator"] = "deaths"
    logger.info(state)
    return state


@app.callback(
    Output("map", "figure"),
    [
        Input("memory", "data")
    ])
def draw_map(state):

    indicator_name = state["indicator"]
    data_selected = data.latest_data(
        data.indicators[state["indicator"]])

    map_figure.update_traces(
        locations=data_selected["iso3"],
        z=data_selected[indicator_name],
        text=data_selected["region"],
        zmax=data_selected[indicator_name]
        .replace([np.inf, -np.inf], np.nan)
        .max()
        * 0.3,
    )

    map_figure.update_layout(
        mapbox_zoom=state["bbox"]["zoom"],
        mapbox_center=state["bbox"]["center"],
    )

    map_figure.layout.uirevision = True
    # map_figure.update_layout(
    #     mapbox_zoom=data.regions[continent]["zoom"],
    #     mapbox_center=data.regions[continent]["center"],
    # )
    logger.info("map")

    return map_figure


@app.callback(
    Output("timeline", "figure"),
    [
        Input("memory", "data")
    ]
)
def draw_timeline(state):
    timeline_figure = timeline(configuration)
    return timeline_figure


"""
start server
"""

application = app.server

if __name__ == "__main__":

    app.run_server(
        debug=True,
        port=configuration.port,
        host=configuration.host)
