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

# constants
index_step_size = 1000
step_time = 2000

default_x_name = "Time"
default_y_name = "Input power"

message_text = {
    "green": "läuft bei der Pumpe",
    "yellow": "Ey, mach mal was!",
    "red": "Es ist kritisch!!!",
    "blank": "",
}

color_codes = {
    "red": "#d94800",
    "yellow": "#ffd105",
    "green": "#88dc08",
    "gray": "#A0A0A0",
}

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="📈", className="header-emoji"),
                html.H1(
                    children="Predictive Maintainance Dashboard",
                    className="header-title",
                ),
                html.P(
                    children="Dashboard for the Visualization of all Pump Sensors. The Traffic Light indicates the possible states of the Pump: ok, warning, critical",
                    className="header-description",
                ),
                html.Div(
                    children=[
                        html.Div(
                            id="green-light",
                            className="traffic-light-single",
                            style={"backgroundColor": color_codes["green"]},
                        ),
                        html.Div(
                            id="yellow-light",
                            className="traffic-light-single",
                            style={"backgroundColor": color_codes["yellow"]},
                        ),
                        html.Div(
                            id="red-light",
                            className="traffic-light-single",
                            style={"backgroundColor": color_codes["red"]},
                        ),
                    ],
                    className="traffic-light-container",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="X:", className="menu-title"),
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
                    ],
                    className="menu-item-container",
                ),
                dcc.Input(
                    id="var_x_name",
                    type="hidden",
                    value=default_x_name,
                ),
                html.Div(
                    children=[
                        html.Div(children="Y:", className="menu-title"),
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
                    ],
                    className="menu-item-container",
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
                    children=[
                        dcc.Graph(
                            id="chart",
                            config={"displayModeBar": False},
                        ),
                    ],
                    className="card",
                ),
                html.Div(
                    id="gif-card",
                    children=[html.Img(id="gif", src="./assets/tempterminal.gif")],
                    className="card",
                    style={
                        "display": "none",
                    },
                ),
            ],
            className="wrapper",
        ),
        dcc.Interval(
            id="interval-component",
            interval=step_time,
            n_intervals=0,  # in milliseconds
        ),
    ],
)


@app.callback(
    [
        Output("chart", "figure"),
        Output("interval-component", "n_intervals"),
        Output("var_x_name", "value"),
        Output("var_y_name", "value"),
        Output("gif", "src"),
        Output("gif-card", "style"),
        Output("green-light", "style"),
        Output("yellow-light", "style"),
        Output("red-light", "style"),
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
    n_result = n_intervals
    if x_col_name != old_x_name or y_col_name != old_y_name:
        n_result = 0

    end_index = min(len(dataframe), n_result * index_step_size)
    data = dataframe.iloc[:end_index, :]
    data[y_col_name] = [float(e) if e != "INVALID" else 0 for e in data[y_col_name]]

    gif_src = "./assets/tempterminal.gif"

    if x_col_name == "Time" and y_col_name == "Temp Terminal":
        colors = [color_of_temp(v) for v in data[y_col_name]]
        price_chart_figure = px.scatter(
            data,
            x=x_col_name,
            y=y_col_name,
            color=colors,
            color_discrete_map=color_codes,
            labels={
                "Time": "Time (sec)",
                "Temp Terminal": "Temp Terminal " + unit,
                "green": "Ok",
            },
        )
        temp_gif_style = {"display": "block"}
    elif x_col_name == "Time" and y_col_name == "Input power":
        colors = [color_of_power(v) for v in data[y_col_name]]
        price_chart_figure = px.scatter(
            data,
            x=x_col_name,
            y=y_col_name,
            color=colors,
            color_discrete_map=color_codes,
            labels={
                "Time": "Time (sec)",
                "Input Power": "Input Power " + unit,
                "green": "Ok",
            },
        )
        temp_gif_style = {"display": "block"}
        gif_src = "./assets/inputpower.gif"
    else:
        colors = []
        price_chart_figure = px.scatter(
            data,
            x=x_col_name,
            y=y_col_name,
        )
        temp_gif_style = {"display": "none"}

    green_style, yellow_style, red_style = get_light_styles(n_result, colors)

    return (
        price_chart_figure,
        n_result,
        x_col_name,
        y_col_name,
        gif_src,
        temp_gif_style,
        green_style,
        yellow_style,
        red_style,
    )


def get_light_styles(n_result, colors):
    green_style = inactive_light_style("green")
    yellow_style = inactive_light_style("yellow")
    red_style = inactive_light_style("red")

    end_index = min(len(dataframe), n_result * index_step_size)
    data = dataframe.iloc[:end_index, :]
    data["Temp Terminal"] = [
        float(e) if e != "INVALID" else 0 for e in data["Temp Terminal"]
    ]

    last_color = colors[-1] if len(colors) > 0 else "green"
    last_temp_color = (
        color_of_temp(data["Temp Terminal"][len(data["Temp Terminal"]) - 1])
        if len(data["Temp Terminal"]) > 0
        else "green"
    )
    # colors = [color_of_temp(v) for v in data["Temp Terminal"]] + colors
    if last_color == "red" or last_temp_color == "red":
        light_color = "red"
    elif last_color == "yellow" or last_temp_color == "yellow":
        light_color = "yellow"
    else:
        light_color = "green"
    if light_color == "red":
        red_style = active_light_syle("red")
    elif light_color == "yellow":
        yellow_style = active_light_syle("yellow")
    else:
        green_style = active_light_syle("green")
    return green_style, yellow_style, red_style


def active_light_syle(name):
    return {"backgroundColor": color_codes[name], "borderColor": color_codes[name]}


def inactive_light_style(name):
    return {"backgroundColor": "#444", "borderColor": color_codes["gray"]}


def color_of_temp(temp):
    if temp > 80:
        return "red"
    if temp > 60:
        return "yellow"
    return "green"


def color_of_power(p):
    if p > 300:
        return "red"
    if p > 250:
        return "yellow"
    return "green"


def main():
    app.run_server(debug=True)


if __name__ == "__main__":
    main()
