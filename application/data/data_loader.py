from datetime import datetime
import pandas as pd
from configparser import ConfigParser
from urllib.request import urlopen
import requests
import json
from bs4 import BeautifulSoup


class DataLoader:
    def __init__(self, parser: ConfigParser):
        self.parser = parser
        self.latest_load = None
        self.data = None

    def load_data(self):
        # local, external

        def load_jhu():
            error_msg = "cannot load jhu data, no url provided"

            try:
                lookup_table = pd.read_csv(
                    self.parser.get("urls", "jhu_lookup_url"))

                lookup_table.rename(
                    columns={"Country_Region": "region", "Long_": "Lon"}, inplace=True
                )

            except BaseException:
                print(error_msg + "3")
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
                        print(error_msg + "4")
                        return None

                def create_timeseries(data, lookup_table, value_name):
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
                        print(error_msg + "5")
                        return None

                confirmed_data = read_prepare_data("jhu_confirmed_url")
                deaths_data = read_prepare_data("jhu_deaths_url")
                recovered_data = read_prepare_data("jhu_recovered_url")

                confirmed = create_timeseries(
                    confirmed_data, lookup_table, "confirmed")
                deaths = create_timeseries(deaths_data, lookup_table, "deaths")
                recovered = create_timeseries(
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
                print(error_msg + "2")
                return None

        self.latest_load = datetime.now()
        self.data = load_jhu()

    def prepare(self):
        # join tables, create timeseries
        pass

    def write_data(self):
        # to csv
        if self.data is not None:
            self.data.to_csv("test.csv")
        else:
            print("nothing to write")
