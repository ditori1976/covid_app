from application.config import dbc, dcc, html


def comparsion_list(parser):
    comparsion = dbc.Row(
        children=[
            dbc.Col(

                children=[
                    html.Div(
                        dcc.Dropdown(
                            id="list-countries",
                            options=[
                                {"label": "World", "value": "World"},
                                {"label": "North-A.", "value": "North-A."},
                                {"label": "Europe", "value": "Europe"},
                                {"label": "Asia", "value": "Asia"},
                                {"label": "South-A.", "value": "South-A."}
                            ],
                            value=[parser.get("data", "region")],
                            multi=True,
                            placeholder="select countries on map",
                            style={
                                "width": "100%",
                                "font-size": 12,
                                "border": "none",
                                "text-align": "center"},
                            searchable=False,
                            clearable=False,
                        ),
                        id="comparsion-style"
                    )
                ],
                lg=10,
                md=9,
                xs=10,
            ),
            dbc.Col(
                children=[
                    html.Button(
                        "clear",
                        id="del",
                        style={"height": 35,
                               "font-weight": "bold",
                               "width": "100%",
                               "background-color": "#f9f9f9",
                               "border": "1px solid  #d6d6d6",
                               "color": "black",
                               "padding": "0px 0px",
                               "text-align": "center",
                               "text-decoration": "none",
                               "display": "inline - block",
                               "font-size": 16,
                               "margin": "0px 0px",
                               "cursor": "pointer"}
                    ),
                ],
                lg=2,
                md=3,
                xs=2,
                style={"text-align": "right"}

            )
        ],
        no_gutters=True,
    )
    return comparsion


def comparsion_add(title, parser):
    return dbc.Row(
        children=[
            html.Button(
                children=[title],
                id="add",
                style={"height": 35,
                       "width": "100%",
                       "background-color": parser.get("layout", "background_color_red"),
                       "border": "none",
                       "color": "#586069",
                       "padding": "0px 0px",
                       "text-align": "center",
                       "text-decoration": "none",
                       "display": "inline - block",
                       "font-size": 16,
                       "margin": "0px 0px",
                       "cursor": "pointer"}
            ),
        ],
        style={"text-align": "center", "width": "90%"}

    )
