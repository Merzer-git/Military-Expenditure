import plotly.express as px

COLORES_REGIONES = {
    'Europe': '#636EFA',
    'Asia & Oceania': '#EF553B',
    'Americas': '#AB63FA',
    'Middle East': '#00CC96',
    'Africa': '#FFA15A',
    "(?)": "#f0f2f6",  
    "Mundo": "#f0f2f6"
}

def histograma(df, var, titulo_eje, usar_log):
    fig= px.histogram(
        df,
        x= var,
        nbins= 40,
        color= 'Region',
        log_y= usar_log,
        title= f'Distribución de {titulo_eje}',
        hover_data= ['Country'],
        color_discrete_map=COLORES_REGIONES
    )
    
    return fig
    
def boxplot(df, var, titulo_eje, usar_log):
    fig= px.box(
        df,
        x= var,
        y= 'Region',
        points= 'all',
        log_x= usar_log,
        title= f'Dispersión y Outliers: {titulo_eje}',
        hover_name= "Country",
        color= 'Region',
        color_discrete_map= COLORES_REGIONES
    )
    
    return fig