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

default_x_name = "Time"
default_y_name = "Temp Terminal"

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
                            value=default_x_name,
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                dcc.Input(
                    id="var_x_name",
                    type="hidden",
                    value=default_x_name,
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
                            value=default_y_name,
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                dcc.Input(
                    id="var_y_name",
                    type="hidden",
                    value=default_y_name,
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
    [
        Output("chart", "figure"),
        Output("interval-component", "n_intervals"),
        Output("var_x_name", "value"),
        Output("var_y_name", "value"),
    ],
    [
        Input("x-filter", "value"),
        Input("y-filter", "value"),
        Input("var_x_name", "value"),
        Input("var_y_name", "value"),
        Input("interval-component", "n_intervals"),
    ],
)
def update_charts(
    x_col_name=default_x_name,
    y_col_name=default_y_name,
    old_x_name=None,
    old_y_name=None,
    n_intervals=1,
):
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
    n_result = n_intervals + 1
    if x_col_name != old_x_name or y_col_name != old_y_name:
        n_result = 0

    end_index = min(len(dataframe), n_result * index_step_size)
    data = dataframe.iloc[:end_index, :]
    data[y_col_name] = data[y_col_name].astype(float)
    if x_col_name == "Time" and y_col_name == "Temp Terminal":
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
        price_chart_figure = px.scatter(
            data,
            x=x_col_name,
            y=y_col_name,
        )

    return price_chart_figure, n_result, x_col_name, y_col_name


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
