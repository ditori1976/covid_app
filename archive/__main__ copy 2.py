from application.timeline import timeline

import pandas as pd
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import dash_daq as daq
import time
#
import numpy as np
from dash.dependencies import Input, Output, State, ALL, MATCH, ClientsideFunction
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


def get_new_data():

    global data
    global latest_update

    data = DataLoader(parser)

    data.load_data()
    latest_update = data.latest_load.strftime("%m/%d/%Y, %H:%M:%S")

    print("Data updated at " + latest_update)


get_new_data()


tabs_div = dcc.Tabs(
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


fig_map = go.Figure(
    go.Choroplethmapbox(
        colorscale="BuPu",
        geojson=data.countries,
        zmin=0,
        marker={"line": {"color": "rgb(180,180,180)", "width": 0.5}},
        colorbar={
            "thickness": 10,
            "len": 0.4,
            "x": 0,
            "y": 0.3,
            "outlinewidth": 0,
        },
    )
)

fig_map.update_layout(
    margin={"r": 0, "t": 0, "l": 0, "b": 0, "pad": 0},
    mapbox_style="mapbox://styles/dirkriemann/ck88smdb602qa1iljg6kxyavd",
    mapbox=go.layout.Mapbox(
        accesstoken="pk.eyJ1IjoiZGlya3JpZW1hbm4iLCJhIjoiY2szZnMyaXoxMDdkdjNvcW5qajl3bzdkZCJ9.d7njqybjwdWOxsnxc3fo9w",
        style="light",
        pitch=0,
    ),
)

fig_map.layout.uirevision = True

map_div = dcc.Graph(
    id="map",
    config={
        "displayModeBar": False},
    style={"height": parser.get(
        "layout", "height_first_row") + "vh", "width": "100%"}
)


tab_map = dbc.Row(
    children=[
        dbc.Col(tabs_div, width=3),
        dbc.Col(map_div, width=9)
    ],
    no_gutters=True
)

comparsion = dbc.Row(
    children=[
        dbc.Col(
            children=[
                html.Button(
                    "add",
                    id="add",
                    style={"height": 35,
                           "width": "100%",
                           # "background-color": background_color_grey,
                           "border": "none",
                           "color": "#586069",
                           "padding": "0px 0px",
                           "text-align": "center",
                           "text-decoration": "none",
                           "display": "inline - block",
                           "font-size": 16,
                           "margin": "0px 0px",
                           "cursor": "pointer"}
                ),
            ],
            width=3,
            style={"text-align": "right"}

        ),
        dbc.Col(
            children=[
                dcc.Dropdown(
                    id="list-countries",
                    options=[
                        {"label": "World", "value": "World"},
                        {"label": "North-A.", "value": "North-A."},
                        {"label": "Europe", "value": "Europe"},
                        {"label": "Asia", "value": "Asia"},
                        {"label": "South-A.", "value": "South-A."}],
                    value=["Europe", "North-A.", "South-A.", "Asia"],
                    multi=True,
                    placeholder="for comparsion",
                    style={"width": "100%", "font-size": 12, "border": "none"},
                    searchable=False,
                    clearable=False,
                )
            ],
            width=8
        ),
        dbc.Col(
            children=[
                html.Button(
                    "clear",
                    id="del",
                    style={"height": 35,
                           "width": "100%",
                           # "background-color": background_color_grey,
                           "border": "none",
                           "color": "red",
                           "padding": "0px 0px",
                           "text-align": "center",
                           "text-decoration": "none",
                           "display": "inline - block",
                           "font-size": 16,
                           "margin": "0px 0px",
                           "cursor": "pointer"}
                ),
            ],
            width=1,
            style={"text-align": "right"}

        )
    ],
    no_gutters=True,
)


def controller():
    from application.controller import select_aggregation, select_per_capita, cases_death_switch
    return [cases_death_switch, select_aggregation, select_per_capita]


@app.callback(
    [Output("list-countries", "options"),
     Output("list-countries", "value"), ],
    [
        Input("add", "n_clicks"),
        Input("del", "n_clicks")
    ],
    [
        State("memory", "data"),
        State("list-countries", "options"),
        State("list-countries", "value")
    ],
)
def edit_list(add, delete, state,
              list_countries, list_countries_values):

    ctx = dash.callback_context
    print(add)
    print(delete)
    if ctx.triggered[0]["prop_id"] == "del.n_clicks":
        return [], []

    if add:
        if state["active"] not in list_countries_values:
            list_countries.append(
                {'label': state["active"], 'value': state["active"]})
            list_countries_values.append(state["active"])

        return list_countries, list_countries_values

    else:

        return dash.no_update, dash.no_update


@app.callback(Output("memory", "data"),
              [Input("select_aggregation", "value"),
               Input("select_per_capita", "on"),
               Input("cases_death_switch", "value"),
               Input("select-continent", "value")],
              [State("map", "figure")])
def set_state(aggregation, per_capita, indicator, continent, figure):
    state["aggregation"] = aggregation
    state["per capita"] = per_capita
    if figure:
        lat = figure["layout"]["mapbox"]["center"]["lat"]
        lon = figure["layout"]["mapbox"]["center"]["lon"]
        zoom = figure["layout"]["mapbox"]["zoom"]
        state["bbox"]["center"]["lat"] = lat
        state["bbox"]["center"]["lon"] = lon
        state["bbox"]["zoom"] = zoom
    else:
        state["bbox"]["center"] = data.regions[continent]["center"]
        state["bbox"]["zoom"] = data.regions[continent]["zoom"]
    if indicator:
        state["indicator"] = "cases"
    else:
        state["indicator"] = "deaths"

    ctx = dash.callback_context

    if ctx.triggered[0]["prop_id"] == "select-continent.value":
        state["active"] = data.regions[continent]["name"]
        state["bbox"]["center"] = data.regions[continent]["center"]
        state["bbox"]["zoom"] = data.regions[continent]["zoom"]

    print(state)

    return state


@app.callback(
    Output("timeline", "figure"),
    [
        Input("memory", "data")
    ],
    [State("timeline", "figure")]
)
def draw_timeline(state, fig):

    fig = timeline()
    data_selected = data.select(
        state["active"],
        data.indicators[state["indicator"]])
    fig.add_trace(
        go.Bar(name=state["active"],
               x=data_selected.date,
               y=data_selected[state["indicator"]]))
    for country in state["regions"]:
        fig.add_trace(
            go.Scatter(name=country,
                       x=data.select(
                           country, data.indicators[state["indicator"]]).date,
                       y=data.select(
                           country, data.indicators[state["indicator"]])[state["indicator"]]
                       )
        )

    return fig


@app.callback(
    Output("map", "figure"),
    [Input("memory", "data")]
)
def draw_map(state):

    indicator_name = state["indicator"]
    data_selected = data.latest_data(
        data.indicators[state["indicator"]])

    fig_map.update_traces(
        locations=data_selected["iso3"],
        z=data_selected[indicator_name],
        text=data_selected["region"],
        zmax=data_selected[indicator_name]
        .replace([np.inf, -np.inf], np.nan)
        .max()
        * 0.3,
    )

    fig_map.update_layout(
        mapbox_zoom=state["bbox"]["zoom"],
        mapbox_center=state["bbox"]["center"],
    )

    fig_map.layout.uirevision = True

    return fig_map


fig_timeline = timeline()

graph_timeline = dcc.Graph(
    figure=fig_timeline,
    id="timeline",
    config={
        "displayModeBar": False},
    style={
        "height": str(
            parser.getint(
                "layout",
                "height_first_row")) +
        "vh",
        "width": "100%"}
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
            children=[graph_timeline]
        ),
        dcc.Tab(
            label="map",
            value="map_tab",
            className="custom-tab",
            selected_className="custom-tab--selected",
            children=[tab_map]
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
        xs=12,
        style={'margin-bottom': '7px'})
]
row_2 = controller()


def set_layout():
    return dbc.Container(
        children=[
            dbc.Row(row_1, no_gutters=True, justify="center"),
            dbc.Row(row_2, no_gutters=False, justify="center"),
            dbc.Row(comparsion, no_gutters=False, justify="center"),

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
