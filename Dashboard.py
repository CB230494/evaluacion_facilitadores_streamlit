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

st.title("📈 Dashboard de Evaluaciones de Facilitadores")

# ==== Filtros ====
facilitadores = data["Facilitador"].unique()
facilitador_seleccionado = st.selectbox("Selecciona un Facilitador:", facilitadores)

# ==== Mostrar desempeño del facilitador seleccionado ====
df_facilitador = data[data["Facilitador"] == facilitador_seleccionado]

st.subheader(f"Evaluaciones de {facilitador_seleccionado}")

# ==== Graficar cada pregunta ====
preguntas = {
    "P1_Dominio_Tema": "Dominio del tema",
    "P2_Claridad_Exposición": "Claridad en la exposición",
    "P3_Organización_Contenidos": "Organización de contenidos",
    "P4_Uso_Presentación": "Uso de presentación",
    "P5_Promueve_Participación": "Promueve participación",
    "P6_Aclaración_Dudas": "Aclaración de dudas",
    "P7_Metodología": "Metodología empleada",
    "P8_Actitud_Respeto": "Actitud respetuosa y motivadora",
    "P9_Duración_Adecuada": "Duración de actividades",
    "P10_Cumplimiento_Objetivos": "Cumplimiento de objetivos",
}

for col, titulo in preguntas.items():
    fig = px.histogram(df_facilitador, x=col, title=titulo)
    st.plotly_chart(fig, use_container_width=True)

# ==== Mostrar tabla completa para control ====
st.subheader("📄 Respuestas Enviadas")
st.dataframe(df_facilitador)

# ==== Eliminar entradas manualmente (extra) ====
st.warning("⚠️ Recuerda que para eliminar respuestas duplicadas debes hacerlo directamente en Google Sheets.")
