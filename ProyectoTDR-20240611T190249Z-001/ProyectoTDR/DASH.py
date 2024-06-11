
import base64
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from dash.dcc import *
from dash.dependencies import Input, Output

# Paletas de colores
logoTDR = ["#20448C", "#1B3059", "#F2B705", "#F29F05"]
logoLIVER = ["#A64985", "#8C3F71", "#F27830", "#D9763D", "#B9B9B9"]
monocromaticosTDR = ["#465E8C", "#1B3059", "#8699BF", "#B3CCFF"]
monocromaticosLIVER = ["#a64985", "#b4639b", "#c17db0", "#cf96c5", '#ebc9ec']

# Cargar los datos
file_path = 'CostoPrevisto_vs_CostoReal.xlsx'
df = pd.read_excel(file_path)
df2 = pd.read_excel('dispach_ordenesidentificadas.xlsx')

# Crear una nueva columna para la ruta
df['Ruta'] = df['Municipo origen'] + ' - ' + df['Municipo destino']
df2['Ruta'] = df2['Municipo origen'] + ' - ' + df2['Municipo destino']

# Agrupar por número de orden y ruta para obtener el número de viajes
df_grouped = df.groupby(['Numero de orden', 'Ruta']).first().reset_index()
ruta_viajes = df_grouped['Ruta'].value_counts().reset_index()
ruta_viajes.columns = ['Ruta', 'No. de viajes']

# Sumar el kilometraje por ruta
ruta_kilometros = df_grouped.groupby('Ruta')['Millas totales'].sum().reset_index()
ruta_kilometros.columns = ['Ruta', 'Kilometraje']

# Sumar el costo de las casetas por ruta
ruta_costo = df_grouped.groupby('Ruta')['Costo previsto'].sum().reset_index()
ruta_costo.columns = ['Ruta', 'Costo Total']

# Gráficas adicionales
df['Fecha'] = pd.to_datetime(df['Fecha'])

df_real = df[['Fecha', 'Costo Real']].copy()
df_real['Tipo de Costo'] = 'Costo Real'
df_real.rename(columns={'Costo Real': 'Costo'}, inplace=True)
df_real = df_real.groupby(['Fecha', 'Tipo de Costo']).sum().reset_index()

df_previsto = df[['Fecha', 'Costo previsto']].copy()
df_previsto['Tipo de Costo'] = 'Costo Previsto'
df_previsto.rename(columns={'Costo previsto': 'Costo'}, inplace=True)
df_previsto = df_previsto.groupby(['Fecha', 'Tipo de Costo']).sum().reset_index()

df_combined = pd.concat([df_real, df_previsto])
fig_comparacion = px.line(df_combined, x='Fecha', y='Costo', color='Tipo de Costo',
                          title='Comparación de Costo Real vs Costo Previsto', color_discrete_sequence=['#A64985', '#F27830'])

df_faltante = df[['Fecha', 'Faltante']].copy()
df_faltante = df_faltante.groupby(pd.Grouper(key='Fecha', freq='D')).sum().reset_index()
fig_faltante = px.line(df_faltante, x='Fecha', y='Faltante', title='Faltante a través del tiempo', color_discrete_sequence=logoLIVER)

fig_faltante_signo = px.bar(df, x='Fecha', y='Faltante',
                            color=df['Faltante'].apply(lambda x: 'Positivo' if x > 0 else 'Negativo'), color_discrete_map={'Positivo': '#A64985', 'Negativo': '#F27830'},
                            title='Faltante a través del tiempo con colores por signo', color_discrete_sequence=logoLIVER)

fig_faltante_sistema = px.bar(df, x='Fecha', y='Faltante',
                              color=df['Faltante'].apply(lambda x: 'Positivo' if x > 0 else 'Negativo'),
                              color_discrete_map={'Positivo': '#A64985', 'Negativo': '#F27830'},
                              title='Faltante a través del tiempo con colores por signo y filtro por Sistema',
                              facet_col='Sistema')

grouped_df = df.groupby('RUTA NUMERO', as_index=False)['Faltante'].sum()
top_5_faltante = grouped_df.nlargest(5, 'Faltante')
fig_top5_faltante = px.bar(top_5_faltante, x='RUTA NUMERO', y='Faltante',
                           color='RUTA NUMERO', color_discrete_sequence=logoLIVER,
                           title='Top 5 RUTA NUMERO con Mayor Faltante')

# Asegurarnos de que la paleta monocromática se aplique correctamente y se eliminen los gaps
fig_top5_faltante.update_layout(
    xaxis=dict(
        type='category',
        categoryorder='total descending'
    ),
    showlegend=False
)
fig_top5_faltante.update_traces(marker=dict(color=logoLIVER))

# Iniciar la aplicación Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

test_png = 'TDR.png'
test_base64 = base64.b64encode(open(test_png, 'rb').read()).decode('ascii')

# Layout de la aplicación
app.layout = html.Div([
    html.Div(
        style={
            'padding': '5px',
            'textAlign': 'center',
            'backgroundColor': '#20448C'
        },
        children=[
            html.Img(
                src='data:image/png;base64,{}'.format(test_base64),
                style={
                    'width': '15%',  # Cambia el valor a tu tamaño deseado
                    'height': 'auto'  # Mantiene la proporción de la imagen
                }
            )
        ]
    ),
    html.H1('Dashboard Interactivo', style={'color': 'white', 'text-align': 'center', 'backgroundColor': '#20448C'}),
    dbc.Tabs([
        dbc.Tab(
            label='Rutas',
            children=[
                html.Div(
                    children=[
                        html.H2('Rutas con más viajes', style={'color': 'white', 'text-align': 'center', 'backgroundColor': '#20448C'}),
                        dcc.Graph(
                            id='bar-chart-viajes',
                            figure=px.bar(
                                ruta_viajes,
                                x='Ruta',
                                y='No. de viajes',
                                title='Rutas con más viajes',
                                color='Ruta',
                                color_discrete_sequence=logoLIVER
                            )
                        ),html.H2('Rutas con más kilómetros', style={'color': 'white', 'text-align': 'center', 'backgroundColor': '#20448C'}),
                        dcc.Graph(
                            id='bar-chart-kilometros',
                            figure=px.bar(
                                ruta_kilometros,
                                x='Ruta',
                                y='Kilometraje',
                                title='Rutas con más kilómetros',
                                color='Ruta',
                                color_discrete_sequence=logoLIVER
                            )
                        )
                    ],
                    style={'backgroundColor': '#FFDD00'}  # Fondo amarillo para el contenido de la pestaña
                )
            ],
            tab_id='rutas',
            label_style={'backgroundColor': '#FFDD00'}  # Fondo amarillo para la pestaña en sí
        ),
        dbc.Tab(
            label='Comparación',
            children=[
                html.Div([
                    html.H2('Costo total por ruta', style={'color': 'white', 'text-align': 'center', 'backgroundColor': '#20448C'}),
                    dcc.Graph(
                        id='bar-chart-costo',
                        figure=px.bar(ruta_costo, x='Ruta', y='Costo Total', title='Costo total por ruta', color='Ruta',
                                      color_discrete_sequence=logoLIVER)
                    ),
                    html.H2('Boxplot de Costos de Caseta', style={'color': 'white', 'text-align': 'center', 'backgroundColor': '#20448C'}),
                    dcc.Graph(
                        id='boxplot-costo',
                        figure=px.box(df2, x='Ruta', y='Costo Caseta', title='Costos de Caseta por Ruta', color='Ruta',
                                      color_discrete_sequence=logoLIVER)
                    )
                ],style={'backgroundColor': '#FFDD00'} )
            ],
            tab_id='Comparación',
            label_style={'backgroundColor': '#FFDD00'}
        ),
        dbc.Tab(
            label='Implementación mejoras',
            children=[
                html.Div([
                    html.H2('Comparación de Costo Real vs Costo Previsto', style={'color': 'white', 'text-align': 'center', 'backgroundColor': '#20448C'}),
                    dcc.Graph(
                        id='line-chart-costos',
                        figure=fig_comparacion
                    ),
                    html.H2('Faltante a través del tiempo', style={'color': 'white', 'text-align': 'center', 'backgroundColor': '#20448C'}),
                    dcc.Graph(
                        id='line-chart-faltante',
                        figure=fig_faltante
                    ),
                    html.H2('Faltante con colores por signo', style={'color': 'white', 'text-align': 'center', 'backgroundColor': '#20448C'}),
                    dcc.Graph(
                        id='bar-chart-faltante-signo',
                        figure=fig_faltante_signo
                    ),

                    html.H2('Top 5 RUTA NUMERO con Mayor Faltante', style={'color': 'white', 'text-align': 'center', 'backgroundColor': '#20448C'}),
                    dcc.Graph(
                        id='bar-chart-top5-faltante',
                        figure=fig_top5_faltante
                    ),
                    html.H2('Faltante con colores por signo y filtro por Sistema', style={'color': 'white', 'text-align': 'center', 'backgroundColor': '#20448C'}),
                    dcc.Dropdown(
                        id='sistema-dropdown',
                        options=[{'label': sistema, 'value': sistema} for sistema in df['Sistema'].unique()],
                        value=df['Sistema'].unique()[0]
                    ),

                    dcc.Graph(id='bar-chart-faltante-sistema')
                ], style={'backgroundColor': '#FFDD00'}
                )
            ],
            #tab_id='Comparación',
            label_style={'backgroundColor': '#FFDD00'}
        )
    ])
])

# Callbacks para actualizar las gráficas
@app.callback(
    Output('bar-chart-faltante-sistema', 'figure'),
    [Input('sistema-dropdown', 'value')]
)
def update_faltante_sistema(selected_sistema):
    filtered_df = df[df['Sistema'] == selected_sistema]
    fig = px.bar(filtered_df, x='Fecha', y='Faltante',
                 color=filtered_df['Faltante'].apply(lambda x: 'Positivo' if x > 0 else 'Negativo'),
                 color_discrete_map={'Positivo': '#A64985', 'Negativo': '#F27830'},
                 title=f'Faltante a través del tiempo con colores por signo ({selected_sistema})')
    return fig

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)



# In[ ]:




