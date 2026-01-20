import streamlit as st
import pandas as pd
from src.datos import cargar_datos
import base64

st.set_page_config(
    page_title= "Global Defense Monitor",
    page_icon= "🌎",
    layout= "wide",
    menu_items={
        'Get Help': 'https://github.com/Merzer-git/',
        'Report a bug': 'https://github.com/Merzer-git/Military-Expenditure/issues',
        'About': """
        ### 🛡️ Dashboard de Gasto Militar Mundial
        
        Esta aplicación analiza la evolución del gasto militar global utilizando datos del **SIPRI**.
        
        **Tech Stack:**
        - Python
        - Streamlit
        - Plotly Express
        - Pandas
        
        **Autor:** Brian Alaníz
        [Ver código en GitHub](https://github.com/Merzer-git)
"""
    }
)

df = cargar_datos()

st.title("🌎 Global Defense Monitor")
st.subheader("La Guerra en números: 75 años de Gasto Militar")
st.markdown("""
    **Este dashboard explora la evolución en el Gasto Militar a nivel global, regional y por países.** Se analizan datos históricos de partidas presupuestarias destinadas a defensa recolectadas por el **SIPRI** (1949 - 2024) complementada con datos del **Banco Mundial** para entender las dinámicas de rearme, hegemonía y los conflictos geopolíticos que moldearon el mundo moderno.
""")
st.divider()
with st.expander("📜 Contexto Histórico: De la Guerra Fría a la actualidad"):
    st.markdown(
    """
    **El Legado de la Guerra Fría**:
    Tras la finalización de la Segunda Guerra Mundial el escenario global entró en un periodo histórico donde los máximos exponentes de la victoria frente a las Potencias del Eje, **Estados Unidos** y la **Unión de Repúblicas Socialistas Soviéticas**, se vieron enfrentados en una confrontación geopolítica atípica: una guerra ideológica. Este periodo, conocido como Guerra Fría, sentó un precedente peligroso para la historia moderna de los países: la "tensa calma".

    **La Amenaza Nuclear**:
    Durante décadas, el mundo estuvo al borde de un conflicto global sin precedentes, donde un error diplomático, un fallo de cálculo en una prueba nuclear o una escalada militar accidental podrían haber sido detonantes catastróficos. En este contexto, se registraron aumentos sustanciales en los presupuestos de defensa, los cuales, en determinadas potencias, fueron destinados a financiar la investigación y desarrollo de armas de destrucción masiva.

    **El Nuevo Orden Mundial**:
    La disolución de la URSS el 26 de diciembre de 1991, tras una serie de complejas reestructuraciones políticas y económicas, marcó el fin formal de este periodo. No obstante, la herencia de esta "paz armada" y la lógica de disuasión estratégica continúan influyendo, hasta el día de hoy, en las planificaciones militares de las naciones soberanas.
    """
)
st.info("**Selecciona una página del menú lateral.**")
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

def get_svg_base64(path_to_file):
    try:
        with open(path_to_file, "rb") as f:
            svg_data = f.read()
            b64_data = base64.b64encode(svg_data).decode()
            # Retorna el formato exacto que necesita HTML para mostrar la imagen
            return f"data:image/svg+xml;base64,{b64_data}"
    except FileNotFoundError:
        return "" # Devuelve vacío si no encuentra el archivo para no romper la app

sipri_svg_data = get_svg_base64('static/logo.svg')

with st.sidebar:
    st.caption("Actualizado con datos de 2024")
    st.markdown("### ℹ️ Enlaces y Fuente")

    # Badge de GITHUB (Usando shields.io como vimos antes)
    st.markdown(
        """
        <a href="https://github.com/Merzer-git/Military-Expenditure" target="_blank">
            <img src="https://img.shields.io/badge/GitHub-Ver_Código-181717?style=for-the-badge&logo=github&logoColor=white"
                 style="width: 100%; margin-bottom: 10px; border-radius: 8px; border: 2px solid #333;">
        </a>
        """,
        unsafe_allow_html=True
    )

    # Badge de SIPRI (Usando TU SVG local)
    # Usamos f-strings (f"...") para inyectar la data base64 dentro del HTML
    st.markdown(
        f"""
        <a href="https://www.sipri.org/databases/milex" target="_blank" title="Ir a la web de SIPRI">
            <div style="background-color: #FFFFFF; /* Fondo blanco para que el logo resalte */
                        padding: 8px;
                        border-radius: 8px;
                        border: 2px solid #E5E7EB; /* Borde gris suave */
                        text-align: center;
                        cursor: pointer;
                        transition: all 0.3s ease;">
                <img src="{sipri_svg_data}" 
                     alt="SIPRI Logo" 
                     style="max-height: 40px; width: auto;"> </div>
        </a>
        <p style="text-align: center; font-size: 0.8em; color: gray; margin-top: 5px;">
            Fuente oficial de los datos.
        </p>
        """,
        unsafe_allow_html=True
    )

    st.divider()
    st.caption("Developed by **Brian Alaníz**")