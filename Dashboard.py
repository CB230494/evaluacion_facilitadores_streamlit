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

# ==== Agregar ID único ====
data.insert(0, "ID", range(1, 1 + len(data)))

st.title("📈 Dashboard de Evaluaciones de Facilitadores")

# ==== Filtro de facilitadores ====
opciones_facilitador = ["Todos"] + sorted(data["Facilitador"].unique().tolist())
facilitador_seleccionado = st.selectbox("Selecciona un Facilitador:", opciones_facilitador)

# ==== Selección de datos según filtro ====
if facilitador_seleccionado == "Todos":
    df_filtrado = data.copy()
else:
    df_filtrado = data[data["Facilitador"] == facilitador_seleccionado]

st.subheader(f"📋 Evaluaciones de: {facilitador_seleccionado}")

# ==== Definir las preguntas ====
preguntas = {
    "P1_Dominio_Tema": "Dominio del tema",
    "P2_Claridad_Exposición": "Claridad en la exposición",
    "P3_Organización_Contenidos": "Organización de contenidos",
    "P4_Uso_Presentación": "Uso de presentación",
    "P5_Promueve_Participación": "Promueve participación",
    "P6_Aclaración_Dudas": "Aclaración de dudas",
    "P7_Metodología": "Metodología aplicada",
    "P8_Actitud_Respeto": "Actitud respetuosa",
    "P9_Duración_Adecuada": "Duración adecuada",
    "P10_Cumplimiento_Objetivos": "Cumplimiento de objetivos"
}

# ==== Graficar preguntas ====
for i, (col, titulo) in enumerate(preguntas.items()):
    st.write(f"### {titulo}")
    conteo = df_filtrado[col].value_counts().reindex(["Excelente", "Muy Bueno", "Bueno", "Regular", "Deficiente"], fill_value=0)

    if i % 2 == 0:
        # Gráfico tipo pastel
        fig = px.pie(
            names=conteo.index,
            values=conteo.values,
            title=f"{titulo} (Gráfico de Pastel)",
            hole=0.4
        )
    else:
        # Gráfico tipo barra
        fig = px.bar(
            x=conteo.index,
            y=conteo.values,
            labels={'x': 'Respuesta', 'y': 'Cantidad'},
            title=f"{titulo} (Gráfico de Barras)"
        )
        fig.update_layout(yaxis=dict(dtick=1))  # Para que suba de 1 en 1
    
    st.plotly_chart(fig, use_container_width=True)

# ==== Mostrar tabla de respuestas ====
st.subheader("📄 Respuestas Registradas")
st.dataframe(df_filtrado)

# ==== Gráfico resumen de evaluaciones por facilitador ====
if facilitador_seleccionado == "Todos":
    st.subheader("🌎 Resumen General del Equipo Evaluador")
    conteo_global = data["Facilitador"].value_counts()
    fig_total = px.bar(
        x=conteo_global.index,
        y=conteo_global.values,
        labels={'x': 'Facilitador', 'y': 'Cantidad de Evaluaciones'},
        title="Total de Evaluaciones por Facilitador"
    )
    fig_total.update_layout(yaxis=dict(dtick=1))
    st.plotly_chart(fig_total, use_container_width=True)
