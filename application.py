#!/usr/bin/env python3

"""
Author: Dirk Riemann, 2020

responsive map
based on dash package
with bootstrap (responsive) layout
and Mapbox map

development/debuggin mode
NOT FOR PRODUCTION
"""

# import packages
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import dash

import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.graph_objects as go
from tools import DataLoader, Config, Style
import pandas as pd
import numpy as np
from configparser import ConfigParser
from dash.dependencies import Input, State, Output
import json
from datetime import date, datetime, timedelta

# UPDADE_INTERVAL = 15
# configuration
parser = ConfigParser()
parser.read("settings.ini")

config = Config()
style = Style()

region = parser.get("data", "region")
continent = parser.get("data", "continent")


def get_new_data():

    """Updates the global variable 'data' with new data"""
    global data, latest_update

    data = DataLoader(parser)
    print("Data updated at " + datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
    latest_update = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")


def get_new_data_every(period=parser.getint("data", "update_interval")):
    """Update the data every 'period' seconds"""
    while True:
        get_new_data()
        time.sleep(period)


get_new_data()

indicators = data.indicators()

# layout
layout_timeline = style.layout.copy()
layout_timeline["height"] = parser.getint("layout", "height_first_row") - 50
layout_timeline["plot_bgcolor"] = "white"

# dropdown
def dropdown_options(indicators):
    options = []
    for i, j in indicators.items():
        options.append({"label": j["name"], "value": i})

    return options


# function for dropdown selector
dropdown = dcc.Dropdown(
    id="indicator-selected",
    value=parser.get("data", "init_indicator"),
    style={"width": "100%", "margin": 0, "padding": 0},
    options=dropdown_options(indicators),
)

# title
def format_title(region, indicator):
    # use latest_data (need to include continents)

    data_selected = data.select(region, indicators[indicator])
    regions = data.regions
    if region in list(data.regions.keys()):
        region = data.regions[region]["name"]
    if region == "World":
        region = "the world"

    title = "{1:.{0}f} {2} in {3} on {4}".format(
        indicators[indicator]["digits"],
        data_selected.loc[
            data_selected.date == data_selected.date.max(),
            indicators[indicator]["name"],
        ].values[0],
        indicators[indicator]["name"],
        region,
        str(data_selected.date.max().strftime("%d %b %Y")),
    )

    return title


# map
layout_map = go.Layout(
    mapbox_style="mapbox://styles/dirkriemann/ck88smdb602qa1iljg6kxyavd",
    height=parser.getint("layout", "height_first_row"),
    mapbox_accesstoken=config.mapbox,
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
)
map_trace = go.Choroplethmapbox(
    colorscale="BuPu",
    geojson=data.countries,
    zmin=0,
    marker={"line": {"color": "rgb(180,180,180)", "width": 0.5}},
    colorbar={"thickness": 10, "len": 0.4, "x": 0, "y": 0.3, "outlinewidth": 0,},
)

fig_map = go.Figure(data=[map_trace], layout=layout_map)


def update_map(fig, indicator, continent):
    indicator_name = indicators[indicator]["name"]
    data_selected = data.latest_data(indicators[indicator])

    fig.update_traces(
        locations=data_selected["iso3"],
        z=data_selected[indicator_name],
        text=data_selected["region"],
        zmax=data_selected[indicator_name].replace([np.inf, -np.inf], np.nan).max()
        * 0.3,
    )
    fig.update_layout(
        mapbox_center=data.regions[continent]["center"],
        mapbox_zoom=data.regions[continent]["zoom"],
    )
    return fig


fig_map = update_map(fig_map, parser.get("data", "init_indicator"), continent)

# timeline
timeline_trace = go.Bar()

fig_timeline = go.Figure(data=[timeline_trace], layout=layout_timeline)


def update_timeline(fig, indicator, region):
    indicator_name = indicators[indicator]["name"]
    data_selected = data.select(region, indicators[indicator])
    fig.update_traces(x=data_selected.date, y=data_selected[indicator_name])

    return fig


fig_timeline = update_timeline(
    fig_timeline, parser.get("data", "init_indicator"), region
)

# create app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

header = dbc.Row(
    [
        dbc.Col(
            html.Img(src=app.get_asset_url("logo.png"), height="auto", width="70%"),
            lg=3,
            md=3,
            xs=2,
            style=style.style_center,
        ),
        dbc.Col(html.H1("COVID-19"), lg=9, md=8, xs=7, style=style.style_center,),
    ],
    justify="center",
)


body = html.Div(
    [
        dbc.Row(
            [
                dbc.Col([header], lg=3, md=6, xs=12),
                dbc.Col(
                    html.Div(
                        id="selector",
                        children=[dropdown],
                        style={"width": "100%", "margin": 0, "padding": 0},
                    ),
                    xl=3,
                    lg=4,
                    md=5,
                    xs=10,
                    style=style.style_center,
                ),
            ],
            justify="center",
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        style={"height": parser.getint("layout", "height_first_row")},
                        children=[
                            dcc.Graph(
                                id="map",
                                figure=fig_map,
                                config={"displayModeBar": False},
                            )
                        ],
                    ),
                    lg=5,
                    md=10,
                    xs=11,
                ),
                dbc.Col(
                    html.Div(
                        children=[
                            html.Div(
                                children=[
                                    html.P(
                                        continent,
                                        id="selected-series",
                                        style={"display": "None"},
                                    ),
                                    html.P(
                                        region,
                                        id="title-region",
                                        style={"display": "None"},
                                    ),
                                    html.H5([], id="title"),
                                ],
                            ),
                            html.Div(
                                children=[
                                    dcc.Graph(
                                        id="timeline",
                                        figure=fig_timeline,
                                        config={"displayModeBar": False},
                                    )
                                ]
                            ),
                        ]
                    ),
                    lg=5,
                    md=10,
                    xs=11,
                ),
            ],
            style={"padding-top": parser.getint("layout", "spacer")},
            justify="center",
        ),
        dbc.Row(
            [
                html.Div(
                    [
                        dcc.Tabs(
                            id="continent-selected",
                            value=continent,
                            children=[
                                dcc.Tab(label=information["name"], value=region)
                                for region, information in data.regions.items()
                            ],
                        )
                    ]
                )
            ],
            justify="center",
        ),
        dbc.Row(id="update", children=[], justify="center",),
    ]
)


app.layout = html.Div([body])


@app.callback(
    [Output("title-region", "children"), Output("continent-selected", "value")],
    [Input("map", "clickData")],
)
def set_title_region(selected_region):

    continent = parser.get("data", "continent")
    region = parser.get("data", "region")

    if selected_region:
        region = selected_region["points"][0]["text"]
        # implement more robust association of region > continent
        continent = (
            data.latest_data("cases")
            .loc[data.latest_data("cases").region == region, "continent"]
            .values[0]
        )

    return [region], continent


@app.callback(
    [Output("selected-series", "children"),],
    [Input("title-region", "children"), Input("continent-selected", "value")],
)
def select_display(selected_region, selected_continent):
    ctx = dash.callback_context

    trigger = ctx.triggered[0]["value"]
    trigger_id = ctx.triggered[0]["prop_id"]

    if type(trigger) == list:
        trigger = trigger.pop()

    return [trigger]


@app.callback(
    [
        Output("title", "children"),
        Output("map", "figure"),
        Output("timeline", "figure"),
        Output("update", "children"),
    ],
    [Input("selected-series", "children"), Input("indicator-selected", "value"),],
)
def select_display(selected_region, selected_indicator):

    continent = data.timeseries[
        data.timeseries.region == selected_region
    ].continent.max()

    return (
        [format_title(selected_region, selected_indicator)],
        update_map(fig_map, selected_indicator, continent),
        update_timeline(fig_timeline, selected_indicator, selected_region),
        [html.P(latest_update, style={"font-size": 8, "color": "grey"})],
    )


# executor = ThreadPoolExecutor(max_workers=1)
# executor.submit(update_data)


application = app.server


def start_multi():
    executor = ProcessPoolExecutor(max_workers=1)
    executor.submit(get_new_data_every)


if __name__ == "__main__":

    # start_multi()
    application.run(debug=True, port=config.port, host=config.host)
