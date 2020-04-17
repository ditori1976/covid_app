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

# configuration
parser = ConfigParser()
parser.read("settings.ini")

config = Config()
style = Style()

region = "World"
continent = region

# initialize data load
data = DataLoader(parser)
indicators = data.indicators()

# layout
layout_timeline = style.layout.copy()
layout_timeline["height"] = parser.getint("layout", "height_first_row") - 30


# dropdown
def dropdown_options(indicators):
    options = []
    for i, j in indicators.items():
        options.append({"label": j["name"], "value": i})

    return options


# function for options
dropdown = dcc.Dropdown(
    id="indicator-selected",
    value="cases_capita",
    style={"width": "100%", "margin": 0, "padding": 0},
    options=dropdown_options(indicators),
)
layout_map = go.Layout(
    mapbox_style="mapbox://styles/dirkriemann/ck88smdb602qa1iljg6kxyavd",
    height=parser.getint("layout", "height_first_row"),
    mapbox_accesstoken=config.mapbox,
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
)
fig_map = go.Figure(data=[], layout=layout_map)  # , data=[map_trace],


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
                        children=[dcc.Graph(id="map", figure=fig_map)],
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
                                    html.H3(
                                        continent,
                                        id="title-continent",
                                        style={"display": "None"},
                                    ),
                                    html.H4(region, id="title-region"),
                                ],
                            ),
                            html.Div(id="timeline"),
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
                            value="World",
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
    ]
)


app.layout = html.Div([body])


"""@app.callback(
    [Output("title-region", "children")],
    [Input("map", "clickData")],
)
def set_title_region(selected_region):
    
    if selected_region:
        region = selected_region["points"][0]["text"]
        continent = data.latest_data.loc[
            data.latest_data.region == region, "continent"
        ].values[0]
    else:
        region = "World"

    return [region]"""


"""@app.callback(
    [Output("title-continent", "children")],
    [Input("continent-selected", "value"), Input("title-region", "children")],
)
def set_title_continent(selected_continent, selected_region):
    print(selected_continent, selected_region)
    if selected_continent != selected_region:
        continent = data.latest_data.loc[
            data.latest_data.region == selected_region, "continent"
        ].values[0]
        print(continent, selected_region)
    else:
        continent = selected_continent

    # continent = selected_continent

    return [continent]"""

"""
@app.callback(
    [Output("title-continent", "children")], [Input("continent-selected", "value")],
)
def set_title_continent(selected_continent):
    print(selected_continent)
  return [selected_continent]"""


@app.callback(
    [
        Output("map", "figure"),
        Output("timeline", "children"),
        Output("title-region", "children"),
    ],
    [
        Input("indicator-selected", "value"),
        Input("title-continent", "children"),
        # Input("title-region", "children"),
        Input("continent-selected", "value"),
        Input("map", "clickData"),
    ],
)
def update_figure(selected_indicator, selected_continent, cont, map):
    ctx = dash.callback_context

    ctx_msg = json.dumps(
        {"states": ctx.states, "triggered": ctx.triggered, "inputs": ctx.inputs},
        indent=2,
    )

    continent = selected_continent
    region = continent

    print(ctx.triggered)
    first_trigger = ctx.triggered[0]

    latest_data = data.latest_data()

    if first_trigger["prop_id"] == "map.clickData":
        region = first_trigger["value"]["points"][0]["text"]
        continent = latest_data.loc[latest_data.region == region, "continent"].values[0]
    if first_trigger["prop_id"] == "continent-selected.value":
        continent = first_trigger["value"]
        region = continent

    print(region, continent)

    # print(region, continent, selected_continent_tab)

    map_trace = go.Choroplethmapbox(
        colorscale="BuPu",
        geojson=data.countries,
        locations=latest_data["iso3"],
        z=latest_data[indicators[selected_indicator]["name"]],
        text=latest_data["region"],
        zmin=0,
        zmax=latest_data[indicators[selected_indicator]["name"]]
        .replace([np.inf, -np.inf], np.nan)
        .max()
        * 0.3,
        marker={"line": {"color": "rgb(180,180,180)", "width": 0.5}},
        colorbar={"thickness": 10, "len": 0.5, "x": 0.85, "y": 0.7, "outlinewidth": 0,},
    )
    layout_map = go.Layout(
        mapbox_style="mapbox://styles/dirkriemann/ck88smdb602qa1iljg6kxyavd",
        mapbox_zoom=data.regions[continent]["zoom"],
        height=parser.getint("layout", "height_first_row"),
        mapbox_center=data.regions[continent]["center"],
        mapbox_accesstoken=config.mapbox,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
    )

    fig_map = go.Figure(data=[map_trace], layout=layout_map)

    # timeline
    scatter = go.Scatter(
        x=data.timeseries.loc[data.timeseries.region == region].date,
        y=data.timeseries.loc[
            data.timeseries.region == region, indicators[selected_indicator]["name"]
        ],
    )
    fig_timeline = go.Figure(layout=layout_timeline, data=[scatter])
    fig_timeline.update_layout(plot_bgcolor="white",)

    return (fig_map, dcc.Graph(figure=fig_timeline), [region])


application = app.server
if __name__ == "__main__":
    application.run(debug=True, port=config.port, host=config.host)
