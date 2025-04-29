import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# ==== Configuración de conexión desde secrets ====
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials_dict = st.secrets["gcp_service_account"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
client = gspread.authorize(credentials)

# ==== Cargar datos de Google Sheets ====
SHEET_NAME = "respuestas_facilitadores"
sheet = client.open(SHEET_NAME).sheet1
data = pd.DataFrame(sheet.get_all_records())

# ==== LIMPIAR nombres de columnas ====
data.columns = data.columns.map(str).str.strip()

# ==== EXPLOTAR facilitadores múltiples ====
data["Facilitador"] = data["Facilitador"].str.split(",\s*")  # Separa múltiples nombres
data = data.explode("Facilitador")                           # Crea filas separadas
data["Facilitador"] = data["Facilitador"].str.strip()        # Limpia espacios

# ==== Agregar ID único (opcional) ====
if "ID" not in data.columns:
    data.insert(0, "ID", range(1, 1 + len(data)))

# ==== Título Principal ====
st.title("📈 Dashboard de Evaluaciones de Facilitadores")

# ==== Filtro de facilitadores ====
opciones_facilitador = ["Todos"] + sorted(data["Facilitador"].unique().tolist())
facilitador_seleccionado = st.selectbox("Selecciona un Facilitador:", opciones_facilitador)

# ==== Filtrar datos según selección ====
if facilitador_seleccionado == "Todos":
    df_filtrado = data.copy()
else:
    df_filtrado = data[data["Facilitador"] == facilitador_seleccionado]

# ==== Subtítulo principal ====
st.subheader(f"📋 Evaluaciones de: {facilitador_seleccionado}")

# ==== Desglose personalizado para facilitador ====
if facilitador_seleccionado != "Todos":
    total_respuestas_facilitador = df_filtrado.shape[0]
    st.markdown(
        f"""
        <div style='display:flex; align-items:center; gap:10px; margin-bottom:10px;'>
            <img src='https://cdn-icons-png.flaticon.com/512/3595/3595455.png' width='20'/>
            <span style='font-size:19px'><strong>Total de evaluaciones para el facilitador {facilitador_seleccionado} en los meses registrados:</strong> {total_respuestas_facilitador}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

# ==== Definir preguntas y nombres bonitos ====
preguntas = {
    "P1_Dominio_Tema": "📚 Dominio del tema",
    "P2_Claridad_Exposición": "🎤 Claridad en la exposición",
    "P3_Organización_Contenidos": "🧠 Organización de contenidos",
    "P4_Uso_Presentación": "🖥️ Uso de presentación",
    "P5_Promueve_Participación": "🤝 Promueve participación",
    "P6_Aclaración_Dudas": "❓ Aclaración de dudas",
    "P7_Metodología": "🛠️ Metodología aplicada",
    "P8_Actitud_Respeto": "🤗 Actitud respetuosa",
    "P9_Duración_Adecuada": "⏳ Duración adecuada",
    "P10_Cumplimiento_Objetivos": "🎯 Cumplimiento de objetivos"
}

# ==== Graficar cada pregunta ====
for i, (col, titulo) in enumerate(preguntas.items()):
    conteo = df_filtrado[col].value_counts().reindex(["Excelente", "Muy Bueno", "Bueno", "Regular", "Deficiente"], fill_value=0)

    if i % 2 == 0:
        # Gráfico tipo pastel
        fig = px.pie(
            names=conteo.index,
            values=conteo.values,
            title=titulo,
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_traces(
            textinfo='percent+label',
            pull=[0.05 for _ in conteo.index],
            textposition='inside'
        )
        fig.update_layout(showlegend=True, title_font_size=24)
    else:
        # Gráfico de barras
        fig = px.bar(
            x=conteo.index,
            y=conteo.values,
            labels={'x': 'Respuesta', 'y': 'Cantidad'},
            title=titulo,
            color=conteo.index,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(
            yaxis=dict(dtick=1),
            showlegend=False,
            title_font_size=24
        )

    st.plotly_chart(fig, use_container_width=True)

# ==== Mostrar tabla de respuestas ====
st.subheader("📄 Respuestas Registradas")
st.dataframe(df_filtrado)

# ==== Resumen general si se selecciona "Todos" ====
if facilitador_seleccionado == "Todos":
    st.title("🌎 Resumen General del Equipo Evaluador")

    conteo_global = data["Facilitador"].value_counts()
    fig_total = px.bar(
        x=conteo_global.index,
        y=conteo_global.values,
        labels={'x': 'Facilitador', 'y': 'Cantidad de Evaluaciones'},
        title="Total de Evaluaciones por Facilitador",
        color=conteo_global.index,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_total.update_layout(
        yaxis=dict(dtick=1),
        showlegend=False,
        title_font_size=24
    )
    st.plotly_chart(fig_total, use_container_width=True)

