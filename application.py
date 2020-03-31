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
ecdc_raw = pd.read_csv(io.StringIO(s.decode('latin-1')))

ecdc_raw.rename(columns={'countriesAndTerritories': 'country'}, inplace=True)
ecdc_raw.iloc[:, 6].replace(
    to_replace=r'_', value=' ', regex=True, inplace=True)
ecdc_raw.loc[:, 'country'].replace(
    to_replace=r'Russia', value='Russian Federation', regex=True, inplace=True)

countries_codes = pd.read_csv('data/country_codes.csv')


app = dash.Dash(__name__)

#app.scripts.config.serve_locally = True
#app.css.config.serve_locally = True

app.layout = html.Div([
    html.H1(MAPBOX)
])

application = app.server

if __name__ == '__main__':
    application.run(debug=True, port=8080)
