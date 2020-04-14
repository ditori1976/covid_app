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

# configuration
parser = ConfigParser()
parser.read("settings.ini")

config = Config()
style = Style()

region = "world"

# initialize data load
data = DataLoader(parser)
indicators = data.indicators()

# layout
layout_timeline = style.layout.copy()
layout_timeline["height"] = parser.getint("layout", "height_first_row")


# dropdown

def dropdown_options(indicators):
    options = []
    for i, j in indicators.items():
        options.append({"label": j["name"], "value": i})

    return options


# function for options
dropdown = dcc.Dropdown(
    id="indicator-selected",
    value="cases",
    style={"width": "100%", "margin": 0, "padding": 0},
    options=dropdown_options(indicators),
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
                    html.Div(id="map", style={"height": parser.getint(
                        "layout", "height_first_row")}),
                    lg=5,
                    md=10,
                    xs=11,
                ),
                dbc.Col(
                    html.Div(id="timeline",
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
                            id="region-selected",
                            value="World",
                            children=[
                                dcc.Tab(
                                    label=information["name"],
                                    value=region) for region, information in data.regions.items()
                            ]
                        )
                    ]
                )

            ],
            justify="center"
        )
    ]
)


app.layout = html.Div([body])


@app.callback(
    [
        Output("map", "children"),
        Output("timeline", "children"),
    ],
    [Input("indicator-selected", "value"),
     Input("region-selected", "value")],
)
def update_figure(selected_indicator, selected_region):

    # map data
    region = selected_region

    map_trace = go.Choroplethmapbox(
        colorscale="BuPu",
        geojson=data.countries,
        locations=data.per_country_max["iso3"],
        z=data.per_country_max[indicators[selected_indicator]["name"]],
        text=data.per_country_max["region"],
        zmin=0,
        zmax=data.per_country_max[indicators[selected_indicator]["name"]].replace(
            [np.inf, -np.inf], np.nan).max()*0.3,
        marker={"line": {"color": "rgb(180,180,180)", "width": 0.5}},
        colorbar={"thickness": 10, "len": 0.5,
                  "x": 0.85, "y": 0.7, "outlinewidth": 0, },
    )
    layout_map = go.Layout(
        mapbox_style="mapbox://styles/dirkriemann/ck88smdb602qa1iljg6kxyavd",
        mapbox_zoom=data.regions[region]["zoom"],
        height=parser.getint("layout", "height_first_row"),
        mapbox_center=data.regions[region]["center"],
        mapbox_accesstoken=config.mapbox,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
    )

    fig_map = go.Figure(data=[map_trace], layout=layout_map,)

    # timeline
    scatter = go.Scatter(
        x=data.timeseries.loc[data.timeseries.continent == region].date, y=data.timeseries.loc[data.timeseries.continent == region,
                                                                                               indicators[selected_indicator]["name"]],
    )
    fig_timeline = go.Figure(layout=layout_timeline, data=[scatter])
    fig_timeline.update_layout(plot_bgcolor="white",)

    return dcc.Graph(figure=fig_map), dcc.Graph(figure=fig_timeline)


application = app.server
if __name__ == "__main__":
    application.run(debug=True, port=config.port, host=config.host)
