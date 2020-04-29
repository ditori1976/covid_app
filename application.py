import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output
from tools import DataLoader, Config
from configparser import ConfigParser

parser = ConfigParser()
parser.read("settings.ini")

configuration = Config()

data = DataLoader(parser)

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
    options=dropdown_options(data.indicators()),
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
            id="continent-selected",
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

# draw map
map_div = dbc.Col(
    children=[dcc.Graph(id="map", config={"displayModeBar": False})],
    style={"height": parser.getint("layout", "height_first_row")},
    width=10,
)

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
            children=[html.H4(children=["World"], id="selected-regions")],
            justify="center",
        ),
    ]
)


app.layout = body


@app.callback(
    [Output("map", "figure"), Output("selected-regions", "children")],
    [Input("continent-selected", "value")],
)
def select_bbox(selected_continent):

    if selected_continent:
        continent = selected_continent

    fig = go.Figure(go.Choroplethmapbox(colorscale="BuPu",))

    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0, "pad": 0},
        mapbox=go.layout.Mapbox(
            accesstoken="pk.eyJ1IjoiZGlya3JpZW1hbm4iLCJhIjoiY2szZnMyaXoxMDdkdjNvcW5qajl3bzdkZCJ9.d7njqybjwdWOxsnxc3fo9w",
            style="light",
            center=go.layout.mapbox.Center(
                lat=data.regions[selected_continent]["center"]["lat"],
                lon=data.regions[selected_continent]["center"]["lon"],
            ),
            pitch=0,
            zoom=data.regions[continent]["zoom"],
        ),
    )

    return fig, [continent]


@app.callback(Output("timeline", "figure"), [Input("continent-selected", "value")])
def draw_timeline(region):

    fig = go.Figure(go.Bar(), layout=layout)
    fig.update_layout({"plot_bgcolor": "white"})
    indicator_name = data.indicators()["cases"]["name"]
    data_selected = data.select(region, data.indicators()[indicator_name])
    fig.update_traces(x=data_selected.date, y=data_selected[indicator_name])
    return fig


application = app.server


if __name__ == "__main__":

    application.run(debug=True, port=configuration.port, host=configuration.host)
