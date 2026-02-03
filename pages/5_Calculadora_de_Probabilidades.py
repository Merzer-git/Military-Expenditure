import streamlit as st
import pandas as pd
import numpy as np
from src.datos import cargar_datos

st.set_page_config(page_title='Calculadora de Probabilidades', page_icon='static/dice-game-icon.svg', layout= 'wide')
st.logo('static/dice-game-icon.svg', icon_image='static/dice-game-icon.svg')

st.sidebar.header('Calculadora de Probabilidad Empírica')
st.sidebar.markdown("""
    <style>
.small-font {
    font-size:18px !important;
    color: #888888;
}
</style>
<p class="small-font">
    Calcula la probabilidad de ocurrencia de eventos basándose en el registro histórico de datos.
</p>""", unsafe_allow_html= True)

options_selectbox = ['Spending_B', 'Growth_Rate', 'Share_of_GDP', 'Per_Capita', 'Share_of_Govt_Spending']

def activar_analisis():
    st.session_state.analisis_listo = True

def formatear_intervalo(intervalo):
    """Convierte un intervalo de Pandas al formato estadístico [a; b)"""
    return f"[{intervalo.left:.3f}; {intervalo.right:.3f})"

def generar_tabla_frecuencias(df, variable, year=None):
    if variable in variables_temporales:
        if year is not None:
            df_frec = df[df['Year'] == year].copy()
        else:
            return pd.DataFrame(), 0, 0, 0, 0, 0
    else:
        df_frec = df.copy()

    datos_validos = df_frec[variable].replace([np.inf, -np.inf], np.nan).dropna()
    total_original = len(datos_validos)  #TAMAÑO DE LA MUESTRA
    
    n = len(datos_validos)
    if n == 0:
        return pd.DataFrame(), 0, 0, 0, 0, 0

    R = datos_validos.max() - datos_validos.min() #RECORRIDO DE LA MUESTRA
    N = int(np.ceil(1 + 3.3 * np.log10(n)))   #FORMULA DE STURGES, CANTIDAD DE INTERVALOS IDONEO
    if N == 0: 
        N = 1
    A = R/N

    interv = pd.cut(datos_validos, bins= N, right= False)
    tabla = interv.value_counts().sort_index().reset_index()
    tabla.columns= ['Intervalo', 'Frecuencia Abs. (fi)']
    
    # Formatear intervalos al formato estadístico [a; b)
    tabla['Intervalo'] = tabla['Intervalo'].apply(formatear_intervalo)
    
    total_datos = tabla['Frecuencia Abs. (fi)'].sum()
    tabla['Frecuencia Rel. (hi)'] = tabla['Frecuencia Abs. (fi)'] / total_datos
    tabla['Frecuencia Abs. Acumulada (Fi)'] = tabla['Frecuencia Abs. (fi)'].cumsum()
    tabla['Frecuencia Rel. Acumulada (Hi)'] = tabla['Frecuencia Rel. (hi)'].cumsum()

    excluidos = total_original - n
        
    return tabla, n, R, N, A, excluidos

variables_temporales = ['Spending_B', 'Per_Capita']

def filtrado_outliers_iqr(df, variable, corte):  #LO RELACIONADO A LA ECONOMIA, POR LO GENERAL, SIGUE UNA DISTRIBUCION DE PARETO
    limite = df[variable].quantile(corte)
    return df[df[variable] <= limite]

def filtro_df_operacion(df, variable, operador, valor):
    if operador == '>':
        return df[variable] > valor
    elif operador == '<':
        return df[variable] < valor
    elif operador == '=':
        return df[variable] == valor
    else:
        return pd.Series(([False]*len(df)))


if __name__ == '__main__':
    df = cargar_datos()
    col_1, col_2= st.columns(2) #col_1 -> COLUMNA DE VARIABLES | col_2 -> COLUMNA DE AÑOS (OPCIONAL)
    tab_tabla, tab_prob = st.tabs(['Tabla de Frecuencias', 'Calculadora de Probabilidades'])
    

    with col_1:
        var_selected = st.selectbox(
            'Variable',
            options= options_selectbox,
            index= 0,
            placeholder= 'Seleccione una variable...'
        )

    with col_2:
        year_selected = st.selectbox(
            'Año',
            options= sorted(df['Year'].unique(), reverse= True),
            index= None,
            placeholder= 'Seleccione un año...',
            disabled= (var_selected not in variables_temporales)
        )

    df_sin_outliers = filtrado_outliers_iqr(df, var_selected, 0.95) #CONSULTAR SOBRE METODO DE CORTE

    var_porcentuales = ['Share_of_GDP', 'Share_of_Govt_Spending', 'Growth_Rate']
    if var_selected in var_porcentuales:
        df_sin_outliers[var_selected] = df_sin_outliers[var_selected] * 100

    with tab_tabla:
        if 'analisis_listo' not in st.session_state:
            st.session_state.analisis_listo = False

        col_btn_1, col_aviso = st.columns([1, 5], vertical_alignment= 'center')
        with col_btn_1:
            if st.button('Generar Tabla', type='primary', on_click=activar_analisis):
                pass
        
        with col_aviso:
            st.info("ℹ️ Se está aplicando Trimming (truncamiento) al 5% superior (recorte del percentil 95) para excluir valores extremos que rompen los intervalos")

        if st.session_state.analisis_listo:
            tabla_frec, n, recorrido, intervalos, amplitud, dif = generar_tabla_frecuencias(df_sin_outliers, var_selected, year_selected)

            df_visual = tabla_frec.copy()
            cols_a_multiplicar = ["Frecuencia Rel. (hi)", "Frecuencia Rel. Acumulada (Hi)"]
            df_visual[cols_a_multiplicar] = df_visual[cols_a_multiplicar] * 100

            st.dataframe(
                df_visual,
                use_container_width= True,
                hide_index=0,
                column_config= {
                    'Intervalo': st.column_config.TextColumn(
                        'Intervalo de Clase',
                        width= 'medium'
                    ),
                    'Frecuencia Rel. (hi)': st.column_config.NumberColumn(
                        'Frecuencia Relativa %',
                        format= "%.4f %%"
                    ),
                    'Frecuencia Rel. Acumulada (Hi)': st.column_config.NumberColumn(
                        'Frecuencia Acumulada %',
                        format= '%.4f %%'
                    ),
                    'Frecuencia Abs. (fi)': st.column_config.NumberColumn(
                        'Frecuencia Absoluta',
                        format= '%d'
                    )
                }
            )
            if dif != 0:
                st.warning(f"⚠️ Se descartaron {dif} muestras (Outliers) ya que rompen la distribución de intervalos")

    with tab_prob:
        tipo_evento = st.radio(
            'Seleccione el tipo de evento a calcular',
            ['Evento Simple', 'Evento Compuesto'],
            index= 0,
            horizontal= True
        )

        if tipo_evento == 'Evento Simple':
            col_P, col_operador, col_operando, col_igual, col_resultado = st.columns([3,2,2,1,2], vertical_alignment= 'bottom')

            with col_P:
                st.markdown(f"#### $P(A):$ **{var_selected}**")
            with col_operador:
                operador = st.selectbox(
                    'Op A',
                    options= ['<', '>'],
                    label_visibility= 'collapsed',
                    key= 'op_a'
                )
            with col_operando:
                if pd.api.types.is_numeric_dtype(df[var_selected]):
                    val_a = st.number_input('Val A', value= 0.0, label_visibility= 'collapsed', key= 'val_a')
                else:
                    val_a = st.selectbox('Val A', df[var_selected].unique(), label_visibility= 'collapsed', key= 'val_a')
            with col_igual:
                igual_button = st.button(
                    '=',
                    type= 'primary',
                    key= 'igual_simple'
                )

            with col_resultado:
                if igual_button:
                    mascara_bool = filtro_df_operacion(df_sin_outliers, var_selected, operador, val_a)
                    tamaño_muestra = len(df_sin_outliers)
                    casos = mascara_bool.sum()

                    if tamaño_muestra > 0:
                        prob = (casos / tamaño_muestra) * 100
                        st.markdown(f"#### ${(prob):.2f}$")
                        st.caption(f"Casos: {casos} / Total Muestra: {tamaño_muestra}")
                    else:
                        st.error("El filtrado de outliers eliminó todos los datos.")

        if tipo_evento == 'Evento Compuesto':
            col_varB, col_yearB= st.columns(2) #col_1 -> COLUMNA DE VARIABLES | col_2 -> COLUMNA DE AÑOS (OPCIONAL)
            titulo_P = st.empty()

            with col_varB:
                options_B = [op for op in options_selectbox if op != var_selected]
                var_selectedB = st.selectbox(
                    'Variable B',
                    options= options_B + ['Region', 'Subregion'],
                    index= 0,
                    placeholder= 'Seleccione una variable...'
                )
            with col_yearB:
                year_selectedB = st.selectbox(
                    'Año B',
                    options= sorted(df_sin_outliers['Year'].unique(), reverse= True),
                    index= None,
                    placeholder= 'Seleccione un año...',
                    disabled= (var_selectedB not in variables_temporales)
                )
            
            cols = st.columns([2.4, 1, 1, 0.8, 2.4, 1, 1.5, 0.5, 1], gap= 'small', vertical_alignment= 'center')

            with cols[0]:   #VARIABLE A
                st.markdown(f"##### **{var_selected}**")
            with cols[1]:   #OPERADOR A
                operadorA = st.selectbox(
                    'Op A',
                    options= ['<', '>'],
                    label_visibility= 'collapsed',
                    key= 'op_a'
                )
            with cols[2]:   #OPERANDO A
                if pd.api.types.is_numeric_dtype(df_sin_outliers[var_selected]):
                    val_a = st.number_input('Val A', value= 0.0, label_visibility= 'collapsed', key= 'val_a')
                else:
                    val_a = st.selectbox('Val A', df_sin_outliers[var_selected].unique(), label_visibility= 'collapsed', key= 'val_a')
            with cols[3]: #OPERACION DE CONJUNTO
                op_Conjunto = st.selectbox(
                    'Op Conj',
                    options= ['∪', '∩', '∣'],
                    label_visibility= 'collapsed',
                    key= 'op_C'
                )
            with cols[4]:   #VARIABLE B
                st.markdown(f"##### **{var_selectedB}**")
            with cols[5]:   #OPERADOR B
                operadorB = st.selectbox(
                    'Op B',
                    options= ['<', '>', '='],
                    label_visibility= 'collapsed',
                    key= 'op_b'
                )
            with cols[6]:   #OPERANDO B
                if pd.api.types.is_numeric_dtype(df_sin_outliers[var_selectedB]):
                    val_b = st.number_input('Val B', value= 0.0, label_visibility= 'collapsed', key= 'val_b')
                else:
                    val_b = st.selectbox('Val B', df_sin_outliers[var_selectedB].unique(), label_visibility= 'collapsed', key= 'val_b')
            with cols[7]:   #IGUAL
                igual_button_C = st.button(
                    '=',
                    type= 'primary',
                    key= 'igual_compuesto'
                )
            with cols[8]:   #RESULTADO
                if igual_button_C:
                    # Usar df completo para variables categóricas (Region, Subregion)
                    if var_selectedB in ['Region', 'Subregion']:
                        df_base = df.copy()  # Usar df original, sin filtrado de outliers
                    else:
                        df_base = df_sin_outliers.copy()  # Usar df filtrado para variables numéricas
                    
                    # Filtrar por año si la variable es temporal
                    if var_selected in variables_temporales and year_selected is not None:
                        df_base = df_base[df_base['Year'] == year_selected]
                    if var_selectedB in variables_temporales and year_selectedB is not None:
                        df_base = df_base[df_base['Year'] == year_selectedB]
                    
                    # Identificar qué variables están disponibles en df_base
                    columnas_necesarias = [var_selected, var_selectedB]
                    columnas_faltantes = [col for col in columnas_necesarias if col not in df_base.columns]
                    
                    if columnas_faltantes:
                        st.error(f"❌ Columnas no encontradas: {', '.join(columnas_faltantes)}")
                    else:
                        df_comun = df_base.dropna(subset=columnas_necesarias)
                        tamaño_muestra = len(df_comun)

                        if tamaño_muestra == 0:
                            st.error("No hay registros que tengan datos para ambas variables simultáneamente.")
                        else:
                            mascara_A = filtro_df_operacion(df_comun, var_selected, operadorA, val_a)
                            mascara_B = filtro_df_operacion(df_comun, var_selectedB, operadorB, val_b)

                            if '∪' in op_Conjunto:
                                mascara_final = mascara_A | mascara_B
                                condicional_bool = False
                            elif '∩' in op_Conjunto:
                                mascara_final = mascara_A & mascara_B
                                condicional_bool = False
                            else:
                                mascara_final = mascara_A & mascara_B
                                condicional_bool = True

                            if not condicional_bool:
                                casos = mascara_final.sum()
                                prob = (casos / tamaño_muestra) * 100
                            else:
                                casos_inter = mascara_final.sum()
                                casos_B = mascara_B.sum()
                                if casos_B == 0:
                                    st.error("No se puede calcular P(A|B) porque el evento B nunca ocurre en esta muestra.")
                                    prob = 0.0
                                else: 
                                    #CALCULO DE LA PROBABILIDAD CONDICIONAL
                                    prob = (casos_inter / casos_B) * 100

                            st.markdown(f"#### ${(prob):.2f}$%")
                            # st.caption(f"Muestra común: {tamaño_muestra} países (donde existen ambos registros).")


            titulo_P.markdown(f"#### $P(A{op_Conjunto}B):$", text_alignment= 'center')



st.markdown("""
    <style>
        /* Reduce el padding superior del contenedor principal */
        .block-container {
            padding-top: 4rem;
            padding-bottom: 0rem;
            margin-top: 0rem;
        }
        
        /* Opcional: Ocultar el menú de hamburguesa y el footer de 'Made with Streamlit' 
           (Recomendado solo para el producto final) */
        
        /* #MainMenu {visibility: hidden;} */
        /* footer {visibility: hidden;} */
        
    </style>
""", unsafe_allow_html=True)