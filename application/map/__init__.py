

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


def tab_map(tabs_div, map_div)


tab_map = dbc.Row(
    children=[
        dbc.Col(tabs_div, width=3),
        dbc.Col(map_div, width=9)
    ],
    no_gutters=True
)
return tab_map
