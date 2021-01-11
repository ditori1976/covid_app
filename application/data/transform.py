from configparser import ConfigParser
from application.data.extract import Extract
import pandas as pd


class Transform(Extract):
    def __init__(self, parser: ConfigParser):

        super().__init__(parser)

        self.timeseries = None

    def add_country_info(self, data, country_info):
        try:
            data = pd.merge(
                data,
                country_info[["iso_alpha", "population", "continent", "area"]],
                left_on="iso3",
                right_on="iso_alpha",
                how="inner",
            )
            data.drop(columns=["iso_alpha"], inplace=True)
        except BaseException:
            print("no data")
            pass

        return data

    def create_timeseries(self, data):
        timeseries_all = data.groupby(["date", "continent"]).agg(
            {
                "iso3": "max",
                "deaths": "sum",
                "cases": "sum",
                #"recovered": "sum",
                "population": "sum",
            }
        )
        timeseries_all.reset_index(inplace=True)
        timeseries_all.rename(columns={"continent": "region"}, inplace=True)
        timeseries_all.loc[:, "continent"] = timeseries_all.loc[:, "region"]

        world = data.groupby(["date"]).agg(
            {
                "region": "max",
                "iso3": "max",
                "deaths": "sum",
                "cases": "sum",
                #"recovered": "sum",
                "population": "sum",
                "continent": "max",
            }
        )
        world.reset_index(inplace=True)
        world.loc[:, "region"] = "World"
        world.loc[:, "continent"] = "World"

        timeseries_all = timeseries_all.append(world)
        timeseries_all.loc[:, "iso3"] = False

        timeseries = timeseries_all.append(self.data)

        return timeseries
