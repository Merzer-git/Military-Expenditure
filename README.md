# Military Expenditure Analysis

## 📊 Descripción

Breve descripción de tu proyecto: qué es, qué datos analiza y cuál es el objetivo principal.

**Ejemplo:** Este proyecto analiza la evolución del gasto militar a nivel mundial durante los últimos 75 años, identificando patrones regionales y tendencias temporales.

---

## 🎯 Características

- Análisis de variables cualitativas
- Análisis de variables cuantitativas
- Visualización global de datos
- Calculadora de probabilidades
- Inferencia estadística
- Laboratorio temporal

---

## 📋 Requisitos

- Python 3.8+
- Streamlit
- Pandas
- Plotly
- (Agregar otros según necesites)

---

## ⚙️ Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone <url-del-repositorio>
   cd Military-Expenditure
   ```

2. **Crear entorno virtual:**
   ```bash
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1  # En Windows
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Uso

Ejecutar la aplicación:

```bash
streamlit run Home.py
```

La app se abrirá en `http://localhost:8501`

---

## 📁 Estructura del Proyecto

```
Military-Expenditure/
├── Home.py                 # Página principal
├── pages/                  # Páginas de análisis
│   ├── 1_Análisis_de_Variables_Cualitativas.py
│   ├── 2_Análisis_de_Variables_Cuantitativas.py
│   ├── 3_Panorama_Global.py
│   └── ...
├── src/                    # Módulos y utilidades
│   ├── clase_analizador.py
│   ├── datos.py
│   └── iso_countries.py
├── data/                   # Datos del proyecto
├── static/                 # Archivos estáticos (iconos, etc.)
└── requirements.txt        # Dependencias
```

---

## 📊 Páginas Disponibles

| Página | Descripción |
|--------|-------------|
| **Análisis de Variables Cualitativas** | Explora países y eras |
| **Análisis de Variables Cuantitativas** | Estadísticas y distribuciones |
| **Panorama Global** | Visualización mundial de datos |
| **Calculadora de Probabilidades** | Herramienta de cálculos |
| **Inferencia Estadística** | Análisis estadísticos avanzados |
| **Laboratorio Temporal** | Análisis de series temporales |

---

## 📝 Notas

- Agregar información sobre los datos utilizados
- Mencionar las fuentes de datos
- Describir el período de análisis

---

## 👤 Autor

Tu nombre

---

## 📄 Licencia

Especificar la licencia del proyecto (MIT, GPL, etc.)
