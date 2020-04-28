#!/usr/bin/env python3

"""
Author: Dirk Riemann, 2020

responsive map
based on dash package
with bootstrap (responsive) layout
and Mapbox map

development/debuggin mode
NOT FOR PRODUCTION
"""

# import packages
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.graph_objects as go
from tools import DataLoader, Config, Style
import pandas as pd
import numpy as np
from configparser import ConfigParser
from dash.dependencies import Input, Output, State
from datetime import date, datetime, timedelta

parser = ConfigParser()
parser.read("settings.ini")


def get_new_data():

    global data, latest_update

    data = DataLoader(parser)
    print("Data updated at " + datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
    latest_update = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")


def get_new_data_every(period=parser.getint("data", "update_interval")):

    while True:
        get_new_data()
        time.sleep(period)


get_new_data()

# configuration
config = Config()
style = Style()

indicators = data.indicators()

# layout
layout_timeline = style.layout.copy()
layout_timeline["height"] = parser.getint("layout", "height_first_row") - 20
layout_timeline["plot_bgcolor"] = "white"

# dropdown
def dropdown_options(indicators):
    options = []
    for i, j in indicators.items():
        options.append({"label": j["name"], "value": i})

    return options


# function for dropdown selector
dropdown = dcc.Dropdown(
    id="indicator-selected",
    value=parser.get("data", "init_indicator"),
    style={"width": "100%", "margin": 0, "padding": 0},
    options=dropdown_options(indicators),
)

# title
def format_title(region, indicator):
    # better use latest_data?  (need to include continents)

    data_selected = data.select(region, indicators[indicator])
    # regions = data.regions
    if region in list(data.regions.keys()):
        region = data.regions[region]["name"]
    if region == "World":
        region = "the world"

    title = "{1:.{0}f} {2} in {3} on {4}".format(
        indicators[indicator]["digits"],
        data_selected.loc[
            data_selected.date == data_selected.date.max(),
            indicators[indicator]["name"],
        ].values[0],
        indicators[indicator]["name"],
        region,
        str(data_selected.date.max().strftime("%d %b %Y")),
    )

    return title


# map
fig_map = go.Figure(
    go.Choroplethmapbox(
        colorscale="BuPu",
        geojson=data.countries,
        zmin=0,
        marker={"line": {"color": "rgb(180,180,180)", "width": 0.5}},
        colorbar={"thickness": 10, "len": 0.4, "x": 0, "y": 0.3, "outlinewidth": 0,},
        uirevision="same",
    )
)

fig_map.update_layout(
    mapbox_style="mapbox://styles/dirkriemann/ck88smdb602qa1iljg6kxyavd",
    height=parser.getint("layout", "height_first_row"),
    mapbox_accesstoken=config.mapbox,
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    geo={"fitbounds": False},
    uirevision="same",
    autosize=False,
    transition={"duration": 500},
)


def update_map(fig, indicator, continent):
    indicator_name = indicators[indicator]["name"]
    data_selected = data.latest_data(indicators[indicator])

    if continent:

        fig.update_layout(
            uirevision="same",
            mapbox_center=data.regions[continent]["center"],
            mapbox_zoom=data.regions[continent]["zoom"],
            autosize=False,
        )

    fig.update_traces(
        locations=data_selected["iso3"],
        z=data_selected[indicator_name],
        text=data_selected["region"],
        zmax=data_selected[indicator_name].replace([np.inf, -np.inf], np.nan).max()
        * 0.3,
        uirevision="same",
    )

    return fig


# timeline
timeline_trace = go.Bar()

fig_timeline = go.Figure(data=[timeline_trace], layout=layout_timeline)


def update_timeline(fig, indicator, region):
    indicator_name = indicators[indicator]["name"]
    data_selected = data.select(region, indicators[indicator])
    fig.update_traces(x=data_selected.date, y=data_selected[indicator_name])

    return fig


# create app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{"title": "COVID-19"}],
)
app.title = "COVID-19"
app.index_string = """<!DOCTYPE html>
<html lang="en">
    <head>
    <meta charset="utf-8">
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=UA-164129496-1"></script>
        <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());

        gtag('config', 'UA-164129496-1');
        </script>

        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""

header = dbc.Row(
    [
        dbc.Col(
            html.Img(src=app.get_asset_url("logo.png"), height="auto", width="70%"),
            lg=3,
            md=3,
            xs=2,
            style=style.style_center,
        ),
        dbc.Col(html.H1("COVID-19"), lg=9, md=8, xs=7, style=style.style_center,),
    ],
    justify="center",
)


body = html.Div(
    [
        dbc.Row(
            [
                dbc.Col([header], lg=3, md=6, xs=12),
                dbc.Col(
                    html.Div(
                        id="selector",
                        children=[dropdown],
                        style={"width": "100%", "margin": 0, "padding": 0},
                    ),
                    xl=3,
                    lg=4,
                    md=5,
                    xs=10,
                    style=style.style_center,
                ),
            ],
            justify="center",
        ),
        dbc.Row(
            [
                dbc.Col(
                    children=[
                        dbc.Row(
                            children=[
                                dbc.Col(
                                    [
                                        dcc.Tabs(
                                            id="continent-selected",
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
                                        )
                                    ],
                                    width=2,
                                    style={"margin": 0, "width": "100%"},
                                ),
                                dbc.Col(
                                    style={
                                        "height": parser.getint(
                                            "layout", "height_first_row"
                                        )
                                    },
                                    children=[
                                        dcc.Graph(
                                            id="map", config={"displayModeBar": False},
                                        )
                                    ],
                                    width=10,
                                ),
                            ],
                            no_gutters=True,
                        )
                    ],
                    lg=6,
                    md=10,
                    xs=11,
                ),
                dbc.Col(
                    html.Div(
                        children=[
                            html.Div(
                                children=[
                                    html.P(
                                        parser.get("data", "continent"),
                                        id="selected-series",
                                        style={"display": "None"},
                                    ),
                                    html.P(
                                        parser.get("data", "region"),
                                        id="title-region",
                                        style={"display": "None"},
                                    ),
                                    html.H5([], id="title"),
                                ],
                            ),
                            html.Div(
                                children=[
                                    dcc.Graph(
                                        id="timeline", config={"displayModeBar": False},
                                    )
                                ]
                            ),
                        ]
                    ),
                    lg=5,
                    md=10,
                    xs=11,
                ),
            ],
            style={"padding-top": parser.getint("layout", "spacer")},
            justify="center",
        ),
        dbc.Row([], justify="center",),
        dbc.Row(id="update", children=[], justify="center",),
    ]
)


app.layout = html.Div([body])


@app.callback(
    [Output("title-region", "children"), Output("continent-selected", "value"),],
    [Input("map", "clickData")],
)
def set_title_region(selected_region):

    region = parser.get("data", "region")

    if selected_region:
        region = selected_region["points"][0]["text"]

    return [region], []


@app.callback(
    [Output("selected-series", "children"),],
    [Input("title-region", "children"), Input("continent-selected", "value"),],
)
def select_display(selected_region, selected_continent):

    ctx = dash.callback_context

    trigger = ctx.triggered[0]["value"]
    # trigger_id = ctx.triggered[0]["prop_id"]

    if type(trigger) == list:
        trigger = trigger.pop()

    return [trigger]


@app.callback(
    [
        Output("title", "children"),
        Output("map", "figure"),
        Output("timeline", "figure"),
        Output("update", "children"),
    ],
    [Input("selected-series", "children"), Input("indicator-selected", "value"),],
)
def create_output(selected_region, selected_indicator):

    continent = data.timeseries[
        data.timeseries.region == selected_region
    ].continent.max()

    if selected_region not in list(data.regions.keys()):
        continent = []
    fig = update_map(fig_map, selected_indicator, continent)

    return (
        [format_title(selected_region, selected_indicator)],
        fig,
        update_timeline(fig_timeline, selected_indicator, selected_region),
        [html.P(latest_update, style={"font-size": 8, "color": "grey"})],
    )


application = app.server


def start_multi():
    if config.UPDATE:
        executor = ProcessPoolExecutor(max_workers=1)
        executor.submit(get_new_data_every)


if __name__ == "__main__":

    start_multi()
    application.run(debug=True, port=config.port, host=config.host)
