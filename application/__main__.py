import pandas as pd
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import dash_daq as daq
#
import numpy as np
from dash.dependencies import Input, Output, State, ALL, MATCH
# import time
import json
# import math
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# data
from application.data.data_loader import DataLoader

# configs
from configparser import ConfigParser
from application.config.config import Config
configuration = Config()
parser = ConfigParser()
parser.read("settings.ini")

state = configuration.state
print(state)

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
app.scripts.config.serve_locally = False
app.config.suppress_callback_exceptions = True


def get_new_data():

    global data
    global latest_update

    data = DataLoader(parser)

    data.load_data()
    latest_update = data.latest_load.strftime("%m/%d/%Y, %H:%M:%S")

    print("Data updated at " + latest_update)


get_new_data()


def timeline():
    from application.timeline import timeline
    return timeline


def tab_map():
    from application.map import tab_map
    return tab_map


def fig_map():
    from application.map import fig_map
    return fig_map


def controller():
    from application.controller import select_aggregation, select_per_capita, cases_death_switch
    return [cases_death_switch, select_aggregation, select_per_capita]


@app.callback(Output("memory", "data"),
              [Input("select_aggregation", "value"),
               Input("select_per_capita", "on"),
               Input("cases_death_switch", "value"),
               Input("select-continent", "value")])
def set_state(aggregation, per_capita, indicator, continent):
    state["aggregation"] = aggregation
    state["per capita"] = per_capita
    if indicator:
        state["indicator"] = "cases"
    else:
        state["indicator"] = "deaths"

    ctx = dash.callback_context

    if ctx.triggered[0]["prop_id"] == "select-continent.value":
        state["active"] = data.regions[continent]["name"]
        state["bbox"]["center"] = data.regions[continent]["center"]
        state["bbox"]["zoom"] = data.regions[continent]["zoom"]

    print(state)
    return state


tab_map = tab_map()
fig_map = fig_map()


@app.callback(
    Output("timeline", "figure"),
    [
        Input("memory", "data")
    ]
)
def draw_timeline(state):
    fig = go.Figure(layout=configuration.layout)
    fig.data = []
    fig.update_layout({"plot_bgcolor": "white",
                       "yaxis": {"side": "right"},
                       })
    indicator_name = data.indicators[state["indicator"]]
    data_selected = data.select(
        state["active"],
        data.indicators[state["indicator"]])
    fig.add_trace(
        go.Bar(name=state["active"],
               x=data_selected.date,
               y=data_selected[state["indicator"]]))
    for country in state["regions"]:
        fig.add_trace(
            go.Scatter(name=country,
                       x=data.select(
                           country, data.indicators[state["indicator"]]).date,
                       y=data.select(
                           country, data.indicators[state["indicator"]])[state["indicator"]]
                       )
        )

    fig.update_layout(legend=dict(x=.1, y=.9, bgcolor='rgba(0, 0, 0, 0)',))

    return fig


@app.callback(
    Output("map", "figure"),
    [Input("memory", "data")]
)
def draw_map(state):
    indicator_name = data.indicators[state["indicator"]]
    data_selected = data.latest_data(
        data.indicators[state["indicator"]])

    fig_map.update_traces(
        locations=data_selected["iso3"],
        z=data_selected[state["indicator"]],
        text=data_selected["region"],
        zmax=data_selected[state["indicator"]]
        .replace([np.inf, -np.inf], np.nan)
        .max()
        * 0.3,
    )

    fig_map.update_layout(
        mapbox_zoom=state["bbox"]["zoom"],
        mapbox_center=state["bbox"]["center"],
    )

    fig_map.layout.uirevision = True

    return fig_map


tabs_div = dcc.Tabs(
    id="timeline_map_tab",
    value="timeline_tab",
    vertical=False,
    children=[
        dcc.Tab(
            label="timeline",
            value="timeline_tab",
            className="custom-tab",
            selected_className="custom-tab--selected",
            children=[timeline()]
        ),
        dcc.Tab(
            label="map",
            value="map_tab",
            className="custom-tab",
            selected_className="custom-tab--selected",
            children=[tab_map]
        )

    ],
    parent_className="custom-tabs",
    className="custom-tabs-container",
    style={"width": "100%", "margin": 0, "padding": 0},
)


row_1 = [
    dbc.Col(
        children=[
            tabs_div,
            html.Div(id="update")
        ],
        lg=12,
        md=6,
        xs=12,
        style={'margin-bottom': '7px'})
]
row_2 = controller()


def set_layout():
    return dbc.Container(
        children=[
            dbc.Row(row_1, no_gutters=True, justify="center"),
            dbc.Row(row_2, no_gutters=False, justify="center"),
            dcc.Store(id='memory', storage_type='local'),
        ],
        fluid=True
    )


app.layout = set_layout

app.title = "COVID-19"

application = app.server

if __name__ == "__main__":

    app.run_server(
        debug=True,
        port=configuration.port,
        host=configuration.host)
