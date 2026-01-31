from click import option
import streamlit as st
import pandas as pd
import numpy as np
import scipy.stats as stat
import plotly.graph_objects as go
from src.datos import cargar_datos

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
#     st.write(f"Era A -> n: {n1}, Var: {var_a:.4f}")
#     st.write(f"Era B -> n: {n2}, Var: {var_b:.4f}")
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
    tab_historica, tab_pbi = st.tabs(['Comparación Histórica (Era)', 'Comparación Regional'])
    df = cargar_datos()
    options_eras = df['Historical_Era'].unique()

    with tab_historica:
        cols_var = st.columns(2)
        with cols_var[0]:
            era_seleccionada_ref = st.selectbox(
                'Seleccione una Era (Referencia)',
                options_eras,
                index= None
            )
        
        with cols_var[1]:
            options_comp = [op for op in options_eras if op != era_seleccionada_ref]
            era_seleccionada_comp = st.selectbox(
                'Seleccione una Era (Comparación)',
                options_comp,
                index= None,
                disabled= (era_seleccionada_ref is None)
            )

        if era_seleccionada_ref == era_seleccionada_comp:
            st.warning('⚠️ Se deben elegir dos variables direfentes para la comparación.')
        else:
            df_a = df[df['Historical_Era'] == era_seleccionada_ref]['Spending_B'].dropna()
            df_b = df[df['Historical_Era'] == era_seleccionada_comp]['Spending_B'].dropna()

            media_estimada_a, (lim_inf_a, lim_sup_a) = IC_media(df_a)
            media_estimada_b, (lim_inf_b, lim_sup_b) = IC_media(df_b)
            
            datos_comparacion = comparar_poblaciones(df_a, df_b)

            res_cero = (datos_comparacion['lim_inf'] < 0 and datos_comparacion['lim_sup'] > 0)
            res_color = 'red' if res_cero else 'green'
            res_mensaje = '❌ No hay diferencia significativa' if res_cero else '✅ Hay diferencia significativa'

            fig_diff = go.Figure()
            fig_diff.add_trace(go.Scatter(
                x= [datos_comparacion['diferencia']],
                y= ['Diferencia Estimada'],
                error_x= dict(
                    type= 'data',
                    array= [datos_comparacion['margen']],
                    arrayminus= [datos_comparacion['margen']],
                    color= res_color,
                    thickness= 3,
                    width= 10
                ),
                mode= 'markers',
                marker= dict(color= res_color, size=20, symbol= 'diamond'),
                name= f'Dif: ${datos_comparacion['diferencia']:.2f} B'
            ))

            fig_diff.add_vline(x=0, line_width=3, line_dash= 'dash', line_color='gray', annotation_text= 'Igualdad (0)')

            fig_diff.update_layout(
                title= f'Intervalo de la Diferencia ({era_seleccionada_ref} vs {era_seleccionada_comp})',
                xaxis_title= 'Diferencia en Billones de USD',
                height= 250,
                margin= dict(l=20, r=20, t=20, b=20)
            )

            st.plotly_chart(fig_diff, use_container_width= True)

            with st.expander('Interpretación', expanded= False):
                st.info(f"""
**Interpretación Estadística:**
* **n1:** {datos_comparacion['n1']} | **n2:** {datos_comparacion['n2']}
* **Homogeneidad:** Se asumieron varianzas **{'IGUALES' if datos_comparacion['varianzas_iguales'] else 'DISTINTAS'}**.
* **Grados de Libertad:** {round(datos_comparacion['gl'], 2)} (Calculado según bibliografía).
* **Conclusión:** El intervalo [{datos_comparacion['lim_inf']:.2f}, {datos_comparacion['lim_sup']:.2f}] **{'INCLUYE' if res_cero else 'NO INCLUYE'}** al cero.
* **Veredicto:** {res_mensaje}.
""")

            # cols= st.columns(3)
            # cols[0].metric('Media Muestral', f'${media_estimada:.2f} B')
            # cols[1].metric('Límite Inferior (95%)', f'${lim_inf:.2f} B')
            # cols[2].metric('Límite Superior (95%)', f'${lim_sup:.2f} B')

            # fig_intervalos = go.Figure()
            # fig_intervalos.add_trace(go.Scatter(
            #     x= [media_estimada], y= [era_seleccionada_ref],
            #     error_x= dict(type='data', array= [lim_sup - media_estimada], arrayminus= [media_estimada - lim_inf]),
            #     mode= 'markers',
            #     marker= dict(color= 'red', size=15),
            #     name= 'Estimación Puntual'
            # ))

            # fig_intervalos.update_layout(title= f'Intervalo de Confianza del Gasto Promedio - {era_seleccionada_ref}')
            # st.plotly_chart(fig_intervalos)






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