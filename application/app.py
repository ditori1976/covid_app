from application.config import Config, logger, daq, dbc, dcc, html, go, DataTable
from application.controller import controller, continents
from application.comparsion import comparsion_list
from application.timeline import timeline
from application.table import table
from application.map import map_fig
from application.layout import graph_template
from application.data.data_loader import DataLoader

from dash import Dash, callback_context, no_update
from dash.dependencies import Input, Output, State, ALL, MATCH, ClientsideFunction
from configparser import ConfigParser
import json
import numpy as np

# configs
configuration = Config()
parser = ConfigParser()
parser.read("settings.ini")

data = DataLoader(parser)
# data.countries_geojson()
# data.read_geonames_country_info()
data.load_geo()
data.load_data()


state = configuration.state

map_figure = map_fig(parser, data)
map_graph = graph_template("map", parser)
map_graph.figure = map_figure

continent_div = continents(parser, data)

timeline_tab = graph_template("timeline", parser)

table_data = data.map_data(True, "days", ["deaths", "cases"])[
    ["region", "continent", "deaths", "cases"]]

map_tab = dbc.Row(
    children=[
        dbc.Col(map_graph,
                lg=10,
                md=9,
                xs=12,),
        dbc.Col(
            children=[
                continent_div
            ],
            lg=2,
            md=3,
            xs=12,)
    ],
    no_gutters=True
)

row_1 = dbc.Col(
    children=[
        html.H1("Country Comparsion COVID-19"),
        html.H3(
            "Course of COVID-19 cases and fatalities. Pick countries from map or continents from list"),
        comparsion_list(parser)
    ],
    lg=11,
    md=11,
    sm=11,
    xs=12,
    style={'margin-bottom': '10px'})

row_2 = dbc.Col(
    children=[
        map_tab,
        controller(),
        timeline_tab
    ],
    lg=11,
    md=11,
    sm=11,
    xs=12,
    style={'margin-bottom': '7px'})

row_3 = dbc.Col(
    children=[
        html.Div(id="table", children=[table(table_data)]),
    ],
    lg=7,
    md=8,
    sm=9,
    xs=12,
    style={'margin-bottom': '7px'})

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[
        {
            "name": "viewport",
            "content": "width=device-width, initial-scale=1.0"
        }
    ]
)
app.title = "COVID-19"


def set_layout():
    return dbc.Container(
        children=[
            dbc.Row(row_1, no_gutters=True, justify="center"),
            dbc.Row(row_2, no_gutters=False, justify="center"),
            dbc.Row(row_3, no_gutters=False, justify="center"),
            html.Div(
                id="state",
                children=json.dumps(state),
                style={'display': 'None'}
            )
        ],
        fluid=True
    )


app.layout = set_layout

"""
callbacks
"""


@app.callback(
    Output("table", "children"),
    [
        Input("state", "children")
    ])
def update_table(state):
    state = json.loads(state)
    data_table = data.map_data(state["per capita"], state["aggregation"], ["deaths", "cases"])[
        ["region", "continent", "deaths", "cases"]].sort_values(by=state["indicator"], ascending=False)
    return table(data_table, selected_rows=state["regions"])


@app.callback(
    Output("state", "children"),
    [
        Input("select-continent", "value"),
        Input("map", "clickData"),
        Input("list-countries", "value"),
        Input("cases_death_switch", "value"),
        Input("select_per_capita", "on"),
        Input("select_aggregation", "value"),
        Input("del", "n_clicks")
    ],
    [State("state", "children"),
     State("map", "figure")])
def update_state(continent, country, regions, indicator,
                 per_capita, aggregation, clear, state, map_figure):

    state = json.loads(state)

    logger.info(country)
    logger.info(regions)

    # neccessary?
    if map_figure:
        lat = map_figure["layout"]["mapbox"]["center"]["lat"]
        lon = map_figure["layout"]["mapbox"]["center"]["lon"]
        zoom = map_figure["layout"]["mapbox"]["zoom"]
        state["bbox"]["center"]["lat"] = lat
        state["bbox"]["center"]["lon"] = lon
        state["bbox"]["zoom"] = zoom
    else:
        state["bbox"]["center"] = data.regions[continent]["center"]
        state["bbox"]["zoom"] = data.regions[continent]["zoom"]

    if callback_context.triggered[0]["prop_id"] == "select-continent.value":
        if not continent == "":
            state["active"] = data.regions[continent]["name"]
            state["bbox"]["center"] = data.regions[continent]["center"]
            state["bbox"]["zoom"] = data.regions[continent]["zoom"]
    if callback_context.triggered[0]["prop_id"] == "map.clickData":
        state["active"] = country["points"][0]["text"]
    if callback_context.triggered[0]["prop_id"] == "del.n_clicks":
        state["active"] = ""

    state["regions"] = regions

    if indicator:
        state["indicator"] = "cases"
    else:
        state["indicator"] = "deaths"

    state["per capita"] = per_capita
    state["aggregation"] = aggregation

    if regions == []:
        state["active"] = []

    logger.info(json.dumps(state))

    return json.dumps(state)


@app.callback(
    Output("map", "figure"),
    [
        Input("state", "children")
    ])
def draw_map(state):
    state = json.loads(state)

    indicator_name = state["indicator"]

    data_selected = data.map_data(
        state["per capita"],
        state["aggregation"],
        state["indicator"])

    # replace in DataLoader
    map_figure.update_traces(
        locations=data_selected["iso3"],
        z=data_selected[indicator_name],
        text=data_selected["region"],
        zmax=data_selected[indicator_name]
        .replace([np.inf, -np.inf], np.nan)
        .max()
        * 0.3,
    )

    map_figure.update_layout(
        mapbox_zoom=state["bbox"]["zoom"],
        mapbox_center=state["bbox"]["center"],
    )

    map_figure.layout.uirevision = True

    return map_figure


@app.callback(
    [Output("list-countries", "options"),
     Output("list-countries", "value"), ],
    [
        Input("select-continent", "value"),
        Input("map", "clickData"),
        Input("del", "n_clicks")
    ],
    [
        State("list-countries", "options"),
        State("list-countries", "value")
    ],
)
def edit_list(continent, country, delete, list_countries,
              list_countries_values):
    region = parser.get("data", "region")
    # logger.info(country)
    # logger.info(list_countries_values)

    if callback_context.triggered[0]["prop_id"] == "select-continent.value":
        if not continent == "":
            region = data.regions[continent]["name"]
    if callback_context.triggered[0]["prop_id"] == "map.clickData":
        region = country["points"][0]["text"]

    if callback_context.triggered[0]["prop_id"] == "del.n_clicks":
        return [], []
    if region:
        if region not in list_countries_values:
            list_countries.append(
                {'label': region, 'value': region})
            list_countries_values.append(region)

        return list_countries, list_countries_values
    else:
        return [], []


@app.callback(
    Output("timeline", "figure"),
    [
        Input("state", "children")
    ]
)
def draw_timeline(state):
    state = json.loads(state)

    timeline_figure = timeline(configuration)

    regions = set(state["active"]) | set(state["regions"])
    for country in regions:
        data_selected = data.series(
            country,
            state["per capita"],
            state["aggregation"],
            state["indicator"])
        timeline_figure.add_trace(
            go.Scatter(name=country,
                       x=data_selected.date,
                       y=data_selected[state["indicator"]]
                       )
        )

    return timeline_figure


application = app.server
if __name__ == "__main__":

    app.run_server(
        debug=True,
        port=configuration.port,
        host=configuration.host)
