#!/usr/bin/env python3

"""
Author: Dirk Riemann, 2020

COVID-19 dashboard
based on dash package,
using plotly graph objects
and mapbox API for mapping

development/debuggin mode
NOT FOR PRODUCTION
"""

# import packages
import os
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

import pandas as pd
import plotly.graph_objects as go

from tools import DataLoader

if "HOST" in os.environ:
    host = os.environ.get("HOST")
else:
    host = "127.0.0.1"

if "PORT" in os.environ:
    port = os.environ.get("PORT")
else:
    port = "8080"


MAPBOX = os.environ.get("MAPBOX")

min_cases = 20000

# load data
def get_data():
    global data
    data = DataLoader()


get_data()

# prepare data
all_infections_deaths = (
    data.ecdc_raw.iloc[:, [0, 4, 5]].groupby(["dateRep"]).sum().cumsum()
)
per_country_max = data.per_country[data.per_country.iloc[:, 0] > min_cases]
per_country_max = per_country_max.sort_values("cases")

# layout
layout = go.Layout(yaxis=dict(type="linear", autorange=True))
layout_log = go.Layout(yaxis=dict(type="linear", autorange=True))

# figures
fig = go.Figure(
    data=[
        go.Scatter(
            x=all_infections_deaths.index, y=all_infections_deaths.loc[:, "cases"],
        )
    ],
    layout=layout,
)
fig.update_layout(
    legend_orientation="h",
    legend=dict(x=0, y=0.95),
    plot_bgcolor="white",
    autosize=True,
    height=400,
)

fig_cc = go.Figure(
    data=[go.Bar(x=per_country_max.index, y=per_country_max.loc[:, "cases"],)],
    layout=layout,
)
fig_cc.update_layout(
    legend_orientation="h",
    legend=dict(x=0, y=0.95),
    plot_bgcolor="white",
    autosize=True,
    height=400,
)

style_dropdown = {
    "width": "100%",
    "border-width": 0,
    "background-color": "#faf9f7",
    # "text-align": "center",
    # "padding": "20 0",
    "display": "inline-block",
    "verticalAlign": "middle",
}

# create app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.themes.GRID])

app.layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.Img(src=app.get_asset_url("logo.png"), height=50),
                    width=1,
                    style={"text-align": "center"},
                ),
                dbc.Col(html.H1("COVID-19"), width=4, lg=3, style={"margin-top": 10}),
                dbc.Col(
                    html.Div(
                        id="select-indicator",
                        children=[
                            dcc.Dropdown(
                                id="value-selected",
                                value="cases",
                                options=[
                                    {"label": "Cases/Mio. capita ", "value": "cases"},
                                    {"label": "Deaths/Mio. capita ", "value": "deaths"},
                                ],
                                style=style_dropdown,
                            )
                        ],
                        style={"display": "flex"},
                    ),
                    width=6,
                    lg=2,
                    style={"margin-top": 20},
                ),
            ],
            justify="center",
            no_gutters=True,
            style={"margin-top": 5},
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        id="div-main-map",
                        children=[dcc.Graph(id="main-map")]  # , style={ "padding": 0},
                        # style={ "padding": 0},
                    ),
                    width=12,
                    lg=6,
                )
            ],
            justify="center",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            id="div-timeline",
                            children=[dcc.Graph(id="timeline", figure=fig),],
                        )
                    ],
                    width=12,
                    lg=6,
                )
            ],
            justify="center",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            id="div-ranking",
                            children=[dcc.Graph(id="ranking", figure=fig_cc),],
                        )
                    ],
                    width=12,
                    lg=6,
                ),
            ],
            justify="center",
        ),
    ]
)


@app.callback(
    [
        dash.dependencies.Output("main-map", "figure"),
        dash.dependencies.Output("timeline", "figure"),
        dash.dependencies.Output("ranking", "figure"),
    ],
    [dash.dependencies.Input("value-selected", "value")],
)
def update_figure(selected):

    dff = data.summary_country

    def config(text):
        if text == "cases":
            return "Cases/Mio. capita", 1000
        elif text == "deaths":
            return "Deaths/Mio. capita", 100
        else:
            return "Cases/Mio. capita", 1000

    title, limit = config(selected)
    trace = go.Choroplethmapbox(
        geojson=data.countries,
        locations=dff["iso_alpha"],
        z=dff[title],
        text=dff["country"],
        zmin=0,
        zmax=limit,
        marker={"line": {"color": "rgb(180,180,180)", "width": 0.5}},
        colorbar={"thickness": 20, "len": 0.6, "x": 0.8, "y": 0.6, "outlinewidth": 0},
    )

    scatter = go.Scatter(
        x=all_infections_deaths.index, y=all_infections_deaths.loc[:, selected],
    )

    bar = go.Bar(x=per_country_max.index, y=per_country_max.loc[:, selected],)

    return [
        {
            "data": [trace],
            "layout": go.Layout(
                height=500,
                mapbox_style="mapbox://styles/dirkriemann/ck88smdb602qa1iljg6kxyavd",
                mapbox_zoom=0.5,
                mapbox_center={"lat": 25, "lon": 0},
                mapbox_accesstoken=MAPBOX,
                # margin={"r": 0, "t": 0, "l": 0, "b": 0},
            ),
        },
        {"data": [scatter]},
        {"data": [bar]},
    ]


application = app.server
if __name__ == "__main__":
    application.run(debug=True, port=port, host=host)
