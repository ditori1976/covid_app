import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output


regions = {
    "World": {"name": "World", "center": {"lat": 35, "lon": 0}, "zoom": 1},
    "EU": {"name": "Europe", "center": {"lat": 50, "lon": 5}, "zoom": 2},
    "NA": {"name": "N.America", "center": {"lat": 45, "lon": -95}, "zoom": 2},
    "SA": {"name": "S.America", "center": {"lat": -20, "lon": -70}, "zoom": 1.7,},
    "AS": {"name": "Asia", "center": {"lat": 40, "lon": 90}, "zoom": 1.7},
    "AF": {"name": "Africa", "center": {"lat": 5, "lon": 20}, "zoom": 1.6},
    "OC": {"name": "Oceania", "center": {"lat": -30, "lon": 145}, "zoom": 2.2},
}

app = dash.Dash(__name__)

body = [
    dcc.Graph(id="map", config={"displayModeBar": False},),
    dcc.Tabs(
        id="continent-selected",
        value="World",
        children=[
            dcc.Tab(label=information["name"], value=region,)
            for region, information in regions.items()
        ],
    ),
]

app.layout = html.Div(body)


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
                lat=regions[selected_continent]["center"]["lat"],
                lon=regions[selected_continent]["center"]["lon"],
            ),
            pitch=0,
            zoom=regions[continent]["zoom"],
        ),
    )

    return fig


application = app.server


if __name__ == "__main__":
    application.run(debug=True)
