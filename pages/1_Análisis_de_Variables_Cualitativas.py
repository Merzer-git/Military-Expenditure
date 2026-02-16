import streamlit as st
import plotly.express as px
import pandas as pd
import json
from src.datos import cargar_datos
import base64
import os
import plotly.graph_objects as go

st.set_page_config(page_title="Analisis de Variables Cualitativas", page_icon='static/report-icon.svg', layout= 'wide')
st.logo('static/report-icon.svg', icon_image='static/report-icon.svg')

st.sidebar.header("Análisis de Variables Cualitativas")
st.sidebar.markdown("""
    <style>
.small-font {
    font-size:18px !important;
    color: #888888;
}
</style>
<p class="small-font">
    Explora que países son parte de la muestra y la definición de las eras que componen este periodo de 75 años.
</p>""", unsafe_allow_html= True)


COLORES_REGIONES = {
    'Europe': '#636EFA',
    'Asia & Oceania': '#EF553B',
    'Americas': '#AB63FA',
    'Middle East': '#00CC96',
    'Africa': '#FFA15A',
    "(?)": "#f0f2f6",  
    "Mundo": "#f0f2f6",
    'Sin datos de gasto': '#C0BABC'
}

iso_codes = {
    # --- AFRICA ---
    "Algeria": "DZA",
    "Libya": "LBY",
    "Morocco": "MAR",
    "Tunisia": "TUN",
    "Angola": "AGO",
    "Benin": "BEN",
    "Botswana": "BWA",
    "Burkina Faso": "BFA",
    "Burundi": "BDI",
    "Cameroon": "CMR",
    "Cape Verde": "CPV",
    "Central African Republic": "CAF",
    "Chad": "TCD",
    "Congo, DR": "COD",       # Democratic Republic of the Congo
    "Congo, Republic": "COG", # Republic of the Congo
    "Cote d'Ivoire": "CIV",
    "Djibouti": "DJI",
    "Equatorial Guinea": "GNQ",
    "Eritrea": "ERI",
    "Ethiopia": "ETH",
    "Gabon": "GAB",
    "Gambia, The": "GMB",
    "Ghana": "GHA",
    "Guinea": "GIN",
    "Guinea-Bissau": "GNB",
    "Kenya": "KEN",
    "Lesotho": "LSO",
    "Liberia": "LBR",
    "Madagascar": "MDG",
    "Malawi": "MWI",
    "Mali": "MLI",
    "Mauritania": "MRT",
    "Mauritius": "MUS",
    "Mozambique": "MOZ",
    "Namibia": "NAM",
    "Niger": "NER",
    "Nigeria": "NGA",
    "Rwanda": "RWA",
    "Senegal": "SEN",
    "Seychelles": "SYC",
    "Sierra Leone": "SLE",
    "Somalia": "SOM",
    "South Africa": "ZAF",
    "South Sudan": "SSD",
    "Sudan": "SDN",
    "Eswatini": "SWZ",
    "Tanzania": "TZA",
    "Togo": "TGO",
    "Uganda": "UGA",
    "Zambia": "ZMB",
    "Zimbabwe": "ZWE",

    # --- AMERICAS ---
    "Belize": "BLZ",
    "Costa Rica": "CRI",
    "Cuba": "CUB",
    "Dominican Republic": "DOM",
    "El Salvador": "SLV",
    "Guatemala": "GTM",
    "Haiti": "HTI",
    "Honduras": "HND",
    "Jamaica": "JAM",
    "Mexico": "MEX",
    "Nicaragua": "NIC",
    "Panama": "PAN",
    "Trinidad and Tobago": "TTO",
    "Canada": "CAN",
    "United States of America": "USA",
    "Argentina": "ARG",
    "Bolivia": "BOL",
    "Brazil": "BRA",
    "Chile": "CHL",
    "Colombia": "COL",
    "Ecuador": "ECU",
    "Guyana": "GUY",
    "Paraguay": "PRY",
    "Peru": "PER",
    "Uruguay": "URY",
    "Venezuela": "VEN",

    # --- ASIA & OCEANIA ---
    "Australia": "AUS",
    "Fiji": "FJI",
    "New Zealand": "NZL",
    "Papua New Guinea": "PNG",
    "Afghanistan": "AFG",
    "Bangladesh": "BGD",
    "India": "IND",
    "Nepal": "NPL",
    "Pakistan": "PAK",
    "Sri Lanka": "LKA",
    "China": "CHN",
    "Japan": "JPN",
    "Korea, North": "PRK",
    "Korea, South": "KOR",
    "Mongolia": "MNG",
    "Taiwan": "TWN",
    "Brunei": "BRN",
    "Cambodia": "KHM",
    "Indonesia": "IDN",
    "Laos": "LAO",
    "Malaysia": "MYS",
    "Myanmar": "MMR",
    "Philippines": "PHL",
    "Singapore": "SGP",
    "Thailand": "THA",
    "Timor Leste": "TLS",
    "Viet Nam": "VNM",
    "Kazakhstan": "KAZ",
    "Kyrgyz Republic": "KGZ",
    "Tajikistan": "TJK",
    "Turkmenistan": "TKM",
    "Uzbekistan": "UZB",

    # --- EUROPE ---
    "Albania": "ALB",
    "Bosnia and Herzegovina": "BIH",
    "Bulgaria": "BGR",
    "Croatia": "HRV",
    "Czechia": "CZE",
    "Estonia": "EST",
    "Hungary": "HUN",
    "Kosovo": "XKX", # Codigo temporal usado comunmente para Kosovo
    "Latvia": "LVA",
    "Lithuania": "LTU",
    "North Macedonia": "MKD",
    "Montenegro": "MNE",
    "Poland": "POL",
    "Romania": "ROU",
    "Serbia": "SRB",
    "Slovakia": "SVK",
    "Slovenia": "SVN",
    "Armenia": "ARM",
    "Azerbaijan": "AZE",
    "Belarus": "BLR",
    "Georgia": "GEO",
    "Moldova": "MDA",
    "Russia": "RUS",
    "Ukraine": "UKR",
    "Austria": "AUT",
    "Belgium": "BEL",
    "Cyprus": "CYP",
    "Denmark": "DNK",
    "Finland": "FIN",
    "France": "FRA",
    "Germany": "DEU",
    "Greece": "GRC",
    "Iceland": "ISL",
    "Ireland": "IRL",
    "Italy": "ITA",
    "Luxembourg": "LUX",
    "Malta": "MLT",
    "Netherlands": "NLD",
    "Norway": "NOR",
    "Portugal": "PRT",
    "Spain": "ESP",
    "Sweden": "SWE",
    "Switzerland": "CHE",
    "United Kingdom": "GBR",

    # --- MIDDLE EAST ---
    "Bahrain": "BHR",
    "Egypt": "EGY",
    "Iran": "IRN",
    "Iraq": "IRQ",
    "Israel": "ISR",
    "Jordan": "JOR",
    "Kuwait": "KWT",
    "Lebanon": "LBN",
    "Oman": "OMN",
    "Qatar": "QAT",
    "Saudi Arabia": "SAU",
    "Syria": "SYR",
    "Türkiye": "TUR",
    "Turkey": "TUR",
    "United Arab Emirates": "ARE",
    "Yemen": "YEM" 
}

# Correcciones para que los nombres de SIPRI coincidan con tu GeoJSON de 1960
correcciones_1960 = {
    # --- ÁFRICA ---
    "Cote d'Ivoire": "Ivory Coast",
    "Congo, DR": "Zaire",           # El GeoJSON usa el nombre de 1971-1997
    "Congo, Republic": "Congo",
    "Eswatini": "Swaziland",
    "Tanzania": "Tanzania",         # Nota: En 1960 era Tanganica, pero tu GeoJSON dice Tanzania
    "Burkina Faso": "Burkina Faso", # Tu GeoJSON usa el nombre moderno
    "Equatorial Guinea": "Equatorial Guinea", 
    "Gambia, The": "Gambia, The",

    # --- AMÉRICA ---
    "United States of America": "United States of America", # Coinciden, pero por seguridad
    "Trinidad and Tobago": "Trinidad", # El GeoJSON solo dice Trinidad

    # --- ASIA ---
    "Myanmar": "Burma",
    "Viet Nam": "Vietnam",
    "Sri Lanka": "Sri Lanka",       # GeoJSON usa el moderno (no Ceylan)
    "Türkiye": "Turkey",
    "Yemen, North": "Yemen",        # Asumimos mapeo al Yemen del GeoJSON
    "Kyrgyz Republic": "USSR",      # Por si se filtran datos modernos
    "Kazakhstan": "USSR",
    "Turkmenistan": "USSR",
    "Uzbekistan": "USSR",
    "Tajikistan": "USSR",
    
    # --- EUROPA (Bloque del Este) ---
    "Russia": "USSR",               # Vital: SIPRI puede tener ambos, unificamos a USSR
    "Ukraine": "USSR",
    "Belarus": "USSR",
    "Moldova": "USSR",
    "Georgia": "USSR",
    "Armenia": "USSR",
    "Azerbaijan": "USSR",
    "Estonia": "USSR",
    "Latvia": "USSR",
    "Lithuania": "USSR",
    "Czechia": "Czechoslovakia",
    "Slovakia": "Czechoslovakia",
    "Serbia": "Yugoslavia",
    "Croatia": "Yugoslavia",
    "Slovenia": "Yugoslavia",
    "Bosnia and Herzegovina": "Yugoslavia",
    "North Macedonia": "Yugoslavia",
    "Montenegro": "Yugoslavia",
    "Kosovo": "Yugoslavia",

    
    # --- OTROS ---
    "German Democratic Republic": "German Democratic Republic", # Coinciden
    "Germany": "Germany",           # Se refiere a Alemania Occidental en el GeoJSON
}

def cargar_imagen_local(ruta_archivo):
    with open(ruta_archivo, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    # Detectar extensión para el header correcto
    ext = os.path.splitext(ruta_archivo)[1].lower()
    tipo = "svg+xml" if ext == ".svg" else "png" if ext == ".png" else "jpeg"
    return f"data:image/{tipo};base64,{encoded_string}"

def activar_analisis():
    st.session_state.analisis_listo = True

if __name__ == '__main__':
    
    df = cargar_datos()

    with open('./data/world_1960.geojson', 'r', encoding= 'utf-8') as f:
        geojson_1960 = json.load(f)

    tab_regiones, tab_eras = st.tabs(['Análisis Geoespacial', 'Análisis Temporal'])

    with tab_regiones:   #MAPA DEL MUNDO (ACTUAL Y 1960) Y GRAFICO DE BARRAS PARA CANTIDAD DE PAISES POR REGION (ANUAL)
        tab_mapa, tab_barra = st.tabs(['Mapa de la muestra', 'Países de la muestra por Región'])

        with tab_mapa:
            cols = st.columns([2,1,1])

            with cols[0]:
                selected_year = st.slider(
                    'Seleccione un año',
                    min_value= 1992,
                    max_value= 2024,
                    value= 2024,
                    step= 1,
                    help= 'Mapa mundial post Guerra Fría.',
                    key='year_slider_map'
                )

            with cols[1]:
                st.write('')
                st.write('')
                mapa_historico = st.toggle(
                    '🗺️ Usar fronteras 1960',
                    help= "Activa el mapa político de la Guerra Fría."
                )
            
            if mapa_historico:
                df_1960 = df[df['Year'] == 1960].copy()
                df_paises = df_1960.copy()
                df_paises['NAME_1960'] = df_paises['Country'].map(correcciones_1960).fillna(df_paises['Country'])
                
                # Identificar países CON datos de gasto (Spending_B no es NaN)
                df_paises['Tiene_Datos'] = df_paises['Spending_B'].notna()
                
                # Extraer todos los nombres de países del GeoJSON
                todos_paises_geojson = [feature['properties']['NAME'] for feature in geojson_1960['features']]
                
                # Crear dataframe base con TODOS los países del GeoJSON
                df_todos = pd.DataFrame({'NAME_1960': todos_paises_geojson})
                
                # Agregar información de los países
                df_con_info = df_paises[['NAME_1960', 'Region', 'Tiene_Datos']].drop_duplicates(subset=['NAME_1960'], keep='first')
                df_todos = df_todos.merge(df_con_info, on='NAME_1960', how='left')
                
                # Asignar región incluso a países sin datos de gasto (si tienen Region asignada)
                # Si un país está en df pero tiene Spending_B = NaN, aún puede tener Region
                df_todos['Tipo'] = df_todos.apply(
                    lambda row: row['Region'] if pd.notna(row['Region']) and row['Tiene_Datos'] == True
                    else 'Sin datos de gasto',
                    axis=1
                )
                
                # Crear mapa de colores con transparencia para países sin datos
                color_map = {}
                for region, color in COLORES_REGIONES.items():
                    color_map[region] = color
                
                fig_mapa = px.choropleth(
                    df_todos,
                    geojson=geojson_1960,
                    locations='NAME_1960',
                    featureidkey='properties.NAME',
                    color='Tipo',
                    color_discrete_map=color_map,
                    hover_name='NAME_1960',
                    hover_data={'NAME_1960': False, 'Region': True, 'Tipo': False},
                    projection='natural earth',
                    title='Mapa Histórico - Fronteras de la Guerra Fría (1960)',
                    category_orders={'Tipo': list(COLORES_REGIONES.keys()) + ['Sin datos de gasto']}
                )

                fig_mapa.update_geos(
                    showcountries=True,
                    countrycolor='lightgray',
                    countrywidth=0.5,
                    fitbounds='locations',
                    visible=False,
                    showland=True,
                    landcolor='white',
                    showocean=True,
                    oceancolor='lightblue'
                )

                st.plotly_chart(fig_mapa, use_container_width=True)

            else:
                df_paises = df[df['Year'] == selected_year].copy()
                df_paises['ISO-3'] = df_paises['Country'].map(iso_codes)
                df_paises = df_paises.dropna(subset=['Spending_B'])
                n_paises = df_paises['Country'].nunique()
                with cols[2]:
                    st.info(f"En el año **{selected_year}**, el dataset cuenta con datos de **{n_paises}** países.")
                
                fig_mapa = px.choropleth(
                    df_paises,
                    locations= 'ISO-3',
                    color= 'Region',
                    color_discrete_map= COLORES_REGIONES,
                    hover_name= 'Country',
                    projection= 'natural earth',
                    title= f'Cobertura Geográfica {selected_year}',
                    color_discrete_sequence= px.colors.qualitative.Bold
                )

                fig_mapa.update_geos(
                    showcountries= True,
                    countrycolor= 'lightgray',
                    showland= True,
                    landcolor= 'white',
                    showocean= True,
                    oceancolor= 'lightblue'
                )

                st.plotly_chart(fig_mapa, use_container_width= True)

        with tab_barra:
            col_barra = st.columns([1,1])
            min_year = int(df['Year'].min())
            max_year = int(df['Year'].max())
            
            with col_barra[0]:
                selected_year = st.slider(
                    'Seleccione un año',
                    min_value= min_year,
                    max_value= max_year,
                    value= 2024,
                    step= 1,
                    help= 'Desliza para ver la disponibilidad de datos por año.',
                    key='year_slider_barra'
                )

            # Filtrar datos por año seleccionado
            df_year = df[df['Year'] == selected_year].copy()
            # Eliminar países sin datos en Spending_B
            df_year = df_year.dropna(subset=['Spending_B'])
            n_paises = df_year['Country'].nunique()
            
            with col_barra[1]:
                st.info(f"En el año **{selected_year}**, el dataset cuenta con datos de **{n_paises}** países.")

            # Contar países por región
            conteo_region = df_year['Region'].value_counts().reset_index()
            conteo_region.columns = ['Region', 'Count']
            
            # Reordenar para mantener consistencia
            conteo_region = conteo_region.sort_values('Region')

            fig_bar = px.bar(
                conteo_region,
                x= 'Region',
                y= 'Count',
                orientation= 'v',
                text= 'Count',
                color = 'Region',
                color_discrete_map= COLORES_REGIONES,
                title= f'Cantidad de países por Región ({selected_year})',
                color_discrete_sequence= px.colors.qualitative.Bold
            )

            fig_bar.update_layout(showlegend= False)
            fig_bar.update_traces(textposition='auto')
            st.plotly_chart(fig_bar, use_container_width= True)

    with tab_eras:    #LINEA DE TIEMPO
        #{"Año": 1949, "Evento": "Inicio Guerra Fría", "Detalle": "Creación de la OTAN / Bomba soviética", "Nivel": 1}
        data_hitos = [
    {'Año': 1950, 'Evento': 'Guerra de Corea', 'Detalle': 'Primera "guerra caliente" de la Guerra Fría entre el bloque comunista y fuerzas de la ONU/EE.UU.', 'Nivel':0.5},
    {'Año': 1956, 'Evento': 'Revolución Húngara', 'Detalle': 'Levantamiento popular contra el gobierno estalinista, sofocado brutalmente por tanques soviéticos.', 'Nivel': 0.3},
    {'Año': 1961, 'Evento': 'Muro de Berlín', 'Detalle': 'Construcción del símbolo físico de la división bipolar para frenar el éxodo hacia Occidente.', 'Nivel': 1},
    {'Año': 1962, 'Evento': 'Crisis de los Misiles', 'Detalle': 'Punto máximo de tensión nuclear tras el descubrimiento de bases soviéticas en Cuba.', 'Nivel': 2.8},
    {'Año': 1964, 'Evento': 'Golfo de Tonkín', 'Detalle': 'Incidente naval que sirvió de detonante para la intervención masiva de EE.UU. en Vietnam.', 'Nivel': 1.2},
    {'Año': 1968, 'Evento': 'Invasión a Checoslovaquia', 'Detalle': 'Tropas del Pacto de Varsovia ponen fin a la "Primavera de Praga" y las reformas liberalizadoras.', 'Nivel': 0.4},
    {'Año': 1979, 'Evento': 'Invasión a Afganistán', 'Detalle': 'Intervención soviética que inició una guerra de desgaste de 10 años contra insurgentes apoyados por EE.UU.', 'Nivel': 1},
    {'Año': 1983, 'Evento': 'Crisis de Euromisiles', 'Detalle': 'Escalada de tensión por el despliegue de misiles nucleares de rango intermedio en Europa (Pershing II/SS-20).', 'Nivel': 1.5},
    {'Año': 1988, 'Evento': 'Glasnost y Perestroika', 'Detalle': 'Reformas de apertura política y económica de Gorbachov que aceleraron el colapso del bloque soviético.', 'Nivel': 2.2},
    {'Año': 1991, 'Evento': 'Caída de la URSS', 'Detalle': 'Disolución oficial de la Unión Soviética, marcando el fin de la Guerra Fría y la bipolaridad.', 'Nivel': 3},
    {'Año': 2001, 'Evento': 'Atentados del 11-S', 'Detalle': 'Ataques terroristas en EE.UU. que desencadenaron la "Guerra contra el Terror" y la invasión de Afganistán.', 'Nivel': 2.8},
    {'Año': 2003, 'Evento': 'Invasión a Irak', 'Detalle': 'Coalición liderada por EE.UU. derroca a Saddam Hussein bajo la premisa de armas de destrucción masiva.', 'Nivel': 1.2},
    {'Año': 2008, 'Evento': 'Crisis Financiera Global', 'Detalle': 'Recesión económica mundial que forzó recortes significativos en los presupuestos de defensa occidentales.', 'Nivel': 0.5},
    {'Año': 2014, 'Evento': 'Anexión de Crimea', 'Detalle': 'Rusia toma control de la península ucraniana, marcando el retorno de la tensión militar en Europa.', 'Nivel': 2.8},
    {'Año': 2015, 'Evento': 'Atentados en París', 'Detalle': 'Ataques del ISIS en Europa que impulsaron un aumento en seguridad interna y operaciones en Siria.', 'Nivel': 1.6},
    {'Año': 2015, 'Evento': 'Guerra en Yemen', 'Detalle': 'Intervención de la coalición liderada por Arabia Saudita, disparando el gasto militar en Medio Oriente.', 'Nivel': 0.6},
    {'Año': 2020, 'Evento': 'Pandemia COVID-19', 'Detalle': 'Crisis sanitaria global que desvió recursos y requirió apoyo logístico de las fuerzas armadas.', 'Nivel': 0.4},
    {'Año': 2022, 'Evento': 'Guerra en Ucrania', 'Detalle': 'Invasión rusa a gran escala, provocando el mayor rearme de la OTAN desde la Guerra Fría.', 'Nivel': 2.5},
    {'Año': 2023, 'Evento': 'Guerra en Gaza', 'Detalle': 'Escalada del conflicto israelí-palestino con alto impacto en la seguridad regional de Medio Oriente.', 'Nivel': 1.4}
]

        # Definimos las franjas de fondo (Las Eras)
        eras = [
            (1947, 1991, "Guerra Fría", "#3F88C5"),
            (1991, 2001, "Posguerra Fría", "#20C997"),
            (2001, 2014, "Guerra contra el Terror", "#E89005"),
            (2014, 2022, "Resurg. de Tensiones", "#6610F2"),
            (2022, 2028, "Inestabilidad Global", "#A31621"),
        ]

        # 2. CONSTRUCCIÓN DEL GRÁFICO
        fig_timeline = go.Figure()

        # A. Añadimos las franjas de colores (Eras)
        for inicio, fin, nombre, color in eras:
            fig_timeline.add_vrect(
                x0=inicio, x1=fin,
                fillcolor=color, opacity=0.15,
                layer="below", line_width=0,
                annotation_text=nombre, annotation_position="top left",
                annotation_font= dict(
                    size=13,
                    color='#1a1a1a',
                    family= 'Arial'
                )
            )

        # B. Añadimos los "Lollipops" (Líneas verticales y puntos)
        # Extraemos listas para plotly
        anios = [d["Año"] for d in data_hitos]
        niveles = [d["Nivel"] for d in data_hitos] # Altura para que no se solapen
        textos = [d["Evento"] for d in data_hitos]
        detalles = [d["Detalle"] for d in data_hitos]

        # Líneas verticales (tallo del lollipop)
        for i in range(len(anios)):
            fig_timeline.add_shape(
                type="line",
                x0=anios[i], y0=0, x1=anios[i], y1=niveles[i],
                line=dict(color="gray", width=1, dash="dot")
            )

        # Puntos (caramelo del lollipop)
        fig_timeline.add_trace(go.Scatter(
            x=anios, 
            y=niveles,
            mode="markers+text",
            text=textos,
            textposition="top center",
            textfont= dict(size=11, color= '#1a1a1a', family= 'Arial'),
            marker=dict(
                size=10,
                color="#2c3e50",
                line= dict(width=2, color= 'white')
            ),
            hovertext=detalles, # Lo que sale al pasar el mouse
            hoverinfo="text+x",
            name="Hitos"
        ))

        # 3. ESTÉTICA FINAL
        fig_timeline.update_layout(
            title="Cronología Geopolítica del Gasto Militar",
            xaxis=dict(range=[1945, 2029], showgrid=False), # Un poco de margen
            yaxis=dict(showgrid=False, showticklabels=False, range=[0, 3.5]), # Ocultamos eje Y
            height=600,
            plot_bgcolor="white",
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=20)
        )

        st.plotly_chart(fig_timeline, use_container_width=True)
#         data = {
#     "title": {
#         "media": {
#           "url": cargar_imagen_local("./static/cold_war_flag.svg"),
#           "caption": "Contexto Global"
#         },
#         "text": {
#           "headline": "Evolución del Gasto Militar",
#           "text": "<p>Hitos clave que definieron los presupuestos de defensa.</p>"
#         }
#     },
#     "events": [
#       {
#         "start_date": {"year": "1949"},
#         "end_date": {"year": "1991"},
#         "text": {"headline": "Inicio Guerra Fría", "text": "Creación de la OTAN y polarización global."}
#       },
#       {
#         "start_date": {"year": "1991"},
#         "text": {"headline": "Caída de la URSS", "text": "Fin de la bipolaridad y reducción del gasto."}
#       },
#       # ... más eventos
#     ]
# }

#         timeline(data, height=500)


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