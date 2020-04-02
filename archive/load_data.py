import os
import requests
import datetime as dt
import pandas as pd
import io
from urllib.request import urlopen
import json

dirname = os.path.dirname(os.path.abspath(__file__))

url = "https://opendata.ecdc.europa.eu/covid19/casedistribution/csv"
s = requests.get(url).content
ecdc_raw = pd.read_csv(io.StringIO(s.decode("utf-8")), parse_dates=["dateRep"], error_bad_lines=False)

ecdc_raw = ecdc_raw[ecdc_raw.dateRep <= dt.datetime.today()].sort_values("dateRep")

ecdc_raw.rename(columns={"countriesAndTerritories": "country"}, inplace=True)
ecdc_raw.iloc[:, 6].replace(to_replace=r"_", value=" ", regex=True, inplace=True)


with urlopen(
    "https://raw.githubusercontent.com/mapbox/geojson-vt-cpp/master/data/countries.geojson"
) as response:
    countries = json.load(response)
    
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
summary_country.loc[:, 'Cases/Mio. capita'] = (summary_country.cases /
                                               summary_country.pop2019*1000000).round(0)
summary_country.loc[:, 'Deaths/Mio. capita'] = (summary_country.deaths /
                                                summary_country.pop2019*1000000).round(0)
