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
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.graph_objects as go
from tools import DataLoader, Config, Style
import pandas as pd

# configuration
config = Config()
min_cases = 20000

# --- data ---
data = DataLoader()

# initialize data load
data.jhu()
data.geonames()


data_norm = pd.merge(
    data.deaths.sort_values(["region", "date"]),
    data.country_info[["iso_alpha", "population", "continent"]],
    left_on="iso3",
    right_on="iso_alpha",
    how="inner",
).drop(columns=["iso3", "iso2", "code3"])
data_norm = pd.merge(
    data_norm,
    data.confirmed.sort_values(["region", "date"])[
        ["date", "confirmed", "iso3"]],
    left_on=["iso_alpha", "date"],
    right_on=["iso3", "date"],
    how="inner",
).drop(columns=["iso3"])
data_norm = pd.merge(
    data_norm,
    data.recovered.sort_values(["region", "date"])[
        ["date", "recovered", "iso3"]],
    left_on=["iso_alpha", "date"],
    right_on=["iso3", "date"],
    how="inner",
).drop(columns=["iso3"])

data_norm.loc[:, "cases/1M capita"] = (
    data_norm.confirmed / data_norm.population * 1000000
).round(0)
data_norm.loc[:, "deaths/1M capita"] = (
    data_norm.deaths / data_norm.population * 1000000
).round(0)
data_norm.loc[:, "recovered/1M capita"] = (
    data_norm.recovered / data_norm.population * 1000000
).round(0)

data_norm.rename(columns={"confirmed": "cases"}, inplace=True)


timeseries = data_norm.groupby(["continent", "date"]).sum()

world = timeseries.groupby("date").sum()
world = pd.DataFrame(
    index=[pd.Series(data="world").repeat(len(world.index)), world.index],
    data=world.values,
    columns=world.columns,
)

timeseries = pd.concat([timeseries, world])


per_country_max = data_norm[data_norm.date == data_norm.date.max()]
per_country_max = per_country_max[per_country_max.cases > min_cases].sort_values(
    "cases")

scatter = go.Scatter(
    x=timeseries.loc["world"].index, y=timeseries.loc["world", "cases"],
)


# --- initialize elements ---
# retrieve layouts
style = Style()

# timeline
fig_timeline = go.Figure(layout=style.layout, data=[scatter])
fig_timeline.update_layout(plot_bgcolor="white",)

# dropdown
dropdown = dcc.Dropdown(
    id="value-selected",
    value="entry",
    style={"width": "100%", "margin": 0, "padding": 0},
    options=[
        {"label": "entry", "value": "entry"},
        {"label": "long entry", "value": "long_entry"},
        {"label": "very very long entry", "value": "very_long_entry"},
    ],
)

# map
# turn off legend

# map data
map_trace = go.Choroplethmapbox(
    colorscale="Oranges",
    geojson=data.countries,
    locations=per_country_max["iso_alpha"],
    z=per_country_max["cases/1M capita"],
    text=per_country_max["region"],
    zmin=0,
    zmax=2000,
    marker={"line": {"color": "rgb(180,180,180)", "width": 0.5}},
    colorbar={"thickness": 20, "len": 0.6,
              "x": 0.8, "y": 0.6, "outlinewidth": 0, },
)

layout_map = go.Layout(
    mapbox_style="mapbox://styles/dirkriemann/ck88smdb602qa1iljg6kxyavd",
    mapbox_zoom=0.2,
    mapbox_center={"lat": 25, "lon": 0},
    mapbox_accesstoken=config.mapbox,
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
)
# create map
fig_map = go.Figure(data=[map_trace], layout=layout_map,)


# create app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


header = dbc.Row(
    [
        dbc.Col(
            html.Img(src=app.get_asset_url("logo.png"),
                     height="auto", width="70%",),
            lg=3,
            md=4,
            xs=2,
            style=style.style_center,
        ),
        dbc.Col(html.H1("COVID-19"), lg=9, md=8,
                xs=7, style=style.style_center,),
    ]
)


body = html.Div(
    [
        dbc.Row(
            [
                dbc.Col([header], lg=3, md=6, xs=12),
                dbc.Col(
                    html.Div(
                        id="select-indicator",
                        children=[dropdown],
                        style={"width": "100%", "margin": 0, "padding": 0},
                    ),
                    lg=2,
                    md=6,
                    xs=10,
                    style=style.style_center,
                ),
            ],
            justify="center",
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(id="div-map",
                             children=[dcc.Graph(figure=fig_map)]),
                    lg=4,
                    md=10,
                    xs=12,
                ),
                dbc.Col(
                    html.Div(
                        id="div-timeline",
                        children=[
                            dcc.Graph(id="timeline", figure=fig_timeline), ],
                    ),
                    lg=7,
                    md=10,
                    xs=12,
                ),
            ],
            style={"padding-top": 30},
            justify="center",
        ),
    ]
)


app.layout = html.Div([body])

application = app.server
if __name__ == "__main__":
    application.run(debug=True, port=config.port, host=config.host)
