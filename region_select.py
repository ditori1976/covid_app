import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output
from tools import DataLoader
from configparser import ConfigParser

parser = ConfigParser()
parser.read("settings.ini")

data = DataLoader(parser)

layout = dict(margin=dict(l=0, r=0, b=0, t=0, pad=0), dragmode="select")

# create app, do not forget to add necessary external stylesheets, such as dbc.themes.BOOTSTRAP
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],)

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
        )
    ]
)


app.layout = body


@app.callback(Output("map", "figure"), [Input("continent-selected", "value")])
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

    return fig


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
    application.run(debug=True)
