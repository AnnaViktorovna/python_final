import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd

df = pd.read_csv("weather_data_cleaned.csv")

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('Weather Dashboard', style={'textAlign': 'center'}),

    html.Div([
        html.Label('Temperature Unit:'),
        dcc.RadioItems(
            id='temp-unit',
            options=[{'label': 'Fahrenheit', 'value': 'F'}, {'label': 'Celsius', 'value': 'C'}],
            value='F'
        ),

        html.Label('Number of cities:'),
        dcc.Slider(id='city-slider', min=10, max=50, value=20, marks={10: '10', 30: '30', 50: '50'}),

        html.Label('Weather Condition:'),
        dcc.Dropdown(
            id='condition-dropdown',
            options=[{'label': c, 'value': c} for c in df['Condition_Normalized'].unique()],
            value=df['Condition_Normalized'].unique().tolist(),
            multi=True
        )
    ], style={'padding': '1em'}),

    dcc.Graph(id='bar-chart'),
    dcc.Graph(id='pie-chart'),
    dcc.Graph(id='box-plot')
])

@app.callback(
    [Output('bar-chart', 'figure'),
     Output('pie-chart', 'figure'),
     Output('box-plot', 'figure')],
    [Input('temp-unit', 'value'),
     Input('city-slider', 'value'),
     Input('condition-dropdown', 'value')]
)
def update_graphs(temp_unit, city_count, conditions):
    filtered = df[df['Condition_Normalized'].isin(conditions)]

    temp_col = 'Temp_Numeric' if temp_unit == 'F' else 'Temp_Celsius'
    unit = '°F' if temp_unit == 'F' else '°C'

    #Bar Chart
    top_cities = filtered.nlargest(city_count, temp_col)
    fig1 = px.bar(top_cities, x='City', y=temp_col, color='Temp_Category',
                  title=f'Top {city_count} Cities by Temperature',
                  labels={temp_col: f'Temperature ({unit})'})
    fig1.update_layout(xaxis_tickangle=-45)

    #Pie Chart
    category_counts = filtered['Temp_Category'].value_counts()
    fig2 = px.pie(values=category_counts.values, names=category_counts.index,
                  title='Temperature Categories')

    #Box Plot
    fig3 = px.box(filtered, x='Condition_Normalized', y=temp_col,
                  title='Temperature by Weather Condition',
                  labels={temp_col: f'Temperature ({unit})'})

    return fig1, fig2, fig3

if __name__ == '__main__':
    app.run(debug=True)