import statsmodels.api as sm
import pandas as pd

def regresion_lineal(df, col_X, col_Y):
    datos = df[[col_X, col_Y]].copy()
    datos = datos.dropna()
    
    Y = datos[col_Y]
    X = datos[col_X]
    
    X = sm.add_constant(X)
    
    modelo = sm.OLS(Y,X).fit()
    
    return modelo