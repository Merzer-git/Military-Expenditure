import streamlit as st
from statsmodels.stats.weightstats import ztest
from scipy import stats
from src.views.test_hipotesis.utils import plot_region_critica

var_options = ['Spending_B', 'Growth_Rate', 'Per_Capita', 'Share_of_GDP', 'Share_of_Govt_Spending', 'Region']

var_porcentuales = ['Share_of_GDP', 'Share_of_Govt_Spending', 'Growth_Rate']

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


def render_parametrico(df):
    """Lógica completa de la pestaña Parámetricos"""
    if 'param_calculado' not in st.session_state:
        st.session_state.param_calculado = False
    if 'estadistico' not in st.session_state:
        st.session_state.param_estadistico = 0.0
    if 'p_valor' not in st.session_state:
        st.session_state.param_p_valor = 0.0

    if 'param_calculado' not in st.session_state:
        st.session_state.param_calculado = False
        
        st.session_state.param_estadistico = 0.0
        st.session_state.param_p_valor = 0.0
    
    def reset_param():
        st.session_state.param_calculado = False
        st.session_state.param_estadistico = 0.0
        st.session_state.param_p_valor = 0.0
    
    col= st.columns(2)
    
    with col[0]: #COLUMNA PARA CONFIGURAR LAS HIPOTESIS
        col_variable = st.columns(2)

        with col_variable[0]:
            var_selected= st.selectbox(
                'Variable',
                var_options,
                index= None,
                placeholder= 'Seleccione una variable...',
                key = 'param_var',
                on_change= reset_param
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
                key= 'param_year',
                on_change= reset_param
            )

        df_filtrado = df[df['Year'] == year_selected].copy()
        df_filtrado = df_filtrado.dropna(subset= [var_selected])
        
        if var_selected in var_porcentuales:
            if df_filtrado[var_selected].mean() < 1.0:
                df_filtrado[var_selected] = df_filtrado[var_selected] * 100
        
        n = len(df_filtrado)
        dist= None
        if n < 30:
            dist= 'T-Student'
        elif n >= 30:
            dist= 'Normal'
        
        col_muestra, col_dist = st.columns(2)
        with col_muestra:
            st.metric('Tamaño de la Muestra', n)
        with col_dist:
            if dist == 'Normal':
                st.info(f'Muestra grande ($n>=30$). Se usará distribución ***{dist}*** (TCL)')
            elif dist == 'T-Student':
                st.info(f'Muestra pequeña ($n<30$). Se usará distribución ***{dist}***')
            else:
                st.warning('⚠️ Seleccione una variable y año para obtener el tamaño de la muestra a trabajar.')
        
        if var_selected in var_porcentuales:    
            valor_h0= st.number_input('Hipótesis Nula (%) - ($\mu=$)', value=0.0, label_visibility= 'visible', key= 'val_hip_nula', on_change= reset_param)
        else:
            valor_h0= st.number_input('Hipótesis Nula $\mu=$', value=0.0, label_visibility= 'visible', key= 'val_hip_nula', on_change= reset_param)

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
        
        stat_valor, p_valor = 0.0, 1.0
        if st.button('Calcular', type='primary', key= 'btn_param'):
            st.session_state.param_calculado = True
            
            # # Ajustar valor H0 si es variable porcentual
            # valor_h0 = valor_h0 * 100 if var_selected in var_porcentuales else valor_h0
        
            if dist == 'Normal':
                val_z, val_z_p = ztest(
                    x1= df_filtrado[var_selected],
                    x2= None,
                    value= float(valor_h0), # type: ignore
                    alternative= mapeo_statmodels[tipo_h1]
                )
                stat_valor = float(val_z)
                p_valor = float(val_z_p)
            else:
                resultado_t = stats.ttest_1samp(
                    df_filtrado[var_selected],
                    popmean= valor_h0,
                    alternative= mapeo_scipy[tipo_h1]
                )
                stat_valor = float(resultado_t[0]) # type: ignore
                p_valor = float(resultado_t[1]) # type: ignore

            st.session_state.param_estadistico = stat_valor
            st.session_state.param_p_valor = p_valor
            
    with col[1]:
        st.latex(fr"H_0: \mu = {valor_h0} \quad | \quad H_1: \mu {simbolos[tipo_h1]} {valor_h0}")
        
        if st.session_state.get('param_calculado', False):
            fig_test = plot_region_critica(st.session_state.param_estadistico, alpha, tipo_h1, n)
            st.plotly_chart(fig_test, use_container_width=True)
        else:
            st.info('Configure los parámetros y presione Calcular para visualizar los resultados.')

        col_resultados = st.columns(2, vertical_alignment='center')

        
        if dist == 'Normal':
            label_estadistico = 'Z'
        elif dist == 'T-Student':
            label_estadistico = 't'
        else:
            label_estadistico = ''

        with col_resultados[0]:   #ESTADISTICO Y P-VALOR
            col_metricas = st.columns(2)
            if st.session_state.param_calculado:
                with col_metricas[0]:
                    st.metric(
                        f'Estadístico {label_estadistico}',
                        value= f'{st.session_state.param_estadistico:.4f}'
                    )

                with col_metricas[1]:
                    st.metric(
                        '*p*-Valor',
                        value= f'{st.session_state.param_p_valor:.4f}'
                    )

            else:
                st.info('Configure los parámetros y presione Calcular.')
                
        with col_resultados[1]:
            if st.session_state.param_calculado:
                if p_valor <= alpha:
                    st.error('La hipótesis nula se **rechaza**.\n\n Hay diferencias significativas')
                else:
                    st.success('La hipótesis nula **no se rechaza**.\n\n No hay diferencias significativas')
            else:
                st.info('Configure los parámetros y presione Calcular.')
    
        with st.expander('Resultado Detallado', expanded= False):
            if st.session_state.param_calculado:
                st.markdown('#### 1. Parámetros del Cálculo')
                col_desc = st.columns(2)
                col_desc[0].info(f'**Estadístico:** {st.session_state.param_estadistico:.4f}')
                col_desc[1].info(f'**p-Valor:** {st.session_state.param_p_valor:.4f}')
                
                st.markdown('#### 2. Regla de Decisión')
                if st.session_state.param_p_valor <= alpha:
                    st.markdown(f"""
                        Dado que el ***p*-valor** ({st.session_state.param_p_valor:.4f}) es menor que el nivel de significancia ({alpha:.4f}), se rechaza la hipótesis nula.
                        """)
                else:
                    st.markdown(f"""
                        Dado que el ***p*-valor** ({st.session_state.param_p_valor:.4f}) es mayor que el nivel de significancia ({alpha:.4f}), no se rechaza la hipótesis nula.
                        """)
                    
                st.divider()
                
                from statsmodels.stats.power import TTestPower
                
                st.markdown('#### 3. Potencia del Test ($1 - \\beta$')
                st.caption('Indica la probabilidad de haber detectado una diferencia significativa asumiendo que el efecto observado es real.')
                
                media = df_filtrado[var_selected].mean()
                desvio_std = df_filtrado[var_selected].std(ddof=1)
                
                if desvio_std > 0:
                    cohens_d = (media - valor_h0) / desvio_std
                else:
                    cohens_d = 0
                
                alter_power = ''
                if dist == 'Normal':
                    alter_power = mapeo_statmodels[tipo_h1]
                elif dist == 'T-Student':
                    alter_power = mapeo_scipy[tipo_h1]
                
                power_analisis = TTestPower()
                potencia = power_analisis.solve_power(
                    effect_size= cohens_d,
                    nobs= len(df_filtrado),
                    alpha= alpha,
                    power= None,
                    alternative= alter_power
                )
                
                c_pot = st.columns([1,3])
                with c_pot[0]:
                    st.metric('Potencia', f'{potencia:.4f}')
                with c_pot[1]:
                    if potencia > 0.8:
                        st.success('La potencia es alta (>0.8). El test es **confiable**.')
                    elif potencia > 0.5:
                        st.warning('La potencia es moderada (0.5 < potencia <= 0.8). Existe riesgo de Error Tipo II (falsos negativos).')
                    else:
                        st.error('La potencia es baja (potencia <= 0.5). Es dificil detectar diferencias, por ende el test **no es confiable**.')
            else:
                st.info('Configure los parámetros y presione Calcular.')