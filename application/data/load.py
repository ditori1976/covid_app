from configparser import ConfigParser
import datetime
from application.data.transform import Transform
import pandas as pd
import logging
#from statsmodels.tsa.seasonal import seasonal_decompose
import numpy as np
from decimal import Decimal

log = logging.getLogger("my-logger")


class Load(Transform):
    def __init__(self, parser: ConfigParser):

        super().__init__(parser)

    def _readable(self, n, d=0):
        digits = 10 ** (np.floor(np.log10(abs(n))) - d - 1)
        return np.floor(n / digits) * digits

    def series(self, country, per_capita, aggregation, indicator):

        try:
            if country == "all":
                series = self.timeseries.sort_values(["region", "date"]).copy()
            else:
                series = self.timeseries[self.timeseries.region == country].sort_values(
                    ["region", "date"]).copy()
            if per_capita:
                series.loc[:, indicator] = 100000 * series.loc[:,
                                                               indicator].div(series.loc[:, "population"], axis=0)
            if aggregation == "daily":
                series.loc[:, indicator] = series.loc[:, indicator].diff()
            elif aggregation == "days":
                series.loc[:,
                           indicator] = series.loc[:,
                                                   indicator].diff(periods=7)
            series.loc[:, indicator] = self._readable(
                series.loc[:, indicator], 1).round(5)
            return series
        except BaseException:
            return None

    def map_data(self, per_capita, aggregation, indicator):
        try:
            # map_data = self.data.copy()

            map_data = self.series('all', per_capita, aggregation, indicator)
            map_data = map_data.loc[map_data.date == map_data.date.max(), :]
            return map_data
        except BaseException:
            return None

    def select(self, country, indicator):
        try:
            select = self.timeseries[self.timeseries.region == country].copy()
            select = self.add_indicator(
                select,
                indicator["name"],
                indicator["columns"],
                indicator["norming"],
                indicator["digits"],
                indicator["function"],
            )
            return select
        except BaseException:
            return None

    def add_indicator(self, data, name, attributes,
                      norming, digits, function=[]):
        #
        # adds columns with values for indicators as calculated from "attributes"
        #
        # print("indicator")
        data.sort_values(["region", "date"], inplace=True)
        if len(attributes) == 2:

            if function == "diff":

                data.loc[:, name] = data.loc[:, attributes[0]].diff()
                data.loc[:, name] = data.loc[:, name] / (
                    data.loc[:, attributes[1]]
                ) * norming
                # data.loc[:, name] = data.loc[:, name].round(digits)
                data.loc[data.loc[:, name] < 0, name] = 0
            elif function == "fraction":
                data.loc[:, name] = data.loc[:, attributes[0]] / (
                    data.loc[:, attributes[1]]
                ) * norming
                # data.loc[:, name] = data.loc[:, name].round(digits)

            else:

                data.loc[:, name] = (
                    data.loc[:, attributes[0]] /
                    data.loc[:, attributes[1]] * norming
                )  # .round(digits)

        else:
            if function:
                if (function == "diff") and (len(attributes) == 1):

                    data.loc[:, name] = data.loc[:, attributes[0]].diff()
                    data.loc[:, name] = data.loc[:, name]  # .round(digits)

                    data.loc[data.loc[:, name] < 0, name] = 0

                if (function == "trend") and (len(attributes) == 1):

                    data.loc[:, name] = ((2 * data.loc[:, attributes[0]].diff(
                        periods=7) / data.loc[:, attributes[0]].diff(periods=14)) - 1) * 100

                    data.loc[data.cases < 50, name] = 0
        data.loc[:, name] = data.loc[:, name].round(digits)
        return data

    def latest_data(self, indicator):

        try:
            # latest_data_sub = self.data[
            #     self.data.date >= self.data.date.max() - datetime.timedelta(20)
            # ].copy()
            latest_data_sub = self.data.copy()

            latest_data = self.add_indicator(
                latest_data_sub,
                indicator["name"],
                indicator["columns"],
                indicator["norming"],
                indicator["digits"],
                indicator["function"],
            )
            latest_data = latest_data.loc[latest_data.date ==
                                          latest_data.date.max(), :]

            return latest_data
        except BaseException:
            return None
