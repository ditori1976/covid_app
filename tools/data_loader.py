from configparser import ConfigParser
import datetime
import pandas as pd
from urllib.request import urlopen
import requests
import json
from bs4 import BeautifulSoup


pd.options.mode.chained_assignment = None


class Extract:
    def __init__(self, parser: ConfigParser):

        self.data = self.load_jhu(parser)

        self.country_info = self.read_geonames_country_info(parser)

    def load_jhu(self, parser):

        lookup = pd.read_csv(parser.get("urls", "jhu_lookup_url"))
        lookup.rename(columns={"Country_Region": "region"}, inplace=True)

        country_info = self.read_geonames_country_info(parser)

        def read_prepare_data(url):
            data_raw = pd.read_csv(parser.get("urls", url))
            data_raw.rename(columns={"Country/Region": "region"}, inplace=True)
            data = (
                data_raw.groupby("region")
                .sum()
                .drop(columns=["Lat", "Long"])
                .reset_index()
            )

            return data

        def create_timeseries(data, lookup, value_name):
            id_vars = "region"
            var_name = "date"
            timeseries = pd.melt(
                data, id_vars=id_vars, var_name=var_name, value_name=value_name
            )
            timeseries = pd.merge(
                lookup[["iso2", "iso3", "code3", id_vars]].groupby(id_vars).first(),
                timeseries,
                on=id_vars,
                how="inner",
            )
            timeseries.loc[:, var_name] = pd.to_datetime(timeseries.loc[:, var_name])
            return timeseries

        confirmed_data = read_prepare_data("jhu_confirmed_url")
        deaths_data = read_prepare_data("jhu_deaths_url")
        recovered_data = read_prepare_data("jhu_recovered_url")

        confirmed = create_timeseries(confirmed_data, lookup, "confirmed")
        deaths = create_timeseries(deaths_data, lookup, "deaths")
        recovered = create_timeseries(recovered_data, lookup, "recovered")

        data = pd.merge(
            deaths[["date", "region", "iso3", "deaths"]],
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

    def read_geonames_country_info(self, parser):

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

        return country_info


class Transform(Extract):
    def __init__(self, parser: ConfigParser, indicators):

        super().__init__(parser)

        self.data = self.add_country_info(self.data, self.country_info)

        timeseries_all = self.data.groupby(["date", "continent"]).agg(
            {
                "iso3": "max",
                "deaths": "sum",
                "cases": "sum",
                "recovered": "sum",
                "population": "sum",
            }
        )
        timeseries_all.reset_index(inplace=True)
        timeseries_all.rename(columns={"continent": "region"}, inplace=True)
        timeseries_all.loc[:, "continent"] = timeseries_all.loc[:, "region"]

        world = self.data.groupby(["date"]).agg(
            {
                "region": "max",
                "iso3": "max",
                "deaths": "sum",
                "cases": "sum",
                "recovered": "sum",
                "population": "sum",
                "continent": "max",
            }
        )
        world.reset_index(inplace=True)
        world.loc[:, "region"] = "World"
        world.loc[:, "continent"] = "World"

        timeseries_all = timeseries_all.append(world)
        timeseries_all.loc[:, "iso3"] = False

        self.timeseries = timeseries_all.append(self.data)

    def select(self, country, indicator):
        select = self.timeseries[self.timeseries.region == country]
        select = self.add_indicator(
            select,
            indicator["name"],
            indicator["columns"],
            indicator["norming"],
            indicator["digits"],
            indicator["function"],
        )
        return select

    def latest_data(self, indicator):

        latest_data = self.data[
            self.data.date >= self.data.date.max() - datetime.timedelta(1)
        ]

        for i, indicator in self.indicators().items():
            latest_data = self.add_indicator(
                latest_data,
                indicator["name"],
                indicator["columns"],
                indicator["norming"],
                indicator["digits"],
                indicator["function"],
            )
        latest_data = latest_data.loc[latest_data.date == latest_data.date.max(), :]

        return latest_data

    def add_indicator(self, data, name, attributes, norming, digits, function=[]):
        #
        # adds columns with values for indicators as calculated from "attributes"
        #

        if len(attributes) == 2:
            data.loc[:, name] = (
                data.loc[:, attributes[0]] / data.loc[:, attributes[1]] * norming
            ).round(digits)
        else:
            data.loc[:, (name)] = norming * data.loc[:, (attributes[0])].round(digits)
            if function:
                if function == "diff":
                    data.sort_values(["region", "date"], inplace=True)
                    data.loc[:, name] = data.loc[:, attributes[0]].diff()

        return data

    def add_country_info(self, data, country_info):
        data = pd.merge(
            data,
            country_info[["iso_alpha", "population", "continent"]],
            left_on="iso3",
            right_on="iso_alpha",
            how="inner",
        )

        data.drop(columns=["iso_alpha"], inplace=True)

        return data

    def create_timeseries(self, data, region):

        if region:
            timeseries = data.groupby([region, "date"]).sum()

            timeseries.reset_index(inplace=True)
        else:
            timeseries = data.groupby("date").sum()

            timeseries.reset_index(inplace=True)

        return timeseries


class DataLoader(Transform):
    def __init__(self, parser: ConfigParser):

        super().__init__(parser, self.indicators)

        self.regions = self.regions()

        self.countries = self.countries_geojson(parser)

    def countries_geojson(self, parser):

        with urlopen(parser.get("urls", "mapbox_countries_url")) as response:
            countries = json.load(response)

        return countries

    def regions(self):

        regions = {
            "World": {"name": "World", "center": {"lat": 35, "lon": 0}, "zoom": 0.2},
            "EU": {"name": "Europe", "center": {"lat": 48, "lon": 0}, "zoom": 2.5},
            "NA": {"name": "N.America", "center": {"lat": 45, "lon": -95}, "zoom": 2},
            "SA": {
                "name": "S.America",
                "center": {"lat": -20, "lon": -70},
                "zoom": 1.7,
            },
            "AS": {"name": "Asia", "center": {"lat": 40, "lon": 90}, "zoom": 1.7},
            "AF": {"name": "Africa", "center": {"lat": 5, "lon": 20}, "zoom": 1.6},
            "OC": {"name": "Oceania", "center": {"lat": -30, "lon": 145}, "zoom": 2.2},
        }

        return regions

    def indicators(self):
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
                "name": "recovered(%)",
                "columns": ["recovered", "cases"],
                "norming": 100,
                "digits": 0,
                "function": [],
            },
            "lethality": {
                "name": "lethality(%)",
                "columns": ["deaths", "cases"],
                "norming": 100,
                "digits": 2,
                "function": [],
            },
            "recovered_cases": {
                "name": "recovered/cases(%)",
                "columns": ["recovered", "cases"],
                "norming": 100,
                "digits": 3,
                "function": [],
            },
            "deaths_recovered": {
                "name": "deaths/recovered(%)",
                "columns": ["deaths", "recovered"],
                "norming": 100,
                "digits": 2,
                "function": [],
            },
        }

        return indicators
