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

data.jhu()
data.geonames()

# prepare data
data_norm = pd.merge(
    data.deaths.sort_values(["region", "date"]),
    data.country_info[["iso_alpha", "population", "continent"]],
    left_on="iso3",
    right_on="iso_alpha",
    how="inner",
).drop(columns=["iso3", "iso2", "code3"])
data_norm = pd.merge(
    data_norm,
    data.confirmed.sort_values(["region", "date"])[["date", "confirmed", "iso3"]],
    left_on=["iso_alpha", "date"],
    right_on=["iso3", "date"],
    how="inner",
).drop(columns=["iso3"])
data_norm = pd.merge(
    data_norm,
    data.recovered.sort_values(["region", "date"])[["date", "recovered", "iso3"]],
    left_on=["iso_alpha", "date"],
    right_on=["iso3", "date"],
    how="inner",
).drop(columns=["iso3"])

data_norm.loc[:, "cases/1M capita"] = (
    data_norm.confirmed / data_norm.population * 1000000
).round(0)
data_norm.loc[:, "deaths/1M capita"] = (
    data_norm.deaths / data_norm.population * 1000000
).round(0)
data_norm.loc[:, "recovered/1M capita"] = (
    data_norm.recovered / data_norm.population * 1000000
).round(0)

data_norm.rename(columns={"confirmed": "cases"}, inplace=True)


timeseries = data_norm.groupby(["continent", "date"]).sum()

world = timeseries.groupby("date").sum()
world = pd.DataFrame(
    index=[pd.Series(data="world").repeat(len(world.index)), world.index],
    data=world.values,
    columns=world.columns,
)

timeseries = pd.concat([timeseries, world])


per_country_max = data_norm[data_norm.date == data_norm.date.max()]
per_country_max = per_country_max[per_country_max.cases > min_cases].sort_values(
    "cases"
)

# layout
layout = go.Layout(yaxis=dict(type="linear", autorange=True))
layout_log = go.Layout(yaxis=dict(type="linear", autorange=True))

# figures
fig = go.Figure(layout=layout)
fig.update_layout(
    legend_orientation="h",
    legend=dict(x=0, y=0.95),
    plot_bgcolor="white",
    autosize=True,
    height=400,
)

fig_cc = go.Figure(
    data=[go.Bar(x=per_country_max.region, y=per_country_max.loc[:, "cases"],)],
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
    "height": "4vh",
    "padding-top": "1vh",
}

style_center = {
    "text-align": "center",
    "display": "flex",
    "justify-content": "center",
    "align-items": "center",
    "verticalAlign": "middle",
}

style_dropdown_div = style_center
style_dropdown_div["font-size"] = "2.5vh"

# create app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


dropdown_kind = dcc.Dropdown(
    id="value-selected",
    value="cases",
    options=[
        {"label": "Cases/Mio. capita ", "value": "cases",},
        {"label": "Deaths/Mio. capita ", "value": "deaths",},
    ],
    style=style_dropdown,
    searchable=False,
    optionHeight=70,
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
                                    width="100%",
                                ),
                                lg=2,
                                md=2,
                                xs=2,
                            ),
                            dbc.Col(
                                html.H1("COVID-19"),
                                lg=5,
                                md=8,
                                xs=10,
                                style=style_center,
                            ),
                            dbc.Col(
                                html.Div(
                                    id="select-indicator",
                                    children=[dropdown_kind],
                                    style=style_dropdown_div,
                                ),
                                lg=5,
                                md=10,
                                xs=10,
                            ),
                        ],
                        justify="center",
                    ),
                    xl=6,
                    lg=8,
                    md=10,
                    xs=12,
                )
            ],
            justify="center",
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        children=[
                            "This site is to inform about the latested developments regarding the spread of COVID-19. The data being used is provided by ECDC. "
                        ],
                        style={"margin-top": "2vh"},
                    ),
                    lg=6,
                    md=10,
                    xs=10,
                )
            ],
            justify="center",
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        id="div-main-map",
                        children=[dcc.Graph(id="main-map")],
                        style={"padding": 0, "margin": 0},
                    ),
                    xl=6,
                    lg=8,
                    md=10,
                    xs=12,
                )
            ],
            justify="center",
        ),
        dbc.Row(
            [dbc.Col(html.Div(html.H4("Most affected countries")), lg=6, md=10, xs=10)],
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
                    xl=6,
                    lg=8,
                    md=10,
                    xs=12,
                )
            ],
            justify="center",
        ),
        dbc.Row(
            [dbc.Col(html.Div(html.H4("Timeline")), lg=6, md=10, xs=10)],
            justify="center",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            id="div-timeline",
                            children=[dcc.Graph(id="timeline", figure=fig_cc),],
                        )
                    ],
                    xl=6,
                    lg=8,
                    md=10,
                    xs=12,
                ),
            ],
            justify="center",
        ),
    ]
)

app.layout = html.Div([body])


@app.callback(
    [
        dash.dependencies.Output("main-map", "figure"),
        dash.dependencies.Output("timeline", "figure"),
        dash.dependencies.Output("ranking", "figure"),
    ],
    [dash.dependencies.Input("value-selected", "value")],
)
def update_figure(selected):

    dff = per_country_max

    def config(text):
        if text == "cases":
            return "cases/1M capita", 2000
        elif text == "deaths":
            return "deaths/1M capita", 100
        else:
            return "cases/1M capita", 2000

    title, limit = config(selected)
    trace = go.Choroplethmapbox(
        geojson=data.countries,
        locations=dff["iso_alpha"],
        z=dff[title],
        text=dff["region"],
        zmin=0,
        zmax=limit,
        marker={"line": {"color": "rgb(180,180,180)", "width": 0.5}},
        colorbar={"thickness": 20, "len": 0.6, "x": 0.8, "y": 0.6, "outlinewidth": 0},
    )

    scatter = go.Scatter(
        x=timeseries.loc["world"].index, y=timeseries.loc["world", selected],
    )

    bar = go.Bar(x=per_country_max.region, y=per_country_max.loc[:, selected],)

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
