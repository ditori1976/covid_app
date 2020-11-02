from application.__main__ import dbc, daq, html

cases_death_switch = dbc.Col(
    daq.ToggleSwitch(
        id='cases_death_switch',
        value=True,
        label=[
            {
                "label": "deaths",
                "style": {
                    "font-size": 16
                }
            },
            {
                "label": "cases",
                "style": {
                    "font-size": 16}
            }
        ],
    ),
    lg=2,
    md=2,
    xs=7
)

select_aggregation = dbc.Col(
    dbc.Row(
        [
            dbc.Col(
                html.Button(
                    "daily",
                    id="daily",
                ),
                width=4
            ),
            dbc.Col(
                html.Button(
                    "7 days",
                    id="days",
                ),
                width=4
            ),
            dbc.Col(
                html.Button(
                    "accum.",
                    id="accum",
                ),
                width=4
            )
        ],
        id="select_aggregation",
        style={"width": "100%", "margin": 0, "pading": 0},
        no_gutters=True
    ),
    lg=4,
    md=4,
    xs=11
)

select_per_capita = dbc.Col(
    daq.BooleanSwitch(
        id='select_per_capita',
        on=True,
        label=[
            {
                "label": "per capita",
                "style": {
                    "font-size": 16
                }
            }
        ],
        labelPosition="right",
        className="label"
    ),
    lg=2,
    md=2,
    xs=6
)
