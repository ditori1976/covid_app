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
import dash_table
import datetime
import pandas as pd
import plotly.graph_objects as go
from urllib.request import urlopen
import json
import requests
import sys
import io

dirname = os.path.dirname(__file__)

if "HOST" in os.environ:
    host = os.environ.get("HOST")
else:
    host = "127.0.0.1"

MAPBOX = os.environ.get("MAPBOX")

with urlopen(
    "https://raw.githubusercontent.com/mapbox/geojson-vt-cpp/master/data/countries.geojson"
) as response:
    countries = json.load(response)

url = "https://opendata.ecdc.europa.eu/covid19/casedistribution/csv"
s = requests.get(url).content
ecdc_raw = pd.read_csv(io.StringIO(s.decode('utf-8')))

ecdc_raw.rename(columns={'countriesAndTerritories': 'country'}, inplace=True)
ecdc_raw.iloc[:, 6].replace(
    to_replace=r'_', value=' ', regex=True, inplace=True)
ecdc_raw.loc[:, 'country'].replace(
    to_replace=r'Russia', value='Russian Federation', regex=True, inplace=True)

print(ecdc_raw.head())

countries_codes = pd.read_csv(dirname + '/data/country_codes.csv')

countries_codes.rename(columns={'name': 'country',
                                'alpha-3': 'iso_alpha',
                                'alpha-2': 'geoId',
                                'country-code': 'iso_num'}, inplace=True)
countries_codes.drop(columns=['iso_3166-2', 'intermediate-region', 'region-code',
                              'sub-region-code', 'intermediate-region-code'], inplace=True)

countries_codes.loc[countries_codes.geoId == 'KP', 'country'] = 'North Korea'
countries_codes.loc[countries_codes.geoId == 'KR', 'country'] = 'South Korea'
countries_codes.loc[countries_codes.geoId == 'VN', 'country'] = 'Vietnam'
countries_codes.loc[countries_codes.geoId == 'IR', 'country'] = 'Iran'
countries_codes.loc[countries_codes.geoId ==
                    'GB', 'country'] = 'United Kingdom'

countries_un = pd.read_csv(dirname + '/data/countries.csv')
countries_un.rename(columns={'name': 'country'}, inplace=True)
countries_un.drop(columns=['Rank', 'pop2018', 'Density'], inplace=True)
countries_un.loc[:, 'pop2019'] = countries_un.pop2019.mul(1000)
countries_un.loc[:, 'country'].replace(
    to_replace=r'United States', value='United States of America', regex=True, inplace=True)
countries_un.loc[:, 'country'].replace(
    to_replace=r'Russia', value='Russian Federation', regex=True, inplace=True)

per_country = ecdc_raw.iloc[:, [0, 4, 5]].groupby(ecdc_raw.iloc[:, 6]).sum()

#
summary_country = pd.merge(per_country, countries_un,
                           how='left', on=['country'])
summary_country = pd.merge(
    summary_country, countries_codes,  how='left', on=['country'])
summary_country.loc[:, 'Cases/Mio. capita'] = summary_country.cases / \
    summary_country.pop2019*1000000
summary_country.loc[:, 'Deaths/Mio. capita'] = summary_country.deaths / \
    summary_country.pop2019*1000000


layout = go.Layout(yaxis=dict(type="linear", autorange=True))
layout_log = go.Layout(yaxis=dict(type="linear", autorange=True))

all_infections_deaths = ecdc_raw.iloc[:, [
    0, 4, 5]].groupby(["dateRep"]).sum().cumsum()

fig = go.Figure(
    data=[
        go.Scatter(name="Cases", x=all_infections_deaths.index,
                   y=all_infections_deaths.iloc[:, 0]),
        go.Scatter(name="Deaths", x=all_infections_deaths.index,
                   y=all_infections_deaths.iloc[:, 1]),
    ],
    layout=layout,
)
fig.update_layout(legend_orientation="h", legend=dict(
    x=0, y=.95), plot_bgcolor='white', autosize=True, height=400)

per_country = ecdc_raw.iloc[:, [0, 4, 5]].groupby(ecdc_raw.iloc[:, 6]).sum()
min_cases = 2000
per_country_max = per_country[per_country.iloc[:, 0] > min_cases]
per_country_max = per_country_max.sort_values('cases')
fig_cc = go.Figure(data=[go.Bar(name='confirmed infections', x=per_country_max.index,
                                y=per_country_max.iloc[:, 0]),
                         go.Bar(name='deaths', x=per_country_max.index,
                                y=per_country_max.iloc[:, 1])],
                   layout=layout_log)
fig_cc.update_layout(legend_orientation="h", legend=dict(
    x=0, y=.95), plot_bgcolor='white', autosize=True, height=400)

app = dash.Dash(__name__, external_stylesheets=[
                dbc.themes.BOOTSTRAP, dbc.themes.GRID])

app.layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.Img(
                        src=app.get_asset_url("logo.PNG"),
                        height=50,
                        # style={'margin': 5},
                    ),
                    width=1,
                ),
                dbc.Col(html.H1("COVID-19"), width=2,),
                dbc.Col(
                    html.Div(
                        id="select-indicator",
                        children=[
                            dcc.Dropdown(
                                id="value-selected",
                                value="cases",
                                options=[
                                    {"label": "Cases/Mio. capita ",
                                        "value": "cases"},
                                    {"label": "Deaths/Mio. capita ",
                                        "value": "deaths"},
                                ],
                                style={
                                    "display": "block",
                                    "margin-left": "auto",
                                    "margin-right": "auto",
                                    "width": "100%",
                                },
                            )
                        ],
                    ),
                    width=2,
                ),
            ],
            justify="start",
            no_gutters=True,
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        id="div-main-map",
                        children=[
                            dcc.Graph(id="main-map",
                                      style={"margin": 0, "padding": 0},)
                        ],
                        style={"margin": 0, "padding": 0},
                    ),
                    width=6,
                    style={"margin": 0},
                ),
                dbc.Col(
                    [
                        html.Div(
                            id="div-main-graph", children=[dcc.Graph(id="main-graph", figure=fig), ]
                        )
                    ],
                    width=6,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            id="div-minor-graph", children=[dcc.Graph(id="minor-graph", figure=fig_cc), ]
                        )
                    ],
                    width=6,
                    style={"margin": 0},
                ),
                dbc.Col(
                    [

                    ],
                    width=6,
                ),
            ]
        ),
    ]
)


@app.callback(
    dash.dependencies.Output("main-map", "figure"),
    [dash.dependencies.Input("value-selected", "value")],
)
def update_figure(selected):
    # .groupby(['iso_alpha', 'country']).mean().reset_index()
    dff = summary_country

    def config(text):
        if text == "cases":
            return "Cases/Mio. capita", 1000
        elif text == "deaths":
            return "Deaths/Mio. capita", 100
        else:
            return "Cases/Mio. capita", 1000

    title, limit = config(selected)
    trace = go.Choroplethmapbox(
        geojson=countries,
        locations=dff["iso_alpha"],
        z=dff[title],
        text=dff["country"],
        zmin=0,
        zmax=limit,
        marker={"line": {"color": "rgb(180,180,180)", "width": 0.5}},
        colorbar={"thickness": 20, "len": 0.6,
                  "x": 0.8, "y": 0.6, "outlinewidth": 0},
    )
    return {
        "data": [trace],
        "layout": go.Layout(
            width=1000,
            height=400,
            mapbox_style="mapbox://styles/dirkriemann/ck88smdb602qa1iljg6kxyavd",
            mapbox_zoom=0.75,
            mapbox_center={"lat": 25, "lon": 0},
            mapbox_accesstoken=MAPBOX,
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
        ),
    }


application = app.server
if __name__ == '__main__':
    application.run(debug=True, port=8080)
