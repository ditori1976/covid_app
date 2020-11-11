import plotly.graph_objects as go


def map_fig(parser, data):

    print("initialize map")

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
            accesstoken=parser.get("map", "accesstoken"),
            style="light",
            pitch=0,
        ),
    )

    fig_map.layout.uirevision = True
    return fig_map
