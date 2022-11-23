import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import seaborn as sns
import numpy as np
from dash.dependencies import Output, Input


app = dash.Dash()

col_names = [
    "Date",
    "Time",
    "Tag Comment",
    "Motor Vol Flow",
    "Motor Flow In",
    "Motor Flow Out",
    "Motor Surf top",
    "Motor Surf Side",
    "Temp Pt100 RTD winding U",
    "Temp Pt100 RTD winding V",
    "Temp Pt100 RTD winding W",
    "Temp PTC thermistor winding",
    "Temp Feed-through plate",
    "Lead intersection",
    "Temp Cable gland",
    "Temp Terminal box seal",
    "Temp Terminal",
    "Temp Ambient",
    "Frequency",
    "Voltage",
    "Current",
    "Power factor",
    "Input power",
    "Output power",
    "Torque",
    "Speed",
    "Slip",
]
units = [
    "",
    "",
    "sec",
    "L/min",
    "°C",
    "°C",
    "°C",
    "°C",
    "°C",
    "°C",
    "°C",
    "°C",
    "°C",
    "°C",
    "°C",
    "°C",
    "°C",
    "°C",
    "Hz",
    "V",
    "A",
    "",
    "kW",
    "kW",
    "Nm",
    "1/min",
    "%",
]
dataframe = pd.read_excel(
    "./HDE-INT-MOT-20221028-01_HT8_03_N85z-4_OC2_50Hz_70C_R_000759_221107_100743.GEV.xlsx",
    header=32,
)
dataframe.columns = col_names
dataframe = dataframe.drop([0], axis=0)
dataframe.head(5)
dataframe["Time"] = list(np.arange(19206))
index_step_size = 1000

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="📈", className="header-emoji"),
                html.H1(children="Analytics", className="header-title"),
                html.P(
                    children="Analyze the parameter of the pump",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="X", className="menu-title"),
                        dcc.Dropdown(
                            id="x-filter",
                            options=[
                                {"label": region, "value": region}
                                for region in col_names
                            ],
                            value="Time",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children="Y", className="menu-title"),
                        dcc.Dropdown(
                            id="y-filter",
                            options=[
                                {"label": region, "value": region}
                                for region in col_names
                            ],
                            value="Temp Terminal",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
            ],
            className="menu",
        ),
        html.Div(
            children=[
                html.Div(
                    dcc.Graph(
                        id="chart",
                        config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
        dcc.Interval(
            id="interval-component", interval=1 * 2000, n_intervals=0  # in milliseconds
        ),
    ],
)


@app.callback(
    Output("chart", "figure"),
    [
        Input("x-filter", "value"),
        Input("y-filter", "value"),
        Input("interval-component", "n_intervals"),
    ],
)
def update_charts(x_col_name="Time", y_col_name="Temp Terminal", n_intervals=1):
    unit = units[col_names.index(y_col_name)]
    """
    price_chart_figure = {
        "data": [
            {
                "x": dataframe[x_col_name],
                "y": dataframe[y_col_name],
                "color": dataframe[y_col_name],
                "type": "lines",
                "hovertemplate": "%{y:.2f}" + unit + "<extra></extra>",
            },
        ],
        "layout": {
            "title": {
                "text": "Chart",
                "x": 0.05,
                "xanchor": "left",
            },
            "xaxis": {"fixedrange": True},
            "yaxis": {"tickprefix": "", "fixedrange": True},
            # "colorway": ["#F7B897"],
        },
    }
    """
    if x_col_name == "Time" and y_col_name == "Temp Terminal":
        end_index = min(len(dataframe), n_intervals * index_step_size)
        data = dataframe.iloc[:end_index, :]
        data[y_col_name] = data[y_col_name].astype(float)
        colors = [color_of_temp(v) for v in data[y_col_name]]
        price_chart_figure = px.scatter(
            data,
            x=x_col_name,
            y=y_col_name,
            color=colors,
            color_discrete_map={
                "red": "#FF0000",
                "yellow": "#FFFF00",
                "green": "#00FF00",
            },
        )
    else:
        end_index = 1000
        price_chart_figure = px.scatter(
            dataframe,
            x=x_col_name,
            y=y_col_name,
        )
    return price_chart_figure


def color_of_temp(temp):
    if temp > 80:
        return "red"
    if temp > 60:
        return "yellow"
    return "green"


def main():
    app.run_server(debug=True)


if __name__ == "__main__":
    main()
