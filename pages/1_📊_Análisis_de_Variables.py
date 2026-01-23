import streamlit as st
import plotly.express as px
import pandas as pd
from src.clase_analizador import Analizador_Estadistico
from src.datos import cargar_datos

st.set_page_config(page_title="Analisis de Variables", page_icon="📊", layout= 'wide')

st.sidebar.header("Análisis de Variables")
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

config_metrics = {
    "Spending_B":{
        "label": "Gasto Militar",
        "suffix": " USD (B)",
        "desc_media": "Promedio Global",
        "desc_mediana": "Valor Típico",
        "desc_desvio": "Desvio Estandar",
        "desc_cv": "Coeficiente de Variación",
        "desc_top1": "Top 1% (C99)",
        "desc_skew": "Asimetría",
        "desc_kurt": "Kurtosis"
    },
    "Growth_Rate":{
        "label": "Tasa de Crecimiento",
        "suffix": "%",
        "desc_media": "Crecimiento Promedio",
        "desc_mediana": "Crecimiento Típico",
        "desc_desvio": "Desvío Estandar",
        "desc_cv": "Coeficiente de Variación",
        "desc_top1": "Top 1% (C99)",
        "desc_skew": "Asimetría",
        "desc_kurt": "Kurtosis"
    },
    "Share_of_GDP": {
        "label": "Carga Económica (% PIB)",
        "suffix": "%",
        "desc_media": "Peso Promedio",
        "desc_mediana": "Peso Típico",
        "desc_desvio": "Desvío Estandar",
        "desc_cv": "Coeficiente de Variación",
        "desc_top1": "Top 1% (C99)",
        "desc_skew": "Asimetría",
        "desc_kurt": "Kurtosis"
    },
    "Per_Capita":{
        "label": "Costo por Habitante",
        "suffix": " USD",
        "desc_media": "Costo Promedio",
        "desc_mediana": "Costo Típico",
        "desc_desvio": "Desvio Estandar",
        "desc_cv": "Coeficiente de Variación",
        "desc_top1": "Top 1% (C99)",
        "desc_skew": "Asimetría",
        "desc_kurt": "Kurtosis"
    },
    "Share_of_Govt_Spending":{
        "label": "Prioridad Fiscal (% Gasto Público)",
        "suffix": " %",
        "desc_media": "Prioridad Promedio",
        "desc_mediana": "Prioridad Típica",
        "desc_desvio": "Desvio Estandar",
        "desc_cv": "Coeficiente de Variación",
        "desc_top1": "Top 1% (C99)",
        "desc_skew": "Asimetría",
        "desc_kurt": "Kurtosis"
    }
}

COLORES_REGIONES = {
    'Europe': '#636EFA',
    'Asia & Oceania': '#EF553B',
    'Americas': '#AB63FA',
    'Middle East': '#00CC96',
    'Africa': '#FFA15A',
    "(?)": "#f0f2f6",  
    "Mundo": "#f0f2f6"
}

def activar_analisis():
    st.session_state.analisis_listo = True

if __name__ == '__main__':
    df = cargar_datos()
    datos = Analizador_Estadistico(df)

    col_sel1, col_sel2 = st.columns(2)

    with col_sel1:
        year_selected = st.selectbox(
            'Año',
            sorted(df['Year'].unique(), reverse= True),
            index= None,
            placeholder= 'Seleccione un año...'
        )

    with col_sel2:
        var_selected = st.selectbox(
            'Variable',
            ['Spending_B', 'Growth_Rate', 'Share_of_GDP', 'Per_Capita', 'Share_of_Govt_Spending'],
            index= None,
            placeholder= 'Seleccione una variable...'
        )

    if 'analisis_listo' not in st.session_state:
        st.session_state.analisis_listo = False

    boton = st.button(
        "Generar Informe",
        on_click= activar_analisis,
        disabled= (year_selected is None),
        type= 'primary'
    )

    if st.session_state.analisis_listo and year_selected and var_selected:
        stats = datos.generate_resumen(var_selected, year_selected)
        cfg = config_metrics.get(var_selected, {"label": var_selected, "suffix": ""})

        if stats:
            st.divider()
            st.subheader(f'Radiografía: {cfg['label']} ({year_selected})')

            col_kpi, col_grafico = st.columns([1,2], gap= 'large')
            
            with col_kpi:
                tab_central, tab_dispersion, tab_forma = st.tabs(["Tend. Central", "Dispersión", "Forma"])

                with tab_central:
                    #METRICA 1 -> MEDIA
                    st.metric(
                        label= cfg.get("desc_media", "Media"),
                        value= f"{stats['media']:,.2f}{cfg['suffix']}"
                    )

                    #METRICA 2 -> MEDIANA
                    st.metric(
                        label= cfg.get("desc_mediana", "Mediana"),
                        value= f"{stats['mediana']:,.2f}{cfg['suffix']}",
                        help= "La mediana es menos sensible a valores extremos (Outliers)"
                    ) 

                with tab_dispersion:
                    #METRICA 1 -> Top 1% (C99)
                    st.metric(
                        label = cfg.get("desc_top1", "Top 1%"),
                        value= f'{stats['c99']:,.2f}{cfg['suffix']}'
                    )
                    #METRICA 2 -> Desvío Estandar
                    st.metric(
                        label = cfg.get("desc_desvio", "Desvío Estandar"),
                        value= f"{stats['std']:,.2f}{cfg['suffix']}"
                    )

                    #METRICA 3 -> Coeficiente de Variación
                    st.metric(
                        label= cfg.get("desc_cv", "Coeficiente de Variación"),
                        value= f'{stats['cv']:,.2f}',
                        help= ">1 es alto, >4 es extremo"
                    )
                
                with tab_forma:
                    col_f1, col_f2 = st.columns(2)
                    #METRICA 1 -> Coeficiente de Asimetrica Skewness
                    col_f1.metric(
                        label= cfg.get("desc_skew", "Asimetría"),
                        value= f'{stats['skew']:,.2f}',
                        help="""Positiva -> Cola alargada a la derecha
                                Negativa -> cola alargada a la izquierda"""
                    )
                    #METRICA 2 -> Kurtosis
                    col_f2.metric(
                        label= cfg.get("desc_kurt", "Kurtosis"),
                        value= f'{stats['kurt']:,.2f}',
                        help=""">0: Leptocúrtica 
                                =0: Mesocúrtica
                                <0: Platicúrtica"""
                    )
                    st.info("Valores altos indican concentración extrema.")
                
                with st.expander("Ver reporte técnico completo"):
                    st.text(datos.format_resumen(stats, var_selected))
            
            df_plot = df[df['Year'] == year_selected].copy()
            df_plot = df_plot.dropna(subset= [var_selected])

            with col_grafico:
                opciones= ['Histograma', 'Boxplot']

                tipo_grafico= st.pills(
                    "Visualización",
                    options= opciones,
                    default= "Histograma",
                    label_visibility= "collapsed"
                )

                if not tipo_grafico:
                    tipo_grafico = "Histograma"

                titulo_eje = cfg.get('label', var_selected)
                color_map = "Region"
                usar_log = st.checkbox('Escala log', value=True, help='Útil para ver datos muy dispares')

                if usar_log:
                    n_excluidos = len(df_plot[df_plot[var_selected] <= 0])
                    df_plot = df_plot[df_plot[var_selected] > 0]

                    if n_excluidos > 0:
                        st.warning(f'⚠️ Nota: Se ocultaron {n_excluidos} paises con valores negativos o cero porque son incompatibles con la escala logarítmica.')

                if tipo_grafico == "Histograma":
                    fig= px.histogram(
                        df_plot,
                        x= var_selected,
                        nbins= 40,
                        color= 'Region',
                        log_y= usar_log,
                        title= f'Distribución de {titulo_eje}',
                        hover_data= ['Country'],
                        color_discrete_map=COLORES_REGIONES
                    )
                    fig.add_vline(x= stats['media'], line_dash = 'dash', line_color= 'red', annotation_text= 'Media', annotation_textangle= -90)
                    fig.add_vline(x= stats['mediana'], line_dash = 'dot', line_color= 'green', annotation_text= 'Mediana', annotation_position= 'top left', annotation_textangle= 90)

                elif tipo_grafico == "Boxplot":
                    fig= px.box(
                        df_plot,
                        x= var_selected,
                        y= 'Region',
                        points= 'all',
                        log_x= usar_log,
                        title= f'Dispersión y Outliers: {titulo_eje}',
                        hover_name= "Country",
                        color= 'Region',
                        color_discrete_map= COLORES_REGIONES
                    )

                fig.update_layout(
                    xaxis_title= f'{titulo_eje} ({cfg.get('suffix', '')})',
                    legend_title= 'Región',
                    margin= dict(l=20, r=20, t=40, b=20),
                    height= 450
                )

                st.plotly_chart(fig, use_container_width= True)

                max_pais = df_plot.loc[df_plot[var_selected].idxmax()]
                st.info(f'**Máximo**: {max_pais['Country']} con {max_pais[var_selected]:,.2f}{cfg['suffix']}')



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