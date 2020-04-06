import os
import requests
import datetime as dt
import pandas as pd
import io
from urllib.request import urlopen
import json

dirname = os.path.dirname(os.path.abspath(__file__))


class DataLoader:
    def __init__(self):

        self.latest_update = dt.date.today()

        with urlopen(
            "https://raw.githubusercontent.com/mapbox/geojson-vt-cpp/master/data/countries.geojson"
        ) as response:
            self.countries = json.load(response)

    def jhu(self):
        def read_prepare_data(url, id_vars):
            data = (
                pd.read_csv(url)
                .groupby(id_vars)
                .sum()
                .drop(columns=["Lat", "Long"])
                .reset_index()
            )

            return data

        def create_timeseries(data, lookup, id_vars, var_name, value_name):
            timeseries = pd.melt(
                data, id_vars=id_vars, var_name=var_name, value_name=value_name
            )
            timeseries = pd.merge(
                lookup[["iso2", "iso3", "code3", id_vars]].groupby(id_vars).first(),
                timeseries,
                on=id_vars,
                how="inner",
            )
            return timeseries

        lookup_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv"
        confirmed_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
        deaths_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
        recovered_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv"

        self.lookup = pd.read_csv(lookup_url)
        self.lookup.rename(columns={"Country_Region": "Country/Region"}, inplace=True)

        confirmed_raw = pd.read_csv(confirmed_url)
        deaths_raw = pd.read_csv(deaths_url)
        recovered_raw = pd.read_csv(recovered_url)

        id_vars = "Country/Region"

        confirmed_data = read_prepare_data(confirmed_url, id_vars)
        deaths_data = read_prepare_data(deaths_url, id_vars)
        recovered_data = read_prepare_data(recovered_url, id_vars)

        self.confirmed = create_timeseries(
            confirmed_data, lookup, id_vars, "date", "confirmed"
        )
        self.deaths = create_timeseries(
            deaths_data.reset_index(), lookup, id_vars, "date", "deaths"
        )
        self.recovered = create_timeseries(
            recovered_data.reset_index(), lookup, id_vars, "date", "recovered"
        )

    def ecdc(self):
        url = "https://opendata.ecdc.europa.eu/covid19/casedistribution/csv"
        csv = requests.get(url).content
        ecdc_raw = pd.read_csv(
            io.StringIO(csv.decode("utf-8")),
            parse_dates=["dateRep"],
            error_bad_lines=False,
        )

        ecdc_raw = ecdc_raw[ecdc_raw.dateRep <= dt.datetime.today()].sort_values(
            "dateRep"
        )

        ecdc_raw.rename(
            columns={
                "countriesAndTerritories": "country",
                "countryterritoryCode": "iso_alpha",
                "dateRep": "date",
                "popData2018": "population",
            },
            inplace=True,
        )

        self.per_country = (
            ecdc_raw.iloc[:, [0, 4, 5]].groupby(ecdc_raw.iloc[:, 6]).sum()
        )

        summary_country = ecdc_raw.loc[
            :, ["cases", "deaths", "country", "iso_alpha", "population"]
        ].groupby("iso_alpha")
        aggregation = {
            "cases": "sum",
            "deaths": "sum",
            "country": "max",
            "population": "max",
        }
        summary_country = summary_country.agg(aggregation)
        summary_country.loc[:, "Cases/Mio. capita"] = (
            summary_country.cases / summary_country.population * 1000000
        ).round(0)
        summary_country.loc[:, "Deaths/Mio. capita"] = (
            summary_country.deaths / summary_country.population * 1000000
        ).round(0)
        summary_country.reset_index(inplace=True)

        self.summary_country = summary_country
        ecdc_raw.drop(columns=["day", "month", "year"], inplace=True)
        self.ecdc_raw = ecdc_raw
