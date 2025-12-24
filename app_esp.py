# ============================================
# ANALIZADOR DE SENTIMIENTOS CON VOZ (WEB READY)
# ============================================

import streamlit as st 
from textblob import TextBlob 
from deep_translator import GoogleTranslator 
from streamlit_mic_recorder import speech_to_text # Nueva librería para voz en web

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Analizador de Sentimientos IA",
    page_icon="😊",
    layout="wide"
)

st.title("😊 Analizador de Sentimientos en Español")
st.markdown("""
Escribe tu texto o **usa tu voz** para analizar el sentimiento.
La IA detectará si es positivo, negativo o neutral.
""")

st.divider()

# --- SECCIÓN 1: ENTRADA POR VOZ ---
st.subheader("🎤 Entrada por Voz")

# Componente que activa el micrófono en el navegador (Streamlit Cloud compatible)
texto_voz = speech_to_text(
    language='es', 
    start_prompt="Haga clic para hablar 🎤", 
    stop_prompt="Detener grabación ⏹️", 
    key='recorder'
)

if texto_voz:
    st.success("✅ ¡Audio reconocido con éxito!")
    st.session_state['texto_para_analizar'] = texto_voz

# --- SECCIÓN 2: ENTRADA DE TEXTO ---
st.subheader("✍️ Entrada de Texto")

# Recuperar texto de voz o usar el predeterminado
if 'texto_para_analizar' in st.session_state:
    texto_predeterminado = st.session_state['texto_para_analizar']
else:
    texto_predeterminado = "¡Estoy muy feliz de aprender inteligencia artificial!"

texto_usuario = st.text_area(
    label="**Escribe o pega tu texto aquí:**",
    value=texto_predeterminado,
    height=150
)

# --- SECCIÓN 3: ANÁLISIS DE SENTIMIENTOS ---
st.divider()
st.subheader("📊 Análisis de Sentimientos")

if st.button("🔍 **Analizar Sentimiento**", type="primary", use_container_width=True):
    if texto_usuario:
        with st.spinner("Analizando..."):
            try:
                # PASO 1: TRADUCCIÓN
                traductor = GoogleTranslator(source='es', target='en')
                texto_traducido = traductor.translate(texto_usuario)
                
                # PASO 2: ANÁLISIS
                analisis = TextBlob(texto_traducido)
                polaridad = analisis.sentiment.polarity
                subjetividad = analisis.sentiment.subjectivity
                
                # PASO 3: MOSTRAR RESULTADOS
                st.success("✅ **Análisis completado!**")
                col_res1, col_res2 = st.columns(2)
                
                with col_res1:
                    st.markdown("#### 📈 Polaridad")
                    if polaridad > 0.1:
                        etiqueta, color = "😊 MUY POSITIVO", "green"
                    elif polaridad < -0.1:
                        etiqueta, color = "😠 NEGATIVO", "red"
                    else:
                        etiqueta, color = "😐 NEUTRAL", "gray"
                    
                    st.progress((polaridad + 1) / 2, text=f"{etiqueta} ({polaridad:.2f})")

                with col_res2:
                    st.markdown("#### 🧠 Subjetividad")
                    st.progress(subjetividad, text=f"Opinión personal: {(subjetividad * 100):.0f}%")

                st.info(f"**Traducción interna:** {texto_traducido}")

            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Por favor, ingresa texto o usa la voz.")

# --- SECCIÓN 4: INFORMACIÓN ---
st.divider()
with st.expander("📚 Acerca de esta aplicación"):
    st.markdown("""
    Esta aplicación utiliza **TextBlob** para el análisis de sentimiento tras traducir 
    el texto con **Google Translate**. El micrófono funciona mediante la API Web del navegador.
    """)