from application.config import dbc, dcc, daq


def controller():
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
        xs=7,
        style={'text-align': 'center', 'margin-top': '7px'}
    )

    select_aggregation = dbc.Col(
        [
            dcc.RadioItems(
                id="select_aggregation",
                options=[
                    {'label': 'daily', 'value': 'daily'},
                    {'label': '7 days', 'value': 'days'},
                    {'label': 'accum.', 'value': 'accum'}
                ],
                inputStyle={
                    'height': '22px',
                    'width': '22px',
                    'margin-top': '-3px',
                    'margin-right': '8px',
                    'vertical-align': 'middle',
                    'border': '2px solid #dbdbdb'},
                value='days',
                labelStyle={
                    'display': 'inline-block',
                    'margin-top': '3px',
                    'margin-right': '10px'}
            )
        ],
        lg=4,
        md=4,
        xs=11,
        # in CSS XXX
        style={'text-align': 'center', 'margin-top': '7px'})

    select_per_capita = dbc.Col(
        daq.BooleanSwitch(
            id='select_per_capita',
            on=True,
            label=[
                {
                    "label": "per 100.000",
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
        xs=6,
        style={'text-align': 'center', 'margin-top': '7px'}
    )
    return dbc.Row([cases_death_switch, select_aggregation,
                    select_per_capita], no_gutters=False, justify="center", style={"margin-bottom": "10px"})


def continents(parser, data):

    continents = dcc.Tabs(
        id="select-continent",
        value="Europe",  # parser.get("data", "continent"),
        vertical=True,
        children=[
            dcc.Tab(
                label=information["name"],
                value=region,
                className="continents-tab",
            )
            for region, information in data.regions.items()
        ],
        parent_className="continents-tabs",
        className="continents-tabs-container",
    )
    return continents
