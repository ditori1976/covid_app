from application.config import Config, logger, daq, dbc, dcc, html
from application.controller import controller
from application.comparsion import comparsion_list

from dash import Dash, callback_context, no_update
#import dash_core_components as dcc
#import dash_bootstrap_components as dbc
# import dash_html_components as html
from dash.dependencies import Input, Output, State, ALL, MATCH, ClientsideFunction
from configparser import ConfigParser
import json

# configs
configuration = Config()
parser = ConfigParser()
parser.read("settings.ini")

state = configuration.state

row_1 = dbc.Col(
    children=[
        html.H1("Countries Comparsion COVID-19"),
        controller(),
        comparsion_list(parser),
    ],
    lg=11,
    md=11,
    sm=11,
    xs=12,
    style={'margin-bottom': '10px'})

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[
        {
            "name": "viewport",
            "content": "width=device-width, initial-scale=1.0"
        }
    ]
)
app.title = "COVID-19"


def set_layout():
    return dbc.Container(
        children=[
            dbc.Row(row_1, no_gutters=True, justify="center"),
            # dbc.Row(row_2, no_gutters=False, justify="center"),
            html.Div(
                id="state",
                children=json.dumps(state),
                # style={'display': 'None'}
            )
        ],
        fluid=True
    )


app.layout = set_layout

application = app.server
if __name__ == "__main__":

    app.run_server(
        debug=True,
        port=configuration.port,
        host=configuration.host)
