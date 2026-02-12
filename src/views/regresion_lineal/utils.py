import pandas as pd
import numpy as np
import plotly.graph_objects as go

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