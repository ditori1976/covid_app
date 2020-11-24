from dash_table import DataTable
import numpy as np
import dash_bootstrap_components as dbc


def table(data, selected_rows=[]):

    table = DataTable(
        id="datatable",
        columns=[
            {"name": i, "id": i, "deletable": False, "selectable": False} for i in data.columns
        ],
        data=data.to_dict('records'),
        # editable=True,
        # filter_action="native",
        sort_action="native",
        sort_mode="multi",
        # column_selectable="single",
        # row_selectable="multi",
        # row_deletable=True,
        # selected_columns=[],
        selected_rows=[1],
        page_action="native",
        page_current=0,
        page_size=10,
        style_cell_conditional=[
            {'if': {'column_id': 'region'},
             'width': '35%'},
            {'if': {'column_id': 'continent'},
             'width': '25%'},
            {'if': {'column_id': 'deaths'},
             'width': '20%'},
            {'if': {'column_id': 'cases'},
                'width': '20%'},

        ],
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ],
        style_header={
            'backgroundColor': 'white',
            'fontWeight': 'bold'
        },
        style_cell={'textAlign': 'left',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                    'maxWidth': 0},
    )
    return table
