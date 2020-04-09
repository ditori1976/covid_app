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
from configparser import ConfigParser

# configuration
parser = ConfigParser()
parser.read("settings.ini")

config = Config()
style = Style()


# initialize data load
data = DataLoader(parser)

# timeline
scatter = go.Scatter(
    x=data.timeseries.loc["world"].index, y=data.timeseries.loc["world", "cases"],
)
layout_timeline = style.layout.copy()
layout_timeline["height"] = parser.getint("layout", "height_first_row")
fig_timeline = go.Figure(layout=layout_timeline, data=[scatter])
fig_timeline.update_layout(plot_bgcolor="white",)

# dropdown
dropdown = dcc.Dropdown(
    id="value-selected",
    value="cases",
    style={"width": "100%", "margin": 0, "padding": 0},
    options=[
        {"label": "cases/1M capita", "value": "cases"},
        {"label": "deaths/1M capita", "value": "deaths"},
        {"label": "recovered/1M capita", "value": "recovered"},
    ],
)

# map


# map data
map_trace = go.Choroplethmapbox(
    colorscale="Oranges",
    geojson=data.countries,
    locations=data.per_country_max["iso_alpha"],
    z=data.per_country_max["cases/1M capita"],
    text=data.per_country_max["region"],
    zmin=0,
    zmax=2000,
    marker={"line": {"color": "rgb(180,180,180)", "width": 0.5}},
    colorbar={"thickness": 20, "len": 0.6,
              "x": 0.8, "y": 0.6, "outlinewidth": 0, },
)

layout_map = go.Layout(
    mapbox_style="mapbox://styles/dirkriemann/ck88smdb602qa1iljg6kxyavd",
    mapbox_zoom=0.2,
    height=parser.getint("layout", "height_first_row"),
    mapbox_center={"lat": 25, "lon": 0},
    mapbox_accesstoken=config.mapbox,
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
)
# create map
fig_map = go.Figure(data=[map_trace], layout=layout_map,)


# create app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


header = dbc.Row(
    [
        dbc.Col(
            html.Img(src=app.get_asset_url("logo.png"),
                     height="auto", width="70%",),
            lg=3,
            md=4,
            xs=2,
            style=style.style_center,
        ),
        dbc.Col(html.H1("COVID-19"), lg=9, md=8,
                xs=7, style=style.style_center,),
    ]
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
                    lg=2,
                    md=6,
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
                             children=[dcc.Graph(figure=fig_map)]),
                    lg=4,
                    md=10,
                    xs=12,
                ),
                dbc.Col(
                    html.Div(
                        id="div-timeline",
                        children=[
                            dcc.Graph(id="timeline", figure=fig_timeline), ],
                    ),
                    lg=7,
                    md=10,
                    xs=12,
                ),
            ],
            style={"padding-top": 30},
            justify="center",
        ),
    ]
)


app.layout = html.Div([body])

application = app.server
if __name__ == "__main__":
    application.run(debug=True, port=config.port, host=config.host)
