import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
import numpy as np
from tools import DataLoader
from configparser import ConfigParser


# configuration
parser = ConfigParser()
parser.read("settings.ini")

# number of seconds between re-calculating the data
UPDADE_INTERVAL = 15


def get_new_data():
    print("get_new_data")
    """Updates the global variable 'data' with new data"""
    global data1
    data = np.random.normal(size=1000)
    data1 = DataLoader(parser)
    print(data1.data.head(1))
    np.save("data1", data)


def get_new_data_every(period=UPDADE_INTERVAL):
    print("get_new_data_every")
    """Update the data every 'period' seconds"""
    while True:
        get_new_data()
        print("data updated")
        time.sleep(period)


def make_layout():
    data = np.load("data1.npy")
    chart_title = "data updates server-side every {} seconds".format(UPDADE_INTERVAL)
    return html.Div(
        dcc.Graph(
            id="chart",
            figure={"data": [go.Histogram(x=data)], "layout": {"title": chart_title}},
        )
    )


app = dash.Dash(__name__)

# get initial data
get_new_data()

# we need to set layout to be a function so that for each new page load
# the layout is re-created with the current data, otherwise they will see
# data that was generated when the Dash app was first initialised
app.layout = make_layout


def start_multi():
    executor = ProcessPoolExecutor(max_workers=1)
    executor.submit(get_new_data_every)


if __name__ == "__main__":

    start_multi()
    app.run_server(debug=True)
