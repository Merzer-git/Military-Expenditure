import scipy.stats as stats
from scipy.stats import shapiro, kstest, chi2_contingency
import numpy as np

def shapiro_wilk(data):
    stat, p_value = shapiro(data)
    
    mu, sigma = stats.norm.fit(data)
    return {
        'estadistico': stat,
        'p-valor': p_value,
        'parametros': (mu, sigma),
        'dist_scipy': 'norm'
    }

def kolmogorov_smirnov(data, distribucion):
    scipy_dist_name = None
    parametros = None
    
    if distribucion == 'Exponencial':
        parametros = stats.expon.fit(data)
        scipy_dist_name = 'expon'
    elif distribucion == 'Uniforme':
        parametros = stats.uniform.fit(data)
        scipy_dist_name = 'uniform'
    elif distribucion == 'Pareto':
        parametros = stats.pareto.fit(data) #DEVUELVE TRES PARAMETROS
        scipy_dist_name = 'pareto'
        
    stat, p_value = stats.kstest(data, scipy_dist_name, parametros)
    
    return {
        'estadistico': stat,
        'p-valor': p_value,
        'parametros': parametros,
        'dist_scipy': scipy_dist_name
    }