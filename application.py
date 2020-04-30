import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output, State
from tools import DataLoader, Config
from configparser import ConfigParser
import time
import json
import math
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

styles = {"pre": {"border": "thin lightgrey solid", "overflowX": "scroll"}}

parser = ConfigParser()
parser.read("settings.ini")

configuration = Config()


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


layout = dict(margin=dict(l=0, r=0, b=0, t=0, pad=0), dragmode="select")

# create app, do not forget to add necessary external stylesheets, such as dbc.themes.BOOTSTRAP
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],)

# title
title_div = dbc.Row(
    children=[
        dbc.Col(
            html.Img(src=app.get_asset_url("logo.png"), height="auto", width="70%"),
            lg=3,
            md=3,
            xs=2,
            className="style_center",
        ),
        dbc.Col(html.H1("COVID-19"), lg=9, md=9, xs=10,),
    ]
)

# sub-title
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

dropdown_div = dbc.Col(
    html.Div(
        id="selector",
        children=[dropdown],
        style={"width": "100%", "margin": 0, "padding": 0},
    ),
    xl=3,
    lg=4,
    md=5,
    xs=10,
)

# continent select via tabs
tabs_div = dbc.Col(
    children=[
        dcc.Tabs(
            id="select-continent",
            value=parser.get("data", "continent"),
            style={"height": parser.getint("layout", "height_first_row")},
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
    width=2,
    style={"margin": 0, "width": "100%"},
)

# map
fig_map = go.Figure(
    go.Choroplethmapbox(
        colorscale="BuPu",
        geojson=data.countries,
        zmin=0,
        marker={"line": {"color": "rgb(180,180,180)", "width": 0.5}},
        colorbar={"thickness": 10, "len": 0.4, "x": 0, "y": 0.3, "outlinewidth": 0,},
    )
)

fig_map.update_layout(
    autosize=False,
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
    children=[dcc.Graph(id="map", config={"displayModeBar": False}, figure=fig_map)],
    style={"height": parser.getint("layout", "height_first_row")},
    width=10,
)

# timeline
timeline_div = dbc.Col(
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
            children=[dcc.Graph(id="timeline", config={"displayModeBar": False},)]
        ),
    ],
    lg=5,
    md=10,
    xs=11,
)


# layout
body = html.Div(
    [
        dbc.Row(children=[title_div, dropdown_div], justify="center"),
        dbc.Row(
            children=[
                dbc.Col(
                    dbc.Row(
                        children=[tabs_div, map_div], justify="center", no_gutters=True,
                    ),
                    lg=5,
                    md=10,
                    xs=11,
                ),
                timeline_div,
            ],
            justify="center",
            no_gutters=True,
            style={"padding-top": parser.getint("layout", "spacer")},
        ),
        dbc.Row(
            children=[
                html.P(
                    parser.get("data", "continent"),
                    id="selected-region",
                    style={"display": "None"},
                ),
                html.P(
                    children=[], id="selected-countries", style={"display": "None"},
                ),
                html.P(children=[], id="sub-title"),
                # html.Div([html.Pre(id="relayout-data", style=styles["pre"]),]),
            ],
            justify="center",
        ),
        dbc.Row(id="update", children=[], justify="center",),
    ]
)


app.layout = body


# @app.callback(Output("relayout-data", "children"), [Input("map", "selectedData")])
# def display_relayout_data(relayoutData):
#    return json.dumps(relayoutData, indent=2)


@app.callback(
    [Output("selected-countries", "children"), Output("select-continent", "value")],
    [Input("map", "clickData")],
)
def select_countries(select_country):

    if select_country:
        region = select_country["points"][0]["text"]
        return region, []
    else:
        return dash.no_update, dash.no_update


@app.callback(
    Output("selected-region", "children"),
    [Input("select-continent", "value"), Input("selected-countries", "children")],
)
def select_region(selected_continent, selected_countries):

    selected_region = selected_countries
    if selected_continent:
        selected_region = selected_continent

    return selected_region


@app.callback(
    [Output("map", "figure"), Output("update", "children")],
    [Input("indicator-selected", "value"), Input("select-continent", "value")],
)
def draw_map(selected_indicator, selected_region):

    ctx = dash.callback_context

    print(ctx.triggered)
    if ctx.triggered[0]["value"] == []:
        print("no update")
        return dash.no_update
    else:
        print(ctx.triggered)
        if (ctx.triggered[0]["prop_id"] == "indicator-selected.value") or (
            ctx.triggered[0]["prop_id"] == "."
        ):

            indicator_name = data.indicators[selected_indicator]["name"]
            data_selected = data.latest_data(data.indicators[selected_indicator])

            fig_map.update_traces(
                locations=data_selected["iso3"],
                z=data_selected[indicator_name],
                text=data_selected["region"],
                zmax=data_selected[indicator_name]
                .replace([np.inf, -np.inf], np.nan)
                .max()
                * 0.3,
            )

        # if selected_region in list(data.regions.keys()):
        if (ctx.triggered[0]["prop_id"] == "select-continent.value") or (
            ctx.triggered[0]["prop_id"] == "."
        ):

            fig_map.update_layout(
                transition={"duration": 5000, "easing": "elastic"},
                mapbox_center=data.regions[selected_region]["center"],
                mapbox_zoom=data.regions[selected_region]["zoom"],
            )

        # else:
        #   region_data = data.latest_data("cases")[
        #       data.latest_data("cases").region == selected_region
        #    ]
        #   center = {
        #        "lon": region_data.Lon.max(),
        #        "lat": region_data.Lat.max(),
        #   }

        #   zoom = 17.5 - math.log(region_data.area.max() + 200000)

        #   fig_map.update_layout(
        #      mapbox_center=center, mapbox_zoom=zoom,
        #   )

        # fig_map.layout.uirevision = True

        return fig_map, [html.P(latest_update, style={"font-size": 8, "color": "grey"})]


@app.callback(
    Output("timeline", "figure"),
    [Input("indicator-selected", "value"), Input("selected-region", "children"),],
)
def draw_timeline(selected_indicator, selected_region):

    fig = go.Figure(go.Bar(), layout=layout)
    fig.update_layout({"plot_bgcolor": "white", "yaxis": {"side": "right"}})

    indicator_name = data.indicators[selected_indicator]["name"]
    data_selected = data.select(selected_region, data.indicators[selected_indicator])
    fig.update_traces(x=data_selected.date, y=data_selected[indicator_name])

    return fig


@app.callback(
    Output("sub-title", "children"),
    [Input("indicator-selected", "value"), Input("selected-region", "children"),],
)
def write_sub_title(selected_indicator, selected_region):
    return sub_title(selected_indicator, selected_region)


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

application = app.server


def start_multi():
    if configuration.UPDATE:
        executor = ProcessPoolExecutor(max_workers=1)
        executor.submit(get_new_data_every)


if __name__ == "__main__":

    start_multi()
    application.run(debug=True, port=configuration.port, host=configuration.host)
