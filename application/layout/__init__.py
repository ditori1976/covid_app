import dash_core_components as dcc


def graph_template(id, parser):
    return dcc.Graph(
        id=id,
        config={
            "displayModeBar": False},
        style={"height": parser.get(
            "layout", "height_first_row") + "vh", "width": "100%"})


def continents(parser, data):

    continents = dcc.Tabs(
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
    return continents
