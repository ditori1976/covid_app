from application import dcc, parser

timeline = dcc.Graph(
    id="timeline",
    config={
        "displayModeBar": False},
    style={
        "height": str(
            parser.getint(
                "layout",
                "height_first_row") -
            10) +
        "vh",
        "width": "100%"}
)
