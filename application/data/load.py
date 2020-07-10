from configparser import ConfigParser
import datetime
from application.data.transform import Transform
import pandas as pd
import logging
from statsmodels.tsa.seasonal import seasonal_decompose

log = logging.getLogger("my-logger")


class Load(Transform):
    def __init__(self, parser: ConfigParser):

        super().__init__(parser)

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

        if len(attributes) == 2:

            if function == "diff":

                data.loc[:, (name)] = norming * data.loc[:,
                                                         (attributes[0])].round(digits)

                data.sort_values(["region", "date"], inplace=True)
                data.loc[:, name] = data.loc[:, attributes[0]].diff()
                data.loc[:, name] = data.loc[:, name] / (
                    data.loc[:, attributes[1]]
                )
                data.loc[:, name] = data.loc[:, name].round(digits)
                data.loc[data.loc[:, name] < 0, name] = 0
            else:

                data.loc[:, name] = (
                    data.loc[:, attributes[0]] /
                    data.loc[:, attributes[1]] * norming
                ).round(digits)

        else:
            data.loc[:, (name)] = norming * data.loc[:,
                                                     (attributes[0])]  # .round(digits)
            if function:
                if (function == "diff") and (len(attributes) == 1):
                    data.sort_values(["region", "date"], inplace=True)
                    data.loc[:, name] = data.loc[:, attributes[0]].diff()
                    data.loc[:, name] = data.loc[:, name].round(digits)

                    data.loc[data.loc[:, name] < 0, name] = 0

                if (function == "trend") and (len(attributes) == 1):
                    data.sort_values(["region", "date"], inplace=True)
                    # decompose = seasonal_decompose(
                    #     data.loc[:, attributes[0]], period=7, extrapolate_trend="freq")
                    # data.loc[:, name] = decompose.trend.diff(
                    #     periods=7) / decompose.trend.mean()

                    # erst ab 100 cases berechnen?

                    data.loc[:, name] = ((2 * data.loc[:, attributes[0]].diff(
                        periods=7) / data.loc[:, attributes[0]].diff(periods=14)) - 1) * 100

                    data.loc[data.cases < 50, name] = 0

        # remove negative values

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
