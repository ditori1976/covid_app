import dash_table
import numpy as np
import dash_bootstrap_components as dbc


def table(data):
    def zscore(series):
        zscore = (2 * (series - series.mean()) /
                  series.std(ddof=0)).round(0) / 2
        return zscore

    trend_data = data.latest_data(data.indicators["cases_trend"]).loc[:, [
        "region", "deaths", "cases", "recovered", "% trend (cases/7d)"]]
    trend_data.rename(
        columns={
            "% trend (cases/7d)": "trend_n",
            "region": ""},
        inplace=True)
    trend_data.loc[:, ["trend_n"]] = zscore(trend_data.loc[:, ["trend_n"]])
    trend_data.sort_values(
        by=["trend_n", "deaths"], ascending=False, inplace=True)
    trend_data.loc[:, "trend"] = np.nan
    trend_data.loc[trend_data.loc[:,
                                  "trend_n"] >= 1,
                   ["trend"]] = "↑"
    trend_data.loc[(trend_data.loc[:,
                                   "trend_n"] < 1) & (trend_data.loc[:,
                                                                     "trend_n"] >= .5),
                   ["trend"]] = "↗"
    trend_data.loc[trend_data.loc[:,
                                  "trend_n"] == 0,
                   ["trend"]] = "→"
    trend_data.loc[trend_data.loc[:,
                                  "trend_n"] <= -0.5,
                   ["trend"]] = "↘"

    table_data = trend_data.loc[trend_data.loc[:, "deaths"]
                                > 100, ["", "trend", "cases", "deaths"]]

    table = dbc.Row(
        dbc.Col(
            dash_table.DataTable(
                id="table",
                columns=[{"name": i, "id": i} for i in table_data.columns],
                data=table_data.to_dict("records"),
                style_data={'border': 'none'},
                style_header={
                    'border': 'none',
                    'backgroundColor': 'white',
                    'fontWeight': 'bold'},
                style_cell_conditional=[
                    {'if': {'column_id': ''}, 'textAlign': 'left', 'width': '8vw'},
                    {'if': {'column_id': 'trend'},
                        'textAlign': 'center', 'width': '15px', "margin": 0, "padding": 0},
                    {'if': {'column_id': ['cases', 'deaths', 'recovered']}, 'textAlign': 'center', 'width': '4vw'}],
                style_data_conditional=(
                    [
                        {'if': {'column_id': ['trend', 'cases', 'deaths'], 'filter_query': '{trend} = "↑"'},
                         'backgroundColor': '#d4bfe0', "margin": 0, "padding": 0},
                        {'if': {'column_id': ['trend', 'cases', 'deaths'], 'filter_query': '{trend} = "↗"'},
                         'backgroundColor': '#cacded', "margin": 0, "padding": 0},
                        {'if': {'column_id': ['trend', 'cases', 'deaths'], 'filter_query': '{trend} = "→"'},
                         'backgroundColor': '#c7daeb', "margin": 0, "padding": 0},
                        {'if': {'column_id': ['trend', 'cases', 'deaths'], 'filter_query': '{trend} = "↘"'},
                         'backgroundColor': '#c7ebde', "margin": 0, "padding": 0},
                        {'if': {'row_index': 'odd', 'column_id': ['']},
                         'backgroundColor': background_color_grey},
                        {
                            "if": {"state": "active"},
                            "backgroundColor": "none",
                            "border": "none",
                            "color": "black",
                        },
                        {
                            "if": {"state": "selected"},
                            "backgroundColor": "none",
                        }

                    ]
                ),
            ),
            width=11),
        no_gutters=True,
        justify="center"
    )
