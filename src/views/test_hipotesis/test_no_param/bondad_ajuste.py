import streamlit as st
import pandas as pd
from src.views.test_hipotesis.pruebas.tests import shapiro_wilk
from src.views.test_hipotesis.pruebas.tests import kolmogorov_smirnov
from src.views.test_hipotesis.utils import plot_bondad_ajuste

var_options = ['Spending_B', 'Growth_Rate', 'Per_Capita', 'Share_of_GDP', 'Share_of_Govt_Spending']
dist_options = ['Normal', 'Uniforme', 'Exponencial', 'Pareto']
var_porcentuales = ['Share_of_GDP', 'Share_of_Govt_Spending', 'Growth_Rate']

def render_bondad_ajuste(df):
    """Lógica completa de la pestaña No Paramétricos (BONDAD DE AJUSTE)"""
    if 'no_param_calculado' not in st.session_state:
        st.session_state.no_param_calculado = False
    if 'no_param_estadistico' not in st.session_state:
        st.session_state.no_param_estadistico = 0.0
    if 'no_param_p_valor' not in st.session_state:
        st.session_state.no_param_p_valor = 0.0
    
    if 'no_param_calculado' not in st.session_state:
        st.session_state.no_param_calculado = False
        st.session_state.no_param_estadistico = 0.0
        st.session_state.no_param_p_valor = 0.0
    
    def reset_no_param():
        st.session_state.no_param_calculado = False
        st.session_state.no_param_estadistico = 0.0
        st.session_state.no_param_p_valor = 0.0
    
    #LOGICA BONDAD DE AJUSTE USANDO PRUEBA DE SHAPIRO-WILK
    col = st.columns(2)
    with col[0]:    #CONFIGURACION DE LA PRUEBA
        col_variable = st.columns([1.5,2,1])
        
        with col_variable[0]:
            var_selected = st.selectbox(
                'Variable',
                var_options,
                index= None,
                placeholder= 'Selecciona una variable...',
                key= 'no_param_var',
                on_change= reset_no_param
            )
        
        if var_selected is None:
            st.info('Por favor, selecciona una variable para comenzar.')
            return
        
        with col_variable[1]:
            year_selected= st.slider(
                'Año',
                min_value= 1949,
                max_value= 2024,
                value= 2024,
                key= 'no_param_year',
                on_change= reset_no_param
            )
        
        df_filtrado = df[df['Year'] == year_selected].copy()
        df_filtrado = df_filtrado.dropna(subset= [var_selected])
        n= len(df_filtrado)
        
        with col_variable[2]:
            st.metric('Tamaño de la muestra', value= n)
            
        valor_h0 = st.selectbox(
            'Hipótesis Nula',
            options= dist_options,
            index= None,
            placeholder= 'Selecciona una distribución...',
            key= 'no_param_dist',
            on_change= reset_no_param
        )
        
        alpha = st.number_input(
            'Significación',
            min_value= 0.000,
            max_value= 1.000,
            value=0.050,
            format= "%.3f",
            step= 0.001,
            label_visibility= 'visible',
            key= 'alpha_bondad',
            help= 'Probabilidad correspodiente a la **Región Crítica** de $H_0$, considerando que la $H_0$ planteada es verdadera: $P(eI)$')

        if valor_h0 is not None:
            with st.container(border=True):
                st.markdown(f"""
                *$H_0$: La variable **{var_selected}** sigue una distribución **{valor_h0}***. \n
                *$H_1$: La variable **{var_selected}** no sigue una distribución **{valor_h0}***.
                """)
    
            if st.button('Calcular', type= 'primary', key= 'btn_no_param'):
                if valor_h0 == 'Normal':
                    resultado = shapiro_wilk(df_filtrado[var_selected])
                else:
                    resultado = kolmogorov_smirnov(df_filtrado[var_selected], valor_h0)
            
                st.session_state.no_param_estadistico = resultado['estadistico']
                st.session_state.no_param_p_valor = resultado['p-valor']
                
                if 'parametros' in resultado:
                    st.session_state.no_param_parametros = resultado['parametros']
                
                st.session_state.no_param_calculado = True
                print(resultado['p-valor'])
        
    with col[1]:    #MUESTRA DE RESULTADO DEL TEST
        if st.session_state.get('no_param_calculado', False):
            if 'no_param_parametros' in st.session_state:
                datos_grafico = df_filtrado[var_selected]
                params_grafico = st.session_state.no_param_parametros
                dist_grafico = valor_h0
                
                figura = plot_bondad_ajuste(datos_grafico, dist_grafico, params_grafico)
                st.plotly_chart(figura, use_container_width= True)
                
            col_resultado = st.columns(2, vertical_alignment= 'center')
            
            with col_resultado[0]:
                col_metricas = st.columns(2)
                
                if st.session_state.no_param_p_valor < 0.0001:
                    p_valor_text = f'{st.session_state.no_param_p_valor:.2e}'
                else:
                    p_valor_text = f'{st.session_state.no_param_p_valor:.4f}'
                    
                with col_metricas[0]:
                    st.metric(
                        'Estadístico',
                        value= f'{st.session_state.no_param_estadistico:.4f}'
                    )
                    
                with col_metricas[1]:
                    st.metric(
                        '*p*-Valor',
                        value= p_valor_text
                    )
            
            with col_resultado[1]:
                if st.session_state.no_param_calculado:
                    if st.session_state.no_param_p_valor < alpha:
                        st.error('La hipótesis nula se **rechaza**. \n\n El ajuste es MALO. Los datos no siguen la distribución teóríca')
                    else:
                        st.success('La hipótesis nula **no se rechaza**. \n\n El ajuste es BUENO. Los datos se parecen a la distribución teórica.')
        else:
            st.info('Configure los parámetros y presione Calcular para visualizar los resultados')