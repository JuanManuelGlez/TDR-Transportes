import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Cargar el dataset
df = pd.read_csv('HRDataset_v14.csv')

# Convertir columnas de fechas a formato datetime
date_columns = ['DOB', 'DateofHire', 'DateofTermination', 'LastPerformanceReview_Date']
for col in date_columns:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')

# Inicializar la aplicación Dash
app = dash.Dash(__name__)

# Layout de la aplicación
app.layout = html.Div([
    html.H1("Tablero Interactivo de HR"),
    
    html.Label("Selecciona el tipo de gráfico:"),
    dcc.Dropdown(
        id='chart-type',
        options=[
            {'label': 'Gráfico de Barras', 'value': 'bar'},
            {'label': 'Gráfico de Dispersión', 'value': 'scatter'},
            {'label': 'Gráfico de Líneas', 'value': 'line'}
        ],
        value='bar'
    ),
    
    html.Label("Selecciona la variable X:"),
    dcc.Dropdown(
        id='x-axis',
        options=[{'label': col, 'value': col} for col in df.columns],
        value='Department'
    ),
    
    html.Label("Selecciona la variable Y:"),
    dcc.Dropdown(
        id='y-axis',
        options=[{'label': col, 'value': col} for col in df.columns],
        value='Salary'
    ),
    
    dcc.Graph(id='graph'),
    
    html.Div(id='graph-legend', style={'marginTop': 20})
])

# Callback para actualizar el gráfico y la leyenda
@app.callback(
    [Output('graph', 'figure'),
     Output('graph-legend', 'children')],
    [Input('chart-type', 'value'),
     Input('x-axis', 'value'),
     Input('y-axis', 'value')]
)
def update_graph_and_legend(chart_type, x_axis, y_axis):
    title = f"Gráfico de {chart_type.capitalize()}: {x_axis} vs {y_axis}"
    
    if chart_type == 'bar':
        fig = px.bar(df, x=x_axis, y=y_axis, title=title, color=x_axis,
                     labels={x_axis: x_axis.replace('_', ' '), y_axis: y_axis.replace('_', ' ')},
                     color_discrete_sequence=px.colors.qualitative.Plotly)
    elif chart_type == 'scatter':
        fig = px.scatter(df, x=x_axis, y=y_axis, title=title, color=x_axis,
                         labels={x_axis: x_axis.replace('_', ' '), y_axis: y_axis.replace('_', ' ')},
                         color_discrete_sequence=px.colors.qualitative.Plotly)
    elif chart_type == 'line':
        # Ordenar por la columna x_axis si es una fecha
        if pd.api.types.is_datetime64_any_dtype(df[x_axis]):
            df_sorted = df.sort_values(by=x_axis)
        else:
            df_sorted = df.copy()
        
        fig = px.line(df_sorted, x=x_axis, y=y_axis, title=title,
                      labels={x_axis: x_axis.replace('_', ' '), y_axis: y_axis.replace('_', ' ')},
                      color_discrete_sequence=px.colors.qualitative.Plotly)
    
    fig.update_layout(
        title={'x': 0.5},
        template='plotly_white',
        xaxis_title=x_axis.replace('_', ' '),
        yaxis_title=y_axis.replace('_', ' '),
        title_font_size=24,
        title_font_color='darkblue',
        title_x=0.5,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        plot_bgcolor='rgba(240, 240, 240, 0.5)'
    )
    
    legend_text = f"Este gráfico muestra la relación entre '{x_axis}' y '{y_axis}' utilizando un gráfico de tipo '{chart_type}'."
    
    return fig, legend_text

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)

#--------------------------------------------------------------------------------
#Link del Video: https://drive.google.com/file/d/1Tvmkj9VSZJkmkfxLs-VzvsWEzWFNJDI0/view?usp=sharing
#Usa la cuenta del tec para poder acceder al video
#--------------------------------------------------------------------------------