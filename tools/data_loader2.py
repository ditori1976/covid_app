import pandas as pd
from urllib.request import urlopen
import requests
import json
from bs4 import BeautifulSoup


class DataLoader:
    """
    Loads data from CSV file "cities15000.txt" in the same folder and prepares data.
    """

    def __init__(self):

        # define column names and columns to use
        columns = {
            "name": "name",
            "population": "population",
            "dem": "elevation",
            "longitude": "lon",
            "latitude": "lat",
        }

        # load data into DataFrame
        csv_data = pd.read_csv("tools/cities15000.txt", sep="\t")
        raw_data = csv_data.loc[csv_data["country code"] == "CH"]
        data = raw_data.loc[:, list(columns.keys())]
        data.rename(columns=columns, inplace=True)

        # format columns for geographical information
        cols = ["lat", "lon"]
        data.loc[:, cols] = data.loc[:, cols].round(5)
        data["lat"].astype("float")
        data["lon"].astype("float")

        self.data = data

        with urlopen(
            "https://raw.githubusercontent.com/mapbox/geojson-vt-cpp/master/data/countries.geojson"
        ) as response:
            self.countries = json.load(response)

    def jhu(self):
        def read_prepare_data(url, id_vars):
            data_raw = pd.read_csv(url)
            data_raw.rename(columns={"Country/Region": "region"}, inplace=True)
            data = (
                data_raw.groupby(id_vars)
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
            timeseries.loc[:, var_name] = pd.to_datetime(timeseries.loc[:, var_name])
            return timeseries

        lookup_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv"
        confirmed_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
        deaths_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
        recovered_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv"

        self.lookup = pd.read_csv(lookup_url)
        self.lookup.rename(columns={"Country_Region": "region"}, inplace=True)

        id_vars = "region"

        confirmed_data = read_prepare_data(confirmed_url, id_vars)
        deaths_data = read_prepare_data(deaths_url, id_vars)
        recovered_data = read_prepare_data(recovered_url, id_vars)

        self.confirmed = create_timeseries(
            confirmed_data, self.lookup, id_vars, "date", "confirmed"
        )
        self.deaths = create_timeseries(
            deaths_data, self.lookup, id_vars, "date", "deaths"
        )
        self.recovered = create_timeseries(
            recovered_data, self.lookup, id_vars, "date", "recovered"
        )

    def geonames(self):
        res = requests.get("http://download.geonames.org/countries/")
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
