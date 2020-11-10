def continent_select():
    from application.__main__ import dcc, parser, data
    return continent_select = dcc.Tabs(
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
