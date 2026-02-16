import streamlit as st
import plotly.express as px
import pandas as pd
from src.clase_analizador import Analizador_Estadistico
from src.datos import cargar_datos
from src.views.analisis_cuantitativo.analisis import resultados_analisis

st.set_page_config(page_title="Analisis de Variables Cuantitativas", page_icon='static/column-chart-icon.svg', layout= 'wide')
st.logo('static/column-chart-icon.svg', icon_image='static/column-chart-icon.svg')

st.sidebar.header("Análisis de Variables Cuantitativas")
st.sidebar.markdown("""
    <style>
.small-font {
    font-size:18px !important;
    color: #888888;
}
</style>
<p class="small-font">
    Explora la distribución estadística detallada (media, cuartiles, outliers) 
    seleccionando una métrica y un año específico.
</p>""", unsafe_allow_html= True)

if __name__ == '__main__':
    if 'activar_analisis' not in st.session_state:
        st.session_state.activar_analisis = False
    
    def reset_analisis():
        st.session_state.activar_analisis = False
    
    df = cargar_datos()
    datos = Analizador_Estadistico(df)

    col_sel = st.columns(2)

    with col_sel[0]:
        var_selected = st.selectbox(
            'Variable',
            ['Spending_B', 'Growth_Rate', 'Share_of_GDP', 'Per_Capita', 'Share_of_Govt_Spending'],
            index= None,
            placeholder= 'Seleccione una variable...',
            key= 'var_A',
            on_change= reset_analisis
        )

    with col_sel[1]:
        year_selected = st.selectbox(
            'Año',
            sorted(df['Year'].unique(), reverse= True),
            index= None,
            placeholder= 'Seleccione un año...',
            key= 'var_B',
            on_change= reset_analisis
        )    

    if st.button('Generar Informe', type= 'primary', key= 'btn_analisis'):
        st.session_state.activar_analisis = True
        
        st.session_state.var_actual = var_selected
        st.session_state.year_actual = year_selected
        
        stats = datos.generate_resumen(var_selected, year_selected)
        
        df_plot = df[df['Year'] == year_selected].copy()
        df_plot = df_plot.dropna(subset= [var_selected])

        var_porcentuales= ['Share_of_GDP', 'Share_of_Govt_Spending', 'Growth_Rate']
        if var_selected in var_porcentuales:
            df_plot[var_selected]= df_plot[var_selected]*100
        
        st.session_state.data_resumen = stats
        st.session_state.df_plot = df_plot 
        
    else:
        st.info('Ingrese las variables para visualizar el informe.')

    if st.session_state.get('activar_analisis', False) and 'df_plot' in st.session_state:
        stats = st.session_state.data_resumen
        df_plot = st.session_state.df_plot
        var = st.session_state.var_actual
        year = st.session_state.year_actual
        
        resultados_analisis(stats, var_selected, year_selected, datos, df_plot)
        



#REDUCCION DEL HEADER Y EL FOOTER
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