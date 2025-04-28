import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json
import qrcode
from io import BytesIO

# ==== Configuración desde secrets ====
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials_dict = st.secrets["gcp_service_account"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
client = gspread.authorize(credentials)

# Nombre de tu Google Sheets
SHEET_NAME = "respuestas_facilitadores"
sheet = client.open(SHEET_NAME).sheet1

# ==== Función para enviar datos ====
def enviar_respuesta(respuesta):
    sheet.append_row(respuesta)

# ==== Formulario en Streamlit ====
st.title("📋 Formulario de Evaluación de Facilitadores")

# ==== Mostrar QR debajo del título ====
link = "https://evaluacionfacilitadoresapp-eu7f2rvkprw5hxjuzuqdez.streamlit.app/"

# Crear código QR
qr = qrcode.make(link)
buf = BytesIO()
qr.save(buf)

# Mostrar imagen del QR
st.image(buf.getvalue(), caption="🔗 Escanea para abrir el Formulario", width=150)
# (Aquí seguiría todo tu formulario como estaba...)


with st.form(key='evaluacion_form'):
    nombre = st.text_input("Nombre del Participante:")
    puesto = st.text_input("Puesto:")
    delegacion = st.text_input("Delegación:")
    facilitador = st.selectbox("Facilitador:", [
        "Esteban Cordero Solórzano", "Pamela Montero Pérez", "Jannia Valles Brizuela",
        "Manfred Rivera Meneses", "Carlos Castro Loaiciga", "Adrián Alvarado García", "Luis Vásquez Solís"
    ])
    fecha_taller = st.date_input("Fecha del Taller:")

    opciones = ["Excelente", "Muy Bueno", "Bueno", "Regular", "Deficiente"]

    p1 = st.radio("¿El facilitador demostró dominio del tema tratado?", opciones)
    p2 = st.radio("¿La exposición del facilitador fue clara y comprensible?", opciones)
    p3 = st.radio("¿El facilitador organizó de manera adecuada los contenidos del taller?", opciones)
    p4 = st.radio("¿El facilitador utilizó adecuadamente la presentación como apoyo?", opciones)
    p5 = st.radio("¿El facilitador promovió la participación activa de los asistentes?", opciones)
    p6 = st.radio("¿El facilitador aclaró dudas de manera efectiva?", opciones)
    p7 = st.radio("¿La metodología fue adecuada para alcanzar los objetivos?", opciones)
    p8 = st.radio("¿El facilitador mantuvo una actitud respetuosa y motivadora?", opciones)
    p9 = st.radio("¿La duración de las actividades fue adecuada?", opciones)
    p10 = st.radio("¿Se cumplieron los objetivos planteados al inicio del taller?", opciones)

    aspectos_positivos = st.text_area("Aspectos positivos del desempeño del facilitador:")
    sugerencias = st.text_area("Sugerencias para mejorar futuras sesiones:")

    submit_button = st.form_submit_button(label='Enviar Evaluación')

    if submit_button:
        respuesta = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            nombre, puesto, delegacion, facilitador, str(fecha_taller),
            p1, p2, p3, p4, p5, p6, p7, p8, p9, p10,
            aspectos_positivos, sugerencias
        ]
        enviar_respuesta(respuesta)
        st.success("✅ ¡Evaluación enviada correctamente!")
