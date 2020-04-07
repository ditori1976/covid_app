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
import os
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.graph_objects as go
from tools import DataLoader

# configuration
if "HOST" in os.environ:
    host = os.environ.get("HOST")
else:
    host = "127.0.0.1"

if "PORT" in os.environ:
    port = os.environ.get("PORT")
else:
    port = "8080"

MAPBOX = os.getenv("MAPBOX")

# example data
data = DataLoader().data

# define layouts
layout = dict(margin=dict(l=0, r=0, b=0, t=0, pad=0), dragmode="select")

style_center = {
    "text-align": "center",
    "display": "flex",
    "justify-content": "center",
    "align-items": "center",
    "verticalAlign": "middle",
    "margin": 0,
    "padding":0
}

dropdown = dcc.Dropdown(
    id="value-selected",
    value="entry",
    options=[
        {"label": "entry", "value": "entry"},
        {"label": "long entry", "value": "long_entry"},
        {"label": "very very long entry", "value": "very_long_entry"},
    ],
)

mapbox_config = dict(
    accesstoken=MAPBOX,
    center=dict(
        lat=(max(data["lat"]) - min(data["lat"])) / 2 + min(data["lat"]),
        lon=(max(data["lon"]) - min(data["lon"])) / 2 + min(data["lon"]),
    ),
    zoom=6,
)

layout_map = layout.copy()
layout_map["mapbox"] = mapbox_config

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# create map
main_map = go.Figure(
    data=go.Scattermapbox(
        lon=data["lon"],
        lat=data["lat"],
        text=data[["name", "population"]],
        mode="markers",
        marker=dict(size=9, color="red"),
    ),
    layout=layout_map,
)

body = html.Div(
    [
        dbc.Row(
            [

                dbc.Col(
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Img(
                                    src=app.get_asset_url("logo.png"),
                                    height="auto",
                                    width="80%"
                                    ),
                                lg=3,
                                md=4,
                                xs=2,
                                
                                style=style_center
                            ),
                            dbc.Col(
                                html.H1("COVID-19"),
                                lg=9,
                                md=8,
                                xs=7,
                                style=style_center
                            )                           
                        ]
                        
                    ),
                        
                    lg=3,
                    md=6,
                    xs=12,
                ),
                dbc.Col(
                    html.Div(id="select-indicator", children=[dropdown],),
                    lg=2,
                    md=6,
                    xs=10,
                ),
            ],
            justify="center"
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(id="div-map", children=[dcc.Graph(figure=main_map)]),
                    lg=4,
                    md=12,
                    xs=12
                )
            ],
            style={"padding-top":30}
        ),
        
    ]
)

# create app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([body])

application = app.server
if __name__ == "__main__":
    application.run(debug=True, port=port, host=host)
