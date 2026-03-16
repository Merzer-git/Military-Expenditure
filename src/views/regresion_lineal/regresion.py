import streamlit as st
import statsmodels.api as sm
import numpy as np
from src.views.regresion_lineal.test_reg.motor_regresion_lineal import regresion_lineal
from src.views.regresion_lineal.utils import plot_regresion_lineal, plot_histograma_residuos, plot_dispersion_datos
from src.views.test_hipotesis.test_no_param.bondad_ajuste import shapiro_wilk

variables_ejeY = ['Spending_B', 'Share_of_GDP']
variables_ejeX = ['Year', 'Per_Capita', 'Share_of_Govt_Spending', 'Share_of_GDP']

def render_regresion(df):
    """Lógica completa de la pestaña Regresión Lineal"""
    if 'regresion_calculado' not in st.session_state:
        st.session_state.regresion_calculado = False
    if 'regresion_resultado' not in st.session_state:
        st.session_state.regresion_resultado = None
    if 'var_X' not in st.session_state:
        st.session_state.var_X = None
    if 'var_Y' not in st.session_state:
        st.session_state.var_Y = None
    
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
            default= 'País',
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
            
        if entidad_selected in options_pais:
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
            
            col_log = st.columns(2)
            with col_log[0]:
                aplicar_log_X = st.checkbox(
                    'log(X)',
                    disabled= (var_selected_X is None or var_selected_X is 'Year')
                )
            with col_log[1]:
                aplicar_log_Y = st.checkbox(
                    'log(Y)',
                    disabled= (var_selected_Y is None)
                )
            if var_selected_X is not None and var_selected_Y is not None:
                if var_selected_X == 'Year':
                    st.warning("**Al seleccionar la variable *Year* se está violando el principio de independencia para el modelo. Tenga esto presente a la hora de analizar los resultados del modelo.**")
                
                if st.button('Ejecutar Modelo', type= 'primary', key= 'btn_regresion'):
                    st.session_state.regresion_calculado = True
                    
                    if len(df_RL) > 5:
                        df_model = df_RL.copy()
                        
                        if aplicar_log_X:
                            df_model = df_model[df_model[var_selected_X] > 0]
                            df_model[var_selected_X] = np.log(df_model[var_selected_X])
                            
                        if aplicar_log_Y:
                            df_model = df_model[df_model[var_selected_Y] > 0]
                            df_model[var_selected_Y] = np.log(df_model[var_selected_Y])
                        
                        modelo = regresion_lineal(df_model, var_selected_X, var_selected_Y)
                        
                        st.session_state.regresion_resultado = modelo
                        st.session_state.df_model = df_model
                        st.session_state.var_X = var_selected_X
                        st.session_state.var_Y = var_selected_Y
                        st.session_state.log_X = aplicar_log_X
                        st.session_state.log_Y = aplicar_log_Y
                    else:
                        st.info('No hay datos suficientes en el rango seleccionado para calcular una regresión.')
        elif entidad_selected in options_region:
            st.error('**🚫 Temporalmente deshabilitado.**')
    
    with col[1]:    #RESULTADOS DE LA REGRESION
        if st.session_state.regresion_calculado and st.session_state.regresion_resultado is not None and st.session_state.get('var_X') is not None:
            modelo = st.session_state.regresion_resultado
            df_model = st.session_state.df_model
            
            var_x = st.session_state.var_X
            var_y = st.session_state.var_Y
            
            intercepto = modelo.params['const']
            pendiente = modelo.params[var_x]
            r2 = modelo.rsquared
            p_valor = modelo.pvalues[var_x]
            residuos = modelo.resid
            valores_x = df_model.loc[residuos.index, var_x]
            
            if abs(pendiente) < 0.0001:
                pendiente_txt = f'{pendiente:.2e}'
            else:
                pendiente_txt = f'{pendiente:.4f}'
            
            if p_valor < 0.0001:
                p_valor_txt = f'{p_valor:.2e}'
            else:
                p_valor_txt = f'{p_valor:.4f}'
            
            if p_valor < 0.05:
                etiqueta_delta = 'Significativo (Existe Relación)'
                color_delta = 'normal'
                flecha_delta = 'up'
            else:
                etiqueta_delta = 'No Significativo (Sin Relación)'
                color_delta = 'inverse'
                flecha_delta = 'down'
            
            signo = '-' if pendiente < 0 else '+'
            pendiente_abs = abs(pendiente)
            
            st.latex(f'Y = {intercepto:.4f} {signo} {pendiente_abs:.4f}X')            
            st.divider()
            
            col_metrics = st.columns(3)
            col_metrics[0].metric('$R^2$ (Ajuste)', f'{r2:.4f}')
            col_metrics[1].metric(r'Pendiente - $\beta$', pendiente_txt)
            col_metrics[2].metric(
                '$p$-valor',
                p_valor_txt,
                delta= etiqueta_delta,
                delta_color= color_delta,
                delta_arrow= flecha_delta
            )
            
            df_plot = df_model.sort_values(by= var_x).copy()
            df_plot = df_plot.reset_index(drop=True)
            
            X_pred = sm.add_constant(df_plot[var_x])
            if 'const' not in X_pred.columns:
                X_pred.insert(0, 'const', 1.0)
            
            predicciones = modelo.get_prediction(X_pred).summary_frame(alpha= 0.05)
            df_plot['ci_bajo'] = predicciones['mean_ci_lower']
            df_plot['ci_alto'] = predicciones['mean_ci_upper']
            df_plot['prediccion_media'] = predicciones['mean']
            
            options_graficos = ['Recta del Modelo de Regresión', 'Histograma de Residuos', 'Dispersión de los Datos']
            grafico = st.pills(
                '',
                options= options_graficos,
                default= options_graficos[0],
                selection_mode= 'single'
            )
            
            if grafico == 'Recta del Modelo de Regresión':
                fig_RL = plot_regresion_lineal(df_plot, var_x, var_y)
            elif grafico == 'Histograma de Residuos':
                resultado_SW = shapiro_wilk(residuos)
                
                fig_RL = plot_histograma_residuos(residuos)
                
                p_valor_Shapiro = resultado_SW['p-valor']
                if p_valor_Shapiro < 0.0001:
                    p_valor_SW_txt = f'{p_valor_Shapiro:.2e}'
                else:
                    p_valor_SW_txt = f'{p_valor_Shapiro:.4f}'
                    
                if p_valor_Shapiro < 0.05:
                    st.error(f'**Prueba de Shapiro-Wilk (p-valor= {p_valor_SW_txt}**. Se rechaza $H_0$.')
                else:
                    st.success(f'**Prueba de Shapiro-Wilk (p-valor= {p_valor_SW_txt}**. No se rechaza $H_0$.')
                    
            elif grafico == 'Dispersión de los Datos':
                varianza_Se = np.sqrt(modelo.mse_resid)
                fig_RL = plot_dispersion_datos(valores_x, residuos, var_x, varianza_Se)
            else:
                st.info('Seleccione una opción de gráfico')
            st.plotly_chart(fig_RL, use_container_width= True)
            
            with st.expander('Ver Reporte Estadístico Completo', expanded= False):
                st.text(modelo.summary())