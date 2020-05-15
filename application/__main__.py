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

# refactoring config/layout/stlyes
configuration = Config()
layout = dict(margin=dict(l=0, r=0, b=0, t=0, pad=0), dragmode="select")
style_full = {
    "height": "100%",
    "width": "100%",
    "paddingLeft": "0px",
    "paddingTop": "0px",
    "paddingRight": "0px",
    "paddingBottom": "0px"
}
style_todo = {"display": "inline", "margin": "10px"}

parser = ConfigParser()
parser.read("settings.ini")


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

# title
title_div = dbc.Row(
    children=[
        dbc.Col(
            html.Img(
                src=app.get_asset_url("logo.png"),
                height="auto",
                width="70%"),
            lg=4,
            md=4,
            xs=3,
            className="style_center",
        ),
        # dbc.Col(html.H1("COVID-19"), lg=9, md=9, xs=0,),
    ]
)

# dropdown


def dropdown_options(indicators):
    options = []
    for i, j in indicators.items():
        options.append({"label": j["name"], "value": i})

    return options


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


# continent select via tabs
tabs_div = dbc.Col(
    children=[
        dcc.Tabs(
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
        ),
    ],
    lg=3,
    xs=3,
    style=style_full,
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

fig_map.layout.uirevision = True

map_div = dbc.Col(
    children=[
        dcc.Graph(
            id="map",
            config={
                "displayModeBar": False},
            style={"height": "45vh", "width": "100%"}
        )],
    lg=9,
    xs=9,
    style=style_full,

)

# timeline
timeline_div = dbc.Col(
    children=[
        html.Div(
            children=[
                # html.P(
                #     parser.get("data", "continent"),
                #     id="selected-series",
                #     style={"display": "None"},
                # ),
                # html.P(
                #     parser.get("data", "region"),
                #     id="title-region",
                #     style={"display": "None"},
                # ),
                html.H5([], id="title"),
            ],
        ),
        html.Div(
            children=[
                dcc.Graph(
                    id="timeline",
                    config={
                        "displayModeBar": False},
                    style={"height": "35vh", "width": "100%"}
                )]
        ),
    ],
    width=12,
)

# compare
compare_div = html.Div(
    [
        html.Button("add to comparsion", id="add"),
        html.Button("clear", id="clear"),
        html.Div(id="list-countries"),
    ]
)

# subtitle


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
# info update


# layout
body = dbc.Container(
    id="outer_container",
    children=[
        dbc.Container(
            [
                dbc.Row(
                    children=[
                        dbc.Col(
                            dbc.Row(
                                children=[tabs_div, map_div], justify="center", no_gutters=True,
                            ),
                            lg=5,
                            md=10,
                            xs=12,
                        ),
                        dbc.Col([
                            dropdown_div,
                            html.P(
                                children=[], id="sub-title", style={"textAlign": "center"}),
                            timeline_div, ],
                            lg=5,
                            md=10,
                            xs=11,
                            align="center"
                        )
                    ],
                    justify="center",
                    no_gutters=True,
                    style={
                        "paddingTop": parser.getint(
                            "layout", "spacer")},
                )
            ],
            style=style_full,
        ),
        # hidden elements & subtitle
        dbc.Row(
            children=[
                html.P(
                    parser.get("data", "continent"),
                    id="selected-region",
                    style={"display": "None"},
                ),
                html.P(
                    children=[],
                    id="selected-countries",
                    style={"display": "None"},
                ),

            ],
            justify="center",
        ),
        dbc.Row(
            id="update",
            children=[],
            justify="center"
        ),
        dbc.Row(
            dbc.Col(
                compare_div,
                lg=5,
                xs=11),
            justify="center",
            # style={"display": "none"}
        )
    ],
    style=style_full)


app.layout = html.Div(id="outer_div", children=[body],
                      style=style_full)


@app.callback(
    Output("update", "children"),
    [Input("select-continent", "value"),
     ],
)
def submit_date(submit):

    return [
        html.P(
            data.latest_load.strftime("%m/%d/%Y, %H:%M:%S"),
            style={"fontSize": 8, "color": "grey"}
        )
    ]


@app.callback(
    Output("list-countries", "children"),
    [
        Input("add", "n_clicks"),
        Input("clear", "n_clicks"),
    ],
    [
        State("selected-region", "children"),
        State({"index": ALL}, "children"),
        State({"index": ALL, "type": "done"}, "value"),
    ],
)
def edit_list(add, clear, add_country, items, items_done):

    triggered = [t["prop_id"] for t in dash.callback_context.triggered]
    adding = len([1 for i in triggered if i in (
        "add.n_clicks", "add_country.n_submit")])
    clearing = len([1 for i in triggered if i == "clear.n_clicks"])

    new_spec = [
        (text, done) for text, done in zip(items, items_done) if not (clearing and not done)
    ]
    if adding:
        new_spec.append((add_country, ["done"]))
    new_list = [
        html.Div(
            [
                dcc.Checklist(
                    id={"index": i, "type": "done"},
                    options=[{"label": "", "value": "done"}],
                    value=done,
                    style={"display": "inline"},
                    labelStyle={"display": "inline"},
                ),
                html.Div(
                    text, id={"index": i}, style=style_todo
                ),
            ],
            style={"clear": "both"},
        )
        for i, (text, done) in enumerate(new_spec)
    ]
    return new_list


@app.callback(
    [Output("selected-countries", "children"),
     Output("select-continent", "value")],
    [Input("map", "clickData")],
)
def select_countries(select_country):

    if select_country:
        region = select_country["points"][0]["text"]
        return region, None
    else:
        return dash.no_update, dash.no_update


@app.callback(
    Output("selected-region", "children"),
    [Input("select-continent", "value"),
     Input("selected-countries", "children")],
)
def select_region(selected_continent, selected_countries):

    selected_region = selected_countries
    if selected_continent:
        selected_region = selected_continent

    return selected_region


@app.callback(
    Output("map", "figure"),
    [Input("indicator-selected", "value"), Input("select-continent", "value")],
)
def draw_map(selected_indicator, selected_region):

    ctx = dash.callback_context

    if (ctx.triggered[0]["value"] is None) and (
        ctx.triggered[0]["prop_id"] == "select-continent.value"
    ):
        return dash.no_update
    else:

        if (ctx.triggered[0]["prop_id"] == "indicator-selected.value") or (
            ctx.triggered[0]["prop_id"] == "."
        ):
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
            fig_map.layout.uirevision = True

        if (ctx.triggered[0]["prop_id"] == "select-continent.value") or (
            ctx.triggered[0]["prop_id"] == "."
        ):
            fig_map.update_layout(
                mapbox_center=data.regions[selected_region]["center"],
                mapbox_zoom=data.regions[selected_region]["zoom"],
            )
            fig_map.layout.uirevision = False

        return fig_map


@app.callback(
    Output("timeline", "figure"),
    [Input("indicator-selected", "value"),
     Input("selected-region", "children"), ],
)
def draw_timeline(selected_indicator, selected_region):

    fig = go.Figure(go.Bar(), layout=layout)
    fig.update_layout({"plot_bgcolor": "white",
                       "yaxis": {"side": "right"},
                       })  # "transition": {"duration": 500}

    indicator_name = data.indicators[selected_indicator]["name"]
    data_selected = data.select(
        selected_region,
        data.indicators[selected_indicator])
    fig.update_traces(x=data_selected.date, y=data_selected[indicator_name])

    return fig


@app.callback(
    Output("sub-title", "children"),
    [Input("indicator-selected", "value"),
     Input("selected-region", "children"), ],
)
def write_sub_title(selected_indicator, selected_region):
    return sub_title(selected_indicator, selected_region)


app.title = "COVID-19"
app.index_string = """<!DOCTYPE html>
<html lang="en">
    <head>
    <meta charset="utf-8">
    <meta name="viewport">
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
