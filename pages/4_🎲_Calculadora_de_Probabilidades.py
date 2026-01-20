from operator import index
from tkinter import Variable
import streamlit as st
import pandas as pd
import numpy as np
from src.datos import cargar_datos

st.set_page_config(page_title='Calculadora de Probabilidades', page_icon='🎲', layout= 'wide')
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

def activar_analisis():
    st.session_state.analisis_listo = True

def generar_tabla_frecuencias(df, variable, year=None):
    if variable in variables_temporales:
        if year is not None:
            df_filtrado = df[df['Year'] == year].copy()
        else:
            return pd.DataFrame(), 0, 0, 0, 0, 0
    else:
        df_filtrado = df.copy()

    datos_validos = df_filtrado[variable].replace([np.inf, -np.inf], np.nan).dropna()
    total_original = len(datos_validos)  #TAMAÑO DE LA MUESTRA
    
    if variable == 'Growth_Rate':
        datos_validos = datos_validos[(datos_validos <= 2.0) & (datos_validos >= -1.0)]
    
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
    total_datos = tabla['Frecuencia Abs. (fi)'].sum()
    tabla['Frecuencia Rel. (hi)'] = tabla['Frecuencia Abs. (fi)'] / total_datos
    tabla['Frecuencia Abs. Acumulada (Fi)'] = tabla['Frecuencia Abs. (fi)'].cumsum()
    tabla['Frecuencia Rel. Acumulada (Hi)'] = tabla['Frecuencia Rel. (hi)'].cumsum()

    excluidos = total_original - n
        
    return tabla, n, R, N, A, excluidos

variables_temporales = ['Spending_B', 'Per_Capita']

if __name__ == '__main__':
    df = cargar_datos()
    col_1, col_2= st.columns(2) #col_1 -> COLUMNA DE VARIABLES | col_2 -> COLUMNA DE AÑOS (OPCIONAL)
    tab_tabla, tab_prob = st.tabs(['Tabla de Frecuencias', 'Calculadora de Probabilidades'])

    with col_1:
        var_selected = st.selectbox(
            'Variable',
            options= ['Spending_B', 'Growth_Rate', 'Share_of_GDP', 'Per_Capita', 'Share_of_Govt_Spending'],
            index= None,
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
    with tab_tabla:
        if 'analisis_listo' not in st.session_state:
            st.session_state.analisis_listo = False
        
        boton = st.button(
            "Generar Tabla de Frecuencias",
            on_click= activar_analisis,
            disabled= (var_selected is None),
            type= 'primary'
        )

        if st.session_state.analisis_listo and var_selected:
            tabla_frec, n, recorrido, intervalos, amplitud, dif = generar_tabla_frecuencias(df, var_selected, year_selected)
            st.dataframe(tabla_frec)
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
                    options= ['<', '<=', '>', '>=', '=='],
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
                    st.markdown("#### $RESULTADO$")
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