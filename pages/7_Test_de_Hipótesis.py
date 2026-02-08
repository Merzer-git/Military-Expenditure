import streamlit as st
from src.datos import cargar_datos
from src.views.test_hipotesis.parametricos import render_parametrico
from src.views.test_hipotesis.no_parametricos import render_no_parametrico

st.set_page_config(page_title= 'Test de Hipótesis', layout='wide')

st.sidebar.subheader('Test de Hipótesis')
st.sidebar.markdown("""
    <style>
.small-font {
    font-size:18px !important;
    color: #888888;
}
</style>
<p class="small-font">
    Evalua las principales pruebas paramétricas y no paramétricas sobre las variables de interés.
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
    tabs= st.tabs(['Contrastes Paramétricos', 'Contrastes No Paramétricos'])
    
    with tabs[0]:
        render_parametrico(df)
    with tabs[1]:
        render_no_parametrico(df)

if __name__ == "__main__":
    main()