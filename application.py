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

app = dash.Dash(__name__)
application = app.server


#app.scripts.config.serve_locally = True
#app.css.config.serve_locally = True

app.layout = html.Div([
    html.H1(ecdc_raw.columns)
])

# start server

if __name__ == '__main__':
    application.run(debug=True, port=8080)
