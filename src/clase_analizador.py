import numpy as np
import pandas as pd

class Analizador_Estadistico:
    def __init__(self, df):
        self.__df = df

    def filtrar_datos(self, var, year):
        df_filtrado = self.__df[self.__df['Year'] == year].copy() if year else self.__df.copy()
        serie = df_filtrado[var]
        serie_limpia = serie.replace([np.inf, -np.inf], np.nan).dropna()
        
        return serie_limpia
    
    def generate_resumen(self, var, year):
        datos = self.filtrar_datos(var, year)

        if datos.empty:
            return None
        
        q1 = datos.quantile(0.25)
        q3 = datos.quantile(0.75)
        iqr = q3- q1

        resumen = {
            "n": len(datos),
            "media": datos.mean(),
            "mediana": datos.median(),
            "var": datos.var(),
            "std": datos.std(),
            "cv": datos.std() / datos.mean() if datos.mean() != 0 else 0,
            "min": datos.min(),
            "max": datos.max(),
            "q1": q1,
            "q2": datos.quantile(0.5),
            "q3": q3,
            "iqr": iqr,
            "lim_inf": q1 - 1.5*iqr,
            "lim_sup": q3 + 1.5*iqr,
            "skew": datos.skew(),
            "kurt": datos.kurt(),
            #DECILES
            "d1": datos.quantile(0.1),
            "d5": datos.quantile(0.5),
            "d9": datos.quantile(0.9),
            #CENTILES
            "c99": datos.quantile(0.99)
        }

        return resumen
    
    def format_resumen(self, stats_dict, var):
        if not stats_dict:
            return "No hay información suficiente para analizar."
        
        return f"""
        ~~~ Análisis de {var} ~~~

        Tendencia Central:
        - Media:        {stats_dict['media']:,.2f}
        - Mediana:      {stats_dict['mediana']:,.2f}

        Dispersión:
        - Varianza:     {stats_dict['var']:,.2f}
        - Desv. Std:    {stats_dict['std']:,.2f}
        - CV:           {stats_dict['cv']:,.2f}

        Analisis de los Cuantiles:
            ~~~ El mundo Típico ~~~
            - Q1 (Percentil 25):     {stats_dict['q1']:,.2f}
            - Q2 (Mediana):          {stats_dict['mediana']:,.2f}
            - Q3 (Percentil 75):     {stats_dict['q3']:,.2f}
            - Rango Central (IQR):   {stats_dict['q3']:,.2f} - {stats_dict['q1']:,.2f} = {stats_dict['iqr']:,.2f}
            - Limite Inferior:       {stats_dict['lim_inf']:,.2f}
            - Limite Superior:       {stats_dict['lim_sup']:,.2f}

            ~~~ Las Potencias ~~~
            - Top 10%, D9 (Percentil 90):   {stats_dict['d9']:,.2f}
            - Top 1%, C99 (Percentil 99):   {stats_dict['c99']:,.2f}

            - Maximo Real:  {stats_dict['max']:,.2f}
            - Minimo Real:  {stats_dict['min']:,.2f}

        Forma:
        - Asimetría:    {stats_dict['skew']:,.2f}
        - Curtosis:     {stats_dict['kurt']:,.2f}
        """