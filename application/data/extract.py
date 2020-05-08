from datetime import datetime
import pandas as pd
from configparser import ConfigParser
from urllib.request import urlopen
import requests
import json
from bs4 import BeautifulSoup


class Extract:
    def __init__(self, parser: ConfigParser):
        self.parser = parser
        self.latest_load = None
        self.data = None
        self.jhu = None
        self.country_info = None
        self.countries = None

    def load_jhu(self):

        print("jhu")

        error_msg = "cannot load JHU data, no url provided"

        try:
            lookup_table = pd.read_csv(
                self.parser.get("urls", "jhu_lookup_url"))

            lookup_table.rename(
                columns={"Country_Region": "region", "Long_": "Lon"}, inplace=True
            )

        except BaseException:
            print(error_msg)
            return None

        if not lookup_table.empty:
            def read_prepare_data(url):
                try:
                    data_raw = pd.read_csv(self.parser.get("urls", url))
                    data_raw.rename(
                        columns={
                            "Country/Region": "region"},
                        inplace=True)
                    data = (
                        data_raw.groupby("region")
                        .sum()
                        .drop(columns=["Lat", "Long"])
                        .reset_index()
                    )

                    return data
                except BaseException:
                    print(error_msg)
                    return None

            def create_timeseries_jhu(data, lookup_table, value_name):
                try:

                    id_vars = "region"
                    var_name = "date"
                    timeseries = pd.melt(
                        data, id_vars=id_vars, var_name=var_name, value_name=value_name
                    )
                    timeseries = pd.merge(
                        lookup_table[["iso2", "iso3",
                                      "code3", "Lat", "Lon", id_vars]]
                        .groupby(id_vars)
                        .first(),
                        timeseries,
                        on=id_vars,
                        how="inner",
                    )
                    timeseries.loc[:, var_name] = pd.to_datetime(
                        timeseries.loc[:, var_name])
                    return timeseries
                except BaseException:
                    print(error_msg)
                    return None

            confirmed_data = read_prepare_data("jhu_confirmed_url")
            deaths_data = read_prepare_data("jhu_deaths_url")
            recovered_data = read_prepare_data("jhu_recovered_url")

            confirmed = create_timeseries_jhu(
                confirmed_data, lookup_table, "confirmed")
            deaths = create_timeseries_jhu(deaths_data, lookup_table, "deaths")
            recovered = create_timeseries_jhu(
                recovered_data, lookup_table, "recovered")

            data = pd.merge(
                deaths[["date", "region", "iso3", "Lat", "Lon", "deaths"]],
                confirmed[["date", "confirmed", "iso3"]],
                on=["iso3", "date"],
                how="inner",
            )
            data = pd.merge(
                data,
                recovered[["date", "recovered", "iso3"]],
                on=["iso3", "date"],
                how="inner",
            )

            data.rename(columns={"confirmed": "cases"}, inplace=True)

            return data

        else:
            print(error_msg)
            return None

    def read_geonames_country_info(self):

        print("geonames")

        error_msg = "cannot load geonames data, no url provided"

        try:
            res = requests.get(
                self.parser.get(
                    "urls", "geonames_countries_url"))
            soup = BeautifulSoup(res.content, "lxml")
            table = soup.find_all("table", id="countries")
            country_info = pd.read_html(
                str(table), keep_default_na=False)[0]
            country_info.rename(
                columns={
                    "ISO-3166alpha2": "iso_alpha2",
                    "ISO-3166alpha3": "iso_alpha",
                    "ISO-3166numeric": "iso_num",
                    "Country": "region",
                    "Population": "population",
                    "Continent": "continent",
                    "Area in km²": "area",
                },
                inplace=True,
            )
            return country_info

        except BaseException:
            print(error_msg)
            return None

    def countries_geojson(self):

        print("geojson")

        error_msg = "cannot load geojson data, no url provided"

        try:
            with urlopen(self.parser.get("urls", "mapbox_countries_url")) as response:
                countries = json.load(response)

            return countries
        except BaseException:
            print(error_msg)
            return None

    def definition_regions(self):

        regions = {
            "World": {"name": "World", "center": {"lat": 35, "lon": 0}, "zoom": 0.5},
            "EU": {"name": "Europe", "center": {"lat": 50, "lon": 5}, "zoom": 2},
            "NA": {"name": "N.America", "center": {"lat": 45, "lon": -95}, "zoom": 2},
            "SA": {
                "name": "S.America",
                "center": {"lat": -20, "lon": -70},
                "zoom": 1.7,
            },
            "AS": {"name": "Asia", "center": {"lat": 40, "lon": 90}, "zoom": 2},
            "AF": {"name": "Africa", "center": {"lat": 5, "lon": 20}, "zoom": 2},
            "OC": {"name": "Oceania", "center": {"lat": -30, "lon": 145}, "zoom": 2},
        }

        return regions

    def definition_indicators(self):
        indicators = {
            "cases": {
                "name": "cases",
                "columns": ["cases"],
                "norming": 1,
                "digits": 0,
                "function": [],
            },
            "deaths": {
                "name": "deaths",
                "columns": ["deaths"],
                "norming": 1,
                "digits": 0,
                "function": [],
            },
            "daily_cases": {
                "name": "daily cases",
                "columns": ["cases"],
                "norming": 1,
                "digits": 0,
                "function": "diff",
            },
            "daily_deaths": {
                "name": "daily deaths",
                "columns": ["deaths"],
                "norming": 1,
                "digits": 0,
                "function": "diff",
            },
            "cases_capita": {
                "name": "cases/1M capita",
                "columns": ["cases", "population"],
                "norming": 100000,
                "digits": 0,
                "function": [],
            },
            "deaths_capita": {
                "name": "deaths/1M capita",
                "columns": ["deaths", "population"],
                "norming": 100000,
                "digits": 1,
                "function": [],
            },
            "recovered_capita": {
                "name": "% recovered",
                "columns": ["recovered", "cases"],
                "norming": 100,
                "digits": 0,
                "function": [],
            },
            "lethality": {
                "name": "% lethality",
                "columns": ["deaths", "cases"],
                "norming": 100,
                "digits": 2,
                "function": [],
            },
            "recovered_cases": {
                "name": "% recovered/cases",
                "columns": ["recovered", "cases"],
                "norming": 100,
                "digits": 3,
                "function": [],
            },
            "deaths_recovered": {
                "name": "% deaths/recovered",
                "columns": ["deaths", "recovered"],
                "norming": 100,
                "digits": 2,
                "function": [],
            },
        }

        return indicators

    def write_data(self):
        # to csv
        if self.data is not None:
            self.data.to_csv("test.csv")
        else:
            print("nothing to write")
