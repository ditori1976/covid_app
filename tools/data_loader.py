from configparser import ConfigParser
import pandas as pd
from urllib.request import urlopen
import requests
import json
from bs4 import BeautifulSoup


class Extract:

    def __init__(self, parser: ConfigParser):

        self.info = "extract data"

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
                lookup[["iso2", "iso3", "code3", id_vars]
                       ].groupby(id_vars).first(),
                timeseries,
                on=id_vars,
                how="inner",
            )
            timeseries.loc[:, var_name] = pd.to_datetime(
                timeseries.loc[:, var_name])
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

        self.data = data.rename(columns={"confirmed": "cases"})

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

    def __init__(self, parser: ConfigParser):

        super().__init__(parser)

        self.data = self.add_country_info(self.data, self.country_info)

        self.data.loc[:, "cases/1M capita"] = (
            self.data.confirmed / self.data.population * 1000000
        ).round(0)
        self.data.loc[:, "deaths/1M capita"] = (
            self.data.deaths / self.data.population * 1000000
        ).round(0)
        self.data.loc[:, "recovered/1M capita"] = (
            self.data.recovered / self.data.population * 1000000
        ).round(0)

        self.data.rename(columns={"confirmed": "cases"}, inplace=True)

        timeseries = self.data.groupby(["continent", "date"]).sum()

        timeseries.loc[:, "lethality"] = (
            100*timeseries.deaths / timeseries.cases
        ).round(1)

        world = timeseries.groupby("date").sum()
        world.loc[:, "lethality"] = (
            100 * world.deaths / world.cases
        ).round(1)
        world = pd.DataFrame(
            index=[pd.Series(data="World").repeat(
                len(world.index)), world.index],
            data=world.values,
            columns=world.columns,
        )

        self.timeseries = pd.concat([timeseries, world])

        self.per_country_max = self.data[self.data.date ==
                                         self.data.date.max()]
        self.per_country_max.loc[:, "lethality"] = (
            100 * self.per_country_max.deaths / self.per_country_max.cases
        ).round(1)

    def add_country_info(self, data, country_info):
        data = pd.merge(
            data,
            country_info[["iso_alpha", "population", "continent"]],
            left_on="iso3",
            right_on="iso_alpha",
            how="inner",
        )

        return data

    def by_continent(self, data):
        pass


class DataLoader(Transform):
    def __init__(self, parser: ConfigParser):

        super().__init__(parser)

        self.regions = self.regions()

        self.countries = self.countries_geojson(parser)

    def countries_geojson(self, parser):
        with urlopen(parser.get("urls", "mapbox_countries_url")) as response:
            countries = json.load(response)

        return countries

    def regions(self):

        regions = {
            "World": {"name": "World", "center": {"lat": 35, "lon": 0}, "zoom": 0.2},
            "EU": {"name": "Europe", "center": {"lat": 50, "lon": 1}, "zoom": 2.5},
            "NA": {"name": "N.America", "center": {"lat": 50, "lon": -95}, "zoom": 2},
            "SA": {"name": "S.America", "center": {"lat": -20, "lon": -70}, "zoom": 1.7},
            "AS": {"name": "Asia", "center": {"lat": 40, "lon": 90}, "zoom": 1.7},
            "AF": {"name": "Africa", "center": {"lat": 5, "lon": 10}, "zoom": 1.6},
            "OC": {"name": "Oceania", "center": {"lat": -30, "lon": 145}, "zoom": 2.2}
        }

        return regions
