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
layout = dict(margin=dict(l=0, r=0, b=0, t=0, pad=0), dragmode="select")
style_todo = {"display": "inline", "margin": "10px"}

parser = ConfigParser()
parser.read("settings.ini")


state = {
    "indicators": ["{}".format(parser.get("data", "init_indicator"))],
    "regions": ["World"],
    "active": "World",
    "axis": {
        "x": "date",
        "y": "linear"
    },
    "bbox": {
        "center": {
            "lat": 0,
            "lon": 0,
        },
        "zoom": 2
    }
}


def get_new_data():

    global data
    global latest_update

    data = DataLoader(parser)

    data.load_data()
    latest_update = data.latest_load.strftime("%m/%d/%Y, %H:%M:%S")

    print("Data updated at " + latest_update)


def update_data(period=parser.getint("data", "update_interval")):
    while True:
        get_new_data()
        time.sleep(period)


get_new_data()


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
app.scripts.append_script({
    "external_url": "https://www.googletagmanager.com/gtag/js?id=UA-164129496-1"
})


def dropdown_options(indicators):
    options = []
    for i, j in indicators.items():
        options.append({"label": j["name"], "value": i})

    return options


def sub_title(indicator, region):

    data_selected = data.select(region, data.indicators[indicator])
    latest_value = data_selected.loc[
        data_selected.date == data_selected.date.max(),
        data.indicators[indicator]["name"],
    ].max()
    if region in list(data.regions.keys()):
        region = data.regions[region]["name"]
    if region == "World":
        region = "the world"

    title = "{1:.{0}f} {2} in {3} on {4}".format(
        data.indicators[indicator]["digits"],
        latest_value,
        data.indicators[indicator]["name"],
        region,
        str(data_selected.date.max().strftime("%d %b %Y")),
    )
    return title


dropdown = dcc.Dropdown(
    id="indicator-selected",
    value=parser.get("data", "init_indicator"),
    style={"width": "100%", "margin": 0, "padding": 0},
    options=dropdown_options(data.indicators),
    searchable=False,
    clearable=False,
    className="stlye_center",
)

dropdown_div = dbc.Row(dbc.Col(
    id="selector",
    children=[dropdown],
    style={
        "width": "100%",
        "margin": 0,
        "padding": 0,
        "textAlign": "center"},
    lg=7, xs=11,
), justify="center")


tabs_div = dcc.Tabs(
    id="select-continent",
    value=parser.get("data", "continent"),
    vertical=True,
    children=[
        dcc.Tab(
            label=information["name"],
            value=region,
            className="custom-tab",
            selected_className="custom-tab--selected",
        )
        for region, information in data.regions.items()
    ],
    parent_className="custom-tabs",
    className="custom-tabs-container",
    style={"width": "100%", "margin": 0, "padding": 0},
)


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

fig_map.layout.uirevision = True

map_div = dcc.Graph(
    id="map",
    config={
        "displayModeBar": False},
    style={"height": parser.get(
        "layout", "height_first_row") + "vh", "width": "100%"}
)

timeline = dcc.Graph(
    id="timeline",
    config={
        "displayModeBar": False},
    style={
        "height": str(
            parser.getint(
                "layout",
                "height_first_row") -
            10) +
        "vh",
        "width": "100%"}
)

timeline_title = dbc.Col(
    children=[
        html.Div(
            children=[
                html.H5([], id="title"),
            ],
        ),
        html.Div(
            children=[
                timeline
            ]
        ),
    ],
    width=12,
)


tab_map = dbc.Row(
    children=[
        dbc.Col(tabs_div, width=3),
        dbc.Col(map_div, width=9)
    ],
    no_gutters=True
)

dropdown_title_timeline = dbc.Col(
    children=[
        dropdown_div,
        html.P(
            id="sub-title",
            children=[],
            style={"textAlign": "center"}
        ),
        timeline_title,

    ]
)

comparsion = dbc.Row(
    children=[
        dbc.Col(
            children=[
                html.Button(
                    "add",
                    id="add",
                    style={"height": 35,
                           "width": "100%",
                           "background-color": "#f9f9f9",
                           "border": "none",
                           "color": "#586069",
                           "padding": "0px 0px",
                           "text-align": "center",
                           "text-decoration": "none",
                           "display": "inline - block",
                           "font-size": 16,
                           "margin": "0px 0px",
                           "cursor": "pointer"}
                ),
            ],
            width=3,
            style={"text-align": "right"}

        ),
        dbc.Col(
            children=[
                dcc.Dropdown(
                    id="list-countries",
                    options=[
                        {"label": "World", "value": "World"},
                        {"label": "North-A.", "value": "North-A."},
                        {"label": "Europe", "value": "Europe"},
                        {"label": "Asia", "value": "Asia"},
                        {"label": "South-A.", "value": "South-A."}],
                    value=["Europe", "North-A.", "South-A.", "Asia"],
                    multi=True,
                    placeholder="for comparsion",
                    style={"width": "100%", "font-size": 12, "border": "none"},
                    searchable=False,
                )
            ],
            width=9
        )
    ],
    no_gutters=True,
)

row_1 = [
    dbc.Col(tab_map, lg=5, md=6, xs=12),
    dbc.Col(dropdown_title_timeline, lg=6, md=6, xs=12)
]
row_2 = [
    dbc.Col(comparsion, lg=5, md=6, xs=12),
    dbc.Col(id="empty", lg=6, md=6, xs=12)
]
row_3 = [
    dbc.Col(id="update", lg=6, md=6, xs=12)
]


def set_layout():
    return dbc.Container(
        children=[
            dbc.Row(row_1, no_gutters=True, justify="center"),
            dbc.Row(row_2, no_gutters=True, justify="center"),
            dbc.Row(row_3, no_gutters=True, justify="center"),
            dcc.Store(id='memory', data=state),
        ],
        fluid=True
    )


app.layout = set_layout


@app.callback(
    Output('memory', 'data'),
    [
        Input("map", "clickData"),
        Input("select-continent", "value"),
        Input("indicator-selected", "value"),
        Input("list-countries", "value")
    ],
    [
        State("map", "figure"),
        State("list-countries", "value"),
        State('memory', 'data')
    ]
)
def change_state(map_select, tab_select, indicator_select,
                 add, figure, list_countries, state):
    print(map_select, tab_select, indicator_select,
          add, list_countries)

    if figure:
        lat = figure["layout"]["mapbox"]["center"]["lat"]
        lon = figure["layout"]["mapbox"]["center"]["lon"]
        zoom = figure["layout"]["mapbox"]["zoom"]
        state["bbox"]["center"]["lat"] = lat
        state["bbox"]["center"]["lon"] = lon
        state["bbox"]["zoom"] = zoom
    else:
        state["bbox"]["center"] = data.regions[tab_select]["center"]
        state["bbox"]["zoom"] = data.regions[tab_select]["zoom"]

    ctx = dash.callback_context

    if ctx.triggered[0]["prop_id"] == "select-continent.value":
        state["active"] = data.regions[tab_select]["name"]
        state["bbox"]["center"] = data.regions[tab_select]["center"]
        state["bbox"]["zoom"] = data.regions[tab_select]["zoom"]
    elif ctx.triggered[0]["prop_id"] == "map.clickData":
        state["active"] = map_select["points"][0]["text"]
    elif ctx.triggered[0]["prop_id"] == "indicator-selected.value":
        state["indicators"][0] = indicator_select

    # if ctx.triggered[0]["prop_id"] == "list-countries.value":
    state["regions"] = list_countries

    # print(state)

    return state


@app.callback(
    Output("timeline", "figure"),
    [
        Input("memory", "data")
    ]
)
def draw_timeline(state):
    fig = go.Figure(layout=layout)
    fig.data = []
    fig.update_layout({"plot_bgcolor": "white",
                       "yaxis": {"side": "right"},
                       })
    indicator_name = data.indicators[state["indicators"][0]]["name"]
    data_selected = data.select(
        state["active"],
        data.indicators[state["indicators"][0]])
    fig.add_trace(
        go.Bar(name=state["active"],
               x=data_selected.date,
               y=data_selected[indicator_name]))
    for country in state["regions"]:
        fig.add_trace(
            go.Scatter(name=country,
                       x=data.select(
                           country, data.indicators[state["indicators"][0]]).date,
                       y=data.select(
                           country, data.indicators[state["indicators"][0]])[indicator_name]
                       )
        )

    fig.update_layout(legend=dict(x=.1, y=.9, bgcolor='rgba(0, 0, 0, 0)',))

    return fig


@app.callback(
    Output("sub-title", "children"),
    [Input("memory", "data")])
def write_sub_title(state):
    return sub_title(state["indicators"][0], state["active"])


@app.callback(
    Output("map", "figure"),
    [Input("memory", "data")]
)
def draw_map(state):

    indicator_name = data.indicators[state["indicators"][0]]["name"]
    data_selected = data.latest_data(
        data.indicators[state["indicators"][0]])

    fig_map.update_traces(
        locations=data_selected["iso3"],
        z=data_selected[indicator_name],
        text=data_selected["region"],
        zmax=data_selected[indicator_name]
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


@app.callback(
    Output("update", "children"),
    [Input("select-continent", "value"),
     ],
)
def submit_date(submit):

    return [
        html.P("last update: " +
               data.latest_load.strftime("%m/%d/%Y, %H:%M:%S"),
               style={"fontSize": 8, "color": "grey"}
               )
    ]


@app.callback(
    [Output("list-countries", "options"),
     Output("list-countries", "value"), ],
    [
        Input("add", "n_clicks"),
    ],
    [
        State("memory", "data"),
        State("list-countries", "options"),
        State("list-countries", "value")
    ],
)
def edit_list(add, state,
              list_countries, list_countries_values):
    print(state)

    if add:
        if state["active"] not in list_countries_values:
            list_countries.append(
                {'label': state["active"], 'value': state["active"]})
            list_countries_values.append(state["active"])

        return list_countries, list_countries_values

    else:

        return dash.no_update, dash.no_update


app.title = "COVID-19"

application = app.server


# def start_multi():
executor = ThreadPoolExecutor(max_workers=1)
executor.submit(update_data)


if __name__ == "__main__":

    # start_multi()
    app.run_server(
        debug=True,
        port=configuration.port,
        host=configuration.host)
