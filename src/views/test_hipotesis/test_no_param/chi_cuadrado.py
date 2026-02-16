import streamlit as st
import pandas as pd
from src.views.test_hipotesis.pruebas.tests import chi_cuadrado
from src.views.test_hipotesis.utils import barras_apiladas, mapa_calor

options_vars = ['Spending_B', 'Share_of_GDP', 'Per_Capita', 'Share_of_Govt_Spending']

def render_ind_homo(df):
    """Lógica completa de la pestaña No Paramétricos (INDEPENDENCIA Y HOMOGENEIDAD)"""
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
    
    col_IH = st.columns(2)
    with col_IH[0]:    #CONFIGURACION DE LA PRUEBA
        col_prueba = st.columns(2)
        with col_prueba[0]:
            tipo_prueba = st.pills(
                label= r'Tipo de Prueba Chi Cuadrado',
                options= ['Independencia', 'Homogeneidad'],
                default= 'Independencia',
                selection_mode= 'single',
            )
        
        if tipo_prueba == 'Independencia':
            with col_prueba[1]:
                st.info('Evalúa si dos variables categóricas están relacionadas en toda la población.')
            
            cols_vars = st.columns(2)
            
            with cols_vars[0]:
                var_interes = st.selectbox(
                    'Variable de Interés (Columnas)',
                    options= options_vars,
                    placeholder= 'Seleccione una Variable...',
                    key= 'indep_v2',
                    index= None,
                    on_change= reset_no_param
                )
            
            with cols_vars[1]:
                year_selected = st.slider(
                    'Año',
                    min_value= 1949,
                    max_value= 2024,
                    value= 2024,
                    key= 'indep_year',
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
                key= 'alpha_ind',
                help= 'Probabilidad correspodiente a la **Región Crítica** de $H_0$, considerando que la $H_0$ planteada es verdadera: $P(eI)$')
            
            if var_interes is not None:
                if st.button('Calcular', type= 'primary', key= 'btn_ind'):
                    st.session_state.no_param_calculado = True
                    df_ind = df[df['Year'] == year_selected].copy()
                    df_ind = df_ind.dropna(subset= [var_interes, 'Region'])
                    
                    df_ind['Cat_Analisis'] = pd.qcut(df_ind[var_interes], 3, labels= ['Bajo', 'Medio', 'Alto'])
                    
                    tabla = pd.crosstab(df_ind['Region'], df_ind['Cat_Analisis'])
                    resultado = chi_cuadrado(tabla)
                    st.session_state.resultado_chi = resultado
                    st.session_state.tabla = tabla
                    st.session_state.alpha = alpha
            else:
                st.info('Ingrese una variable para generar la tabla')
            
        elif tipo_prueba == 'Homogeneidad':
            with col_prueba[1]:
                st.info('Evalúa si una variable se comporta igual en dos grupos distintos (Eras).')
            options_eras = df['Historical_Era'].unique()
            
            col_era = st.columns(2)
            with col_era[0]:
                var_era_A = st.selectbox(
                    'Era A (Grupo 1)',
                    options= options_eras,
                    index= None,
                    key= 'homo_eraA',
                    on_change= reset_no_param
                )
            
            with col_era[1]:
                era_filtrada = [op for op in options_eras if op != var_era_A]
                var_era_B = st.selectbox(
                    'Era B (Grupo 2)',
                    options= era_filtrada,
                    index= None,
                    key= 'homo_eraB',
                    on_change= reset_no_param
                )
                
            var_interes = st.selectbox(
                'Variable de Interés',
                options= options_vars,
                key= 'homo_v1',
                index= None,
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
                        key= 'alpha_homo',
                        help= 'Probabilidad correspodiente a la **Región Crítica** de $H_0$, considerando que la $H_0$ planteada es verdadera: $P(eI)$')
            
            if var_interes and var_era_A and var_era_B:
                if st.button('Calcular', type= 'primary', key= 'btn_homo'):
                    st.session_state.no_param_calculado = True
                    df_homo = df[df['Historical_Era'].isin([var_era_A, var_era_B])].copy()
                    df_homo = df_homo.dropna(subset= [var_interes, 'Historical_Era'])
                    
                    df_homo['Cat_Analisis'] = pd.qcut(df_homo[var_interes], 3, labels= ['Bajo', 'Medio', 'Alto'])
                    tabla = pd.crosstab(df_homo['Historical_Era'], df_homo['Cat_Analisis'])
                    resultado = chi_cuadrado(tabla)
                    st.session_state.resultado_chi = resultado
                    st.session_state.tabla = tabla
                    st.session_state.alpha = alpha
            else:
                st.info('Ingrese una variable para generar la tabla')
    
    with col_IH[1]: #RESULTADOS
        if st.session_state.get('no_param_calculado', False):
            if 'resultado_chi' in st.session_state and 'tabla' in st.session_state and 'alpha' in st.session_state:
                res = st.session_state.resultado_chi
                tabla_obs = st.session_state.tabla
                alpha = st.session_state.alpha

                stat, p_valor, gl, tabla_esperada = res
                
                col_res = st.columns(3)
                
                with col_res[0]:
                    st.metric(
                        'Estadístico',
                        value= f'{stat:.2f}'
                    )
                
                if float(p_valor) < 0.0001:
                    p_valor_txt = f'{p_valor:.2e}'
                else:
                    p_valor_txt = f'{p_valor:.4f}'
                
                with col_res[1]:
                    st.metric(
                        'p_valor',
                        value= p_valor_txt
                    )
                
                with col_res[2]:
                    st.metric(
                        '$gl$',
                        value= int(gl)
                    )
                
                if float(p_valor) < alpha:
                    st.error('La hipótesis nula se **rechaza**.')
                else:
                    st.success('La hípótesis nula **no se rechaza**.')
                
                vista = st.pills(
                    'Selecciona Visualización',
                    ['Valores Observados', 'Valores Esperados', 'Barras Apiladas'],
                    default= 'Valores Observados',
                    selection_mode = 'single'
                )
                
                df_esperados = pd.DataFrame(
                    tabla_esperada,
                    index= tabla_obs.index,
                    columns= tabla_obs.columns
                )
                
                max_valor_escala = max(tabla_obs.max().max(), df_esperados.max().max())
                
                if vista == 'Valores Observados':
                    st.caption("Muestra de la concentración de los países (Frecuencias Observadas)")
                    fig_obs = mapa_calor(tabla_obs, max_valor_escala)
                    
                    st.plotly_chart(fig_obs, use_container_width= True)
                elif vista == 'Valores Esperados':
                    st.caption('Frecuencias Esperadas')
                    
                    fig_esp = mapa_calor(df_esperados, max_valor_escala)
                    
                    st.plotly_chart(fig_esp, use_container_width= True)
                elif vista == 'Barras Apiladas':
                    st.caption('Ideal para la comparacion entre grupos.')
                    fig_barra = barras_apiladas(tabla_obs)
                    
                    st.plotly_chart(fig_barra, use_container_width= True)