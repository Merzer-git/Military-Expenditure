import pandas as pd
import numpy as np
from scipy import stats
import plotly.graph_objects as go
import plotly.express as px

def plot_regresion_lineal(df, col_x, col_y):
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x= df[col_x],
        y= df['ci_alto'],
        mode= 'lines',
        line= dict(width=0),
        showlegend= False,
        hoverinfo= 'skip'
    ))
    
    fig.add_trace(go.Scatter(
        x= df[col_x],
        y= df['ci_bajo'],
        mode= 'lines',
        line= dict(width=0),
        fill= 'tonexty',
        fillcolor= 'rgba(255,0,0,0.15)',
        name= 'Intervalo de Confianza 95%',
        hoverinfo= 'skip'
    ))
    
    fig.add_trace(go.Scatter(
        x= df[col_x],
        y= df[col_y],
        mode= 'markers',
        name= 'Datos Observados',
        marker= dict(color= '#3498db', opacity=0.7)
    ))
    
    fig.add_trace(go.Scatter(
        x= df[col_x],
        y= df['prediccion_media'],
        mode= 'lines',
        name= 'Regresión Ajustada',
        line= dict(color= 'red', width=2)
    ))
    
    fig.update_layout(
        title= f'Regresión Lineal con IC 95%: {col_x} vs {col_y}',
        xaxis_title= col_x,
        yaxis_title= col_y,
        template= 'plotly_white',
        hovermode= 'x unified'
    )
    
    return fig
    
def plot_histograma_residuos(residuos):
    mu, std = stats.norm.fit(residuos)
    xmin, xmax = residuos.min(), residuos.max()
    x_norm = np.linspace(xmin, xmax, 100)
    p_norm = stats.norm.pdf(x_norm, mu, std)
    n_datos = len(residuos)
    ancho_barra = (xmax - xmin) / 20
    y_norm = p_norm * n_datos * ancho_barra
    
    fig = px.histogram(
        x= residuos,
        nbins= 20,
        title= 'Distribución de los Errores (Residuos)',
        labels= {'x': 'Valor del Residuo', 'y': 'Frecuencia'},
        color_discrete_sequence= ['#4B8BBE']
    )
    fig.add_vline(x=0, line_dash= 'dash', line_color= 'red', annotation_text= 'Media = 0')
    fig.add_scatter(
        x= x_norm,
        y= y_norm,
        mode= 'lines',
        name= 'Distribución Normal Teórica',
        line= dict(
            color= 'orange',
            width= 2
        ))
    
    return fig
    
def plot_dispersion_datos(valores_x, residuos, var_x, varianza_Se):
    fig = px.scatter(
        x= valores_x,
        y= residuos,
        title= f'Dispersión de Residuos vs {var_x}',
        labels= {'x': var_x, 'y': 'Residuos'},
        color_discrete_sequence= ['#4B8BBE']    
    )
    fig.add_hline(y=0, line_dash= 'dash', line_color= 'red')
    fig.add_hline(y=2*varianza_Se, line_dash= 'dot', line_color= 'orange', annotation_text= '+2Se')
    fig.add_hline(y=-2*varianza_Se, line_dash= 'dot', line_color= 'orange', annotation_text= '-2Se')
    
    return fig