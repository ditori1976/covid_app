from configparser import ConfigParser
import pandas as pd
from urllib.request import urlopen
import requests
import json
from bs4 import BeautifulSoup


class DataLoader:

    def __init__(self, parser: ConfigParser):

        res = requests.get(parser.get("urls", "geonames_countries_url"))
        soup = BeautifulSoup(res.content, "lxml")
        table = soup.find_all("table", id="countries")
        country_info = pd.read_html(str(table), keep_default_na=False)[0]
        country_info.rename(
            columns={
                "ISO-3166alpha2": "iso_alpha2",
                "ISO-3166alpha3": "iso_alpha",
                "ISO-3166numeric": "iso_num",
                "Country": "region",
                "Population": "population",
                "Continent": "continent",
            },
            inplace=True,
        )
        self.country_info = country_info

        self.lookup = pd.read_csv(parser.get("urls", "jhu_lookup_url"))
        self.lookup.rename(columns={"Country_Region": "region"}, inplace=True)

        id_vars = "region"

        confirmed_data = self.__read_prepare_data(
            parser.get("urls", "jhu_confirmed_url"), id_vars)
        deaths_data = self.__read_prepare_data(
            parser.get("urls", "jhu_deaths_url"), id_vars)
        recovered_data = self.__read_prepare_data(
            parser.get("urls", "jhu_recovered_url"), id_vars)

        self.confirmed = self.__create_timeseries(
            confirmed_data, self.lookup, id_vars, "date", "confirmed"
        )
        self.deaths = self.__create_timeseries(
            deaths_data, self.lookup, id_vars, "date", "deaths"
        )
        self.recovered = self.__create_timeseries(
            recovered_data, self.lookup, id_vars, "date", "recovered"
        )

        with urlopen(parser.get("urls", "mapbox_countries_url")) as response:
            self.countries = json.load(response)

        data_norm = pd.merge(
            self.deaths,
            self.country_info[["iso_alpha", "population", "continent"]],
            left_on="iso3",
            right_on="iso_alpha",
            how="inner",
        ).drop(columns=["iso3", "iso2", "code3"])
        data_norm = pd.merge(
            data_norm,
            self.confirmed[["date", "confirmed", "iso3"]],
            left_on=["iso_alpha", "date"],
            right_on=["iso3", "date"],
            how="inner",
        ).drop(columns=["iso3"])
        data_norm = pd.merge(
            data_norm,
            self.recovered[["date", "recovered", "iso3"]],
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

        self.data_norm = data_norm

        self.timeseries = data_norm.groupby(["continent", "date"]).sum()

        self.world = self.timeseries.groupby("date").sum()
        self.world = pd.DataFrame(
            index=[pd.Series(data="World").repeat(
                len(self.world.index)), self.world.index],
            data=self.world.values,
            columns=self.world.columns,
        )

        self.timeseries = pd.concat([self.timeseries, self.world])

        self.per_country_max = data_norm[data_norm.date ==
                                         data_norm.date.max()]
        self.regions = {
            "World": {"name": "World", "center": {"lat": 35, "lon": 0}, "zoom": 0.2},
            "EU": {"name": "Europe", "center": {"lat": 50, "lon": 1}, "zoom": 2.5},
            "NA": {"name": "N.America", "center": {"lat": 50, "lon": -95}, "zoom": 2},
            "SA": {"name": "S.America", "center": {"lat": -20, "lon": -70}, "zoom": 1.7},
            "AS": {"name": "Asia", "center": {"lat": 40, "lon": 90}, "zoom": 1.7},
            "AF": {"name": "Africa", "center": {"lat": 5, "lon": 10}, "zoom": 1.6},
            "OC": {"name": "Oceania", "center": {"lat": -30, "lon": 145}, "zoom": 2.2}
        }

    def __read_prepare_data(self, url, id_vars):
        data_raw = pd.read_csv(url)
        data_raw.rename(columns={"Country/Region": "region"}, inplace=True)
        data = (
            data_raw.groupby(id_vars)
            .sum()
            .drop(columns=["Lat", "Long"])
            .reset_index()
        )

        return data

    def __create_timeseries(self, data, lookup, id_vars, var_name, value_name):
        timeseries = pd.melt(
            data, id_vars=id_vars, var_name=var_name, value_name=value_name
        )
        timeseries = pd.merge(
            lookup[["iso2", "iso3", "code3", id_vars]
                   ].groupby(id_vars).first(),
            timeseries,
            on=id_vars,
            how="inner",
        )
        timeseries.loc[:, var_name] = pd.to_datetime(
            timeseries.loc[:, var_name])
        return timeseries
