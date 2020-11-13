from application.timeline import timeline
from application.map import map_fig
from application.controller import controller
from application.comparsion import comparsion_add, comparsion_list
from application.data.data_loader import DataLoader
from application.layout import graph_template, continents
from application.config import Config, logger


from dash import Dash, callback_context, no_update
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ALL, MATCH, ClientsideFunction
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from configparser import ConfigParser
import json


# import pandas as pd
# import dash_table
# from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
# import dash_daq as daq
# import time
import numpy as np
# import time

# import math
# from datetime import datetime


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
# timeline_tab.figure = timeline_figure

add_compare = comparsion_add("add to compare", parser)

info1 = dbc.Row("select continent")
info2 = dbc.Row("or click on map")


"""
layout
"""
map_tab = dbc.Row(
    children=[
        dbc.Col(map_graph, lg=10,
                md=9,
                xs=12,),
        dbc.Col(
            children=[

                continent_div

                # add_compare
            ],
            lg=2,
            md=3,
            xs=12,)
    ],
    no_gutters=True
)

tabs_div = dcc.Tabs(
    id="timeline_map_tab",
    value="map_tab",
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
            label="select country",
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
        html.Div(
            id="state",
            children=json.dumps(state), style={'display': 'None'})

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
            comparsion_list(parser),
            dcc.Store(id='memory')
        ],
        fluid=True
    )


app.layout = set_layout


"""
callbacks
"""


@app.callback(
    Output("state", "children"),
    [
        Input("select-continent", "value"),
        Input("map", "clickData"),
        Input("list-countries", "value"),
        Input("cases_death_switch", "value"),
        Input("select_per_capita", "on"),
        Input("select_aggregation", "value")
    ],
    [State("state", "children")])
def update_state(continent, country, regions, indicator,
                 per_capita, aggregation, state):
    state = json.loads(state)
    print(state)

    if callback_context.triggered[0]["prop_id"] == "select-continent.value":
        state["active"] = data.regions[continent]["name"]
        state["bbox"]["center"] = data.regions[continent]["center"]
        state["bbox"]["zoom"] = data.regions[continent]["zoom"]
    if callback_context.triggered[0]["prop_id"] == "map.clickData":
        state["active"] = country["points"][0]["text"]

    state["regions"] = regions

    if indicator:
        state["indicator"] = "cases"
    else:
        state["indicator"] = "deaths"

    state["per capita"] = per_capita
    state["aggregation"] = aggregation

    logger.info(json.dumps(state))

    return json.dumps(state)


@app.callback(
    Output("map", "figure"),
    [
        Input("state", "children")
    ])
def draw_map(state):
    state = json.loads(state)

    indicator_name = state["indicator"]

    data_selected = data.map_data(
        state["per capita"],
        state["aggregation"],
        state["indicator"])

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

    return map_figure


@app.callback(
    Output("timeline", "figure"),
    [
        Input("state", "children")
    ]
)
def draw_timeline(state):
    state = json.loads(state)

    timeline_figure = timeline(configuration)

    regions = set([state["active"]]) | set(state["regions"])
    for country in regions:
        data_selected = data.series(
            country,
            state["per capita"],
            state["aggregation"],
            state["indicator"])
        timeline_figure.add_trace(
            go.Scatter(name=country,
                       x=data_selected.date,
                       y=data_selected[state["indicator"]]
                       )
        )

    return timeline_figure


# @app.callback(
#     Output("add", "children"),
#     [
#         Input("state", "children")
#     ]
# )
# def add_comparsion(state):
#     state = json.loads(state)
#     return "add {} to comparsion".format(state["active"])


@app.callback(
    [Output("list-countries", "options"),
     Output("list-countries", "value"), ],
    [
        Input("state", "children"),
        Input("del", "n_clicks")
    ],
    [

        State("list-countries", "options"),
        State("list-countries", "value")
    ],
)
def edit_list(state, delete,
              list_countries, list_countries_values):

    state = json.loads(state)

    if callback_context.triggered[0]["prop_id"] == "del.n_clicks":
        return [], []

    # if add:
    if state["active"] not in list_countries_values:
        list_countries.append(
            {'label': state["active"], 'value': state["active"]})
        list_countries_values.append(state["active"])

    return list_countries, list_countries_values

    # else:

    #     return no_update, no_update


"""
start server
"""

application = app.server
if __name__ == "__main__":

    app.run_server(
        debug=True,
        port=configuration.port,
        host=configuration.host)
