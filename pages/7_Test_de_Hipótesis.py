import streamlit as st
import numpy as np
import plotly.graph_objects as go
from src.datos import cargar_datos
from statsmodels.stats.weightstats import ztest
from scipy import stats
from scipy.stats import norm, t

simbolos = {
    'Diferente (≠)': r"\neq",
    'Mayor (>)': '>',
    'Menor (<)': '<'
}

mapeo_scipy = {
    'Diferente (≠)': 'two-sided',
    'Mayor (>)': 'greater',
    'Menor (<)': 'less'
}

mapeo_statmodels = {
    'Diferente (≠)': 'two-sided',
    'Mayor (>)': 'larger',
    'Menor (<)': 'smaller'
}

var_options = ['Spending_B', 'Growth_Rate', 'Per_Capita', 'Share_of_GDP', 'Share_of_Govt_Spending', 'Region']

var_porcentuales = ['Share_of_GDP', 'Share_of_Govt_Spending', 'Growth_Rate']

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


if __name__ == '__main__':
    # Inicializar session_state al inicio
    if 'calculado' not in st.session_state:
        st.session_state.calculado = False
    if 'estadistico' not in st.session_state:
        st.session_state.estadistico = 0.0
    if 'p_valor' not in st.session_state:
        st.session_state.p_valor = 0.0
    
    df = cargar_datos()
    tabs = st.tabs(['Contrastes Paramétricos', 'Constraste No Paramétricos'])


    with tabs[0]:
        cols = st.columns(2)

        with cols[0]: #COLUMNA PARA CONFIGURAR LAS HIPOTESIS
            col_variable = st.columns(2)

            with col_variable[0]:
                var_selected= st.selectbox(
                    'Variable',
                    var_options,
                    index= 0,
                    placeholder= 'Seleccione una variable...'
                )
            
            with col_variable[1]:
                year_selected= st.slider(
                    'Año',
                    min_value= 1949,
                    max_value= 2024,
                    value= 2024
                )

            df_filtrado = df[df['Year'] == year_selected].copy()
            df_filtrado = df_filtrado.dropna(subset= [var_selected])
            
            # Multiplicar por 100 las variables porcentuales
            if var_selected in var_porcentuales:
                df_filtrado[var_selected] = df_filtrado[var_selected] * 100
            

            col_muestra, col_dist = st.columns(2)
            n = len(df_filtrado)
            if n < 30:
                dist= 'T-Student'
            elif n >= 30:
                dist= 'Normal'
            
            with col_muestra:
                st.metric('Tamaño de la Muestra', n)
            with col_dist:
                if dist == 'Normal':
                    st.info(f'Muestra grande ($n>=30$). Se usará distribución ***{dist}*** (TCL)')
                elif dist == 'T-Student':
                    st.info(f'Muestra pequeña ($n<30$). Se usará distribución ***{dist}***')
                else:
                    st.warning('⚠️ Seleccione una variable y año para obtener el tamaño de la muestra a trabajar.')

                
            valor_h0= st.number_input('Hipótesis Nula ($\mu=$)', value=0.0, label_visibility= 'visible', key= 'val_hip_nula')

            tipo_h1= st.selectbox(
                'Hipótesis Alternativa',
                options= list(simbolos.keys())
            )

            alpha = st.number_input(
                'Significación',
                min_value= 0.000,
                max_value= 1.000,
                value=0.050,
                format= "%.3f",
                step= 0.001,
                label_visibility= 'visible',
                key= 'significacion',
                help= 'Probabilidad correspodiente a la **Región Crítica** de $H_0$, considerando que la $H_0$ planteada es verdadera: $P(eI)$')
            

            if st.button('Calcular', type='primary'):
                st.session_state.calculado = True
                
                # Ajustar valor H0 si es variable porcentual
                valor_h0_ajustado = valor_h0 * 100 if var_selected in var_porcentuales else valor_h0

                if dist == 'Normal':
                    stat_valor, p_valor = ztest(
                        x1= df_filtrado[var_selected],
                        x2= None,
                        value= valor_h0_ajustado,
                        alternative= mapeo_statmodels[tipo_h1]
                    )
                else:
                    stat_valor, p_valor = stats.ttest_1samp(
                        df_filtrado[var_selected],
                        popmean= valor_h0_ajustado,
                        alternative= mapeo_scipy[tipo_h1]
                    )

                st.session_state.estadistico = stat_valor
                st.session_state.p_valor = p_valor
                    

        with cols[1]:
            st.latex(fr"H_0: \mu = {valor_h0} \quad | \quad H_1: \mu {simbolos[tipo_h1]} {valor_h0}")

            if st.session_state.calculado:
                fig_test = plot_region_critica(st.session_state.estadistico, alpha, tipo_h1, n)
                st.plotly_chart(fig_test, use_container_width=True)
            else:
                st.info('Configure los parámetros y presione Calcular para visualizar el gráfico.')

            col_resultados = st.columns(2)

            if dist == 'Normal':
                label_estadistico = 'Z'
            elif dist == 'T-Student':
                label_estadistico = 't'
            else:
                label_estadistico = ''

            with col_resultados[0]:   #ESTADISTICO Y P-VALOR
                col_metricas = st.columns(2)
                if st.session_state.calculado:
                    with col_metricas[0]:
                        st.metric(
                            f'Estadístico {label_estadistico}',
                            value= f'{st.session_state.estadistico:.4f}'
                        )

                    with col_metricas[1]:
                        st.metric(
                            '*p*-Valor',
                            value= f'{st.session_state.p_valor:.4f}'
                        )

                    # st.error('')
                    # st.success('')
                else:
                    st.info('Configure los parámetros y presione Calcular.')
            with st.expander('Resultado Detallado', expanded= False):
                st.markdown('Resultados')