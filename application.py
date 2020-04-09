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

# configuration
parser = ConfigParser()
parser.read("settings.ini")

config = Config()
style = Style()

values_titles = {"cases": "cases/1M capita",
                 "deaths": "deaths/1M capita",
                 "recovered": "recovered/1M capita"}


# initialize data load
data = DataLoader(parser)

# layout
layout_timeline = style.layout.copy()
layout_timeline["height"] = parser.getint("layout", "height_first_row")


# dropdown
dropdown = dcc.Dropdown(
    id="value-selected",
    value="cases",
    style={"width": "100%", "margin": 0, "padding": 0},
    options=[
        {"label": values_titles["cases"], "value": "cases"},
        {"label": values_titles["deaths"], "value": "deaths"},
        {"label": values_titles["recovered"], "value": "recovered"},
    ],
)

# create app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


header = dbc.Row(
    [
        dbc.Col(
            html.Img(src=app.get_asset_url("logo.png"),
                     height="auto", width="70%"),
            lg=3,
            md=3,
            xs=2,
            style=style.style_center,
        ),
        dbc.Col(html.H1("COVID-19"), lg=9, md=8,
                xs=7, style=style.style_center,),
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
                        id="select-indicator",
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
                    html.Div(id="div-map",
                             children=[dcc.Graph(id="map")]),
                    lg=5,
                    md=10,
                    xs=12,
                ),
                dbc.Col(
                    html.Div(
                        id="div-timeline",
                        children=[
                            dcc.Graph(id="timeline"), ],
                    ),
                    lg=5,
                    md=10,
                    xs=12,
                ),
            ],
            style={"padding-top": parser.getint("layout", "spacer")},
            justify="center",
        ),
    ]
)


app.layout = html.Div([body])


@app.callback(
    [
        dash.dependencies.Output("map", "figure"),
        dash.dependencies.Output("timeline", "figure"),
    ],
    [dash.dependencies.Input("value-selected", "value")],
)
def update_figure(selected):

    # map data

    map_trace = go.Choroplethmapbox(
        colorscale="BuPu",
        geojson=data.countries,
        locations=data.per_country_max["iso_alpha"],
        z=data.per_country_max[values_titles[selected]],
        text=data.per_country_max["region"],
        zmin=0,
        zmax=data.per_country_max[values_titles[selected]].replace(
            [np.inf, -np.inf], np.nan).max()*0.3,
        marker={"line": {"color": "rgb(180,180,180)", "width": 0.5}},
        colorbar={"thickness": 10, "len": 0.5,
                  "x": 0.85, "y": 0.7, "outlinewidth": 0, },
    )

    layout_map = go.Layout(
        mapbox_style="mapbox://styles/dirkriemann/ck88smdb602qa1iljg6kxyavd",
        mapbox_zoom=0.2,
        height=parser.getint("layout", "height_first_row"),
        mapbox_center={"lat": 35, "lon": 0},
        mapbox_accesstoken=config.mapbox,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
    )

    fig_map = go.Figure(data=[map_trace], layout=layout_map,)

    # timeline
    scatter = go.Scatter(
        x=data.timeseries.loc["world"].index, y=data.timeseries.loc["world", selected],
    )
    fig_timeline = go.Figure(layout=layout_timeline, data=[scatter])
    fig_timeline.update_layout(plot_bgcolor="white",)
    return fig_map, fig_timeline


application = app.server
if __name__ == "__main__":
    application.run(debug=True, port=config.port, host=config.host)
