import streamlit as st
import plotly.express as px
import pandas as pd
from src.datos import cargar_datos

st.set_page_config(page_title= "Análisis Temporal", page_icon="🕚", layout= 'wide')
st.sidebar.header("Análisis Temporal")
st.sidebar.markdown("""
    <style>
.small-font {
    font-size:18px !important;
    color: #888888;
}
</style>
<p class="small-font">
    Explora el análisis enfocado en los principales actores militares del mundo a lo largo de tres fases temporales.
</p>""", unsafe_allow_html= True)

COLORE_REGIONES = {
    'Europe': '#636EFA',
    'Asia & Oceania': '#EF553B',
    'Americas': '#AB63FA',
    'Middle East': '#00CC96',
    'Africa': '#FFA15A',
    "(?)": "#f0f2f6",  
    "Mundo": "#f0f2f6"
}

#Formato del diccionario de miembros de la OTAN -> {'País': Año_Ingreso}
OTAN = {
    #Miembros fundadores
    "Belgium": 1949,
    "Canada": 1949,
    "Denmark": 1949,
    "United States": 1949, # O "USA" según tu dataset
    "France": 1949,        # *Status especial 1966-2009
    "Iceland": 1949,       # *Sin ejército propio, gasto casi nulo
    "Italy": 1949,
    "Luxembourg": 1949,
    "Norway": 1949,
    "Netherlands": 1949,
    "Portugal": 1949,
    "United Kingdom": 1949, # O "UK"

    #Primera expansión
    "Greece": 1952,
    "Turkey": 1952,        # O "Turkiye" (nombre actual)

    #Segunda expansión
    "Germany": 1955,

    #Tercera expansión
    "Spain": 1982
}

#Formato del diccionario de miembros del Pacto de Varsovia -> {'Pais': Año_Ingreso, Año_Salida}
VARSOVIA = {
    'USSR': (1955, 1991),
    'Albania': (1955, 1968),
    'Bulgaria': (1955, 1991),
    'Czechoslovakia': (1955, 1991),
    'German Democratic Republic': (1956, 1990),
    'Hungary': (1955, 1991),
    'Poland': (1955, 1991),
    'Romania': (1955, 1991)
}

color_bloque= {
    'OTAN': '#324376',
    'Pacto de Varsovia': '#BA1200',
    'USSR': '#BA1200',
    'United States of America': '#324376',
    'United Kingdom': '#9D4EDD',
    'Germany': '#DC9E82',
    'France': '#173753',
    'Russia': '#A5402D',
    'Ukraine': '#E5D352',
    'China': '#F8333C',
    'India': '#DC851F',
    'Saudi Arabia': '#63A46C',
    'Israel': '#2892D7'

}

eventos_importantes= {
    #EVENTOS DE LA GUERRA FRIA
    "Guerra de Corea (1950)": 1950,
    "Revolución Húngara (1956)": 1956,
    "Muro de Berlín (1961)": 1961,
    "Crisis de los Misiles (1962)": 1962,
    "Golfo de Tonkín / Escalada Vietnam (1964)": 1964, 
    "Invasión Checoslovaquia (1968)": 1968,
    "Invasión a Afganistán (1979)": 1979,
    "Crisis Euromisiles (1983)": 1983,

    #EVENTOS TRANsIcION (PRE A POST GUERRA FRIA)
    'Glasnost (1985)': 1985,
    'Disolución de la URSS (1991)': 1991,

    #EVENTOS POST GUERRA FRIA
    'Dividendos de la Paz (1991)': 1991,
    'Atentado a las Torres Gemelas (2001)': 2001,
    'Invasión de Irak (2003)': 2003,
    'Crisis Financiera (2008)': 2008,
    'Anexión de Crimea (2014)': 2014,
    'Atentados en París (2015)': 2015,
    'Intervención Saudí en Yemen (2015)': 2015,
    'Pandemia COVID-19 (2020)': 2020,
    'Guerra Ucrania (2022)': 2022,
    'Guerra de Gaza (2023)': 2023
}

potencias_modernas = [
    #AMERICAS
    'United States of America',
    #EUROPE
    'United Kingdom',
    'Germany',
    'France',
    'Russia',
    'Ukraine',
    #ASIA & OCEANIA
    'China',
    'India',
    #MIDDLE EAST
    'Saudi Arabia',
    'Israel'
]

if __name__ == '__main__':
    df = cargar_datos()
    list_otan = list(OTAN.keys())
    list_varsovia = list(VARSOVIA.keys())

    def etiquetar_bloques(pais):
        if pais in list_otan:
            return "OTAN"
        elif pais in list_varsovia:
            return "Pacto de Varsovia"
        else:
            return "Otros"
        
    df['Bloque'] = df['Country'].apply(etiquetar_bloques)

    with st.expander("📜 ¿Por que un análisis en tres fases?"):
        st.markdown("""
        Durante la Guerra Fría, el bloque soviético mantuvo una estricta política de secretismo de estado, clasificando el gasto militar como información confidencial. Reconociendo esta limitación estructural en los datos, el análisis se fragmenta en tres fases metodológicas:

    * **Fase Asimétrica (1949-1987):** Nos centramos en el bloque occidental. Utilizamos a la **OTAN como "sismógrafo"**: ante la falta de registros soviéticos fiables, interpretamos los picos de gasto de la OTAN como respuestas reactivas a aumentos de tensión o capacidad del **Pacto de Varsovia**.

    * **Fase de Transición y Apertura (1988-1991):** El análisis se torna bipolar y directo (EE.UU. vs URSS). Gracias a las reformas de la *Perestroika* y, fundamentalmente, al **Glasnost** (transparencia impulsada por Gorbachov), accedemos por primera vez a registros oficiales fehacientes del gasto soviético previo a su disolución.

    * **Fase Global Moderna (1992-2024):** El análisis se vuelve global. Observamos cómo la hegemonía indiscutida de EE.UU. tras la Guerra Fría es desafiada primero por el terrorismo global y, recientemente, por el ascenso de nuevas potencias militares en un escenario multipolar.
    """)

    tab_1, tab_2, tab_3 = st.tabs(['Fase Asimétrica (1949-1987)','Fase de Transición y Apertura (1988-1991)', 'Fase Global Moderna (1992-2024)'])

    with tab_1: #TAB DE GUERRA FRIA
        df_fase1 = df[
            (df['Bloque'].isin(['OTAN', 'Pacto de Varsovia'])) &
            (df['Year'] >= 1949) & (df['Year'] < 1988)
        ]

        df_evolucion_fase1 = df_fase1.groupby(['Year', 'Bloque'])['Spending_B'].sum().reset_index()

        with st.expander("💥 Agrega eventos al gráfico", expanded= False):
            eventos_seleccionados= st.multiselect(
                'Selecciona eventos',
                options= list(eventos_importantes.keys()),
                default= ['Guerra de Corea (1950)', 'Muro de Berlín (1961)', 'Crisis de los Misiles (1962)', 'Golfo de Tonkín / Escalada Vietnam (1964)']
            )

        fig_fase1= px.line(
            df_evolucion_fase1,
            x= 'Year',
            y= 'Spending_B',
            color= 'Bloque',
            color_discrete_map= color_bloque,
            labels= {'Spending_B': 'Gasto (Billones USD)', 'Year': 'Año'},
            title= 'Evolución de Gasto por Bloque'
        )

        for evento in eventos_seleccionados:
            year_evento = eventos_importantes[evento]

            fig_fase1.add_vline(
                x= year_evento,
                line_width= 1,
                line_dash= 'dash',
                line_color= 'gray',
                annotation_text= evento,
                annotation_position= 'top left',
                annotation_textangle= -90 
            )

        st.plotly_chart(fig_fase1, use_container_width= True)

    with tab_2:
        df_fase2 = df[
            (df['Country'].isin(['United States of America', 'USSR'])) &
            (df['Year'] >= 1985) & (df['Year'] <= 1991)
        ]

        df_evolucion_fase2 = df_fase2.groupby(['Year', 'Country'])['Spending_B'].sum().reset_index()

        with st.expander("📌 Agrega eventos al gráfico", expanded= False):
            eventos_seleccionados= st.multiselect(
                'Selecciona eventos',
                options= ['Glasnost (1985)', 'Disolución de la URSS (1991)']
            )

        fig_fase2= px.line(
            df_evolucion_fase2,
            x= 'Year',
            y='Spending_B',
            color= 'Country',
            color_discrete_map= color_bloque,
            labels= {'Spenfing_B': 'Gasto (Billones USD)', 'Year': 'Año'},
            title= 'Evolución del Gasto: EE.UU vs. URSS'
        )

        for evento in eventos_seleccionados:
            year_evento = eventos_importantes[evento]

            fig_fase2.add_vline(
                x= year_evento,
                line_width= 1,
                line_dash= 'dash',
                line_color= 'gray',
                annotation_text= evento,
                annotation_position= 'top left',
                annotation_textangle= -90 
            )

        st.plotly_chart(fig_fase2, use_container_width= True)

    with tab_3:
        df_fase3 = df[
            (df['Country'].isin(potencias_modernas)) &
            (df['Year'] >= 1991)
        ]

        df_evolucion_fase3 = df_fase3.groupby(['Year', 'Country'])['Spending_B'].sum().reset_index()
        with st.expander("💥 Agrega eventos al gráfico", expanded= False):
            eventos_seleccionados = st.multiselect(
                'Selecciona eventos',
                options= ['Dividendos de la Paz (1991)', 'Atentado a las Torres Gemelas (2001)','Invasión de Irak (2003)', 'Crisis Financiera (2008)', 'Anexión de Crimea (2014)', 'Atentados en París (2015)', 'Intervención Saudí en Yemen (2015)', 'Pandemia COVID-19 (2020)', 'Guerra Ucrania (2022)', 'Guerra de Gaza (2023)']
            )

        fig_fase3= px.line(
            df_evolucion_fase3,
            x= 'Year',
            y= 'Spending_B',
            color= 'Country',
            color_discrete_map= color_bloque,
            labels= {'Spending_B': 'Gasto (Billones USD)', 'Year': 'Año'},
            title= 'Evolución del Gasto de las Potencias Modernas'
        )

        for evento in eventos_seleccionados:
            year_evento = eventos_importantes[evento]

            fig_fase3.add_vline(
                x= year_evento,
                line_width= 1,
                line_dash= 'dash',
                line_color= 'gray',
                annotation_text= evento,
                annotation_position= 'top left',
                annotation_textangle= -90
            )

        st.plotly_chart(fig_fase3, use_container_width= True)

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