from flask import Flask, render_template, request, redirect
import dash
from dash import dcc, html
import plotly.graph_objs as go
from weather_api import get_city_coordinates, get_weather_data

app = Flask(__name__)

dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dash/')

cities = []

@app.route('/', methods=['GET', 'POST'])
def index():
    global cities
    if request.method == 'POST':
        start_point = request.form['start_point']
        end_point = request.form['end_point']
        intermediate_cities = request.form.getlist('intermediate_city')
        cities = [start_point, end_point] + intermediate_cities
        return redirect('/dash/')
    return render_template('index.html')

dash_app.layout = html.Div([
    html.H1("Карта маршрута", style={'textAlign': 'center'}),
    dcc.Dropdown(
        id='days-dropdown',
        options=[
            {'label': '3 дня', 'value': 3},
            {'label': '5 дней', 'value': 5}
        ],
        value=3,
        clearable=False,
        style={'width': '50%'}
    ),
    html.Div(id='weather-graph-container', style={'width': '100%', 'height': 'auto'}),
])

@dash_app.callback(
    dash.Output("weather-graph-container", "children"),
    dash.Input("days-dropdown", "value")
)
def update_graph(days):
    graphs = []
    for city_name in cities:
        weather_data = get_weather_data(city_name, days)
        if weather_data is not None:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=weather_data['date'],
                y=weather_data['temperature'],
                mode='lines+markers',
                name=f'Температура в {city_name}'
            ))
            fig.add_trace(go.Scatter(
                x=weather_data['date'],
                y=weather_data['precipitation'],
                mode='lines+markers',
                name=f'Вероятность осадков в {city_name}'
            ))
            fig.update_layout(
                title=f'Прогноз погоды в {city_name} на {days} дней',
                xaxis_title='Дата',
                yaxis_title='Значение',
                template='plotly_white'
            )
            graphs.append(dcc.Graph(figure=fig))
    return graphs if graphs else [html.Div("Нет данных для отображения")]

if __name__ == "__main__":
    app.run(port=8000)