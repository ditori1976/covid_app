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
        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        column_selectable="single",
        row_selectable="multi",
        row_deletable=True,
        selected_columns=[],
        selected_rows=[1],
        page_action="native",
        page_current=0,
        page_size=10,
    )
    return table
