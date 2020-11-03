from application.__main__ import dcc, parser, pd, go, configuration

# Create figure
fig = go.Figure(layout=configuration.layout)

fig.update_layout(
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=1,
                     label="1m"),
                dict(count=4,
                     label="4m"),
                dict(step="all"),
            ])
        ),
        rangeslider=dict(
            visible=True
        ),
        type="date"
    ),
    plot_bgcolor="white",
    yaxis=dict(side="right"),
    legend=dict(x=.1, y=.9, bgcolor='rgba(0, 0, 0, 0)',)
)

# example data
df = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv")
df.columns = [col.replace("AAPL.", "") for col in df.columns]
fig.add_trace(
    go.Scatter(x=list(df.Date), y=list(df.High)))


timeline = dcc.Graph(
    figure=fig,
    id="timeline",
    config={
        "displayModeBar": False},
    style={
        "height": str(
            parser.getint(
                "layout",
                "height_first_row")) +
        "vh",
        "width": "100%"}
)
