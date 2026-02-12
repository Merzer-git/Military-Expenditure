import numpy as np
import plotly.graph_objects as go
from scipy.stats import t, norm
from scipy import stats
import plotly.express as px
import pandas as pd

def plot_region_critica(estadistico, alpha, tipo_h1, n=None):
    """
    Genera un gráfico de la distribución (Normal o T) sombreando la región de rechazo usando Plotly.
    """
    # 1. Definir Distribución (Normal o T)
    x = np.linspace(-4, 4, 1000)
    if n and n < 30:
        y = t.pdf(x, df=n-1)
        dist_name = f"T-Student (gl={n-1})"
        crit_val = t.ppf(1 - alpha/2, df=n-1)  # Base para dos colas
    else:
        y = norm.pdf(x)
        dist_name = "Normal Estándar (Z)"
        crit_val = norm.ppf(1 - alpha/2)

    fig = go.Figure()
    
    # Dibujar la curva base
    fig.add_trace(go.Scatter(
        x=x, y=y,
        mode='lines',
        name=dist_name,
        line=dict(color='black', width=2),
        fill='tozeroy',
        fillcolor='rgba(200, 200, 200, 0.2)'
    ))
    
    # 2. Sombrear Región de Rechazo (Roja)
    if tipo_h1 == 'Diferente (≠)':
        # Dos colas
        x_left = x[x < -crit_val]
        y_left = t.pdf(x_left, df=n-1) if n and n < 30 else norm.pdf(x_left)
        x_right = x[x > crit_val]
        y_right = t.pdf(x_right, df=n-1) if n and n < 30 else norm.pdf(x_right)
        
        fig.add_trace(go.Scatter(
            x=x_left, y=y_left,
            fill='tozeroy',
            fillcolor='rgba(255, 0, 0, 0.5)',
            line=dict(color='rgba(255, 0, 0, 0)'),
            name='Región de Rechazo'
        ))
        fig.add_trace(go.Scatter(
            x=x_right, y=y_right,
            fill='tozeroy',
            fillcolor='rgba(255, 0, 0, 0.5)',
            line=dict(color='rgba(255, 0, 0, 0)'),
            showlegend=False
        ))
    elif tipo_h1 == 'Mayor (>)':
        # Cola derecha
        limit = t.ppf(1 - alpha, df=n-1) if n and n < 30 else norm.ppf(1 - alpha)
        x_right = x[x > limit]
        y_right = t.pdf(x_right, df=n-1) if n and n < 30 else norm.pdf(x_right)
        
        fig.add_trace(go.Scatter(
            x=x_right, y=y_right,
            fill='tozeroy',
            fillcolor='rgba(255, 0, 0, 0.5)',
            line=dict(color='rgba(255, 0, 0, 0)'),
            name='Región de Rechazo'
        ))
    elif tipo_h1 == 'Menor (<)':
        # Cola izquierda
        limit = t.ppf(alpha, df=n-1) if n and n < 30 else norm.ppf(alpha)
        x_left = x[x < limit]
        y_left = t.pdf(x_left, df=n-1) if n and n < 30 else norm.pdf(x_left)
        
        fig.add_trace(go.Scatter(
            x=x_left, y=y_left,
            fill='tozeroy',
            fillcolor='rgba(255, 0, 0, 0.5)',
            line=dict(color='rgba(255, 0, 0, 0)'),
            name='Región de Rechazo'
        ))
    
    # 3. Marcar tu Estadístico (Línea Azul)
    y_max = max(y) * 1.1
    fig.add_trace(go.Scatter(
        x=[estadistico, estadistico],
        y=[0, y_max],
        mode='lines',
        name=f'Estadístico = {estadistico:.4f}',
        line=dict(color='blue', width=2, dash='dash')
    ))
    
    # Decoración
    fig.update_layout(
        title=f"Región Crítica vs Estadístico Calculado ({dist_name})",
        xaxis_title="Valor del Estadístico",
        yaxis_title="Densidad de Probabilidad",
        hovermode='x unified',
        plot_bgcolor='white',
        height=500
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    
    return fig
    
def generar_curva_teorica(datos, dist_nombre, params):
    """Generar las coordenadas X e Y para dibujar la línea suave"""
    x_min, x_max = datos.min(), datos.max()
    buffer = (x_max - x_min) * 0.1
    x_teorico = np.linspace(x_min - buffer, x_max + buffer, 1000)
    
    y_teorico= []
    
    if dist_nombre == 'Normal':
        # params= (loc, scale)
        y_teorico = stats.norm.pdf(x_teorico, *params)
    elif dist_nombre == 'Exponencial':
        y_teorico = stats.expon.pdf(x_teorico, *params)
    elif dist_nombre == 'Uniforme':
        y_teorico = stats.uniform.pdf(x_teorico, *params)
    elif dist_nombre == 'Pareto':
        y_teorico = stats.pareto.pdf(x_teorico, *params)
    
    return x_teorico, y_teorico

def plot_bondad_ajuste(datos, dist_nombre, params):
    x_linea, y_linea = generar_curva_teorica(datos, dist_nombre, params)
    
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x= datos,
        histnorm= 'probability density',
        name= 'Datos',
        marker_color= '#1f77b4',
        opacity= 0.6,
        nbinsx= 30
    ))
    
    fig.add_trace(go.Scatter(
        x= x_linea,
        y= y_linea,
        mode= 'lines',
        name= f'Distribución {dist_nombre}',
        line= dict(color= 'red', width= 3)
    ))
    
    fig.update_layout(
        title= f'Prueba de Bondad de Ajuste vs Distribución {dist_nombre}',
        xaxis_title= 'Valor de la Variable',
        yaxis_title= 'Densidad de la Probabilidad',
        template= 'plotly_white',
        bargap= 0.05,
        legend= dict(yanchor= 'top', y= 0.99, xanchor= 'right', x= 0.99)
    )
    
    return fig
    
def mapa_calor(tabla, max_valor_escala):
    fig = px.imshow(
        tabla,
        text_auto = True,
        aspect= 'auto',
        color_continuous_scale= 'Blues',
        title= 'Mapa de Calor de Frecuencias',
        range_color= [0, max_valor_escala]
    )
    return fig
    
def barras_apiladas(tabla):
    df = tabla.reset_index()
    df_melt = df.melt(id_vars= df.columns[0], var_name= 'Categoría', value_name= 'Cantidad')
    
    fig = px.bar(
        df_melt,
        x= df.columns[0],
        y= 'Cantidad',
        color= 'Categoría',
        barmode= 'group',
        text_auto= True,
        title= 'Distribución Comparativa'
    )
    
    return fig