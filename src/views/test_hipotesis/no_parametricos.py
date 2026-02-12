import streamlit as st
import pandas as pd
from src.views.test_hipotesis.test_no_param.bondad_ajuste import render_bondad_ajuste
from src.views.test_hipotesis.test_no_param.chi_cuadrado import render_ind_homo

def render_no_parametrico(df):
    tabs = st.tabs(['Prueba de Bondad de Ajuste', 'Prueba de Independencia & Homogeneidad'])
    
    with tabs[0]:
        render_bondad_ajuste(df)
        
    with tabs[1]:   #PRUEBAS DE INDEPENDENCIA Y HOMOGENEIDAD
        render_ind_homo(df)