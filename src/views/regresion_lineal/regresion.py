import streamlit as st
import statsmodels.api as sm
from src.views.regresion_lineal.test_reg.motor_regresion_lineal import regresion_lineal
from src.views.regresion_lineal.utils import plot_regresion_lineal

variables_ejeY = ['Spending_B', 'Share_of_GDP']
variables_ejeX = ['Year', 'Per_Capita', 'Share_of_Govt_Spending', 'Share_of_GDP']

def render_regresion(df):
    """Lógica completa de la pestaña Regresión Lineal"""
    if 'regresion_calculado' not in st.session_state:
        st.session_state.regresion_calculado = False
    
    if 'regresion_resultado' not in st.session_state:
        st.session_state.regresion_resultado = None
    
    def reset_regresion():
        st.session_state.regresion_calculado = False
        st.session_state.regresion_resultado = None
    
    col = st.columns([1,2])
    options_pais = df['Country'].unique()
    options_region = df['Region'].unique()
    
    with col[0]:    #CONFIGURACION DEL MODELO DE REGRESION
        entidad = st.pills(
            'Selector de Alcance',
            options= ['Región', 'País'],
            default= 'Región',
            selection_mode= 'single'
        )
        
        entidad_selected = ''
        if entidad == 'Región':
            entidad_selected = st.selectbox(
                'Región',
                options= options_region,
                placeholder= 'Seleccione una Región...',
                index= None,
                on_change= reset_regresion,
                key= 'ent_region'
            )
            df_RL = df[df['Region'] == entidad_selected].copy()
        elif entidad == 'País':
            entidad_selected = st.selectbox(
                'País',
                options= options_pais,
                placeholder= 'Seleccione un País...',
                index= None,
                on_change= reset_regresion,
                key= 'ent_pais'
            )
            df_RL = df[df['Country'] == entidad_selected].copy()
            
        if entidad_selected is not None:
            min_year, max_year = int(df['Year'].min()), int(df['Year'].max())
            rango_años = st.slider(
                'Periodo a Analizar',
                min_year,
                max_year,
                (min_year, max_year)
            )
            
            df_RL = df_RL[(df_RL['Year'] >= rango_años[0]) & (df_RL['Year'] <= rango_años[1])]
            
            col_var = st.columns(2)
            
            with col_var[0]: 
                var_selected_X = st.selectbox(
                    'Eje X',
                    options= variables_ejeX,
                    placeholder= 'Seleccione la variable independiente...',
                    index= None,
                    on_change= reset_regresion,
                    key= 'eje_X'
                )
            
            with col_var[1]:
                var_filtrada = [op for op in variables_ejeY if op != var_selected_X]  
                var_selected_Y = st.selectbox(
                    'Eje Y',
                    options = var_filtrada,
                    placeholder= 'Seleccione la variable dependiente...',
                    index= None,
                    on_change= reset_regresion,
                    key= 'eje_Y'
                )
            
            if var_selected_X is not None and var_selected_Y is not None:
                if st.button('Ejecutar Modelo', type= 'primary', key= 'btn_regresion'):
                    st.session_state.regresion_calculado = True
                    
                    if len(df_RL) > 5:
                        modelo = regresion_lineal(df_RL, var_selected_X, var_selected_Y)
                        st.session_state.regresion_resultado = modelo
                    else:
                        st.info('No hay datos suficientes en el rango seleccionado para calcular una regresión.')
            
        else:
            st.info('Ingrese los datos para la ejecución del modelo.')
    
    with col[1]:    #RESULTADOS DE LA REGRESION
        if st.session_state.regresion_calculado and st.session_state.regresion_resultado is not None:
            modelo = st.session_state.regresion_resultado
            
            intercepto = modelo.params['const']
            pendiente = modelo.params[var_selected_X]
            r2 = modelo.rsquared
            p_valor = modelo.pvalues[var_selected_X]
            if p_valor < 0.0001:
                p_valor_txt = f'{p_valor:.2e}'
            else:
                p_valor_txt = f'{p_valor:.4f}'
            
            if p_valor < 0.05:
                etiqueta_delta = 'Significativo (Existe Relación)'
                color_delta = 'normal'
            else:
                etiqueta_delta = 'No Significativo (Sin Relación)'
                color_delta = 'inverse'
            
            st.latex(f'Y = {intercepto:.4f} + {pendiente:.4f}X')            
            st.divider()
            
            col_metrics = st.columns(3)
            col_metrics[0].metric('$R^2$ (Ajuste)', f'{r2:.4f}')
            col_metrics[1].metric(r'Pendiente - $\beta$', f'{pendiente:.4f}')
            col_metrics[2].metric(
                '$p$-valor',
                p_valor_txt,
                delta= etiqueta_delta,
                delta_color= color_delta
            )
            
            df_plot = df_RL.sort_values(by= var_selected_X).copy()
            predicciones = modelo.get_prediction(sm.add_constant(df_plot[var_selected_X])).summary_frame(alpha= 0.05)
            df_plot['ci_bajo'] = predicciones['mean_ci_lower']
            df_plot['ci_alto'] = predicciones['mean_ci_upper']
            df_plot['prediccion_media'] = predicciones['mean']
            
            fig_RL = plot_regresion_lineal(df_plot, var_selected_X, var_selected_Y)
            
            st.plotly_chart(fig_RL, use_container_width= True)
            
            with st.expander('Ver Reporte Estadístico Completo', expanded= False):
                st.text(modelo.summary())
        else:
            st.info('Configure los parámetros y presione Calcular para visualizar los resultados')