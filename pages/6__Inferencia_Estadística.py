import streamlit as st
import pandas as pd
import numpy as np
import scipy.stats as stat
import plotly.graph_objects as go
from src.datos import cargar_datos

st.set_page_config(page_title='Inferencia Estadística', page_icon='static/scale-icon.svg', layout= 'wide')
st.logo('static/scale-icon.svg', icon_image='static/scale-icon.svg')

st.sidebar.subheader('Inferencia Estadística')
st.sidebar.markdown("""
    <style>
.small-font {
    font-size:18px !important;
    color: #888888;
}
</style>
<p class="small-font">
    Calcula y analiza intervalos de confianza y detecta diferencias significativas en el gasto entre distintas Eras y Regiones.
</p>""", unsafe_allow_html= True)

eras_color = {
    '1. Guerra Fría (1949-1991)': '#3F88C5',
    '2. Posguerra Fría (1992-2000)': '#20C997',
    '3. Guerra contra el Terror (2001-2013)': '#E89005',
    '4. Resurgimiento de Tensiones (2014-2022)': '#6610F2',
    '5. Inestabilidad Global (2022-Presente)': '#A31621'
}

COLORES_REGIONES = {
    'Europe': '#636EFA',
    'Asia & Oceania': '#EF553B',
    'Americas': '#AB63FA',
    'Middle East': '#00CC96',
    'Africa': '#FFA15A'
}

#CALCULO DEL INTERVALO DE CONFIANZA PARA UNA ERA SELECCIONADA
def IC_media (datos, confianza= 0.95):
    n = len(datos)
    media= np.mean(datos)
    desvio_s = np.std(datos, ddof=1)    #-> con ddof=1 se trabaja la varianza muestral (n-1)

    #A VARIANZA DESCONOCIDA SE TRABAJA CON LA T DE STUDENT
    intervalo = stat.t.interval(confianza, df= n-1, loc=media, scale= desvio_s/np.sqrt(n))

    return media, intervalo

def comparar_poblaciones(datos_a, datos_b, confianza= 0.95):
    n1, n2 = len(datos_a), len(datos_b)
    var_a, var_b = np.var(datos_a, ddof=1), np.var(datos_b, ddof=1)

    ratio = max(var_a, var_b) / min(var_a, var_b)
    varianzas_iguales = ratio < 4

    if varianzas_iguales:
        sp = np.sqrt(((n1-1)*var_a + (n2-1)*var_b) / (n1+n2-2)) #AMALGAMADO DE VARIANZA
        error_std = sp * np.sqrt((1/n1) + (1/n2)) #DENOMINADOR DE LA VARIABLE T
        gl = n1 + n2 - 2
    else:
        error_std = np.sqrt((var_a/n1) + (var_b/n2))

        #VARIANZAS DESCONOCIDAS Y DISTINTAS (FORMULA DE WELSH) - grados de libertad
        num= ((var_a/n1) + (var_b/n2))**2
        den= ((var_a/n1)**2 / (n1-1)) + ((var_b/n2)**2 / (n2-1))
        gl = (num / den) - 2
    
    diff_medias = np.mean(datos_a) - np.mean(datos_b)
    t_critico = stat.t.ppf((1 + confianza) / 2, gl)
    margen_error = t_critico * error_std
    
# # --- BORRAR ESTO DESPUÉS DE PROBAR ---
#     st.write("--- DATOS PARA CALCULADORA ---")
#     st.write(f"Era A -> n: {n1}, Var: {var_a:.2f}")
#     st.write(f"Era B -> n: {n2}, Var: {var_b:.2f}")
#     st.write(f"¿Usó Welch?: {not varianzas_iguales}")
#     st.write("------------------------------")

    return {
        'n1': n1,
        'n2': n2,
        'diferencia': diff_medias,
        'margen': margen_error,
        'lim_inf': diff_medias - margen_error,
        'lim_sup': diff_medias + margen_error,
        'varianzas_iguales': varianzas_iguales,
        'gl': gl
    }




if __name__ == '__main__':
    tab_historica, tab_region = st.tabs(['Comparación Histórica (Era)', 'Comparación Regional'])
    df = cargar_datos()
    options_eras = df['Historical_Era'].unique()
    options_region = df['Region'].unique()

    with tab_historica:
        cols_var = st.columns(2)
        with cols_var[0]:
            era_seleccionada_ref = st.selectbox(
                'Seleccione una Era (Referencia)',
                options_eras,
                index= None
            )
        
        with cols_var[1]:
            era_filtrada = [op for op in options_eras if op != era_seleccionada_ref]
            era_seleccionada_comp = st.selectbox(
                'Seleccione una Era (Comparación)',
                era_filtrada,
                index= None,
                disabled= (era_seleccionada_ref is None)
            )

        df_era_a = df[df['Historical_Era'] == era_seleccionada_ref]['Spending_B'].dropna()
        media_estimada_era_a, (lim_inf_era_a, lim_sup_era_a) = IC_media(df_era_a)

        if era_seleccionada_ref is not None and era_seleccionada_comp is None:
            cols_era_a= st.columns(3)
            cols_era_a[0].metric('Media Muestral', f'${media_estimada_era_a:.2f} B')
            cols_era_a[1].metric('Límite Inferior (95%)', f'${lim_inf_era_a:.2f} B')
            cols_era_a[2].metric('Límite Superior (95%)', f'${lim_sup_era_a:.2f} B')

            color_era_actual = eras_color.get(era_seleccionada_ref, 'gray')
            fig_intervalos_era = go.Figure()
            fig_intervalos_era.add_trace(go.Scatter(
                x= [media_estimada_era_a], y= [era_seleccionada_ref],
                error_x= dict(type='data', array= [lim_sup_era_a - media_estimada_era_a], arrayminus= [media_estimada_era_a - lim_inf_era_a], thickness= 3, width= 10, color= color_era_actual),
                mode= 'markers',
                marker= dict(color= color_era_actual, size=20, symbol= 'square'),
                name= 'Estimación Puntual',
                
            ))

            fig_intervalos_era.update_layout(
                title= f'Intervalo de Confianza del Gasto Promedio - {era_seleccionada_ref}',
                xaxis_title= 'Gasto en Billones de USD',
                height= 300,
                margin= dict(l=20, r=20, t=20, b=20)
                )
            st.plotly_chart(fig_intervalos_era)
        else:
            if era_seleccionada_ref == era_seleccionada_comp:
                st.info('ℹ️ Eliga una era como referencia.')
            else:
                df_era_b = df[df['Historical_Era'] == era_seleccionada_comp]['Spending_B'].dropna()
                media_estimada_era_b, (lim_inf_era_b, lim_sup_era_b) = IC_media(df_era_b)
                
                datos_comparacion_era = comparar_poblaciones(df_era_a, df_era_b)

                res_era_cero = (datos_comparacion_era['lim_inf'] < 0 and datos_comparacion_era['lim_sup'] > 0)
                res_era_color = 'red' if res_era_cero else 'green'
                res_era_mensaje = '❌ No hay diferencia significativa' if res_era_cero else '✅ Hay diferencia significativa'

                cols_b = st.columns(3)
                cols_b[0].metric('Diferencia Estimada (A - B)', f'${datos_comparacion_era["diferencia"]:.2f} B')
                cols_b[1].metric('Límite Inferior (95%)', f'${datos_comparacion_era["lim_inf"]:.2f} B')
                cols_b[2].metric('Límite superior (95%)', f'${datos_comparacion_era["lim_sup"]:.2f} B')

                fig_diff_era = go.Figure()
                fig_diff_era.add_trace(go.Scatter(
                    x= [datos_comparacion_era['diferencia']],
                    y= ['Diferencia Estimada'],
                    error_x= dict(
                        type= 'data',
                        array= [datos_comparacion_era['margen']],
                        arrayminus= [datos_comparacion_era['margen']],
                        color= res_era_color,
                        thickness= 3,
                        width= 10
                    ),
                    mode= 'markers',
                    marker= dict(color= res_era_color, size=20, symbol= 'diamond'),
                    name= f'Dif: ${datos_comparacion_era['diferencia']:.2f} B'
                ))

                fig_diff_era.add_vline(x=0, line_width=3, line_dash= 'dash', line_color='gray', annotation_text= 'Igualdad (0)')

                fig_diff_era.update_layout(
                    title= f'Intervalo de la Diferencia ({era_seleccionada_ref} vs {era_seleccionada_comp})',
                    xaxis_title= 'Diferencia en Billones de USD',
                    height= 300,
                    margin= dict(l=20, r=20, t=20, b=20)
                )

                st.plotly_chart(fig_diff_era, use_container_width= True)

                with st.expander('Interpretación', expanded= False):
                    st.info(f"""
    **Interpretación Estadística:**
    * **n1:** {datos_comparacion_era['n1']} | **n2:** {datos_comparacion_era['n2']}
    * **Homogeneidad:** Se asumieron varianzas **{'IGUALES' if datos_comparacion_era['varianzas_iguales'] else 'DISTINTAS'}**.
    * **Grados de Libertad:** {round(datos_comparacion_era['gl'], 2)} (Calculado según bibliografía).
    * **Conclusión:** El intervalo [{datos_comparacion_era['lim_inf']:.2f}, {datos_comparacion_era['lim_sup']:.2f}] **{'INCLUYE' if res_era_cero else 'NO INCLUYE'}** al cero.
    * **Veredicto:** {res_era_mensaje}.
    """)

            
    with tab_region:
        cols = st.columns(2)
        with cols[0]:
            region_seleccionada_ref = st.selectbox(
                'Seleccione un Región (Referencia)',
                options_region,
                index= None
            )
        
        region_filtrada = [op for op in options_region if op != region_seleccionada_ref]

        with cols[1]:
            region_seleccionada_comp = st.selectbox(
                'Seleccione una Región (Comparación)',
                region_filtrada,
                index= None,
                disabled= (region_seleccionada_ref is None)
            )

        df_region_a = df[df['Region'] == region_seleccionada_ref]['Share_of_GDP'].dropna()
        media_estimada_region_a, (lim_inf_region_a, lim_sup_region_a) = IC_media(df_region_a)

        if region_seleccionada_ref is not None and region_seleccionada_comp is None:
            cols_region_a = st.columns(3)
            cols_region_a[0].metric('Media Muestral', f'{media_estimada_region_a*100:.2f}%')
            cols_region_a[1].metric('Límite Inferior (95%)', f'{lim_inf_region_a*100:.2f}%')
            cols_region_a[2].metric('Límite Superior (95%)', f'{lim_sup_region_a*100:.2f}%')

            color_region_actual = COLORES_REGIONES.get(region_seleccionada_ref, 'gray')
            fig_intervalos_region = go.Figure()
            fig_intervalos_region.add_trace(go.Scatter(
                x= [media_estimada_region_a],
                y= [region_seleccionada_ref],
                error_x= dict(
                    type= 'data',
                    array= [lim_sup_region_a - media_estimada_region_a],
                    arrayminus= [media_estimada_region_a - lim_inf_region_a],
                    thickness= 3,
                    width= 10,
                    color= color_region_actual
                ),
                mode= 'markers',
                marker= dict(
                    color= color_region_actual,
                    size= 20,
                    symbol= 'square'
                ),
                name= 'Estimacion Puntual'
            ))

            fig_intervalos_region.update_layout(
                title= f'Intervalos de Confianza del Esfuerzo Económico Promedio - {region_seleccionada_ref}',
                xaxis_title= 'Porcentaje del PBI',
                height= 300,
                margin= dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig_intervalos_region, use_container_width= True)

        else:
            if region_seleccionada_ref == region_seleccionada_comp:
                st.info('ℹ️ Eliga una región como referencia.')
            else:
                df_region_b = df[df['Region'] == region_seleccionada_comp]['Share_of_GDP'].dropna()
                media_estimada_region_b, (lim_inf_era_b, lim_sup_era_b) = IC_media(df_region_b)
                
                datos_comparacion_region = comparar_poblaciones(df_region_a, df_region_b)

                res_region_cero = (datos_comparacion_region['lim_inf'] < 0 and datos_comparacion_region['lim_sup'] > 0)
                res_region_color = 'red' if res_region_cero else 'green'
                res_region_mensaje = '❌ No hay diferencia significativa' if res_region_cero else '✅ Hay diferencia significativa'

                cols_b = st.columns(3)
                cols_b[0].metric('Diferencia Estimada (A - B)', f'{datos_comparacion_region["diferencia"]*100:.2f}%')
                cols_b[1].metric('Límite Inferior (95%)', f'{datos_comparacion_region["lim_inf"]*100:.2f}%')
                cols_b[2].metric('Límite superior (95%)', f'{datos_comparacion_region["lim_sup"]*100:.2f}%')

                fig_diff_region = go.Figure()
                fig_diff_region.add_trace(go.Scatter(
                    x= [datos_comparacion_region['diferencia']],
                    y= ['Diferencia Estimada'],
                    error_x= dict(
                        type= 'data',
                        array= [datos_comparacion_region['margen']],
                        arrayminus= [datos_comparacion_region['margen']],
                        color= res_region_color,
                        thickness= 3,
                        width= 10
                    ),
                    mode= 'markers',
                    marker= dict(color= res_region_color, size=20, symbol= 'diamond'),
                    name= f'Dif: ${datos_comparacion_region['diferencia']*100:.2f} B'
                ))

                fig_diff_region.add_vline(x=0, line_width=3, line_dash= 'dash', line_color='gray', annotation_text= 'Igualdad (0)')

                fig_diff_region.update_layout(
                    title= f'Intervalo de la Diferencia ({region_seleccionada_ref} vs {region_seleccionada_comp})',
                    xaxis_title= 'Diferencia en %',
                    height= 300,
                    margin= dict(l=20, r=20, t=20, b=20)
                )

                st.plotly_chart(fig_diff_region, use_container_width= True)

                with st.expander('Interpretación', expanded= False):
                    st.info(f"""
    **Interpretación Estadística:**
    * **n1:** {datos_comparacion_region['n1']} | **n2:** {datos_comparacion_region['n2']}
    * **Homogeneidad:** Se asumieron varianzas **{'IGUALES' if datos_comparacion_region['varianzas_iguales'] else 'DISTINTAS'}**.
    * **Grados de Libertad:** {round(datos_comparacion_region['gl'], 2)} (Calculado según bibliografía).
    * **Conclusión:** El intervalo [{datos_comparacion_region['lim_inf']:.2f}, {datos_comparacion_region['lim_sup']:.2f}] **{'INCLUYE' if res_region_cero else 'NO INCLUYE'}** al cero.
    * **Veredicto:** {res_region_mensaje}.
    """)

            
            



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