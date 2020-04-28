import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.graph_objects as go
from tools import DataLoader, Config, Style
import pandas as pd
from configparser import ConfigParser
from dash.dependencies import Input, Output
from datetime import date, datetime, timedelta

parser = ConfigParser()
parser.read("settings.ini")

config = Config()


def get_new_data():
    global data, latest_update

    data = DataLoader(parser)
    latest_update = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")


def get_new_data_every(period=parser.getint("data", "update_interval")):
    while True:
        get_new_data()
        time.sleep(period)


get_new_data()

indicators = data.indicators()

# layout
# layout_timeline = style.layout.copy()
# layout_timeline["height"] = parser.getint("layout", "height_first_row") - 20
# layout_timeline["plot_bgcolor"] = "white"

# dropdown
"""def dropdown_options(indicators):
    options = []
    for i, j in indicators.items():
        options.append({"label": j["name"], "value": i})

    return options"""


# function for dropdown selector
"""dropdown = dcc.Dropdown(
    id="indicator-selected",
    value=parser.get("data", "init_indicator"),
    style={"width": "100%", "margin": 0, "padding": 0},
    options=dropdown_options(indicators),
)"""

# title
"""def format_title(region, indicator):
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
"""

# map
"""layout_map = go.Layout(
    mapbox_style="mapbox://styles/dirkriemann/ck88smdb602qa1iljg6kxyavd",
    height=parser.getint("layout", "height_first_row"),
    mapbox_accesstoken=config.mapbox,
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
)
map_trace = go.Choroplethmapbox(
    colorscale="BuPu",
    geojson=data.countries,
    zmin=0,
    marker={"line": {"color": "rgb(180,180,180)", "width": 0.5}},
    colorbar={"thickness": 10, "len": 0.4, "x": 0, "y": 0.3, "outlinewidth": 0,},
    # uirevision="same",
)

fig_map = go.Figure(data=[map_trace], layout=layout_map)"""


def bbox(continent):

    if continent:
        fig = go.Figure(
            go.Choroplethmapbox(
                colorscale="BuPu",
                geojson=data.countries,
                zmin=0,
                marker={"line": {"color": "rgb(180,180,180)", "width": 0.5}},
                # colorbar={
                #    "thickness": 10,
                #    "len": 0.4,
                #    "x": 0,
                #    "y": 0.3,
                #    "outlinewidth": 0,
                # },
                # uirevision="same",
            )
        )
        # fig.update_layout(mapbox_center=data.regions["NA"]["center"])
        fig.update_layout(
            # height=parser.getint("layout", "height_first_row"),
            # margin=go.layout.Margin(b=10, t=10),
            # mapbox_style="mapbox://styles/dirkriemann/ck88smdb602qa1iljg6kxyavd",
            # autosize=False,
            margin={"r": 0, "t": 0, "l": 0, "b": 0, "pad": 0},
            # transition={"duration": 500},
            # geo={"fitbounds": False},
            template="plotly",
            mapbox=go.layout.Mapbox(
                accesstoken=config.mapbox,
                style="light",
                # The direction you're facing, measured clockwise as an angle from true north on a compass
                bearing=0,
                center=go.layout.mapbox.Center(
                    lat=data.regions[continent]["center"]["lat"],
                    lon=data.regions[continent]["center"]["lon"],
                ),
                pitch=0,
                zoom=data.regions[continent]["zoom"],
            )
            # mapbox_center=data.regions[continent]["center"],
        )

    return fig


# fig_map = bbox(fig_map, "World")


"""def update_map(fig, indicator, continent):
    indicator_name = indicators[indicator]["name"]
    data_selected = data.latest_data(indicators[indicator])

    if continent:

        fig.update_layout(
            mapbox_center=data.regions[continent]["center"],
            mapbox_zoom=data.regions[continent]["zoom"],
        )
        #print(data.regions[continent]["center"])
    else:
        fig.update_layout(uirevision="same",)

    fig.update_traces(
        locations=data_selected["iso3"],
        z=data_selected[indicator_name],
        text=data_selected["region"],
        zmax=data_selected[indicator_name].replace([np.inf, -np.inf], np.nan).max()
        * 0.3,
    )

    return fig"""


# timeline
"""timeline_trace = go.Bar()

fig_timeline = go.Figure(data=[timeline_trace], layout=layout_timeline)


def update_timeline(fig, indicator, region):
    indicator_name = indicators[indicator]["name"]
    data_selected = data.select(region, indicators[indicator])
    fig.update_traces(x=data_selected.date, y=data_selected[indicator_name])

    return fig
"""

# create app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{"title": "COVID-19"}],
)

'''app.title = "COVID-19"
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
'''
"""header = dbc.Row(
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
)"""


body = html.Div(
    [
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
                                                )
                                                for region, information in data.regions.items()
                                            ],
                                        )
                                    ],
                                    width=2,
                                ),
                                dbc.Col(
                                    children=[
                                        html.Div(
                                            dcc.Graph(
                                                style={
                                                    "height": parser.getint(
                                                        "layout", "height_first_row"
                                                    )
                                                },
                                                id="map",
                                                config={"displayModeBar": False},
                                            )
                                        )
                                    ],
                                    width=6,
                                ),
                            ],
                            # no_gutters=True,
                        )
                    ],
                    lg=6,
                    md=10,
                    xs=11,
                ),
            ],
            style={"padding-top": parser.getint("layout", "spacer")},
            justify="center",
        ),
        dbc.Row([], justify="center",),
        #       dbc.Row(id="update", children=[], justify="center",),
    ]
)


app.layout = html.Div([body])


@app.callback(Output("map", "figure"), [Input("continent-selected", "value")])
def select_bbox(selected_continent):
    continent = "World"
    if selected_continent:
        continent = selected_continent

    fig = go.Figure(
        go.Choroplethmapbox(
            colorscale="BuPu",
            # geojson=data.countries,
            # zmin=0,
            # marker={"line": {"color": "rgb(180,180,180)", "width": 0.5}},
            # colorbar={
            #    "thickness": 10,
            #    "len": 0.4,
            #    "x": 0,
            #    "y": 0.3,
            #    "outlinewidth": 0,
            # },
            # uirevision="same",
        )
    )
    # fig.update_layout(mapbox_center=data.regions["NA"]["center"])
    fig.update_layout(
        # height=parser.getint("layout", "height_first_row"),
        # margin=go.layout.Margin(b=10, t=10),
        # mapbox_style="mapbox://styles/dirkriemann/ck88smdb602qa1iljg6kxyavd",
        # autosize=False,
        # margin={"r": 0, "t": 0, "l": 0, "b": 0, "pad": 0},
        # transition={"duration": 500},
        # geo={"fitbounds": False},
        mapbox=go.layout.Mapbox(
            accesstoken=config.mapbox,
            style="light",
            # The direction you're facing, measured clockwise as an angle from true north on a compass
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=data.regions[continent]["center"]["lat"],
                lon=data.regions[continent]["center"]["lon"],
            ),
            pitch=0,
            zoom=data.regions[continent]["zoom"],
        )
        # mapbox_center=data.regions[continent]["center"],
    )
    # fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0, "pad": 0},)

    return fig


"""@app.callback(
    [Output("title-region", "children"), Output("continent-selected", "value"),],
    [Input("map", "clickData")],
)
def set_title_region(selected_region):

    region = parser.get("data", "region")

    if selected_region:
        region = selected_region["points"][0]["text"]

    return [region], []
"""


# dash.no_update  # bbox(fig_map, continent)


"""
@app.callback(
    [
        Output("title", "children"),
        Output("map", "figure"),
        Output("timeline", "figure"),
        Output("update", "children"),
    ],
    [Input("selected-series", "children"), Input("indicator-selected", "value"),],
)
def select_display(selected_region, selected_indicator):

    continent = data.timeseries[
        data.timeseries.region == selected_region
    ].continent.max()

    if selected_region not in list(data.regions.keys()):
        continent = []

    print(selected_region, selected_indicator, continent)

    return (
        [format_title(selected_region, selected_indicator)],
        update_map(fig_map, selected_indicator, continent),
        update_timeline(fig_timeline, selected_indicator, selected_region),
        [html.P(latest_update, style={"font-size": 8, "color": "grey"})],
    )

"""
application = app.server


def start_multi():
    if config.UPDATE:
        executor = ProcessPoolExecutor(max_workers=1)
        executor.submit(get_new_data_every)


if __name__ == "__main__":

    start_multi()
    application.run(debug=True, port=config.port, host=config.host)
