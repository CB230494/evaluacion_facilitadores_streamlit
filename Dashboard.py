import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# ==== Configuración desde secrets ====
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials_dict = st.secrets["gcp_service_account"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
client = gspread.authorize(credentials)

# ==== Cargar datos de Google Sheets ====
SHEET_NAME = "respuestas_facilitadores"
sheet = client.open(SHEET_NAME).sheet1
data = pd.DataFrame(sheet.get_all_records())

# ==== LIMPIAR NOMBRES DE COLUMNAS ====
data.columns = data.columns.str.strip()

# ==== Agregar ID ÚNICO basado en fila ====
data.insert(0, "ID", range(1, 1 + len(data)))

st.title("📈 Dashboard de Evaluaciones de Facilitadores")

# ==== Filtros ====
facilitadores = data["Facilitador"].unique()
facilitador_seleccionado = st.selectbox("Selecciona un Facilitador:", facilitadores)

# ==== Mostrar desempeño del facilitador seleccionado ====
df_facilitador = data[data["Facilitador"] == facilitador_seleccionado]

st.subheader(f"📋 Evaluaciones de {facilitador_seleccionado}")

# ==== Definimos las preguntas y nombres bonitos ====
preguntas = {
    "P1_Dominio_Tema": "Dominio del tema",
    "P2_Claridad_Exposición": "Claridad en la exposición",
    "P3_Organización_Contenidos": "Organización de contenidos",
    "P4_Uso_Presentación": "Uso de la presentación",
    "P5_Promueve_Participación": "Promueve participación",
    "P6_Aclaración_Dudas": "Aclaración de dudas",
    "P7_Metodología": "Metodología aplicada",
    "P8_Actitud_Respeto": "Actitud respetuosa",
    "P9_Duración_Adecuada": "Duración adecuada",
    "P10_Cumplimiento_Objetivos": "Cumplimiento de objetivos"
}

# ==== Graficar cada pregunta individual como pastel ====
for col, titulo in preguntas.items():
    st.write(f"### {titulo}")
    conteo = df_facilitador[col].value_counts().reindex(["Excelente", "Muy Bueno", "Bueno", "Regular", "Deficiente"], fill_value=0)
    fig = px.pie(
        names=conteo.index,
        values=conteo.values,
        title=f"{titulo} - Evaluaciones",
        hole=0.4
    )
    st.plotly_chart(fig, use_container_width=True)

# ==== Mostrar tabla de respuestas del facilitador ====
st.subheader("📄 Respuestas del Facilitador Seleccionado")
st.dataframe(df_facilitador)

# ==== Sección Total Global ====
st.title("🌎 Resumen General de Todo el Equipo")

# ==== Gráfica resumen general - Total evaluaciones ====
st.write("### Evaluaciones por Facilitador")

conteo_global = data["Facilitador"].value_counts()

fig_total = px.bar(
    x=conteo_global.index,
    y=conteo_global.values,
    labels={'x': 'Facilitador', 'y': 'Cantidad de Evaluaciones'},
    title="Cantidad Total de Evaluaciones por Facilitador"
)
st.plotly_chart(fig_total, use_container_width=True)

# ==== Tabla general completa ====
st.subheader("📋 Tabla Completa de Todas las Evaluaciones")
st.dataframe(data)

