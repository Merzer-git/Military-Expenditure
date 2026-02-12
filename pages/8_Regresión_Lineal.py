import streamlit as st
from src.datos import cargar_datos
from src.views.regresion_lineal.regresion import render_regresion

st.set_page_config(page_title= 'Regresión Lineal', layout= 'wide')
st.sidebar.subheader('Regresión Lineal')
st.sidebar.markdown("""
    <style>
.small-font {
    font-size:18px !important;
    color: #888888;
}
</style>
<p class="small-font">
    
</p>""", unsafe_allow_html= True)
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

def main():
    df = cargar_datos()
    
    render_regresion(df)
    
if __name__ == '__main__':
    main()