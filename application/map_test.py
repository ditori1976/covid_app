import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, ClientsideFunction

app = dash.Dash(__name__)

fig_data = {
    "data": [{"type": "bar", "x": [1, 2, 3], "y": [1, 3, 2]}],
    "layout": {"title": {"text": ""}}
}

app.layout = html.Div([
    dcc.Store("fig-data", data=fig_data),
    dcc.Graph(id="graph"),
    dcc.Dropdown(
        id="city",
        options=[{'label': z, "value": z} for z in ["Sydney", "Montreal"]],
        value="Sydney"
    )
])

app.clientside_callback(
    ClientsideFunction("clientside", "figure"),
    Output(component_id="graph", component_property="figure"),
    [Input("fig-data", "data"), Input("city", "value")],
)

if __name__ == "__main__":

    app.run_server(
        debug=True)
