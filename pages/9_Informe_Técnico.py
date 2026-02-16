import streamlit as st

st.set_page_config(page_title= 'Informe Técnico', page_icon= 'static/file-black-icon.svg', layout= 'wide')
st.logo('static/file-black-icon.svg', icon_image='static/file-black-icon.svg')

st.sidebar.header('Informe Técnico')
st.sidebar.markdown("""
    <style>
.small-font {
    font-size:18px !important;
    color: #888888;
}
</style>
<p class="small-font">
    Lee el infome técnico del trabajo de investigación.
</p>
    """, unsafe_allow_html= True)

st.header('🔜**PROXIMAMENTE**')
st.divider()


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