import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output, State, ALL, MATCH
import time
import json
import math
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from configparser import ConfigParser

from application.data.data_loader import DataLoader
from application.config.config import Config

configuration = Config()


parser = ConfigParser()
parser.read("settings.ini")


data = DataLoader(parser)

data.load_data()
latest_update = data.latest_load.strftime("%m/%d/%Y, %H:%M:%S")
state = {
    "indicators": ["cases"],
    "regions": ["World"],
    "axis": {
        "x": "date",
        "y": "linear"
    }
}

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[
        {
            "name": "viewport",
            "content": "width=device-width, initial-scale=1.0"
        }
    ]
)

# map
fig_map = go.Figure(
    go.Choroplethmapbox(
        colorscale="BuPu",
        geojson=data.countries,
        zmin=0,
        marker={"line": {"color": "rgb(180,180,180)", "width": 0.5}},
        colorbar={
            "thickness": 10,
            "len": 0.4,
            "x": 0,
            "y": 0.3,
            "outlinewidth": 0,
        },
    )
)

fig_map.update_layout(
    margin={"r": 0, "t": 0, "l": 0, "b": 0, "pad": 0},
    mapbox_style="mapbox://styles/dirkriemann/ck88smdb602qa1iljg6kxyavd",
    mapbox=go.layout.Mapbox(
        accesstoken="pk.eyJ1IjoiZGlya3JpZW1hbm4iLCJhIjoiY2szZnMyaXoxMDdkdjNvcW5qajl3bzdkZCJ9.d7njqybjwdWOxsnxc3fo9w",
        style="light",
        pitch=0,
    ),
)

map_div = dcc.Graph(
    id="map",
    config={
        "displayModeBar": False},
    style={"height": parser.get(
        "layout", "height_first_row") + "vh", "width": "100%"}
)

row_tap_map = dbc.Row(
    children=[
        dbc.Col("tab", width=3),
        dbc.Col(map_div, width=9)
    ]
)

row_1 = [
    dbc.Col(row_tap_map, lg=6, xs=12),
    dbc.Col("col2", lg=6, xs=12)
]
row_2 = [
    dbc.Col("col3", lg=6, xs=12),
    dbc.Col(latest_update, lg=6, xs=12)
]


def set_layout():
    return dbc.Container(
        children=[
            dbc.Row(row_1, no_gutters=True),
            dbc.Row(row_2, no_gutters=True),
            dcc.Store(id='memory')
        ],
        fluid=True
    )


app.layout = set_layout


@app.callback(Output('memory', 'data'),
              [Input("map", "clickData")])
def change_state(map_select):
    print(map_select)
    if map_select:
        region = map_select["points"][0]["text"]
        state["regions"][0] = region
        print(state)
        return state
    else:
        return state


@app.callback(
    Output("map", "figure"),
    [Input('memory', 'data')],
)
def draw_map(state):
    print(state)

    if not state:
        return dash.no_update
    else:
        selected_indicator = state["indicators"][0]
        indicator_name = data.indicators[selected_indicator]["name"]
        data_selected = data.latest_data(
            data.indicators[selected_indicator])

        fig_map.update_traces(
            locations=data_selected["iso3"],
            z=data_selected[indicator_name],
            text=data_selected["region"],
            zmax=data_selected[indicator_name]
            .replace([np.inf, -np.inf], np.nan)
            .max()
            * 0.3,
        )
        if state["regions"] in list(data.regions):
            selected_region = state["regions"][0]
            fig_map.update_layout(
                mapbox_center=data.regions[selected_region]["center"],
                mapbox_zoom=data.regions[selected_region]["zoom"],
            )

        return fig_map


if __name__ == "__main__":

    # start_multi()
    app.run_server(
        debug=True,
        port=configuration.port,
        host=configuration.host)
