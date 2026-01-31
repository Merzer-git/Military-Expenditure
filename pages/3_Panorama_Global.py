import streamlit as st
import pandas as pd
import plotly.express as px
from src.datos import cargar_datos

st.set_page_config(page_title="Panorama Global", page_icon="🌐", layout= 'wide')
st.sidebar.header("Panorama Global")
st.sidebar.markdown("""
    <style>
.small-font {
    font-size:18px !important;
    color: #888888;
}
</style>
<p class="small-font">
    Explora la evolución histórica de los bloques de poder, las tendencias mundiales y el gasto promedio por periodo histórico.
</p>""", unsafe_allow_html= True
)

COLORES_REGIONES = {
    'Europe': '#636EFA',
    'Asia & Oceania': '#EF553B',
    'Americas': '#AB63FA',
    'Middle East': '#00CC96',
    'Africa': '#FFA15A',
    "(?)": "#f0f2f6",  
    "Mundo": "#f0f2f6"
}

PALETA_ERAS= {
    '1. Guerra Fría (1949-1991)': '#3F88C5',
    '2. Posguerra Fría (1992-2000)': '#20C997',
    '3. Guerra contra el Terror (2001-2013)': '#E89005',
    '4. Resurgimiento de Tensiones (2014-2022)': '#6610F2',
    '5. Inestabilidad Global (2022-Presente)': '#A31621'
}

def activar_analisis():
    st.session_state.analisis_listo = True

if __name__ == '__main__':
    df = cargar_datos()
    col1, col2 = st.columns([3,1])

    with st.expander("Filtrar Regiones"):
        region_filter = st.multiselect("Selecciona Regiones", df['Region'].unique(), default= df['Region'].unique())
    
    df_filtrado = df[df['Region'].isin(region_filter)]
    tab_1, tab_2, tab_3 = st.tabs(['La Carrera Armamentista en el Tiempo', 'Composición del Poder Global', 'Promedios por Era Histórica'])

    with tab_1:
        df_evolucion = df_filtrado.groupby(['Year', 'Region'])['Spending_B'].sum().reset_index()

        fig_area= px.area(
            df_evolucion,
            x= 'Year',
            y= 'Spending_B',
            color= 'Region',
            title= 'Evolución del Gasto Militar por Region',
            labels= {'Spending_B': 'Gasto (Billones USD)'},
            color_discrete_map=COLORES_REGIONES
        )
        st.plotly_chart(fig_area, use_container_width= True)
        c1, c2 = st.columns([3,1])
        cols_jerarquia = ['Region', 'Subregion', 'Country']

    with tab_2:
        year_selected = st.slider(
            "Año de Análisis",
            min_value= int(df['Year'].min()),
            max_value= int(df['Year'].max()),
            value= 2024)
        df_year= df_filtrado[df_filtrado['Year'] == year_selected].copy()
        for col in cols_jerarquia:
            df_year[col] = df_year[col].fillna('Desconocido')
        
        df_year['Subregion'] = df_year['Subregion'].fillna(df_year['Region'])

        metrica_treemap = st.radio(
            "El tamaño representa: ",
            ['Gasto Total (Spending_B)', 'Esfuerzo Económico (Share_of_GDP)'],
            horizontal= True
        )

        variable_valor = 'Spending_B' if 'Gasto' in metrica_treemap else 'Share_of_GDP'
        df_year = df_year[df_year[variable_valor] > 0]

        fig_treemap = px.treemap(
            df_year,
            path= [px.Constant("Mundo"), 'Region', 'Subregion', 'Country'],
            values= variable_valor,
            color= 'Region',
            color_discrete_map= COLORES_REGIONES,
            hover_data= [variable_valor],
            title= f'Jerarquía Global en {year_selected} ({variable_valor})'
        )

        fig_treemap.update_traces(root_color= '#f0f2f6')
        fig_treemap.update_layout(margin= dict(t=50, l=0, r=0, b=0))

        st.plotly_chart(fig_treemap, use_container_width= True)

        top_pais= df_year.loc[df_year[variable_valor].idxmax()]
        st.info(f'💡 En **{year_selected}**, el líder indiscutible fue **{top_pais['Country']}**, representando una gran parte de su región.')

    with tab_3:
        st.markdown('Comparativa de intesidad promedio a precios constantes.')

        df_eras = df_filtrado.groupby('Historical_Era')['Spending_B'].mean().reset_index()

        fig_bar= px.bar(
            df_eras,
            x= 'Historical_Era',
            y= 'Spending_B',
            labels= {'Spending_B': 'Gasto (Billones USD)', 'Historical_Era': 'Periodo Histórico'},
            color= 'Historical_Era',
            color_discrete_map= PALETA_ERAS,
            text_auto= '.2s',
            title= 'Gasto Promedio según el Contexto Histórico'
        )

        fig_bar.update_layout(showlegend= False)
        st.plotly_chart(fig_bar, use_container_width= True)

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