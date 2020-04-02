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

        url = "https://opendata.ecdc.europa.eu/covid19/casedistribution/csv"
        csv = requests.get(url).content
        ecdc_raw = pd.read_csv(
            io.StringIO(csv.decode("utf-8")),
            parse_dates=["dateRep"],
            error_bad_lines=False,
        )

        with urlopen(
            "https://raw.githubusercontent.com/mapbox/geojson-vt-cpp/master/data/countries.geojson"
        ) as response:
            self.countries = json.load(response)

        ecdc_raw = ecdc_raw[ecdc_raw.dateRep <= dt.datetime.today()].sort_values(
            "dateRep"
        )

        ecdc_raw.rename(
            columns={
                "countriesAndTerritories": "country",
                "countryterritoryCode": "iso_alpha",
            },
            inplace=True,
        )
        ecdc_raw.iloc[:, 6].replace(
            to_replace=r"_", value=" ", regex=True, inplace=True
        )

        self.per_country = (
            ecdc_raw.iloc[:, [0, 4, 5]].groupby(ecdc_raw.iloc[:, 6]).sum()
        )

        summary_country = ecdc_raw.loc[
            :, ["cases", "deaths", "country", "iso_alpha", "popData2018"]
        ].groupby("iso_alpha")
        aggregation = {
            "cases": "sum",
            "deaths": "sum",
            "country": "max",
            "popData2018": "max",
        }
        summary_country = summary_country.agg(aggregation)
        summary_country.loc[:, "Cases/Mio. capita"] = (
            summary_country.cases / summary_country.popData2018 * 1000000
        ).round(2)
        summary_country.loc[:, "Deaths/Mio. capita"] = (
            summary_country.deaths / summary_country.popData2018 * 1000000
        ).round(2)
        summary_country.reset_index(inplace=True)

        self.summary_country = summary_country
        self.ecdc_raw = ecdc_raw
