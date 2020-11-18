import dash_core_components as dcc


def graph_template(id, parser):
    return dcc.Graph(
        id=id,
        config={
            "displayModeBar": False},
        style={"height": parser.get(
            "layout", "height_first_row") + "vh", "width": "100%"})
