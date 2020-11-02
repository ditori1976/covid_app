from application.__main__ import dcc, dbc, daq, html

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
    lg=3,
    md=4,
    xs=11,
    style={'text-align': 'center'})

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
